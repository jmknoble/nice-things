#!/usr/bin/env python

from __future__ import print_function

import os
import os.path
import random
import subprocess
import sys

import utilutil.argparsing as argparsing
import utilutil.runcommand as runcommand

DEFAULT_VERSION_FILENAME = "VERSION"
DEFAULT_STABLE_VERSION_FILENAME = "STABLE_VERSION"
DEFAULT_STABLE_TAG = "stable"

DESCRIPTION = (
    "Add an annotated tag corresponding to the version of the current "
    "git project.  The version is expected to live in a file named "
    "'{version_filename}' in the project root."
).format(version_filename=DEFAULT_VERSION_FILENAME)

DEFAULT_TAG_PREFIX = "v"
DEFAULT_TAG_SUFFIX = ""

SAFETY_MESSAGES = [
    "Make sure there are sufficient parallel universes available.",
    "Are you wearing your paradox protection headgear?",
    "Commit log may turn into a big ball of wibbly-wobbly, timey-wimey stuff.",
    "1.21 Gigawatts?! Great Scott!",
    "Avoid gate addresses that cause wormhole to pass through solar flares.",
    "Reconfiguring sensor array to generate inverse tachyon pulse.",
    "Time to learn how to speak Heptapod.",
    "Alerting Time Enforcement Commission...",
    "Is the drive plate sealed?  Only You Can Prevent Radiation Leaks!",
    "Safety not guaranteed.",
]


def _get_safety_message():
    return random.choice(SAFETY_MESSAGES)


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
    argparser.add_argument(
        "-c",
        "--commit",
        dest="commit",
        action="store",
        default=None,
        help="Commit to tag (default: currently checked out HEAD)",
    )
    argparser.add_argument(
        "-m",
        "--message",
        dest="message",
        action="store",
        default=None,
        help=(
            "Message to add to annotated version tag "
            "(default: same as the tag, like git-flow)"
        ),
    )
    argparser.add_argument(
        "--push",
        action="store_true",
        help="Push the tags after creating them.",
    )
    argparser.add_argument(
        "-S",
        "--stable",
        dest="stable",
        action="store_true",
        default=False,
        help="Mark the current version as stable by adding/updating a 'stable' tag.",
    )
    argparser.add_argument(
        "--stable-tag",
        dest="stable_tag",
        action="store",
        default=DEFAULT_STABLE_TAG,
        help=(
            "The name of the tag to use when marking the current version stable "
            "(default: {default})"
        ).format(default=DEFAULT_STABLE_TAG),
    )
    argparser.add_argument(
        "-M",
        "--stable-message",
        dest="stable_message",
        action="store",
        default=None,
        help="Commit message for 'stable' tag (default: the version being tagged)",
    )
    argparser.add_argument(
        "-F",
        "--stable-file",
        "--stable-version-file",
        dest="stable_version_file",
        action="store",
        default=None,
        help=(
            "File containing stable version "
            "(default: '{default}' in root of project)"
        ).format(default=DEFAULT_STABLE_VERSION_FILENAME),
    )
    argparser.add_argument(
        "-T",
        "--time-travel",
        "--rewrite-history",
        dest="rewrite_history",
        action="store_true",
        default=False,
        help=(
            "Rewrite history by changing a pre-existing version tag to point "
            "to the current commit (this is inadvisable, but may be necessary "
            "in some cases)."
        ),
    )
    argparser.add_argument(
        "--accept-paradoxes",
        "--peril-sensitive-sunglasses",
        dest="peril_sensitive_sunglasses",
        action="store_true",
        default=False,
        help="When rewriting history, ignore warnings and continue blindly ahead.",
    )
    return argparser


def _does_tag_exist(tag):
    tags = runcommand.run_command(
        ["git", "tag", "--list", tag],
        check=False,
        return_output=True,
        show_trace=True,
        dry_run=False,
    )
    return tag in tags.split("\n")


def _should_continue(
    prompt="Are you sure you want to do this (yes/no)? ", dry_run=False
):
    if dry_run:
        runcommand.print_trace(
            ["Would prompt:", prompt], trace_prefix="", dry_run=dry_run
        )
        return True

    try:
        get_input = raw_input
    except NameError:
        get_input = input

    prompt = "".join([runcommand.get_message_prefix(dry_run=dry_run), prompt])
    text = get_input(prompt).strip().lower()
    return text in {"yes", "y", "1", "t", "true", "go ahead", "ok", "why not?"}


def _store_stable_version(version, stable_version_file, dry_run):
    if os.path.exists(stable_version_file):
        runcommand.print_trace(
            ["Storing", version, "as stable version ..."],
            trace_prefix="",
            dry_run=dry_run,
        )
        if not dry_run:
            with open(stable_version_file, "w") as f:
                f.write(version + "\n")
        status = runcommand.run_command(
            ["git", "diff", "-s", "--exit-code", stable_version_file],
            check=False,
            show_trace=True,
            dry_run=dry_run,
        )
        if dry_run or status == 1:
            commit_command = [
                "git",
                "commit",
                "-m",
                "Update stable version to {version}".format(version=version),
                stable_version_file,
            ]
            runcommand.run_command(
                commit_command,
                check=True,
                show_trace=True,
                dry_run=dry_run,
            )


def main(*argv):  # pylint: disable=too-many-branches
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

    if args.stable_version_file is None:
        args.stable_version_file = os.path.join(
            _get_project_dir(), DEFAULT_STABLE_VERSION_FILENAME
        )

    with open(args.version_file, "r") as version_file:
        bare_project_version = _get_project_version(version_file)
        project_version = "".join(
            [args.tag_prefix, bare_project_version, args.tag_suffix]
        )

    if args.message is None:
        args.message = project_version
    if args.stable_message is None:
        args.stable_message = project_version

    base_tag_command = ["git", "tag"]

    tag_command = list(base_tag_command)
    tag_command.extend(["-a", "-m", args.message])

    if args.rewrite_history:
        tag_command.append("--force")
        if _does_tag_exist(project_version):
            for message in [
                "CAUTION!!! History may be rewritten!",
                _get_safety_message(),
            ]:
                runcommand.print_trace([message], trace_prefix="", dry_run=args.dry_run)
            if args.peril_sensitive_sunglasses:
                runcommand.print_trace(
                    ["Peril-sensitive sunglasses deployed, proceeding anyway..."],
                    trace_prefix="",
                    dry_run=args.dry_run,
                )
            elif not _should_continue(dry_run=args.dry_run):
                runcommand.print_trace(
                    ["Aborting..."], trace_prefix="", dry_run=args.dry_run
                )
                return 1

    tag_command.append(project_version)

    if args.commit is not None:
        tag_command.append(args.commit)

    try:
        if args.stable:
            # Must do this before tagging
            _store_stable_version(
                bare_project_version, args.stable_version_file, dry_run=args.dry_run
            )

        runcommand.run_command(
            tag_command,
            check=True,
            show_trace=True,
            dry_run=args.dry_run,
        )

        if args.stable:
            stable_tag_command = list(base_tag_command)
            stable_tag_command.extend(["--force", args.stable_tag])
            if args.commit is not None:
                stable_tag_command.append(args.commit)
            runcommand.print_trace(
                ["Tagging", project_version, "as stable ..."],
                trace_prefix="",
                dry_run=args.dry_run,
            )
            runcommand.run_command(
                stable_tag_command,
                check=True,
                show_trace=True,
                dry_run=args.dry_run,
            )

        if args.push:
            base_push_command = ["git", "push"]
            if args.stable:
                # Push updated stable version file
                runcommand.run_command(
                    base_push_command, check=True, show_trace=True, dry_run=args.dry_run
                )

            push_command = list(base_push_command)
            if args.rewrite_history:
                push_command.append("--force")
            push_command.extend(
                ["origin", "+refs/tags/{tag}".format(tag=project_version)]
            )
            runcommand.run_command(
                push_command, check=True, show_trace=True, dry_run=args.dry_run
            )

            if args.stable:
                push_command = list(base_push_command)
                push_command.extend(
                    [
                        "--force",
                        "origin",
                        "+refs/tags/{tag}".format(tag=args.stable_tag),
                    ]
                )
                runcommand.run_command(
                    push_command, check=True, show_trace=True, dry_run=args.dry_run
                )

    except subprocess.CalledProcessError as e:
        print("{prog}: error: {e}".format(prog=prog, e=e), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
