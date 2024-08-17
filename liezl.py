import csv
import sys
from pathlib import Path
from typing import List

try:
    from tqdm import tqdm
except ImportError:
    print("Cannot import tqdm. Progress bar will not be displayed.")
    tqdm = lambda x: x


def parse_dependencies(file_path):
    dependencies = {}
    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line and not (
            line.startswith("#")
            or line.startswith("─")
            or "Name" in line
            or line.startswith("List of")
        ):
            if "==" in line:  # absl-py==1.0.0
                parts = line.split("==")
            elif (
                "@" in line
            ):  # h5py @ file:///home/conda/feedstock_root/build_artifacts/h5py_1604753641401/work
                parts = line.split("@")
            elif "|" in line:
                parts = line.split("|")
            else:  # attrs              21.4.0        pyhd8ed1ab_0            conda-forge
                parts = line.split()
            if len(parts) >= 2:
                package_name = (
                    parts[0].strip().lower().replace(".", "_").replace("-", "_")
                )
                if "git+" in package_name:
                    package_name = package_name.split("/")[-1]
                package_version = parts[1].strip()
                dependencies[package_name] = package_version

    return dependencies


def compare_dependencies(file_paths: List[str], output_file: str, remove_same=False):

    fpaths = [Path(file_path) for file_path in file_paths]

    print("Gathering dependencies...")
    dependencies_list = [
        parse_dependencies(file_path) for file_path in tqdm(file_paths)
    ]

    all_packages = sorted(
        set(
            package_name
            for dependencies in dependencies_list
            for package_name in dependencies.keys()
        )
    )

    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Package Name"] + [fp.stem for fp in fpaths])

        print(f"Comparing {len(all_packages)} packages...")
        for package_name in tqdm(all_packages):
            versions = [
                dependencies.get(package_name, "") for dependencies in dependencies_list
            ]

            # Negative of "remove_same and len(set(versions)) == 1" for short-circuiting
            # not(AB) = not(A) or not(B)
            if (not remove_same) or (len(set(versions)) > 1):
                writer.writerow([package_name] + versions)


if __name__ == "__main__":

    file_paths = ["passing.txt", "failing.txt"]
    output_file = "output.csv"  # Replace with the desired output CSV file path

    # Check if we should prompt user for overwriting output file
    quiet = False
    if "-y" in sys.argv:
        sys.argv.remove("-y")
        quiet = True

    # Remove the same versions if two or more input files (and an output) are provided.
    remove_same = len(sys.argv) >= 4
    if "-a" in sys.argv:
        sys.argv.remove("-a")
        remove_same = False

    print(f"\nRemoving same versions: {remove_same}")

    # Check if sys.argv is empty
    if len(sys.argv) < 2:
        print("Using filepaths listed in script.")
    elif len(sys.argv) == 2:
        print("Using output path listed in script.")
        file_paths = sys.argv[1:]
    else:
        print("Using filepaths and output path from CLI.")
        file_paths = sys.argv[1:-1]
        output_file = sys.argv[-1]

    # Inform user of input and output files
    fp_string = "\n\t".join(file_paths)
    print(f"\nInput files:\n\t{fp_string}\nOutput file:\n\t{output_file}")

    # Check if output_file exists
    if not quiet and len(sys.argv) >= 2 and Path(output_file).exists():
        response = input(
            f"\nOutput file already exists at: \n\t{output_file}.\nOverwrite [y/n]: "
        )
        if response.lower() != "y":
            print("Exiting...")
            sys.exit(1)

    print("\nComparing dependencies...")

    compare_dependencies(
        file_paths=file_paths,
        output_file=output_file,
        remove_same=True,
    )

    print("Done!")