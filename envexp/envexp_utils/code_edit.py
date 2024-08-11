
import shutil

from envexp_utils.commit import gitignore_repo, un_gitignore_prev_repo
from envexp_utils.file import EXP_DIR

def delete_old_experiment_code():
    """Removes all directories in ./envexp folder that does not contain "envexp"."""

    print("\nCleaning up envexp directory...")

    envexp_dir = EXP_DIR
    for directory in envexp_dir.iterdir():
        if directory.is_dir() and ("envexp" not in directory.name):
            print(f"Removing directory [{directory}]...")
            shutil.rmtree(directory)

    un_gitignore_prev_repo()

def copy_source_code(input_dir, repo_name, library=None):
    """Finds all imports from a given library in Python files and copies them to test.

    Args:
        input_dir (str): The directory to search for Python files.
            E.g. 'C:\path\to\sleap'.
        repo_name (str): The name of the repo to copy imports from. E.g. 'sleap'.
        library (str): The library to search for in the imports. E.g. 'qtpy'. If None,
            the function will search for imports all non-tabbed imports.
    """

    # Remove the imports directory if it exists
    delete_old_experiment_code()

    # Set-up output path to copy and test code
    output_path = EXP_DIR / repo_name
    output_path.mkdir(
        parents=True, exist_ok=True
    )  # Create output directory if it doesn't exist

    gitignore_repo(repo_name)

    # Only find and copy specific imports if a library is provided
    if library is not None:
        print(f"\nFinding and copying imports from [{library}]...")
        find_and_copy_imports(
            input_dir=input_dir, output_path=output_path, library=library
        )
        print(f"Finished copying imports from [{library}].")
    else:
        print("\nCopying entire repo from input directory...")
        copy_repo(input_dir=input_dir, output_path=output_path)
        print("Finished copying entire repo.")

    return

def copy_repo(input_dir, output_path):
    """Copies the entire repo to the output path."""

    # Copy the entire repo to the output path
    shutil.copytree(input_dir, output_path, dirs_exist_ok=True)


def find_and_copy_imports(input_dir, output_path, library):

    def is_import(line):
        """Check if the line is an import statement from the library."""

        if line.startswith(f"from {library}") or line.startswith(f"import {library}"):
            return True
        return False

    # Create __init__.py file in output directory to add all imports
    init_path = output_path / "__init__.py"

    # Find all Python files in the input directory
    for python_file in input_dir.rglob("*.py"):
        with python_file.open("r") as infile:
            lines = infile.readlines()

        # Find and collect multi-line imports that start with 'from qtpy'
        matching_imports = []
        multi_line_import = False
        current_import = ""

        # Find imports from the library
        for line in lines:
            if multi_line_import:
                current_import += line.strip()
                if line.strip().endswith(")"):
                    matching_imports.append(current_import)
                    multi_line_import = False
                    current_import = ""
                continue

            if is_import(line):
                # Determine if the import is a multi-line import
                if line.strip().endswith("("):
                    multi_line_import = True
                    current_import = line.strip()
                else:
                    matching_imports.append(line.strip())

        # Only write to the output file if there are matching lines
        if matching_imports:
            relative_path = python_file.relative_to(input_dir)
            with init_path.open("a") as initfile:
                initfile.write(f"\n# {relative_path}\n")
                initfile.write("\n".join(matching_imports) + "\n")

