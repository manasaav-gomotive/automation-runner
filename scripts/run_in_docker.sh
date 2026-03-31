#!/usr/bin/env bash
set -euo pipefail

: "${RUNNER_IMAGE:?RUNNER_IMAGE must be set}"
: "${ENVIRONMENT:?ENVIRONMENT must be set}"
: "${REGION:?REGION must be set}"
: "${TARGET_SUITE:?TARGET_SUITE must be set}"

tmp_env_file="$(mktemp)"
cleanup() {
  rm -f "${tmp_env_file}"
}
trap cleanup EXIT

env | sort | awk -F= '
  /^(AWS_|MOTIVE_|motive_|FC_|MARQETA_|TWILIO_|VRT_|COMMENT=|API_TOKEN=|SLACK_WEBHOOK_URL=|ENVIRONMENT=|REGION=|TARGET_SUITE=|MOTIVE_TEST_REPORT_BUCKET=)/ {
    print
  }
' > "${tmp_env_file}"

docker run --rm \
  --env-file "${tmp_env_file}" \
  -e RUNNER_DIR=/opt/automation-runner \
  -e FRAMEWORK_DIR=/opt/motive-testing-automationframework \
  "${RUNNER_IMAGE}" \
  bash -lc '
    set -euo pipefail
    export PROJECT_DIR="${FRAMEWORK_DIR}"
    export BASH_ENV="${FRAMEWORK_DIR}/.ci/ci-test-helper.sh"
    source "${BASH_ENV}"
    /opt/automation-runner/scripts/generate_framework_env.sh
    download_test_framework_settings "${ENVIRONMENT}" "${REGION}"
    test_exit=0
    cd /opt/automation-runner
    python3 runner.py "${ENVIRONMENT}" "${TARGET_SUITE}" || test_exit=$?
    cd "${FRAMEWORK_DIR}"
    report_id=$(date +%s)
    upload_intellij_xml_report "${report_id}" "api" || true
    upload_api_usage_log "${report_id}" || true
    generate_and_upload_allure_report "${report_id}" "api" || true
    exit "${test_exit}"
  '
