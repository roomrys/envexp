import argparse
import inspect
import logging
import shutil
import subprocess
import time
from pathlib import Path

# TODO(LM): Separate test code from the main code
# from pygments import highlight
# from pygments.formatters import TerminalFormatter
# from pygments.lexers import PythonLexer


def print_code(code):
    """Prints code with syntax highlighting."""

    print(code)
    return

    # TODO(LM): Separate test code from the main code
    print(highlight(code, PythonLexer(), TerminalFormatter()))


def wait_for_log_update(logfile_path, timeout=10):
    logfile_path = Path(logfile_path)  # Ensure logfile_path is a Path object
    start_time = time.time()
    initial_mod_time = logfile_path.stat().st_mtime
    while time.time() - start_time < timeout:
        current_mod_time = logfile_path.stat().st_mtime
        if current_mod_time != initial_mod_time:
            return True  # Log file has been updated
        time.sleep(0.5)  # Wait for half a second before checking again
    return False  # Timeout reached without detecting an update


# Function to close and remove all handlers from the logger
def close_logger_handlers(logger):
    for handler in logger.handlers[:]:  # Iterate over a copy of the list
        handler.close()
        logger.removeHandler(handler)


# Configure commonly reused paths
FILE_PATH = Path(__file__)
FILE_DIR = FILE_PATH.parent
BASE_DIR = FILE_DIR.parent.absolute()

# Configure gitignore
GITIGNORE_PATH = BASE_DIR / ".gitignore"
GITIGNORE_FLAG = "# added by envexp\n"

# Configure the logging module to write logs to a file
LOGFILE = BASE_DIR / "test.log"
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def determine_conda():
    """Determines the conda executable to use (i.e. mm, mamba, or conda)."""

    print("\nDetermining conda executable...")

    # Check if mamba is installed
    try:
        output = subprocess.run("mamba --version", shell=True, capture_output=True)
        if len(output.stderr) > 0:
            raise FileNotFoundError("No mamba executable found.")
        print("\t... using mamba")
        return "mamba"
    except Exception as e:
        print(output.stderr.decode())
        pass

    # Check if micromamba is installed
    try:
        output = subprocess.run("micromamba --version", shell=True, capture_output=True)
        if len(output.stderr) > 0:
            raise FileNotFoundError("No micromamba executable found.")
        print("\t... using micromamba")
        return "micromamba"
    except FileNotFoundError:
        pass

    # Check if conda is installed
    try:
        output = subprocess.run("conda --version", shell=True, capture_output=True)
        if len(output.stderr) > 0:
            raise FileNotFoundError("No conda executable found.")
        print("\t... using conda")
        return "conda"
    except FileNotFoundError:
        pass

    raise FileNotFoundError("No conda executable found.")


def remove_environment(conda_command):
    """Removes the conda environment created for the experiment."""

    print("\nRemoving experiment environment...")

    # Remove the conda environment
    command = f"{conda_command} env remove -n experiment"
    if conda_command == "micromamba":
        command += " -y"
    subprocess.run(f"{command}", shell=True)


def create_environment(conda_command):
    """Creates a new conda environment with the required dependencies."""

    print("\n(Re)creating experiment environment...")

    parent_dir = Path(__file__).resolve().parent
    environment_file = parent_dir / "environment.yml"

    # Create a new conda environment with the required dependencies
    command = f"{conda_command} env create -f {environment_file.as_posix()}"
    if conda_command == "micromamba":
        command += " -y"

    fail_message = "Failed to create environment!"
    pass_message = "Environment created successfully!"

    try:
        run_and_log(
            command=command, fail_message=fail_message, pass_message=pass_message
        )
    except Exception as e:
        raise e
    finally:
        # Log the dependencies
        log_dependencies(conda_command=conda_command)


def remove_imports(imports_dir):
    """Removes the imports directory if it exists."""
    imports_dir = Path(imports_dir)
    if imports_dir.exists():
        print("Removing imports directory...")
        shutil.rmtree(imports_dir)


def find_imports(input_dir, repo_name=None, library=None):
    """Finds all imports from a given library in Python files and copies them to test.

    Args:
        input_dir (str): The directory to search for Python files.
            E.g. 'C:\path\to\sleap'.
        repo_name (str): The name of the repo to copy imports from. E.g. 'sleap'.
            If None, then will use the name of the input directory.
        library (str): The library to search for in the imports. E.g. 'qtpy'. If None,
            the function will search for imports all non-tabbed imports.
    """

    current_file = Path(__file__).resolve()
    output_dir = Path(current_file.parent) / "experiment"  # TODO: Change to repo_name

    # Remove the imports directory if it exists
    remove_imports(imports_dir=output_dir)

    # Set-up input and output paths
    input_path = Path(input_dir)
    repo_name = input_path.name
    output_path = Path(
        output_dir
    ).resolve()  # Resolve to absolute path but keep it relative if given so
    output_path.mkdir(
        parents=True, exist_ok=True
    )  # Create output directory if it doesn't exist
    init_path = (
        output_path / "__init__.py"
    )  # Create __init__.py file in output directory

    if library is None:

        def check_import(line):
            """Check if the line is an import statement."""

            if line.startswith("from ") or line.startswith("import "):
                return True
            return False

    else:

        def check_import(line):
            """Check if the line is an import statement from the library."""

            if line.startswith(f"from {library}") or line.startswith(
                f"import {library}"
            ):
                return True
            return False

    for python_file in input_path.rglob("*.py"):  # Search recursively for Python files
        with python_file.open("r") as infile:
            lines = infile.readlines()

        # Find and collect multi-line imports that start with 'from qtpy'
        matching_imports = []
        multi_line_import = False
        current_import = ""

        for line in lines:
            if multi_line_import:
                current_import += line.strip()
                if line.strip().endswith(")"):
                    matching_imports.append(current_import)
                    multi_line_import = False
                    current_import = ""
                continue

            if check_import(line):

                # Skip the line if the repo name is in the line
                if repo_name in re.split(r"[ .,\(\)\n]+", line):
                    continue
                    # line = line.replace(repo_name, "experiment")

                # Determine if the import is a multi-line import
                if line.strip().endswith("("):
                    multi_line_import = True
                    current_import = line.strip()
                else:
                    matching_imports.append(line.strip())

        # Only write to the output file if there are matching lines
        if matching_imports:
            # Create the output file path
            realtive_path = python_file.relative_to(input_path)
            output_file_path = output_path / realtive_path
            if not output_file_path.parent.exists():
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with output_file_path.open("w") as outfile:
                outfile.write("\n".join(matching_imports) + "\n")

            if library is not None:
                # Append the output file path to the __init__.py file
                with init_path.open("a") as initfile:
                    initfile.write(
                        f"from {output_path.name} import {python_file.stem}\n"
                    )


def user_test_code():
    """User-defined test code to run after the imports have been tested."""

    import experiment


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
            cwd=Path(__file__).resolve().parent,
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


def test_code(conda_command):
    """Runs user-defined test code."""

    logger.info("Running user-defined test code...")
    print(f"\nRunning user-defined test code:")
    user_code = inspect.getsource(user_test_code)
    logger.info(user_code)
    print_code(user_code)

    fail_message = "Tests failed!"
    pass_message = "Tests passed successfully!"
    command = f'{conda_command} run -n experiment python -c "import test_env; test_env.user_test_code()"'
    run_and_log(command=command, fail_message=fail_message, pass_message=pass_message)


def test_imports(conda_command):
    """Tests the imports in the experiment environment."""

    # TODO(LM): Change to import the repo name
    fail_message = "Imports failed!"
    pass_message = "Imports passed successfully!"
    command = f'{conda_command} run -n experiment python -c "import experiment"'
    run_and_log(command=command, fail_message=fail_message, pass_message=pass_message)


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


def commit_changes(commit_message: str):
    """Commits the changes to the root directory."""

    # Commit the changes to the root directory
    subprocess.run("git add .", shell=True, cwd=BASE_DIR)
    subprocess.run(f'git commit -m "{commit_message}"', shell=True)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--library",
        type=str,
        help="The library to search for in the imports. E.g. 'qtpy'.",
        default=None,
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        help="The directory to search for Python files. E.g. 'C:\path\to\sleap'.",
        default=None,
    )
    parser.add_argument(
        "--repo-name",
        type=str,
        help="The name of the repo to copy imports from. E.g. 'sleap'.",
        default=None,
    )
    parser.add_argument(
        "--commit-message",
        type=str,
        help="The commit message to use when committing the changes.",
    )
    return parser


def parse_args(library=None, input_dir=None, repo_name=None, commit_message=None):
    # Parse the command-line arguments
    parser = create_parser()
    args = parser.parse_args()

    # Set the arguments
    library = library or args.library
    input_dir = input_dir or args.input_dir
    repo_name = repo_name or args.repo_name
    commit_message = commit_message or args.commit_message

    # Print the arguments
    print(f"Arguments:\n{args}")

    if commit_message is None:
        parser.print_usage()
        raise ValueError(
            "Missing required argument --commit-message. "
            "Please provide a commit message.",
        )
    return library, input_dir, repo_name, commit_message


def main(library=None, input_dir=None, repo_name=None, commit_message=None):

    # Parse the command-line arguments
    library, input_dir, repo_name, commit_message = parse_args(
        library=library,
        input_dir=input_dir,
        repo_name=repo_name,
        commit_message=commit_message,
    )

    # Determine the conda executable to use
    conda_command = determine_conda()

    # Remove environment
    # remove_environment(conda_command=conda_command)

    # Reset log file
    with open(LOGFILE, "w") as f:
        pass

    try:
        # Create a new conda environment
        # create_environment(conda_command=conda_command)

        # Test the imports
        if input_dir is not None:
            # Find imports from library in the given directory
            find_imports(
                input_dir=input_dir,
                repo_name=repo_name,
                library=library,
            )
            test_imports(conda_command=conda_command)

        # Run user-defined test code
        test_code(conda_command=conda_command)

        # If no errors, add P: to the commit message
        commit_message = f"P: {commit_message}"
    except Exception as e:
        # If there are errors, add F: to the commit message
        commit_message = f"F: {commit_message}"
        raise e
    finally:
        # Commit the changes
        close_logger_handlers(logger)
        wait_for_log_update(LOGFILE)
        # commit_changes(commit_message=commit_message)


if __name__ == "__main__":
    main(
        # library="qtpy",
        repo_name="sleap",
        input_dir="/Users/liezlmaree/Projects/sleap/sleap",
        commit_message="Run test code",
    )
