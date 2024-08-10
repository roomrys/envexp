# envexp

To get started with the ENVironment EXPeriment package:

1. create an environment with
   ```bash
   mamba env create -f environment.yml
   ```
2. activate the environemnt with
   ```bash
   mamba activate envexp
   ```
3. edit the `envexp/environment.yml` to contain the dependencies you need
4. edit the `user_test_code` function in `envexp/test_env.py` to test a specific code block
5. test that all the imports/tests work using CLI
   ```bash
   test-env --library <optional> --input-dir <optional> --commit-message <required>
   ```

## test-env

```bash
usage: test-env [-h] [--library LIBRARY] [--input-dir INPUT_DIR] [--commit-message COMMIT_MESSAGE]

options:
  -h, --help            show this help message and exit
  --library LIBRARY     The library to search for in the imports. E.g. 'qtpy'.
  --input-dir INPUT_DIR
                        The path to the source code of a repo. E.g. 'C:\path\to\sleap'. If no directory is provided, then testing the
                        repo import is skipped. If a directory is provided without a library argument, then the entire repo is copied
                        and tested for import-ability. If both a directory and a library are provided, then only the imports from the
                        library are copied.
  --commit-message COMMIT_MESSAGE
                        The commit message to use when committing the changes.
```

> Note: this project was created to verify that Python 3.10, PySide6, and QtPy could work
> together in an environment.
