import sys
from engine.executor import execute_suite
from config.loader import load_env_config
from utils.logger import log

def main():
    if len(sys.argv) < 3:
        print("Usage: python runner.py <env> <suite>")
        sys.exit(1)

    env = sys.argv[1]
    suite = sys.argv[2]

    log(f"Environment: {env}")
    log(f"Suite: {suite}")

    config = load_env_config(env)

    # execute_suite(env, suite, config)

    summary = execute_suite(env, suite, config)

    status = "SUCCESS" if summary["exit_code"] == 0 else "FAILED"

    print("\n================ TEST RUN SUMMARY ================")
    print(f"Environment      : {env}")
    print(f"Suite            : {suite}")
    print(f"Status           : {status}")
    print(f"Total Attempts   : {summary['attempts']}")
    print(f"Failure Type     : {summary['failure_type']}")
    print(f"Retried Testcases: {summary['retried_tests']}")
    print("==================================================\n")

    sys.exit(summary["exit_code"])

if __name__ == "__main__":
    main()