"""Wrapper functions for running commands via `subprocess`:py:mod:."""

from __future__ import print_function

import os
import subprocess
import sys

TRACE_PREFIX = os.environ.get("PS4", "+ ")
DRY_RUN_PREFIX = "[DRY-RUN] "
WET_RUN_PREFIX = ""


def get_message_prefix(dry_run=False):
    """Return a standard dry-run or wet-run prefix for trace messages."""
    return DRY_RUN_PREFIX if dry_run else WET_RUN_PREFIX


def print_trace(
    args, message_prefix=None, trace_prefix=TRACE_PREFIX, dry_run=False, msgfile=None
):
    """
    Print a message tracing execution of a command.

    :Args:
        args
            The words that form the command

        message_prefix
            (optional) The text to prepend to the message before `trace_prefix`

        trace_prefix
            (optional) The text to prepend to the command indicating this is a
            trace

        dry_run
            (optional) If `message_prefix` is none, use a standard dry-run
            (`True`-ish) or wet-run (`False`-ish) message prefix
    """
    message_prefix = (
        get_message_prefix(dry_run) if message_prefix is None else message_prefix
    )
    msgfile = sys.stderr if msgfile is None else msgfile
    print("".join([message_prefix, trace_prefix, " ".join(args)]), file=msgfile)


def run_command(
    args,
    check=True,
    dry_run=False,
    return_output=False,
    show_trace=False,
    trace_prefix=TRACE_PREFIX,
    msgfile=None,
    # fmt: off
    **kwargs
    # fmt: on
):
    """
    Run a command with various behaviors in a Python-2-compatible fashion.

    :Args:
        args
            The words that form the command

        check
            (optional) If `True`-ish, raise an exception if the command returns
            unsuccessful status (uses `subprocess.check_call()`:py:meth:);
            otherwise, simply return the status (uses
            `subprocess.call()`:py:meth:)

        dry_run
            (optional) If `True`-ish, only print what command would run without
            executing it

        return_output
            (optional) If `True`-ish, return the output from the command (uses
            `subprocess.check_output()`:py:meth: with
            ``universal_newlines``=`True`)

        show_trace
            (optional) If `True`-ish, print a trace of the command right before
            it is executed

        trace_prefix
            (optional) The text to prepend to a trace message

        kwargs
            (optional) Any additional keyword arguments to pass to
            `subprocess.call()`:py:meth:, `subprocess.check_call()`:py:meth:,
            or `subprocess.check_output()`:py:meth:

    :Returns:
        - If `dry_run` is `True`, returns `None` if `return_output` is `True`,
          or 0 if `return_output` is `False`; otherwise,
        - If `return_output` is `True, returns the result of
          `subprocess.check_output()`:py:meth:; otherwise,
        - If `check` is `True`, returns the result of
          `subprocess.check_call()`:py:meth:; otherwise,
        - Returns the result of `subprocess.call()`:py:meth:

    :Raises:
        See `subprocess.check_output()`:py:meth:,
        `subprocess.check_call()`:py:meth:, and `subprocess.call()`:py:meth:.
    """
    if dry_run:
        msgfile = sys.stderr if msgfile is None else msgfile
        print(
            "{prefix}Would run the following command:".format(
                prefix=get_message_prefix(dry_run)
            ),
            file=msgfile,
        )

    if dry_run or show_trace:
        print_trace(args, trace_prefix=trace_prefix, dry_run=dry_run)
    if dry_run:
        return None if return_output else 0
    if return_output:
        return subprocess.check_output(args, universal_newlines=True, **kwargs)
    if check:
        return subprocess.check_call(args, **kwargs)
    return subprocess.call(args, **kwargs)
