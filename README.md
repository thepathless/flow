<div align="center">

# 🌀 flow

**A mouse-first terminal focus app.**
Pomodoro timer · nested to-dos · daily habit tracker · ambient/lofi audio mixer · app blocker —
all on one screen, in one file, with zero Python dependencies.

[![CI](https://github.com/thepathless/flow/actions/workflows/ci.yml/badge.svg)](https://github.com/thepathless/flow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform: Linux | macOS](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-555?style=flat-square)
![Dependencies: 0](https://img.shields.io/badge/dependencies-0-22c55e?style=flat-square)
![Source: single file](https://img.shields.io/badge/source-single%20file-8b5cf6?style=flat-square)

</div>

https://github.com/user-attachments/assets/ed1a6ea4-03de-444f-9d69-c06aade97988

<div align="center">
<sub>▶ Full demo, with sound. If the player doesn't load, <a href="https://github.com/thepathless/flow/releases/tag/demo">watch it on the Releases page</a> · <a href="assets/flow-poster.png">screenshot</a></sub>
</div>

---

## Why flow?

Most focus tools scatter your attention across a timer app, a to-do app, a habit
tracker, a music tab and a website blocker. **flow** folds all of that into a
single calm terminal screen you can drive entirely with the mouse — or never
leave the home row. No accounts, no telemetry, no cloud. Your data is just three
JSON files under `~/.config/flow/`.

- **One file, zero Python dependencies.** The whole app is one ~2,800-line script — pure standard library + `curses`.
- **Mouse-first, keyboard-fast.** Click anything, or learn the shortcuts shown right on each tab.
- **Yours, offline, forever.** All state lives in plain JSON under `~/.config/flow/`.

---

## Features

| | |
| --- | --- |
| ⏱️ **Pomodoro timer** | Work / break cycles, auto-start, session targets and a named countdown to your big day. |
| ✅ **Nested to-dos** | Unlimited subtasks, collapse/expand, progress counts — a real outline, not a flat list. |
| 🔥 **Habit tracker** | Daily habits with streaks and a 7-day ●/○ grid. |
| 🎧 **Ambient audio mixer** | Layer multiple sounds at once — rain, café, brown noise, lofi and more — each mixed live. |
| 📊 **Stats** | Daily / Habits / Month / Year views with goal-based progress rings, plus CSV + JSON export. |
| 🚫 **App blocker** | Fuzzy-search installed apps and have flow kill distractions while you focus. |
| 🌈 **Live visualizer** | A real audio-reactive spectrum strip (via `cava`) along the bottom. |

---

## Install

> [!NOTE]
> flow runs on **Linux and macOS**. It needs nothing beyond Python 3.8+ —
> optional system tools (below) unlock audio, the visualizer and native dialogs.

### pipx — recommended

[`pipx`](https://pipx.pypa.io) installs flow into its own isolated environment and
puts the `flow` command on your `PATH`. It's the cleanest way to install a CLI app
and it works everywhere — including Arch / Omarchy, where a plain `pip install`
is blocked (see the note below).

```sh
pipx install flow-focus
flow
```

<sub>Don't have pipx? Install it once: `sudo pacman -S python-pipx` (Arch/Omarchy) · `brew install pipx` (macOS) · `python3 -m pip install --user pipx` (others).</sub>

### pip

```sh
pip install flow-focus
flow
```

> [!NOTE]
> On Arch, Omarchy, Debian, Ubuntu and other distros with an
> **externally-managed** Python, a bare `pip install` is refused on purpose
> ([PEP 668](https://peps.python.org/pep-0668/)). Use **pipx** (above), or
> install into a virtual environment:
> ```sh
> python3 -m venv .venv && source .venv/bin/activate
> pip install flow-focus
> ```

<sub>Want the absolute latest, straight from `main`? `pipx install git+https://github.com/thepathless/flow.git`</sub>

### From source

```sh
git clone https://github.com/thepathless/flow.git
cd flow
./flow                 # run directly — no install step needed
./install.sh           # or copy the script to ~/.local/bin
```

> **Windows:** not supported yet — ambient audio and the app blocker rely on
> Linux/macOS facilities. Use [WSL](https://learn.microsoft.com/windows/wsl/install) in the meantime.

---

## Optional system tools

flow works with nothing else installed, but these unlock extra features — it
detects them at runtime and degrades gracefully:

| Tool | Enables |
| --- | --- |
| `mpv` | ambient / lofi audio playback |
| `paplay` | transition chimes (else terminal bell) |
| `cava` | real audio-reactive spectrum visualizer |
| `zenity` / `kdialog` | native folder picker for stats export |
| `fzf` | terminal fuzzy folder picker for stats export |

---

## Keyboard cheatsheet

Every view's shortcut is the highlighted letter on its tab, so you can learn
navigation at a glance — but here's the full set:

| Key | Action | | Key | Action |
| --- | --- | --- | --- | --- |
| `Tab` | switch panel | | `space` | start / pause timer |
| `h` | home | | `m` | mute |
| `f` | focus | | `+` / `-` | volume |
| `o` | sounds | | `v` | toggle visualizer |
| `t` | stats | | `?` | help |
| `s` | settings | | `q` | quit |

---

## Repository layout

```
flow                 the application — a single script, the source of truth
install.sh           installs the flow script to ~/.local/bin from a checkout
pyproject.toml       pip / packaging metadata
setup.py             installs the `flow` script via pip
packaging/           AUR PKGBUILD + Homebrew formula for maintainers
assets/              poster image used in this README
tools/               byte-compile + render smoke tests
.github/workflows/   CI (byte-compile + package build check)
```

---

## Contributing

The entire app is the single `flow` script, so contributing is refreshingly
simple: edit `flow`, then **run it in a real terminal** and exercise the view you
changed — curses UIs can't be meaningfully checked by reading output alone.
The smoke tests in `tools/` byte-compile and render-check the script; CI runs the
same on every push. Issues and pull requests are welcome.

---

## License

[MIT](LICENSE). Bundled ambient recordings are CC0 / public-domain.
