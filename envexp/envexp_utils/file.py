"""File constants."""

from pathlib import Path

# Configure commonly reused paths
FILE_PATH = Path(__file__)
EXP_DIR = FILE_PATH.parent.parent
ROOT_DIR = EXP_DIR.parent.absolute()