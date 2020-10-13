#!/usr/bin/env python

"""Update hooks in `.pre-commit-config.yaml`."""

from __future__ import print_function

import subprocess
import sys

TRACE_PREFIX = "+"

AUTOUPDATE_COMMAND = [
    "pre-commit",
    "autoupdate",
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


def main():
    """Run the pre-commit command to update hooks."""
    (_prog, args) = grok_args(sys.argv)
    command = AUTOUPDATE_COMMAND + args
    print(" ".join([TRACE_PREFIX] + command), file=sys.stderr)
    status = subprocess.call(command)
    sys.exit(status)


if __name__ == "__main__":
    main()
