#!/usr/bin/env bash
set -euo pipefail

FRAMEWORK_DIR="${FRAMEWORK_DIR:-${PROJECT_DIR:-}}"
if [[ -z "${FRAMEWORK_DIR}" ]]; then
  echo "FRAMEWORK_DIR or PROJECT_DIR must be set"
  exit 1
fi

target_dir="${FRAMEWORK_DIR}/gomotive-automation-framework/core/src/main/resources"
target_file="${target_dir}/.env"

mkdir -p "${target_dir}"

python3 - <<'PY' > "${target_file}"
import os

allowed_prefixes = ("MOTIVE_", "motive_", "FC_", "MARQETA_", "TWILIO_", "VRT_")
entries = []

for key, value in sorted(os.environ.items()):
    if key == "COMMENT" or key.startswith(allowed_prefixes):
        entries.append((key, value))
        if key.isupper() and key != "COMMENT":
            entries.append((key.lower(), value))

seen = set()
for key, value in entries:
    if key in seen:
        continue
    seen.add(key)
    print(f"{key}={value}")
PY

echo "Generated framework env file at ${target_file}"
