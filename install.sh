#!/usr/bin/env bash
#
# flow — installer for Linux & macOS (from a source checkout).
#
#   ./install.sh           Install the `flow` script to a bin directory on PATH
#   ./install.sh --pip      Install via pip instead (python -m pip install .)
#   ./install.sh --uninstall Remove a previously installed `flow`
#   ./install.sh --help
#
# `flow` is a single, dependency-free Python script. The default install simply
# copies it onto your PATH. The optional system tools below unlock extra
# features and are reported (never required).

set -euo pipefail

GREEN=$'\033[0;32m'; YELLOW=$'\033[0;33m'; RED=$'\033[0;31m'; BOLD=$'\033[1m'; OFF=$'\033[0m'
ok()   { printf '  %s✓%s %s\n' "$GREEN" "$OFF" "$1"; }
warn() { printf '  %s!%s %s\n' "$YELLOW" "$OFF" "$1"; }
err()  { printf '  %s✗%s %s\n' "$RED" "$OFF" "$1"; }
info() { printf '%s%s%s\n' "$BOLD" "$1" "$OFF"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Resolve the real user's home even under sudo (config must land there). ──
real_home() {
  if [ -n "${SUDO_USER:-}" ]; then eval echo "~$SUDO_USER"; else echo "$HOME"; fi
}

# ── Pick an install prefix: system-wide as root, else the user's ~/.local. ──
if [ "${EUID:-$(id -u)}" -eq 0 ]; then
  BIN_DIR="/usr/local/bin"
else
  BIN_DIR="$HOME/.local/bin"
fi

usage() {
  cat <<'EOF'
flow — installer for Linux & macOS (from a source checkout).

  ./install.sh              Install the `flow` script to a bin dir on PATH
  ./install.sh --pip        Install via pip instead (python -m pip install --user .)
  ./install.sh --uninstall  Remove a previously installed `flow`
  ./install.sh --help       Show this help

flow is a single, dependency-free Python script. The default install copies it
onto your PATH. Optional system tools (mpv, paplay, cava, zenity) are detected
at runtime and only ever reported — never required.
EOF
  exit 0
}

uninstall() {
  info "Uninstalling flow…"
  local removed=0
  for d in /usr/local/bin "$HOME/.local/bin" /usr/bin; do
    if [ -f "$d/flow" ]; then rm -f "$d/flow" && ok "removed $d/flow" && removed=1; fi
  done
  command -v pip3 >/dev/null 2>&1 && pip3 show flow-tui >/dev/null 2>&1 \
    && pip3 uninstall -y flow-tui >/dev/null 2>&1 && ok "removed pip package flow-tui" && removed=1
  [ "$removed" -eq 1 ] || warn "no installed flow found"
  printf '\nYour data in %s/.config/flow was left untouched.\n' "$(real_home)"
  exit 0
}

pip_install() {
  info "Installing flow via pip…"
  local py; py="$(command -v python3 || command -v python)" \
    || { err "Python 3 not found."; exit 1; }
  "$py" -m pip install --user . && ok "installed package flow-tui"
  printf '\nRun: %sflow%s\n' "$BOLD" "$OFF"
  exit 0
}

# ── Parse args ──
case "${1:-}" in
  -h|--help) usage ;;
  --uninstall) uninstall ;;
  --pip) pip_install ;;
  "") : ;;
  *) err "unknown option: $1"; usage ;;
esac

# ── Default install: copy the script onto PATH ──
info "Installing flow → $BIN_DIR/flow"
[ -f flow ] || { err "cannot find 'flow' next to this script"; exit 1; }
mkdir -p "$BIN_DIR"
install -m 0755 flow "$BIN_DIR/flow"
ok "installed flow"

# Pre-seed the bundled Krishna-flute recording so it is available offline.
# (flow also self-copies it on first run when the MP3 sits beside the script.)
KRISHNA_SRC="$(ls krishna*.mp3 2>/dev/null | head -1 || true)"
if [ -n "$KRISHNA_SRC" ]; then
  SOUNDS_DIR="$(real_home)/.config/flow/sounds"
  mkdir -p "$SOUNDS_DIR"
  cp -n "$KRISHNA_SRC" "$SOUNDS_DIR/krishna_flute.mp3" 2>/dev/null \
    && ok "bundled ambient track → $SOUNDS_DIR/krishna_flute.mp3"
fi

# ── Report optional runtime tools (informational only) ──
printf '\n%sOptional tools (flow works without them)%s\n' "$BOLD" "$OFF"
check() { if command -v "$1" >/dev/null 2>&1; then ok "$1 — $2"; else warn "$1 not found — $3"; fi; }
check python3 "interpreter"                       "flow needs Python 3 to run"
check mpv     "ambient / lofi audio"              "no audio playback"
check paplay  "transition chimes"                 "falls back to the terminal bell"
check cava    "audio-reactive visualizer"         "falls back to a simulated visualizer"
check zenity  "native folder picker (stats export)" "export falls back to fzf or typing a path"

# ── PATH hint ──
case ":$PATH:" in
  *":$BIN_DIR:"*) : ;;
  *) printf '\n%sNote:%s %s is not on your PATH. Add to your shell rc:\n  export PATH="%s:$PATH"\n' \
       "$YELLOW" "$OFF" "$BIN_DIR" "$BIN_DIR" ;;
esac

printf '\n%sDone.%s Run %sflow%s to start.\n' "$GREEN" "$OFF" "$BOLD" "$OFF"
