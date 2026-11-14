#!/usr/bin/env bash
# One-shot setup: tools, Databricks login, local .venv, Unity Catalog bootstrap, .env, sync.
# Safe to re-run. Usage:
#   ./setup.sh                       # interactive (asks for workspace URL on first run)
#   DATABRICKS_HOST=https://adb-....azuredatabricks.net ./setup.sh
set -euo pipefail
cd "$(dirname "$0")"

PROFILE="azure-ml"          # OAuth profile used by CLI, bundle and VS Code extension
PAT_PROFILE="azure-ml-pat"  # token profile used by local notebook runs (Feature Engineering client)
SCHEMA="ml_deployment"
export PATH="$HOME/.local/bin:$PATH"

say()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- 1. tools
say "Checking tools"
if ! command -v databricks >/dev/null; then
  echo "Installing Databricks CLI into ~/.local/bin (no sudo)"
  mkdir -p "$HOME/.local/bin"; tmp=$(mktemp -d)
  V=$(curl -fsSL https://api.github.com/repos/databricks/cli/releases/latest | grep -m1 '"tag_name"' | cut -d'"' -f4 | sed 's/^v//')
  case "$(uname -m)" in x86_64) ARCH=amd64;; aarch64|arm64) ARCH=arm64;; *) warn "unsupported CPU"; exit 1;; esac
  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
  F="databricks_cli_${V}_${OS}_${ARCH}.zip"
  curl -fsSL -o "$tmp/$F" "https://github.com/databricks/cli/releases/download/v${V}/$F"
  curl -fsSL -o "$tmp/sums" "https://github.com/databricks/cli/releases/download/v${V}/databricks_cli_${V}_SHA256SUMS"
  (cd "$tmp" && grep " $F\$" sums | sha256sum -c -)
  unzip -q -o "$tmp/$F" -d "$tmp/out" && install -m 755 "$tmp/out/databricks" "$HOME/.local/bin/databricks"
  rm -rf "$tmp"
fi
if ! command -v uv >/dev/null; then
  echo "Installing uv into ~/.local/bin"
  curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
fi
databricks -v; uv --version

# ---------------------------------------------------------------- 2. login
say "Databricks authentication (profile: $PROFILE)"
if ! databricks current-user me -p "$PROFILE" >/dev/null 2>&1; then
  HOST="${DATABRICKS_HOST:-}"
  [ -z "$HOST" ] && read -rp "Workspace URL (e.g. https://adb-123.4.azuredatabricks.net): " HOST
  databricks auth login --host "$HOST" --profile "$PROFILE"
fi
USER_EMAIL=$(databricks current-user me -p "$PROFILE" -o json | python3 -c 'import json,sys;print(json.load(sys.stdin)["userName"])')
HOST=$(databricks auth describe -p "$PROFILE" -o json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("details",{}).get("host") or d.get("host"))')
echo "Logged in as $USER_EMAIL on $HOST"

# ---------------------------------------------------------------- 3. local venv
say "Local Python environment (.venv, Python 3.12 = serverless env v5)"
[ -d .venv ] || uv venv .venv --python 3.12
uv pip install --python .venv -q pip nbformat ipykernel databricks-connect \
  "mlflow==3.12.0" databricks-sdk databricks-feature-engineering scikit-learn pandas optuna
echo "Installed: $(.venv/bin/python -c 'from importlib.metadata import version as v;print("databricks-connect",v("databricks-connect"),"| mlflow",v("mlflow"))')"

# ---------------------------------------------------------------- 4. Unity Catalog bootstrap
say "Unity Catalog bootstrap"
CATALOG=$(databricks settings default-namespace get -p "$PROFILE" -o json 2>/dev/null \
  | python3 -c 'import json,sys;print(json.load(sys.stdin)["namespace"]["value"])' 2>/dev/null || echo workspace)
WAREHOUSE=$(databricks warehouses list -p "$PROFILE" -o json | python3 -c '
import json,sys;w=json.load(sys.stdin)
w.sort(key=lambda x:(x.get("state")!="RUNNING", not x.get("enable_serverless_compute",False)))
print(w[0]["id"] if w else "")')
[ -n "$WAREHOUSE" ] || { warn "No SQL warehouse found; create one (Serverless, 2X-Small) and re-run."; exit 1; }
echo "Default catalog: $CATALOG | SQL warehouse: $WAREHOUSE"

run_sql() {
  databricks api post /api/2.0/sql/statements -p "$PROFILE" --json "$(python3 -c '
import json,sys;print(json.dumps({"warehouse_id":sys.argv[1],"statement":sys.argv[2],"wait_timeout":"50s"}))' "$WAREHOUSE" "$1")" \
  | python3 -c 'import json,sys;d=json.load(sys.stdin);s=d["status"]
if s["state"]!="SUCCEEDED": sys.exit("SQL failed: "+s.get("error",{}).get("message",""))'
}

# Marketplace shares the course reads from (get them from Databricks Marketplace, free)
declare -A SHARES=(
  [telco]=databricks_telco_customer_dataset
  [cdc_diabetes]=databricks_diabetes_health_indicators_dataset
  [ca_housing]=databricks_california_housing_data
  [banking]=databricks_bank_loan_modelling_dataset
)
CATALOGS=$(databricks catalogs list -p "$PROFILE" -o json | python3 -c 'import json,sys;[print(c["name"]) for c in json.load(sys.stdin)]')
ROWS="('username','$USER_EMAIL'),('catalog_name','$CATALOG'),('schema_name','$SCHEMA'),"
ROWS+="('pseudonym','$(echo "${USER_EMAIL%@*}" | tr '._-' '   ')'),"
ROWS+="('paths.working_dir','/Volumes/$CATALOG/$SCHEMA/working_dir')"
for key in "${!SHARES[@]}"; do
  share=${SHARES[$key]}
  if grep -qx "$share" <<<"$CATALOGS"; then
    echo "  [ok]      $share"
    [[ $key == telco || $key == cdc_diabetes ]] && ROWS+=",('paths.datasets.$key','/Volumes/$share/v01'),('datasets.$key','$share')"
  else
    warn "missing $share: add it from Databricks Marketplace (Get instant access), then re-run"
  fi
done

run_sql "CREATE SCHEMA IF NOT EXISTS $CATALOG.ops COMMENT 'DBAcademy course metadata'"
run_sql "CREATE SCHEMA IF NOT EXISTS $CATALOG.$SCHEMA COMMENT 'Databricks Academy ML courses'"
run_sql "CREATE VOLUME IF NOT EXISTS $CATALOG.$SCHEMA.working_dir"
run_sql "CREATE OR REPLACE TABLE $CATALOG.ops.meta (key STRING, value STRING)"
run_sql "INSERT INTO $CATALOG.ops.meta VALUES $ROWS"
echo "Created $CATALOG.ops.meta, schema $CATALOG.$SCHEMA and volume working_dir"

# ---------------------------------------------------------------- 5. PAT profile + .env
say "Local run configuration"
if ! databricks current-user me -p "$PAT_PROFILE" >/dev/null 2>&1; then
  read -rp "Create a 90-day personal access token for local Feature Engineering runs? [Y/n] " ans
  if [[ ! $ans =~ ^[Nn] ]]; then
    TOKEN=$(databricks tokens create --comment vscode-ml-course --lifetime-seconds 7776000 -p "$PROFILE" -o json \
      | python3 -c 'import json,sys;print(json.load(sys.stdin)["token_value"])')
    printf '\n[%s]\nhost  = %s\ntoken = %s\n' "$PAT_PROFILE" "$HOST" "$TOKEN" >> "$HOME/.databrickscfg"
    unset TOKEN; chmod 600 "$HOME/.databrickscfg"; echo "Saved profile $PAT_PROFILE"
  fi
fi
LOCAL_PROFILE=$PAT_PROFILE
databricks current-user me -p "$PAT_PROFILE" >/dev/null 2>&1 || LOCAL_PROFILE=$PROFILE
sed -e "s#^DATABRICKS_CONFIG_PROFILE=.*#DATABRICKS_CONFIG_PROFILE=$LOCAL_PROFILE#" \
    -e "s#<your-email>#$USER_EMAIL#" .env.example > .env
echo "Wrote .env (profile $LOCAL_PROFILE)"

# ---------------------------------------------------------------- 6. sync
say "Syncing course to the workspace"
databricks bundle validate >/dev/null
databricks bundle sync --full | tail -1
echo "Files: /Workspace/Users/$USER_EMAIL/.bundle/ml-deployment-course/dev/files"

say "Done. Open this folder in VS Code, select the .venv interpreter, and run notebooks
    with right-click -> 'Run File as Workflow' (or open them in the Databricks UI)."
