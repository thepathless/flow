# Linux packaging

Everything needed to ship `flow` on Linux. `flow` is a single, dependency-free
Python script, so most of this is just metadata + install locations.

Priority order (as requested): **AppImage → Arch/AUR → everything else.**

---

## 1. AppImage (recommended — works on every distro)

A self-contained binary that bundles its own Python. No install, no dependencies.

```sh
cd linux/appimage
./build-appimage.sh                 # → ../../flow-x86_64.AppImage
# build for ARM:
ARCH=aarch64 ./build-appimage.sh
# pick a different bundled Python:
PY_VERSION=3.11 ./build-appimage.sh
```

Run it:

```sh
chmod +x flow-x86_64.AppImage
./flow-x86_64.AppImage
```

The script downloads `appimagetool` + a relocatable CPython (from
[python-appimage]), injects `flow`, and repacks. Needs only `bash` + `curl`
(FUSE not required). This is also what the GitHub release workflow runs
automatically on every `v*` tag — see [`../.github/workflows/release.yml`](../.github/workflows/release.yml).

---

## 2. Arch Linux / Manjaro — pacman via the AUR

```sh
yay -S flow-tui        # or: paru -S flow-tui
```

To publish/update the AUR package from [`PKGBUILD`](PKGBUILD):

```sh
# in a clean dir with PKGBUILD
updpkgsums                                  # pin the source checksum
makepkg -si                                 # build + install locally to test
makepkg --printsrcinfo > .SRCINFO           # AUR requires this
git clone ssh://aur@aur.archlinux.org/flow-tui.git
cp PKGBUILD .SRCINFO flow-tui/ && cd flow-tui
git add -A && git commit -m "flow-tui 1.0.0" && git push
```

Local build straight from this repo (no AUR):

```sh
makepkg -si -p linux/PKGBUILD
```

---

## 3. Any distro — Makefile

```sh
sudo make -C linux install            # → /usr/local/bin/flow + desktop + icon
make -C linux install PREFIX=~/.local # per-user, no root
sudo make -C linux uninstall
```

## 4. Debian/Ubuntu (.deb) & Fedora/openSUSE (.rpm) — nfpm

Generate native packages from [`nfpm.yaml`](nfpm.yaml) (install [nfpm] first):

```sh
# run from the repository root
nfpm pkg -f linux/nfpm.yaml -p deb -t dist/
nfpm pkg -f linux/nfpm.yaml -p rpm -t dist/

sudo apt install ./dist/flow-tui_1.0.0_all.deb
sudo dnf install ./dist/flow-tui-1.0.0.noarch.rpm
```

## 5. pip (fallback, also cross-platform)

```sh
pip install flow-tui
```

---

### Optional runtime tools

`flow` runs with none of these, enabling features when present: `mpv` (audio),
`paplay`/`libpulse` (chimes), `cava` (visualizer), `zenity`/`kdialog` or `fzf`
(folder picker for stats export).

[python-appimage]: https://github.com/niess/python-appimage
[nfpm]: https://nfpm.goreleaser.com
