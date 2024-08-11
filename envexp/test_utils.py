
import inspect
import user_test_code
from logging_utils import logger, print_code, run_and_log


def test_code(conda_command):
    """Runs user-defined test code."""

    user_code = inspect.getsource(user_test_code)
    logger.info(f"Running user-defined test code:\n{user_code}")
    print(f"\nRunning user-defined test code:")
    print_code(user_code)

    fail_message = "Tests failed!"
    pass_message = "Tests passed successfully!"
    command = f"{conda_command} run -n experiment python user_test_code.py"
    run_and_log(command=command, fail_message=fail_message, pass_message=pass_message)


def test_imports(conda_command, repo_name):
    """Tests the imports in the experiment environment.

    Args:
        conda_command (str): The conda command to use (i.e. micromamba, mamba, or conda)
        repo_name (str): The name of the repo to test imports for. E.g. 'sleap'.
    """

    logger.info("Testing imports with:")
    print("\nTesting imports with:")
    logger.info(f"\timport {repo_name}")
    print_code(f"\timport {repo_name}")

    fail_message = "Imports failed!"
    pass_message = "Imports passed successfully!"
    command = f'{conda_command} run -n experiment python -c "import {repo_name}"'
    run_and_log(command=command, fail_message=fail_message, pass_message=pass_message)

