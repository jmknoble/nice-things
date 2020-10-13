#!/bin/sh

set -e
set -u

PATH="/bin:/usr/bin:/sbin:/usr/sbin"

SUDO_PROMPT="%u@%h's password:"
export SUDO_PROMPT

PS4="${PS4:-+ }"
PREFIX="/usr/local"

PrintHelp() {
    cat <<EOF
usage: $0 [OPTIONS]
usage: $0 --help

Install the 'nice-things' command into PREFIX/bin.

options:
    -p/--prefix PREFIX (default: ${PREFIX})
    -c/--with-crontab

    -n/--dry-run
    -q/--quiet
EOF
    exit 42
}

########################################

MessagePrefix() {
    if [ x"${DRY_RUN}" = x"1" ]; then
        echo "[DRY-RUN] "
    else
        echo ""
    fi
}

Message() {
    echo "`MessagePrefix`$*"
}

DryRun() {
    if [ x"${DRY_RUN}" = x"1" ]; then
        Message "$*"
    fi
}

WetRun() {
    if [ x"${DRY_RUN}" = x"0" ]; then
        Message "$*"
    fi
}

DryRunWetRun() {
    local dry_run_message="$1"
    local wet_run_message="$2"
    if [ x"${DRY_RUN}" = x"1" ]; then
        Message "${dry_run_message}"
    else
        Message "${wet_run_message}"
    fi
}

Trace() {
    DryRun "Would run:"
    if [ x"${DRY_RUN}" = x"1" ] || [ x"${VERBOSE}" = x"1" ]; then
        echo "${PS4}$*" >&2
    fi
}

Run() {
    if [ x"${DRY_RUN}" = x"0" ]; then
        ${1:+"$@"}
    fi
}

Do() {
    Trace ${1:+"$@"}
    Run ${1:+"$@"}
}

Sudo() {
    if [ x"${MY_UID}" = x"0" ]; then
        Do ${1:+"$@"}
    else
        Do sudo ${1:+"$@"}
    fi
}

QuietSudo() {
    if [ x"${MY_UID}" = x"0" ]; then
        ${1:+"$@"}
    else
        sudo ${1:+"$@"}
    fi
}

CreateDir() {
    local mode="$1"
    local owner="$2"
    local group="$3"
    local target="$4"
    if [ -d "${target}" ]; then
        Message "OK: Directory exists: ${target}"
    else
        DryRunWetRun \
            "Would create directory: ${target}" \
            "Creating directory: ${target}"
        Sudo mkdir -p "${target}"
        Sudo chown "${owner}" "${target}"
        Sudo chgrp "${group}" "${target}"
        Sudo chmod "${mode}" "${target}"
    fi
}

InstallAs() {
    local mode="$1"
    local owner="$2"
    local group="$3"
    local source="$4"
    local target="$5"
    DryRunWetRun \
        "Would install: ${target}" \
        "Installing: ${target}"
    Sudo install -m "${mode}" -o "${owner}" -g "${group}" "${source}" "${target}"
}

CreateTempFile() {
    mktemp -t install-nice-things
}

GetCrontab() {
    set +e
    QuietSudo crontab -u root -l 2>/dev/null
    set -e
}

InstallCrontab() {
    local file="$1"
    Sudo crontab -u root "${file}"
}

FindMailTo() {
    local file="$1"
    egrep '^[ 	]*MAILTO=' "${file}"
}

FindNiceThingsCommand() {
    local file="$1"
    egrep '^[^#]*[ 	]'"${PREFIX}"'/bin/nice-things([ 	].*)?$' "${file}"
}

CompareFiles() {
    local source="$1"
    local target="$2"
    local status=0
    set +e
    cmp "${source}" "${target}" >/dev/null 2>&1
    status=$?
    set -e
    if [ ${status} -gt 1 ]; then
        cmp "${source}" "${target}"
    fi
    return ${status}
}

DiffFiles() {
    local source="$1"
    local target="$2"
    set +e
    diff -u "${source}" "${target}" 2>/dev/null
    status=$?
    set -e
    if [ ${status} -gt 1 ]; then
        diff -u "${source}" "${target}" >/dev/null
    fi
    return ${status}
}

OnExit() {
    set +u
    for i in \
        "${OLD_CRONTAB}" \
        "${NEW_CRONTAB}" \
    ; do
        if [ -n "${i}" ] && [ -f "${i}" ]; then
            rm -f "${i}"
        fi
    done
}

########################################

DRY_RUN=0
VERBOSE=1
WITH_CRONTAB=0

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            PrintHelp
            ;;
        -n|--dry-run|--dryrun)
            DRY_RUN=1
            shift
            ;;
        -q|--quiet)
            VERBOSE=0
            shift
            ;;
        -p|--prefix)
            PREFIX="$2"
            shift 2
            ;;
        --prefix=*)
            PREFIX="${1#--prefix=}"
            shift
            ;;
        -c|--with-crontab)
            WITH_CRONTAB=1
            shift
            ;;
        *)
            echo "$0: error: unrecognized option '$1'" >&2
            exit 1
            ;;
    esac
done

MY_UID="`id -u`"

if [ x"${MY_UID}" != x"0" ]; then
    QuietSudo true
fi

for i in \
    "${PREFIX}" \
    "${PREFIX}/bin" \
; do
    CreateDir 0755 0 0 "${i}"
done

InstallAs 0755 0 0 bin/nice-things.sh "${PREFIX}/bin/nice-things"

if [ x"${WITH_CRONTAB}" = x"1" ]; then
    OLD_CRONTAB=`CreateTempFile`
    NEW_CRONTAB=`CreateTempFile`
    trap OnExit 0 1 2 15

    Message "Retrieving root's crontab ..."
    GetCrontab >"${OLD_CRONTAB}"
    GetCrontab >"${NEW_CRONTAB}"
    if ! FindMailTo "${NEW_CRONTAB}" >/dev/null 2>&1; then
        echo >>"${NEW_CRONTAB}"
        echo >>"${NEW_CRONTAB}" 'MAILTO=""'
    fi
    if ! FindNiceThingsCommand "${NEW_CRONTAB}" >/dev/null 2>&1; then
        echo >>"${NEW_CRONTAB}"
        echo >>"${NEW_CRONTAB}" "* * * * * ${PREFIX}/bin/nice-things --quiet"
    fi

    if CompareFiles "${OLD_CRONTAB}" "${NEW_CRONTAB}"; then
        Message "OK: Crontab entry for nice-things already exists:"
        FindNiceThingsCommand "${NEW_CRONTAB}"
    else
        DryRunWetRun \
            "Would add the following to root's crontab:" \
            "Adding the following to root's crontab:"
        DiffFiles "${OLD_CRONTAB}" "${NEW_CRONTAB}" || true
        InstallCrontab "${NEW_CRONTAB}"
    fi
fi
