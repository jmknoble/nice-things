#!/bin/sh

set -e
set -u

PATH="/bin:/usr/bin:/sbin:/usr/sbin"

DEFAULT_PROCESS_NAMES='
    iCoreService
    mdworker
'

PrintHelp() {
    cat <<EOF
usage: $0 [OPTIONS] [PROCESS_NAME [PROCESS_NAME...]]
       $0 --help

Renice processes that match PROCESS_NAME to a priority of 20 (i.e., least
important).

PROCESS_NAME is matched the same as pgrep(1).  If -f/--full is supplied,
the name is matched against the full argument list (i.e., 'pgrep -f ...').

The default PROCESS_NAMEs are: ${DEFAULT_PROCESS_NAMES}

options:
    -f/--full
    -n/--dry-run
    -q/--quiet
    -v/--verbose
EOF
    exit 42
}

########################################

Pgrep() {
    set +u
    set +e
    if [ x"${PGREP_FULL}" = x"0" ]; then
        pgrep -f ${1:+"$@"}
    else
        pgrep ${1:+"$@"}
    fi
    set -e
    set -u
}

GetPids() {
    local i
    for i in ${1:+"$@"}; do
        Pgrep ${i}
    done
}

FormatPids() {
    awk '
        {
            if (NR > 1) {
                printf(",")
            }
            printf("%s", $0)
        }
        END {
            printf("\n")
        }
    '
}

GetPidInfo() {
    local pids="$1"
    ps -o pid,nice -p "${pids}"
}

Logging() {
    local line
    if [ x"${DRY_RUN}" = x"0" ]; then
        while read line; do
            logger -s -t nice-things "${line}"
        done
    else
        cat >&2
    fi
}

Renice() {
    awk \
        -v MyUid="${MY_UID}" \
        -v DryRun="${DRY_RUN}" \
        -v Verbose="${VERBOSE}" \
        -v TracePrompt="${PS4:-+ }" \
        'BEGIN {
            n = 0
            RenicePids[n] = ""
            del RenicePids[n]
        }
        !/PID/ {
            Pid = $1
            Nice = $2
            if (Nice < 20) {
                n += 1
                RenicePids[n] = Pid
            }
        }
        END {
            Command = ""
            if (n > 0) {
                if (MyUid != 0) {
                    Command = Command "sudo "
                }
                Command = Command "renice 20 -p"
                for (i = 1; i <= n; i++) {
                    Command = Command " " RenicePids[i]
                }
            }
            if (DryRun || Verbose) {
                if (("" == Command) && (Verbose > 1)) {
                    print("No pids to renice")
                } else {
                    if (DryRun) {
                        print "[DRY-RUN] Would run:"
                    }
                    print(TracePrompt Command)
                }
            }
            if (!DryRun) {
                system(Command)
            }
        }
    '
}

########################################

PGREP_FULL=0
DRY_RUN=0
VERBOSE=1

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            PrintHelp
            ;;
        -f|--full)
            PGREP_FULL=1
            shift
            ;;
        -n|--dry-run|--dryrun)
            DRY_RUN=1
            shift
            ;;
        -q|--quiet)
            VERBOSE=0
            shift
            ;;
        -v|--verbose)
            VERBOSE=2
            shift
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "$0: error: unrecognized option '$1'" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

MY_UID=`id -u`

if [ x"${MY_UID}" != x"0" ] && [ x"${DRY_RUN}" = x"0" ]; then
    sudo true
fi

if [ $# -eq 0 ]; then
    set ${DEFAULT_PROCESS_NAMES}
fi

PIDS="`GetPids ${1:+"$@"} | FormatPids`"

GetPidInfo ${PIDS} \
| Renice \
| Logging
