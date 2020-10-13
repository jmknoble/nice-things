"""Utility functions for use with argparse."""

from __future__ import print_function

import argparse
import sys


def grok_argv(argv):
    """
    Figure out whether we have any arguments and extract the program "name".

    :Args:
        argv
            A list of program arguments, including the program "name" as the
            zero-th argument (see `sys.argv`:py:attr:)

    :Returns:
        A best guess at (`prog`, `argv`), where:

        - `prog` is the program "name"
        - `argv` is the list of program arguments, beginning with the first
          argument (i.e., _not_ including the program name)
    """
    if not argv:
        argv = sys.argv
    try:
        prog = argv[0]
    except IndexError:
        prog = None
    return (prog, argv[1:])


def setup_argparse(prog=None, description=None, epilog=None, formatter_class=None):
    """
    Create an `argparse.ArgumentParser`:py:class: with some stuff populated.

    :Args:
        prog
            (optional) The program name, if any; if not supplied, let
            `argparse.ArgumentParser`:py:class: figure it out

        description
            (optional) The program description, if any

        epilog
            (optional) The epilog to the program help text, if any

        formatter_class
            (optional) The formatter class to use when printing help text
            (see `argparse`:py:mod: documentation)

    :Returns:
        The `argparse.ArgumentParser`:py:class: instance
    """
    kwargs = {"add_help": True}
    if prog is not None:
        kwargs["prog"] = prog
    if description is not None:
        kwargs["description"] = description
    if epilog is not None:
        kwargs["epilog"] = epilog
    if formatter_class is not None:
        kwargs["formatter_class"] = formatter_class
    argparser = argparse.ArgumentParser(**kwargs)
    return argparser


def add_dry_run_argument(argparser):
    """
    Add a standardized "dry-run" argument to an argument parser.

    :Args:
        argparser
            The `argparse.ArgumentParser`:py:class: to add the argument to

    :Returns:
        Nothing
    """
    argparser.add_argument(
        "-n",
        "--dry-run",
        "--dryrun",
        dest="dry_run",
        action="store_true",
        help="Show what would be done, but don't actually do it",
    )


def add_chdir_argument(argparser):
    """
    Add a standardized "change dir" argument to an argument parser.

    :Args:
        argparser
            The `argparse.ArgumentParser`:py:class: to add the argument to

    :Returns:
        Nothing
    """
    argparser.add_argument(
        "-C",
        "--cd",
        "--chdir",
        dest="working_dir",
        action="store",
        default=None,
        help="Directory to change to (default: current directory)",
    )
