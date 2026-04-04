# Automation Runner

`automation-runner` is the orchestration layer we use to run Motive API suites from GitHub Actions with less repeated setup work and better control over parallelism.

The current design has two execution paths:

- GitHub-hosted execution through [`run-tests.yml`](/Users/manasa.av/PycharmProjects/automation-runner/.github/workflows/run-tests.yml)
- Kubernetes scaffolding for namespace `sqa` through [`k8s/job-runner.yaml`](/Users/manasa.av/PycharmProjects/automation-runner/k8s/job-runner.yaml)

## What This Repo Does

- Resolves a user’s workflow selection into a concrete suite or class target
- Builds one shared Docker runtime image per workflow run
- Reuses that image across parallel matrix jobs so dependencies are not reinstalled in every shard
- Generates the framework `.env` file from injected secrets
- Runs the selected suite through [`runner.py`](/Users/manasa.av/PycharmProjects/automation-runner/runner.py)
- Uploads IntelliJ XML, API usage, and Allure reports after execution

## Repository Layout

```text
automation-runner/
├── .github/workflows/
│   ├── run-tests.yml
│   └── build-test-runner-image.yml
├── config/
│   └── suite_map.py
├── docker/
│   └── test-runner-entrypoint.sh
├── engine/
├── k8s/
│   ├── job-runner.yaml
│   └── secret-template.yaml
├── scripts/
│   ├── generate_framework_env.sh
│   ├── resolve_test_targets.py
│   ├── run_in_docker.sh
│   └── submit_k8s_job.sh
└── runner.py
```

## Current GitHub Workflow

The main workflow is [`run-tests.yml`](/Users/manasa.av/PycharmProjects/automation-runner/.github/workflows/run-tests.yml).

It is manual-only and supports these inputs:

- `branch`: framework branch or ref to test against
- `environment`: `staging` or `preview`
- `region`: region used for framework settings download
- `run_mode`: `single` or `group`
- `parallelization_level`: `suite` or `class`
- `pod`: top-level test pod
- `sub_package`: optional package override for single mode
- `suite_group`: curated group used when `run_mode=group`

### How Execution Works

1. `resolve-suites` checks out the framework repo and resolves the selected target set.
2. `build-runtime-image` builds a shared Docker image once for the workflow run.
3. `test` fans out a matrix and loads that same image in each shard.
4. Each shard runs the selected target inside the container using [`run_in_docker.sh`](/Users/manasa.av/PycharmProjects/automation-runner/scripts/run_in_docker.sh).

This is the main optimization in the current design:

- dependencies are installed once into the image
- parallel jobs reuse that image instead of rebuilding the environment independently

## Parallelization Modes

### Suite parallelization

When `parallelization_level=suite`, each matrix shard runs one suite target.

Examples:

- `single + safety.safetyDriverApp.*`
- `group + safety-core`

### Class parallelization

When `parallelization_level=class`, [`resolve_test_targets.py`](/Users/manasa.av/PycharmProjects/automation-runner/scripts/resolve_test_targets.py) discovers matching Java test classes under the framework repo and creates one matrix entry per class.

This is GitHub job-level parallelism, not in-process JUnit threading.

## Curated Groups

Curated groups are defined in [`resolve_test_targets.py`](/Users/manasa.av/PycharmProjects/automation-runner/scripts/resolve_test_targets.py).

Current groups:

- `safety-smoke`
  - `safety.settings`
  - `safety.publicApi.*`
- `safety-core`
  - `safety.settings`
  - `safety.publicApi.*`
  - `safety.reports.*`
- `safety-driver-subset`
  - `safety.settings`
  - `safety.safetyDriverApp.*`

Important note:

- [`suite_map.py`](/Users/manasa.av/PycharmProjects/automation-runner/config/suite_map.py) currently maps `safety.settings` to `com.gomotive.system.tests.safety.safetyDriverApp.*`

That means `safety.settings` is broader than the name suggests today.

## Recommended Workflow Inputs

### Run a single safety driver app package

- `environment`: `staging`
- `region`: `us`
- `run_mode`: `single`
- `parallelization_level`: `suite`
- `pod`: `safety`
- `sub_package`: `safety.safetyDriverApp.*`

### Run safety driver app classes in parallel

- `environment`: `staging`
- `region`: `us`
- `run_mode`: `single`
- `parallelization_level`: `class`
- `pod`: `safety`
- `sub_package`: `safety.safetyDriverApp.*`

### Run a curated group in parallel

- `environment`: `staging`
- `region`: `us`
- `run_mode`: `group`
- `parallelization_level`: `suite`
- `pod`: `safety`
- `sub_package`: leave empty
- `suite_group`: one of:
  - `safety-smoke`
  - `safety-core`
  - `safety-driver-subset`

## Runtime Image

The test runtime image is built from [`Dockerfile`](/Users/manasa.av/PycharmProjects/automation-runner/Dockerfile).

It contains:

- `automation-runner`
- `motive-testing-automationframework`
- Java 17
- Python 3
- AWS CLI
- runner scripts used by the workflow

The image layout assumes:

- runner code at `/opt/automation-runner`
- framework repo at `/opt/motive-testing-automationframework`

## Secrets and Framework Env

The framework `.env` file is generated inside the container by [`generate_framework_env.sh`](/Users/manasa.av/PycharmProjects/automation-runner/scripts/generate_framework_env.sh).

It writes:

- uppercase keys like `MOTIVE_AI_ELD_IDENTIFIER`
- lowercase aliases like `motive_ai_eld_identifier`

That aliasing is important because the framework resolves a mix of uppercase and lowercase placeholders.

The current workflow validates a base set of required secrets before execution, including:

- `MOTIVE_ADMIN_EMAIL`
- `MOTIVE_ADMIN_PASSWORD`
- `MOTIVE_WEBUSERNAMEPASSWORD`
- `MOTIVE_ELDAPIKEY_STAGING`
- `MOTIVE_MOBILEAPIAUTHORIZATIONKEY`
- `MOTIVE_TESTING_API_KEY_STAGING`
- `MOTIVE_INTERNAL_API_KEY_STAGING`
- `MOTIVE_AI_ELD_IDENTIFIER`
- `MOTIVE_SAFETY1_VEHICLE_ID`

Additional suite-specific secrets may still be needed depending on what package you run.

## Kubernetes Scaffolding

We also have the first K8s scaffolding checked in for namespace `sqa`.

Files:

- [`k8s/job-runner.yaml`](/Users/manasa.av/PycharmProjects/automation-runner/k8s/job-runner.yaml)
- [`k8s/secret-template.yaml`](/Users/manasa.av/PycharmProjects/automation-runner/k8s/secret-template.yaml)
- [`scripts/submit_k8s_job.sh`](/Users/manasa.av/PycharmProjects/automation-runner/scripts/submit_k8s_job.sh)

These are intended for manual cluster validation first, before wiring GitHub directly to submit Jobs.

Example:

```bash
scripts/submit_k8s_job.sh staging safety.safetyDriverApp.* ghcr.io/manasaav-gomotive/automation-runner:latest us
```

Useful follow-up commands:

```bash
kubectl get jobs -n sqa
kubectl get pods -n sqa
kubectl logs -n sqa job/<job-name> -f
```

## Local Usage

If you need to run the runner directly:

```bash
python3 runner.py staging safety.safetyDriverApp.*
```

For most team use, the GitHub workflow is the preferred path because it handles:

- target resolution
- image build
- secret injection
- parallel fan-out
- report generation

## Known Limitations

- `safety.settings` currently maps into the `safetyDriverApp` package and may pull in more tests than expected
- some suites depend on many environment-specific secret values and real test data
- the K8s path is scaffolded but not yet fully wired into GitHub as the primary execution backend
- some Docker build and framework fetch flows still depend on `GH_PAT`

## Next Likely Improvements

- narrow `safety.settings` to what the name actually implies
- reduce required secret surface for smoke-friendly suites
- mature the `sqa` Kubernetes execution path
- move image publishing to a stable registry flow and reuse it across runs
