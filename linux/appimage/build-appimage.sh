#!/usr/bin/env bash
#
# Build a self-contained flow AppImage that runs on ANY glibc Linux distro with
# no Python installed — the interpreter is bundled.
#
#   ./build-appimage.sh                 # build for the host architecture
#   PY_VERSION=3.12 ARCH=x86_64 ./build-appimage.sh
#
# How it works (the most reliable recipe — no guesswork at runtime):
#   1. grab the official `appimagetool` (stable "continuous" release),
#   2. grab a relocatable CPython AppImage from python-appimage (bundles _curses),
#   3. unpack it, drop the single `flow` script + ambient track inside,
#   4. point AppRun at the bundled python, then repack with appimagetool.
#
# Requires only: bash, curl, and the ability to run AppImages (FUSE not needed —
# we use --appimage-extract / --appimage-extract-and-run).

set -euo pipefail

# ── Configuration ───────────────────────────────────────────────────────────
PY_VERSION="${PY_VERSION:-3.12}"          # bundled CPython minor version
ARCH="${ARCH:-$(uname -m)}"               # x86_64 or aarch64
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"         # repository root (where `flow` lives)
BUILD="$HERE/build"
APPDIR="$BUILD/AppDir"
CPVER="cp${PY_VERSION//./}"               # e.g. 3.12 -> cp312
OUT="$REPO/flow-${ARCH}.AppImage"

log() { printf '\033[1;32m▶\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || die "curl is required"
[ -f "$REPO/flow" ] || die "cannot find 'flow' at repo root ($REPO)"

rm -rf "$BUILD"; mkdir -p "$BUILD"

# ── 1. appimagetool ───────────────────────────────────────────────────────────
TOOL="$BUILD/appimagetool-${ARCH}.AppImage"
log "Fetching appimagetool…"
curl -fsSL -o "$TOOL" \
  "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
chmod +x "$TOOL"

# ── 2. base CPython AppImage (find the exact asset via the GitHub API) ─────────
log "Resolving python-appimage base for Python ${PY_VERSION} (${ARCH})…"
API="https://api.github.com/repos/niess/python-appimage/releases/tags/python${PY_VERSION}"
BASE_URL="$(curl -fsSL "$API" \
  | grep -oE "https://[^\"]*${CPVER}-${CPVER}-manylinux[^\"]*_${ARCH}\.AppImage" \
  | head -1 || true)"
[ -n "$BASE_URL" ] || die "no python-appimage build found for ${CPVER}/${ARCH}. Try another PY_VERSION."
log "Base: $BASE_URL"
BASE="$BUILD/python-base.AppImage"
curl -fsSL -o "$BASE" "$BASE_URL"
chmod +x "$BASE"

# ── 3. unpack and inject flow ─────────────────────────────────────────────────
log "Unpacking base interpreter…"
( cd "$BUILD" && "$BASE" --appimage-extract >/dev/null )
mv "$BUILD/squashfs-root" "$APPDIR"

# Ensure a plain `python3` symlink exists beside the versioned binary.
if [ ! -e "$APPDIR/usr/bin/python3" ]; then
  ln -sf "python${PY_VERSION}" "$APPDIR/usr/bin/python3"
fi

log "Installing flow into the AppDir…"
install -Dm755 "$REPO/flow" "$APPDIR/usr/bin/flow"
# Place the bundled ambient track beside the script so flow auto-loads it.
mp3="$(ls "$REPO"/krishna*.mp3 2>/dev/null | head -1 || true)"
[ -n "$mp3" ] && install -Dm644 "$mp3" "$APPDIR/usr/bin/$(basename "$mp3")"

# ── 4. metadata: AppRun, desktop, icon ────────────────────────────────────────
log "Writing AppRun + desktop + icon…"
# python-appimage ships its own python*.desktop/AppRun — replace them with ours.
rm -f "$APPDIR"/*.desktop "$APPDIR"/python*.png "$APPDIR"/.DirIcon "$APPDIR"/AppRun

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="$HERE/usr/bin:$PATH"
# ncurses needs a terminfo database; prefer the host's, fall back sanely.
export TERMINFO="${TERMINFO:-/usr/share/terminfo}"
export TERM="${TERM:-xterm-256color}"
exec "$HERE/usr/bin/python3" "$HERE/usr/bin/flow" "$@"
EOF
chmod +x "$APPDIR/AppRun"

install -Dm644 "$HERE/../flow.desktop" "$APPDIR/flow.desktop"
install -Dm644 "$HERE/../flow.svg" "$APPDIR/flow.svg"
install -Dm644 "$HERE/../flow.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/flow.svg"
cp "$HERE/../flow.svg" "$APPDIR/.DirIcon"

# ── 5. pack ───────────────────────────────────────────────────────────────────
log "Packing → $OUT"
ARCH="$ARCH" "$TOOL" --appimage-extract-and-run "$APPDIR" "$OUT"
chmod +x "$OUT"

log "Done: $OUT"
printf '   Test it:  %s\n' "$OUT"
