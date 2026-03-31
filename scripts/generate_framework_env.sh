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

# The framework resolves placeholders against dotenv entries. We persist the
# injected runtime secrets here instead of hardcoding a fixed key list.
env | sort | awk -F= '
  /^(MOTIVE_|motive_|FC_|MARQETA_|TWILIO_|VRT_|COMMENT=)/ {
    print
  }
' > "${target_file}"

echo "Generated framework env file at ${target_file}"
