import re

def classify_failure(output: str):
    output_lower = output.lower()

    # 🔥 Extract actual status code from "Expected status code <201> but was <401>"
    match = re.search(r'but was <(\d+)>', output_lower)
    if match:
        status_code = match.group(1)

        if status_code == "401":
            return f"{status_code} AUTH_FAILURE"
        elif status_code == "429":
            return f"{status_code} RATE_LIMIT"
        elif status_code.startswith("5"):
            return f"{status_code} SERVER_ERROR"
        else:
            return f"{status_code} TEST_FAILURE"

    # fallback checks
    if "there were failing tests" in output_lower:
        return "TEST_FAILURE"

    if "build failed" in output_lower:
        return "TEST_FAILURE"

    return "UNKNOWN"

def extract_failed_tests(output: str):
    pattern = r'^\s*([A-Za-z0-9_.]+Tests?)\s*>'
    matches = re.findall(pattern, output, re.MULTILINE)

    seen = set()
    result = []

    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)

    return result