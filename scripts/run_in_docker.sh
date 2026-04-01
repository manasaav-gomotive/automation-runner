#!/usr/bin/env bash
set -euo pipefail

: "${RUNNER_IMAGE:?RUNNER_IMAGE must be set}"
: "${ENVIRONMENT:?ENVIRONMENT must be set}"
: "${REGION:?REGION must be set}"
: "${SELECTED_SUITE:?SELECTED_SUITE must be set}"

tmp_env_file="$(mktemp)"
cleanup() {
  rm -f "${tmp_env_file}"
}
trap cleanup EXIT

env | sort | awk -F= '
  /^(AWS_|MOTIVE_|motive_|FC_|MARQETA_|TWILIO_|VRT_|COMMENT=|API_TOKEN=|SLACK_WEBHOOK_URL=|ENVIRONMENT=|REGION=|SELECTED_SUITE=|MOTIVE_TEST_REPORT_BUCKET=|AWS_REGION=)/ {
    print
  }
' > "${tmp_env_file}"

docker run --rm \
  --env-file "${tmp_env_file}" \
  "${RUNNER_IMAGE}" \
  bash -lc '
    set -euo pipefail
    export RUNNER_DIR="/opt/automation-runner"
    export FRAMEWORK_DIR="/opt/motive-testing-automationframework"
    export PROJECT_DIR="${FRAMEWORK_DIR}"
    export BASH_ENV="${FRAMEWORK_DIR}/.ci/ci-test-helper.sh"
    source "${BASH_ENV}"
    /opt/automation-runner/scripts/generate_framework_env.sh
    if [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
      download_test_framework_settings "${ENVIRONMENT}" "${REGION}"
    else
      echo "AWS credentials not configured; skipping download_test_framework_settings"
    fi
    cd /opt/automation-runner
    test_exit=0
    python3 runner.py "${ENVIRONMENT}" "${SELECTED_SUITE}" || test_exit=$?
    cd "${FRAMEWORK_DIR}"
    report_id=$(date +%s)
    upload_intellij_xml_report "${report_id}" "api" || true
    upload_api_usage_log "${report_id}" || true
    generate_and_upload_allure_report "${report_id}" "api" || true
    exit "${test_exit}"
  '
