import os
import subprocess

def run_process(cmd, config):

    env = os.environ.copy()

    if hasattr(config, "env_vars"):
        env.update(config.env_vars)

    if hasattr(config, "java_home"):
        env["JAVA_HOME"] = config.java_home
        env["PATH"] = config.java_home + "/bin:" + env["PATH"]

    if "--info" in cmd:
        cmd.remove("--info")

    if "-DuseSeedData=true" in cmd:
        cmd.remove("-DuseSeedData=true")

    print(" ".join(cmd))
    process = subprocess.Popen(
        cmd,
        cwd=config.project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        bufsize=1,  # important for line buffering
    )

    output = ""
    test_failed = False
    for line in iter(process.stdout.readline, ""):
        print(line, end="")
        output += line
        if any(keyword in line for keyword in ["FAILED", "ERROR", "EXCEPTION"]):
            test_failed = True

    process.stdout.close()
    process.wait()


    # check weather the command has failed inside subprocess execution

    
    if test_failed:
        return 2, output
    return process.returncode, output