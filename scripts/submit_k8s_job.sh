#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_k8s_job.sh <environment> <selected_suite> [runner_image] [region]

Example:
  scripts/submit_k8s_job.sh staging safety.safetyDriverApp.* ghcr.io/manasaav-gomotive/automation-runner:latest us
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

ENVIRONMENT="$1"
SELECTED_SUITE="$2"
RUNNER_IMAGE="${3:-ghcr.io/manasaav-gomotive/automation-runner:latest}"
REGION="${4:-us}"
NAMESPACE="${K8S_NAMESPACE:-sqa}"
AWS_REGION="${AWS_REGION:-us-east-1}"
REPORT_BUCKET="${MOTIVE_TEST_REPORT_BUCKET:-motive-automated-test-report}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE_PATH="${REPO_ROOT}/k8s/job-runner.yaml"

if [[ ! -f "${TEMPLATE_PATH}" ]]; then
  echo "Job template not found at ${TEMPLATE_PATH}"
  exit 1
fi

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
}

suite_slug="$(slugify "${SELECTED_SUITE}")"
suite_slug="${suite_slug:0:38}"
job_name="automation-runner-${suite_slug:-suite}-$(date +%s)"

tmp_manifest="$(mktemp)"
cleanup() {
  rm -f "${tmp_manifest}"
}
trap cleanup EXIT

sed \
  -e "s|namespace: sqa|namespace: ${NAMESPACE}|g" \
  -e "s|__JOB_NAME__|${job_name}|g" \
  -e "s|__TARGET_LABEL__|${suite_slug:-suite}|g" \
  -e "s|__RUNNER_IMAGE__|${RUNNER_IMAGE}|g" \
  -e "s|__ENVIRONMENT__|${ENVIRONMENT}|g" \
  -e "s|__REGION__|${REGION}|g" \
  -e "s|__SELECTED_SUITE__|${SELECTED_SUITE}|g" \
  -e "s|__REPORT_BUCKET__|${REPORT_BUCKET}|g" \
  -e "s|__AWS_REGION__|${AWS_REGION}|g" \
  "${TEMPLATE_PATH}" > "${tmp_manifest}"

echo "Applying Kubernetes Job ${job_name} to namespace ${NAMESPACE}"
kubectl apply -n "${NAMESPACE}" -f "${tmp_manifest}"

cat <<EOF

Submitted job: ${job_name}

Useful commands:
  kubectl get jobs -n ${NAMESPACE}
  kubectl get pods -n ${NAMESPACE} -l job-name=${job_name}
  kubectl logs -n ${NAMESPACE} job/${job_name} -f
EOF
