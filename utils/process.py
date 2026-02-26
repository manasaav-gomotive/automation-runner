import os
import subprocess


def run_process(cmd, config):
    env = os.environ.copy()

    # Update environment with any custom variables from config
    if hasattr(config, "env_vars") and config.env_vars:
        env.update(config.env_vars)

    print(f"🚀 Executing in: {config.project_dir}")
    print(f"💻 Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

    process = subprocess.Popen(
        cmd,
        cwd=config.project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        bufsize=1,
        shell=isinstance(cmd, str)  # Use shell if cmd is a string
    )

    output = ""
    test_failed = False
    for line in iter(process.stdout.readline, ""):
        print(line, end="")
        output += line
        if any(keyword in line for keyword in ["FAILED", "ERROR", "EXCEPTION"]):
            test_failed = True

    process.stdout.close()
    return_code = process.wait()

    if test_failed:
        return 2, output
    return return_code, output