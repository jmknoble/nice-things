#!/usr/bin/env python

"""Install pre-commit hooks."""

from __future__ import print_function

import os.path
import subprocess
import sys

TRACE_PREFIX = "+"

CONFIG = ".pre-commit-config.yaml"

CONFIG_NOT_FOUND_MESSAGE = """
WARNING: No {config} file found.  Some hook installation steps will fail.
You can re-run this script after creating a {config} file.
You can create a sample {config} file using 'seed-hook-config.py'.
""".format(
    config=CONFIG
).strip()

INSTALL_HOOKS_COMMAND = [
    "pre-commit",
    "install",
    "-f",
    "--install-hooks",
    "-t",
    "pre-commit",
]


def main():
    """Run the pre-commit command to install hooks."""
    if not os.path.exists(CONFIG):
        print(CONFIG_NOT_FOUND_MESSAGE, file=sys.stderr)

    print(" ".join([TRACE_PREFIX] + INSTALL_HOOKS_COMMAND), file=sys.stderr)
    status = subprocess.call(INSTALL_HOOKS_COMMAND)
    sys.exit(status)


if __name__ == "__main__":
    main()
