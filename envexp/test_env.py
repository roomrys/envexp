import argparse
from pathlib import Path

from envexp_utils.code_edit import delete_old_experiment_code, copy_source_code
from envexp_utils.commit import commit_experiment
from envexp_utils.environment import (
    determine_conda,
    create_environment,
    remove_environment,
)
from envexp_utils.log import reset_logfile
from envexp_utils.test import test_code, test_imports


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
        help=(
            "The path to the source code of a repo. E.g. 'C:\path\\to\sleap'. If no "
            "directory is provided, then testing the repo import is skipped. If a "
            "directory is provided without a library argument, then the entire "
            "repo is copied and tested for import-ability. If both a directory and "
            "a library are provided, then only the imports from the library are copied."
        ),
        default=None,
    )
    parser.add_argument(
        "--commit-message",
        type=str,
        help="The commit message to use when committing the changes.",
    )
    return parser


def parse_args(library=None, input_dir=None, commit_message=None):
    # Parse the command-line arguments
    parser = create_parser()
    args = parser.parse_args()

    # Print the arguments
    print(f"CLI Arguments:\n\t{args}")

    # Set the arguments
    args.library = library or args.library
    args.input_dir = input_dir or args.input_dir
    args.commit_message = commit_message or args.commit_message

    # Modify the input_dir and repo_name if input_dir is provided
    repo_name = None
    if args.input_dir is not None:
        args.input_dir = Path(input_dir)
        repo_name = args.input_dir.name

    # Print the modified arguments
    print(f"Modified Arguments:\n\t{args}")

    if commit_message is None:
        parser.print_usage()
        raise ValueError(
            "Missing required argument --commit-message. "
            "Please provide a commit message.",
        )
    return args.library, args.input_dir, repo_name, args.commit_message


def main(library=None, input_dir=None, commit_message=None):
    """Main function to run the environment experiment.

    This function:
        1. removes any existing environment called 'experiment'
        2. creates a new environment called 'experiment' from the envexp/environment.yml
        3. logs the dependencies of the experiment environment to mamaba_list.txt and
            pipdeptree.txt
        3. copies the source code from the input directory to the envexp directory
        4. tests the importability of the copied source code
        5. runs user-defined test code
        6. logs results of the experiment to test.log
        7. commits the changes to the root directory

    Args:
        library (str): The library to search for in the imports. E.g. 'qtpy'.
        input_dir (str): The path to the source code of a repo. E.g. 'C:\path\\to\sleap'.
        commit_message (str): The commit message to use when committing the changes.
    """

    # Parse the command-line arguments
    library, input_dir, repo_name, commit_message = parse_args(
        library=library,
        input_dir=input_dir,
        commit_message=commit_message,
    )

    # Determine the conda executable to use
    conda_command = determine_conda()
    remove_environment(conda_command=conda_command)
    reset_logfile()
    delete_old_experiment_code()

    try:
        # Create a new conda environment
        create_environment(conda_command=conda_command)

        # Test the imports
        if input_dir is not None:
            # Copy imports from the given directory
            copy_source_code(
                input_dir=input_dir,
                repo_name=repo_name,
                library=library,
            )
            test_imports(conda_command=conda_command, repo_name=repo_name)

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
        commit_experiment(commit_message=commit_message)

    return


if __name__ == "__main__":
    main(
        # library="qtpy",
        # input_dir="/Users/liezlmaree/Projects/sleap/sleap",
        commit_message="tensorflow-macos==2.10.0",
    )
