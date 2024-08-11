"""File constants."""

from pathlib import Path

# Configure commonly reused paths
FILE_PATH = Path(__file__)
FILE_DIR = FILE_PATH.parent
BASE_DIR = FILE_DIR.parent.absolute()