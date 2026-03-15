# import time
# from utils.failure_parser import classify_failure, extract_failed_tests
# from engine.command_builder import build_command
#
#
# RETRYABLE_FAILURES = {"RATE_LIMIT", "SERVER_ERROR", "TEST_FAILURE"}
#
#
# def retry_if_needed(run_fn, retries, delay, config, env, suite):
#     """
#     retries = number of retry attempts AFTER first run
#     total runs = retries + 1
#     """
#
#
#     attempt = 0
#
#     print(f"[CONFIG DEBUG] retries={config.retries}, delay={config.delay}")
#
#     while True:
#         print(f"[RETRY] Attempt {attempt + 1} of {retries + 1}")
#         exit_code, output = run_fn()
#         # import pdb
#         # pdb.set_trace()
#         if exit_code == 0:
#             print("[RETRY] Success")
#             return 0
#
#         failure_type = classify_failure(output)
#         print(f"[RETRY] Failure Type: {failure_type}")
#
#         if failure_type not in RETRYABLE_FAILURES:
#             print(f"[RETRY] Non-retryable failure detected: {failure_type}. Exiting.")
#             return exit_code
#
#         if attempt >= retries:
#             print("[RETRY] Max retries reached. Exiting.")
#             return exit_code
#
#         # Only retry certain failures
#         if failure_type in RETRYABLE_FAILURES:
#
#             failed_tests = extract_failed_tests(output)
#
#             if failed_tests:
#                 print(f"[RETRY] Retrying failed tests only: {failed_tests}")
#
#                 cmd = build_command(env, suite, config, tests=failed_tests)
#
#                 time.sleep(delay)
#                 delay *= 2
#                 attempt += 1
#
#                 # Run selective retry
#                 exit_code, output = run_fn(cmd_override=cmd)
#
#                 if exit_code == 0:
#                     print("[RETRY] Success after selective retry")
#                     return 0
#
#                 print("[RETRY] Selective retry failed, continuing...")
#                 continue
#
#             else:
#                 print("[RETRY] No failed tests detected, retrying full suite.")
#
#         # Full suite retry fallback
#         print(f"[RETRY] Retrying full suite in {delay} seconds...")
#         time.sleep(delay)
#         delay *= 2
#         attempt += 1

import time
from utils.failure_parser import classify_failure, extract_failed_tests
from engine.command_builder import build_command


RETRYABLE_FAILURES = {"RATE_LIMIT", "SERVER_ERROR", "TEST_FAILURE"}


def retry_if_needed(run_fn, retries, delay, config, env, suite):
    attempt = 0
    retried_tests = []
    final_failure_type = None
    execution_mode = getattr(config, "execution_mode", "gradle")

    while True:
        print(f"\n[RETRY] Attempt {attempt + 1} of {retries + 1}")

        exit_code, output = run_fn()

        if exit_code == 0:
            print("[RETRY] Success")
            return {
                "exit_code": 0,
                "attempts": attempt + 1,
                "failure_type": None,
                "retried_tests": retried_tests
            }

        failure_type = classify_failure(output)
        final_failure_type = failure_type

        print(f"[RETRY] Failure Type: {failure_type}")

        if failure_type not in RETRYABLE_FAILURES:
            print(f"[RETRY] Non-retryable failure detected: {failure_type}. Exiting.")
            return {
                "exit_code": exit_code,
                "attempts": attempt + 1,
                "failure_type": failure_type,
                "retried_tests": retried_tests
            }

        if attempt >= retries:
            print("[RETRY] Max retries reached. Exiting.")
            return {
                "exit_code": exit_code,
                "attempts": attempt + 1,
                "failure_type": failure_type,
                "retried_tests": retried_tests
            }

        failed_tests = extract_failed_tests(output) if execution_mode == "gradle" else []

        if failed_tests:
            print(f"[RETRY] Retrying failed tests only: {failed_tests}")
            retried_tests.extend(failed_tests)

            cmd = build_command(env, suite, config, tests=failed_tests)

            time.sleep(delay)
            delay *= 2
            attempt += 1

            exit_code, output = run_fn(cmd_override=cmd)

            if exit_code == 0:
                print("[RETRY] Success after selective retry")
                return {
                    "exit_code": 0,
                    "attempts": attempt + 1,
                    "failure_type": None,
                    "retried_tests": retried_tests
                }

            print("[RETRY] Selective retry failed. Continuing...")
            continue

        print(f"[RETRY] Retrying full suite in {delay} seconds...")
        time.sleep(delay)
        delay *= 2
        attempt += 1
