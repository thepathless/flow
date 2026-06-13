# 🌀 flow

A mouse-first **terminal focus app** — Pomodoro timer, nested to-dos, daily habit
tracker, ambient/lofi audio mixer, and an app blocker, all in one screen.

- **One file, zero Python dependencies.** Pure standard library + `curses`.
- Runs on **Linux, macOS, and Windows**.
- All state lives under `~/.config/flow/` (`config.json`, `tasks.json`, `habits.json`).

> Replace `<your-username>` below with your GitHub username after you create the repo
> (see [`github/README.md`](github/README.md) for a first-time upload walkthrough).

---

## Install

### Linux

| Method | Command | Notes |
| --- | --- | --- |
| **AppImage** (recommended) | Download `flow-x86_64.AppImage` from [Releases], `chmod +x`, run it | Bundles Python — works on any glibc distro, nothing to install |
| **Arch / Manjaro (AUR)** | `yay -S flow-tui` | Or `paru -S flow-tui`; builds the PKGBUILD |
| **Any distro (Make)** | `sudo make -C linux install` | Copies `flow` to `/usr/local/bin` + a desktop entry |
| **Debian/Ubuntu/Fedora** | install the `.deb`/`.rpm` from [Releases] | Built with `nfpm` (see `linux/`) |
| **pip** | `pip install flow-tui` | Cross-platform fallback |

### macOS

```sh
brew install <your-username>/flow/flow-tui     # once published; see macos/README.md
# or, simplest, with no extra setup:
pip3 install flow-tui
```

### Windows

```powershell
pip install "flow-tui[windows]"
```

`flow` is a console app — run it from **Windows Terminal** for best results. See
[`windows/README.md`](windows/README.md).

### From source (any OS)

```sh
git clone https://github.com/<your-username>/flow.git
cd flow
./flow                 # run directly
./install.sh           # or install to ~/.local/bin (Linux/macOS)
pip install .          # or install via pip
```

---

## Optional system tools

flow works with nothing else installed, but these unlock extra features (it
detects them at runtime and degrades gracefully):

| Tool | Enables |
| --- | --- |
| `mpv` | ambient / lofi audio playback |
| `paplay` | transition chimes (else terminal bell) |
| `cava` | real audio-reactive spectrum visualizer |
| `zenity` / `kdialog` | native folder picker for stats export |
| `fzf` | terminal fuzzy folder picker for stats export |

---

## Keyboard cheatsheet

`Tab` switch panel · `h`/`o`/`t` home/sounds/stats · `f`/`s` focus/settings ·
`space` start/pause · `m` mute · `+`/`-` volume · `v` visualizer · `?` help · `q` quit

---

## Repository layout

```
flow                 the application (single script — the source of truth)
install.sh           simple installer for Linux/macOS from a checkout
pyproject.toml       pip / PyPI metadata
setup.py             installs the `flow` script via pip
linux/               AppImage, AUR PKGBUILD, Makefile, .deb/.rpm, desktop entry
macos/               Homebrew formula + instructions
windows/             pip-based install notes
github/              first-time "how to upload to GitHub" guide
.github/workflows/   CI (syntax check) + release (builds the AppImage on a tag)
```

## License

MIT — see [`LICENSE`](LICENSE). Bundled ambient recordings are CC0/public-domain.

[Releases]: https://github.com/<your-username>/flow/releases
