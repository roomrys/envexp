"""Defines functions for managing the environment."""

import subprocess

from envexp_utils.file import EXP_DIR
from envexp_utils.log import log_dependencies, run_and_log

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

def create_environment(conda_command):
    """Creates a new conda environment with the required dependencies."""

    print("\n(Re)creating experiment environment...")

    environment_file = EXP_DIR / "environment.yml"

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


def remove_environment(conda_command):
    """Removes the conda environment created for the experiment."""

    print("\nRemoving experiment environment...")

    # Remove the conda environment
    command = f"{conda_command} env remove -n experiment"
    if conda_command == "micromamba":
        command += " -y"
    subprocess.run(f"{command}", shell=True)