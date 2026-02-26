<<<<<<< HEAD
# automation-runner
=======
# Automation Runner

A Python-based test automation runner that executes test suites using Gradle with support for multiple environments, retry logic, and failure classification.

## Overview

The Automation Runner is designed to execute test suites from a Gradle-based test framework. It provides a simple command-line interface to run specific test suites across different environments with configurable retry mechanisms and failure handling.

## Features

- **Environment-based Configuration**: Support for multiple test environments (e.g., staging, production)
- **Suite Mapping**: Predefined mappings for common test suites (vehicle, driver, asset, session, group, devices, login)
- **Retry Logic**: Automatic retry of failed tests with configurable retry count and delay
- **Failure Classification**: Intelligent parsing and classification of test failures
- **Gradle Integration**: Seamless integration with Gradle test execution
- **Parallel Execution**: Configurable parallelism for test execution

## Project Structure

```
automation-runner/
├── runner.py              # Main entry point
├── config/
│   ├── loader.py          # Configuration loader
│   ├── suite_map.py       # Test suite mappings
│   ├── validator.py       # Configuration validation
│   └── environments/      # Environment-specific configs
│       └── <env>.json     # e.g. staging.json, production.json
├── engine/
│   ├── executor.py        # Test execution engine
│   ├── command_builder.py # Gradle command builder
│   ├── planner.py         # Test planning logic
│   └── retry.py           # Retry mechanism
└── utils/
    ├── logger.py          # Logging utilities
    ├── process.py         # Process execution
    ├── failure_parser.py  # Failure classification
    ├── gradle_parser.py   # Gradle output parsing
    └── env_loader.py      # Environment variable loader
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd automation-runner
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies (if any):
```bash
pip install -r requirements.txt  # If requirements.txt exists
```

## Configuration

All environment-specific settings live under `config/environments/`. One JSON file per environment (e.g. `staging.json`, `production.json`) keeps config easy to find and extend.

### Environment Configuration Files

Create a JSON file per environment in `config/environments/`. Example: `config/environments/staging.json`

```json
{
  "name": "staging",
  "gradle_task": "api-system-tests:test",
  "java_home": "/path/to/java/home",
  "project_dir": "/path/to/test/project",
  "parallelism": 1,
  "retries": 3,
  "delay": 5
}
```

### Configuration Options

- `name`: Environment name (descriptive)
- `gradle_task`: Gradle task to execute (e.g., `test`, `api-system-tests:test`)
- `java_home`: Path to Java installation (required for Gradle)
- `project_dir`: Absolute path to the Gradle project directory
- `parallelism`: Number of parallel test executions (default: 1)
- `retries`: Number of retry attempts for failed tests (default: 0)
- `delay`: Delay in seconds between retries (default: 5)

### Default Values

If not specified in the environment config, the following defaults are used:
- `retries`: 0
- `delay`: 5 seconds
- `gradle_task`: "test"

## Usage

### Basic Usage

Run a test suite for a specific environment:

```bash
python runner.py <environment> <suite>
```

### Examples

```bash
# Run vehicle tests in staging environment
python runner.py staging vehicle

# Run driver tests in staging environment
python runner.py staging driver

# Run custom suite (will use pattern *CustomSuite*)
python runner.py staging CustomSuite
```

### Available Test Suites

The following test suites are pre-mapped in `config/suite_map.py`:

- `vehicle` → `*Vehicle*`
- `driver` → `*Driver*`
- `asset` → `*Asset*`
- `session` → `*Session*`
- `group` → `*Group*`
- `devices` → `*Devices*`
- `login` → `*Login*`

Custom suite names will automatically use the pattern `*<suite>*` if not found in the suite map.

## How It Works

1. **Configuration Loading**: Loads environment-specific configuration from JSON files in `config/environments/`
2. **Command Building**: Constructs Gradle command with appropriate test pattern
3. **Test Execution**: Executes tests using Gradle in the specified project directory
4. **Failure Handling**: Classifies failures and retries if configured
5. **Logging**: Provides timestamped logging throughout the execution

### Execution Flow

```
runner.py
  ↓
load_env_config(env)
  ↓
build_command(env, suite, config)
  ↓
execute_suite(env, suite, config)
  ├── run_process(cmd, config)
  ├── classify_failure(output)
  └── retry_if_needed(...)
```

## Requirements

- Python 3.x
- Java (JDK) - version specified in environment config
- Gradle project with test framework
- Access to the test project directory

## Logging

The runner provides timestamped logging for all operations. Log messages follow the format:
```
[HH:MM:SS] <message>
```

## Error Handling

- **Missing Configuration**: Raises `FileNotFoundError` if the environment config file is not found in `config/environments/`
- **Invalid Arguments**: Exits with error message if required arguments are missing
- **Test Failures**: Classified and optionally retried based on configuration

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Add new environment configs under `config/environments/` as needed
4. Test changes with existing test suites

## License

[Add your license information here]
>>>>>>> 8b25023 (Initial automation runner)
