#!/usr/bin/env python

from __future__ import print_function

import os
import os.path
import sys

import utilutil.argparsing as argparsing
import utilutil.runcommand as runcommand

DEFAULT_VERSION_FILENAME = "VERSION"

DESCRIPTION = (
    "Add an annotated tag corresponding to the version of the current "
    "git project.  The version is expected to live in a file named "
    "'{version_filename}' in the project root."
).format(version_filename=DEFAULT_VERSION_FILENAME)

DEFAULT_TAG_PREFIX = "v"
DEFAULT_TAG_SUFFIX = ""


def _get_project_dir():
    """Return the top-level directory of the current Git project"""
    project_dir = runcommand.run_command(
        ["git", "rev-parse", "--show-toplevel"],
        dry_run=False,
        return_output=True,
        show_trace=False,
    )
    return project_dir[:-1] if project_dir.endswith("\n") else project_dir


def _get_project_version(version_file):
    """Return the version as read from `version_file`"""
    version = version_file.read().lstrip().splitlines()
    if not version:
        raise RuntimeError(
            "{path}: version file appears to be blank".format(path=version_file.path)
        )
    return version[0].rstrip()


def _add_arguments(argparser):
    """Add command-line arguments to an argument parser"""
    argparsing.add_dry_run_argument(argparser)
    argparsing.add_chdir_argument(argparser)
    prefix_args = argparser.add_mutually_exclusive_group(required=False)
    prefix_args.add_argument(
        "-p",
        "--prefix",
        dest="tag_prefix",
        action="store",
        default=DEFAULT_TAG_PREFIX,
        help="String to prepend to version tag (default: {default})".format(
            default=repr(DEFAULT_TAG_PREFIX)
        ),
    )
    prefix_args.add_argument(
        "--no-prefix",
        dest="tag_prefix",
        action="store_const",
        const="",
        help="Do not use any tag prefix",
    )
    suffix_args = argparser.add_mutually_exclusive_group(required=False)
    suffix_args.add_argument(
        "-s",
        "--suffix",
        dest="tag_suffix",
        action="store",
        default=DEFAULT_TAG_SUFFIX,
        help="String to append to version tag (default: {default})".format(
            default=repr(DEFAULT_TAG_SUFFIX)
        ),
    )
    suffix_args.add_argument(
        "--no-suffix",
        dest="tag_suffix",
        action="store_const",
        const="",
        help="Do not use any tag suffix",
    )
    argparser.add_argument(
        "-f",
        "--file",
        "--version-file",
        dest="version_file",
        action="store",
        default=None,
        help="File containing version (default: '{default}' in root of project)".format(
            default=DEFAULT_VERSION_FILENAME
        ),
    )
    return argparser


def main(*argv):
    """Do the thing"""
    (prog, argv) = argparsing.grok_argv(argv)
    argparser = argparsing.setup_argparse(prog=prog, description=DESCRIPTION)
    _add_arguments(argparser)
    args = argparser.parse_args(argv)

    if args.working_dir is not None:
        runcommand.print_trace(["cd", args.working_dir], dry_run=args.dry_run)
        os.chdir(args.working_dir)

    if args.version_file is None:
        args.version_file = os.path.join(_get_project_dir(), DEFAULT_VERSION_FILENAME)

    with open(args.version_file, "r") as version_file:
        project_version = "".join(
            [args.tag_prefix, _get_project_version(version_file), args.tag_suffix]
        )

    status = runcommand.run_command(
        [
            "git",
            "tag",
            "-a",
            "-m",
            project_version,
            project_version,  # Correct, not a duplicate
        ],
        check=False,
        show_trace=True,
        dry_run=args.dry_run,
    )
    return status


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
