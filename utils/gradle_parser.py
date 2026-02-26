import re

FAILED_HEADER = re.compile(r"(.+?) > (.+?) FAILED")
STATUS_LINE = re.compile(r"Expected status code <(\d+)> but was <(\d+)>")
ASSERTION_LINE = re.compile(r"java\.lang\.AssertionError:\s*(.*)")
EXCEPTION_LINE = re.compile(r"(java\.[\w\.]+Exception):?\s*(.*)")
NULLPTR_PATTERN = re.compile(r'Cannot invoke "(.+?)" because "(.+?)" is null')
RATE_LIMIT_PATTERN = re.compile(r'Expected status code <\d+> but was <429>')

class GradleFailureParser:
    def __init__(self):
        self.failures = []
        self.current = None

    def process_line(self, line: str):

        # --- Detect new failed test ---
        header = FAILED_HEADER.search(line)
        if header:
            self.current = {
                "suite": header.group(1).strip(),
                "test": header.group(2).strip(),
                "reason": None
            }
            self.failures.append(self.current)
            return

        if not self.current:
            return

        # --- Status mismatch ---
        status = STATUS_LINE.search(line)
        if status:
            expected, actual = status.groups()
            self.current["reason"] = f"Status mismatch → expected {expected}, got {actual}"
            return

        # --- Assertion error ---
        assertion = ASSERTION_LINE.search(line)
        if assertion and not self.current["reason"]:
            msg = assertion.group(1).strip()
            if msg:
                self.current["reason"] = msg
            return

        # --- Exceptions ---
        exc = EXCEPTION_LINE.search(line)
        if exc and not self.current["reason"]:
            self.current["reason"] = f"{exc.group(1)} {exc.group(2)}".strip()
            return

        null_match = NULLPTR_PATTERN.search(line)
        if null_match:
            obj = null_match.group(2)
            self.current["reason"] = f"Missing test data → object '{obj}' is null"
            return

        if RATE_LIMIT_PATTERN.search(line):
            self.current["reason"] = "Rate limited (429)"
            self.current["type"] = "INFRA"

    def print_summary(self):
        if not self.failures:
            return

        print("\n❌ FAILED TEST SUMMARY")
        print("=" * 60)

        for i, f in enumerate(self.failures, 1):
            print(f"\n{i}. {f['suite']}")
            print(f"   Test   : {f['test']}")
            print(f"   Reason : {f['reason'] or 'Unknown failure'}")