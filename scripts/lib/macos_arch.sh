#!/bin/bash
# Apple Silicon helpers - keep ragdex native (arm64) so it never needs Rosetta.
#
# Source this file. Every function follows the same contract: returns 0/1,
# and the find_* functions print the path they found on stdout.
# On Intel Macs and Linux every check passes, so callers need no branching.

# True on Apple Silicon hardware, even when this shell runs under Rosetta
is_apple_silicon() {
    [ "$(uname -s)" = "Darwin" ] && [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = "1" ]
}

# True if the current process is being translated by Rosetta
is_running_under_rosetta() {
    [ "$(sysctl -n sysctl.proc_translated 2>/dev/null)" = "1" ]
}

# True if the command (name or path) runs natively on this machine.
# Scripts count as native; their interpreter is checked separately.
is_native_executable() {
    local exe_path
    exe_path=$(command -v "$1" 2>/dev/null) || return 1
    is_apple_silicon || return 0
    case "$(file -bL "$exe_path" 2>/dev/null)" in
        *arm64*|*script*) return 0 ;;
        *) return 1 ;;
    esac
}

# True if the Python interpreter runs as arm64 on Apple Silicon
is_native_python() {
    local py_cmd="$1"
    is_apple_silicon || return 0
    [ "$("$py_cmd" -c 'import platform; print(platform.machine())' 2>/dev/null)" = "arm64" ]
}

# True if a virtualenv is fully native: its Python runs as arm64 and none of
# its compiled extensions are Intel-only. A universal interpreter (e.g. the
# Command Line Tools Python) can still carry x86_64-only wheels from an Intel Mac.
is_native_venv() {
    local venv_dir="$1"
    is_native_python "$venv_dir/bin/python" || return 1
    is_apple_silicon || return 0
    # Each file's summary line (the one with the '|' separator) lists every
    # architecture it contains; per-slice lines of universal binaries are skipped
    ! find "$venv_dir/lib" -name '*.so' -print0 2>/dev/null \
        | xargs -0 file -F '|' 2>/dev/null \
        | grep -F '|' | grep -v arm64 | grep -q x86_64
}

# Print the interpreter from a script's shebang (e.g. a pip console script)
script_interpreter() {
    local script_path="$1"
    head -n 1 "$script_path" 2>/dev/null | sed -n 's/^#![[:space:]]*\([^[:space:]]*\).*/\1/p'
}

# Print the Homebrew to use. On Apple Silicon only the native /opt/homebrew
# install qualifies - an Intel /usr/local Homebrew installs Rosetta-only tools.
find_native_brew() {
    if is_apple_silicon; then
        [ -x /opt/homebrew/bin/brew ] && echo /opt/homebrew/bin/brew && return 0
        return 1
    fi
    command -v brew 2>/dev/null
}

# Print the first timeout command that actually runs here
find_working_timeout() {
    local cmd
    for cmd in gtimeout timeout; do
        if command -v "$cmd" >/dev/null 2>&1 && "$cmd" 1 true >/dev/null 2>&1; then
            command -v "$cmd"
            return 0
        fi
    done
    return 1
}
