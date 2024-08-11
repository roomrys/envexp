"""Utility functions for logging."""

import logging
import subprocess
import time

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

from file_utils import FILE_DIR, BASE_DIR

# Configure the logging module to write logs to a file
LOGFILE = BASE_DIR / "test.log"
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

def reset_logfile():
    """Resets the log file."""
    
    with open(LOGFILE, "w") as f:
        pass

def log_dependencies(conda_command):
    """Logs the dependencies of the experiment environment to file."""

    def post_process_file(filename):
        """Removes empty lines from a file."""

        with open(filename, "r") as f:
            lines = f.readlines()

        with open(filename, "w") as f:
            for line in lines:
                if line.strip():  # only write the line if it's not empty
                    f.write(line)

    mamba_filename = BASE_DIR / "mamba_list.txt"
    pip_filename = BASE_DIR / "pipdeptree.txt"

    # Reset the files
    for filename in [mamba_filename, pip_filename]:
        with open(filename, "w") as f:
            pass

    # mamba list > mamba_list.txt
    with open(mamba_filename, "w") as f:
        subprocess.run(
            f"{conda_command} run -n experiment {conda_command} list",
            shell=True,
            stdout=f,
        )

    # Find python path of experiment environment
    result = subprocess.run(
        f"{conda_command} run -n experiment which python",
        shell=True,
        capture_output=True,
    )
    python_path = result.stdout.decode().strip()

    # pipdeptree -f > pipdeptree.txt
    with open(pip_filename, "w") as f:
        # Run pipdeptree in the envexp environment on the experiment environment
        subprocess.run(
            f"{conda_command} run -n envexp pipdeptree --python {python_path} -f",
            shell=True,
            stdout=f,
        )

    # Remove empty lines from the files
    for filename in [mamba_filename, pip_filename]:
        post_process_file(filename)


def print_code(code):
    """Prints code with syntax highlighting."""

    print(highlight(code, PythonLexer(), TerminalFormatter()))

# Function to close and remove all handlers from the logger
def close_logger_handlers(logger):
    for handler in logger.handlers[:]:  # Iterate over a copy of the list
        handler.close()
        logger.removeHandler(handler)

def wait_for_log_update(timeout=10):
    start_time = time.time()
    initial_mod_time = LOGFILE.stat().st_mtime
    while time.time() - start_time < timeout:
        current_mod_time = LOGFILE.stat().st_mtime
        if current_mod_time != initial_mod_time:
            return True  # Log file has been updated
        time.sleep(0.5)  # Wait for half a second before checking again
    return False  # Timeout reached without detecting an update


def run_and_log(command, fail_message=None, pass_message=None):
    """Runs a command and logs the output."""

    if fail_message is None:
        fail_message = "Failed!"

    if pass_message is None:
        pass_message = "Passed!"

    try:
        output = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            cwd=FILE_DIR,
        )
        if output.returncode != 0:
            error = output.stderr.decode()
            error = error.replace("\r\r", "")
            raise Exception(error)
        print(output.stdout.decode())
        logger.info(pass_message)
        print(pass_message)
    except Exception as e:
        logger.exception(fail_message)
        print(fail_message)
        raise e