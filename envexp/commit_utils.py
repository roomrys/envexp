
import subprocess
from pathlib import Path

from file_utils import BASE_DIR

# Configure gitignore
GITIGNORE_PATH = BASE_DIR / ".gitignore"
GITIGNORE_FLAG = "# added by envexp\n"

def gitignore_repo(repo_name):
    """Appends the repo name to the .gitignore file.

    Args:
        repo_name (str): The name of the repo to append to the .gitignore file.
    """

    # Ensure the .gitignore file ends with a newline
    with GITIGNORE_PATH.open("rb+") as file:
        file.seek(-1, 2)  # Move the cursor to the last byte in the file
        last_char = file.read(1)
        if last_char != b"\n":
            file.write(b"\n")

    with GITIGNORE_PATH.open("a") as gitignore:
        gitignore.write(f"\n{GITIGNORE_FLAG}{repo_name}/\n")

    assume_unchanged_gitignore()
    return


def assume_unchanged_gitignore():
    """Assumes the .gitignore file is unchanged."""

    subprocess.run(
        "git update-index --assume-unchanged .gitignore", shell=True, cwd=BASE_DIR
    )


def no_assume_unchanged_gitignore():
    """Removes the assume-unchanged flag from the .gitignore file."""

    subprocess.run(
        "git update-index --no-assume-unchanged .gitignore", shell=True, cwd=BASE_DIR
    )


def un_gitignore_prev_repo():
    """Removes the previous repo name from the .gitignore file."""

    def is_gitignore_block(prev_line, line, next_line):
        """Determines if the line is part of the gitignore block.

        Args:
            prev_line (str): The previous line.
            next_line (str): The next line.
        """

        if (
            (GITIGNORE_FLAG in prev_line)
            or (GITIGNORE_FLAG in line)
            or (GITIGNORE_FLAG in next_line)
        ):
            return True
        return False

    with GITIGNORE_PATH.open("r") as gitignore:
        lines = gitignore.readlines()

    with GITIGNORE_PATH.open("w") as gitignore:
        # Write the first line (we assume it's not part of the block)
        gitignore.write(lines[0])

        # Only write lines that are not part of the envexp gitignore block
        for line_idx, line in enumerate(lines[1:-1]):

            prev_line = lines[line_idx]
            next_line = lines[line_idx + 2]
            if is_gitignore_block(prev_line, line, next_line):
                continue

            gitignore.write(line)
        # Write the last line if it's not part of the block
        if not is_gitignore_block(prev_line=line, line=next_line, next_line=lines[-1]):
            gitignore.write(lines[-1])

    return


def commit_changes(commit_message: str):
    """Commits the changes to the root directory."""

    # Commit the changes to the root directory
    subprocess.run("git add .", shell=True, cwd=BASE_DIR)
    subprocess.run(f'git commit -m "{commit_message}"', shell=True)