#!/usr/bin/env python

"""Run pre-commit hooks with manual stages."""

from __future__ import print_function

import subprocess
import sys

TRACE_PREFIX = "+"

RUN_HOOKS_COMMAND = [
    "pre-commit",
    "run",
    "--hook-stage",
    "manual",
]


def grok_args(args):
    """
    Figure out whether we have any arguments and extract the program "name".

    :Args:
        args
            A list of program arguments, including the program "name" as the
            zero-th argument (see `sys.argv`:py:attr:)

    :Returns:
        A best guess at (`prog`, `args`), where:

        - `prog` is the program "name"
        - `args` is the list of program arguments, beginning with the first
          argument (i.e., _not_ including the program name)
    """
    if not args:
        args = sys.argv
    try:
        prog = args[0]
    except IndexError:
        prog = None
    return (prog, args[1:])


def filter_args(args):
    """Add needed arguments to `args` only when needed."""
    for arg in ["-a", "--all-files", "-h", "--help", "--files"]:
        if arg in args:
            return args
    return ["--all-files"] + args


def main():
    """Run the pre-commit command to run manual hooks."""
    (_prog, args) = grok_args(sys.argv)

    if not args:
        print(
            "ERROR: Please supply the name of at least one hook to run manually.",
            file=sys.stderr,
        )
        sys.exit(1)

    args = filter_args(args)
    command = RUN_HOOKS_COMMAND + args
    print(" ".join([TRACE_PREFIX] + command), file=sys.stderr)
    status = subprocess.call(command)
    sys.exit(status)


if __name__ == "__main__":
    main()
