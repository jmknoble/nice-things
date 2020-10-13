#!/usr/bin/env python

"""Create or print a sample `.pre-commit-config.yaml`."""

from __future__ import print_function

import os.path
import subprocess
import sys

TRACE_PREFIX = "+"

CONFIG = ".pre-commit-config.yaml"

CONFIG_FOUND_MESSAGE = """
WARNING: {config} file already exists!
Printing sample config file to stdout instead.
You may redirect stdout to the file of your choice.
""".format(
    config=CONFIG
).strip()

SAMPLE_CONFIG_COMMAND = [
    "pre-commit",
    "sample-config",
]


def print_sample_config(outfile=sys.stdout):
    """Print a sample config to `outfile`."""
    print(" ".join([TRACE_PREFIX] + SAMPLE_CONFIG_COMMAND), file=sys.stderr)

    try:
        output = subprocess.check_output(SAMPLE_CONFIG_COMMAND, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return e.returncode

    outfile.write(output)

    return 0


def main():
    """Run the pre-commit command to print a sample config."""
    if os.path.exists(CONFIG):
        print(CONFIG_FOUND_MESSAGE, file=sys.stderr)
        status = print_sample_config()
    else:
        with open(CONFIG, "w") as outfile:
            status = print_sample_config(outfile=outfile)

    sys.exit(status)


if __name__ == "__main__":
    main()
