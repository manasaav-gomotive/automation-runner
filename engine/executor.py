from utils.process import run_process
from engine.retry import retry_if_needed
from engine.command_builder import build_command


def execute_suite(env, suite, config):
    base_cmd = build_command(env, suite, config)

    def run(cmd_override=None):
        cmd_to_run = cmd_override if cmd_override else base_cmd
        # Ensure your command_builder produces a LIST or string correctly
        exit_code, output = run_process(cmd_to_run, config)
        return exit_code, output

    return retry_if_needed(
        run_fn=run,
        retries=config.retries,
        delay=config.delay,
        config=config,
        env=env,
        suite=suite
    )