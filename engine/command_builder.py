import os


def build_command(env, suite, config, tests=None):
    execution_mode = getattr(config, "execution_mode", "gradle")

    if execution_mode == "ci_script":
        script_path = getattr(config, "ci_script_path", ".ci/run-api-tests-by-pod.sh")
        resolved_script = script_path
        if not os.path.isabs(script_path):
            resolved_script = os.path.join(config.project_dir, script_path)
        return [resolved_script, env, suite]

    gradle_task = getattr(config, "gradle_task", "api-system-tests:test")
    use_seed_data = str(getattr(config, "use_seed_data", True)).lower()
    gradle_executable = getattr(config, "gradle_executable", "./gradlew")
    gradle_flags = list(getattr(config, "gradle_flags", ["--info"]))

    base_cmd = [
        gradle_executable,
        gradle_task,
        f"-Denvironment={env}",
        f"-DuseSeedData={use_seed_data}",
    ]
    base_cmd.extend(gradle_flags)

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
