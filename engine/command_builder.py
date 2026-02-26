def build_command(env, suite, config, tests=None):
    base_cmd = [
        "./gradlew",
        "api-system-tests:test",
        f"-Denvironment={env}",
        "-DuseSeedData=true",
        "--info"
    ]

    # If retry is passing specific test classes
    if tests:
        for test in tests:
            base_cmd.extend(["--tests", test])
        return base_cmd

    # If suite looks like a fully qualified class name
    if "." in suite:
        base_cmd.extend(["--tests", suite])
        return base_cmd

    # Otherwise treat it as suite alias
    suite_map = getattr(config, "suite_map", {})
    pattern = suite_map.get(suite, f"*{suite}*")
    base_cmd.extend(["--tests", pattern])

    return base_cmd