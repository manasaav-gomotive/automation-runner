#!/usr/bin/env bash
set -euo pipefail

export RUNNER_DIR="${RUNNER_DIR:-/opt/automation-runner}"
export FRAMEWORK_DIR="${FRAMEWORK_DIR:-/opt/motive-testing-automationframework}"
export PROJECT_DIR="${PROJECT_DIR:-${FRAMEWORK_DIR}}"
export BASH_ENV="${BASH_ENV:-${FRAMEWORK_DIR}/.ci/ci-test-helper.sh}"

if [[ -f "${BASH_ENV}" ]]; then
  # shellcheck disable=SC1090
  source "${BASH_ENV}"
fi

exec "$@"
