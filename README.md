# 🌀 flow

A mouse-first **terminal focus app** — Pomodoro timer, nested to-dos, daily habit
tracker, ambient/lofi audio mixer, and an app blocker, all in one screen.

- **One file, zero Python dependencies.** Pure standard library + `curses`.
- Runs on **Linux and macOS**.
- All state lives under `~/.config/flow/` (`config.json`, `tasks.json`, `habits.json`).

---

## Install

Two supported ways — both work on **Linux and macOS**.

### pip

```sh
pip install flow-tui
flow
```

### From source

```sh
git clone https://github.com/thepathless/flow.git
cd flow
./flow                 # run directly — no install needed
./install.sh           # or install to ~/.local/bin
pip install .          # or install via pip from the checkout
```

> **Windows:** not supported yet — several features (ambient audio, the app
> blocker) rely on Linux/macOS facilities. Use [WSL] in the meantime; native
> Windows support may come later.

[WSL]: https://learn.microsoft.com/windows/wsl/install

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

Every view's shortcut is shown as the highlighted letter on its tab, so you can
learn navigation at a glance — but here's the full set:

`Tab` switch panel · `h` home · `f` focus · `o` sounds · `t` stats · `s` settings ·
`space` start/pause · `m` mute · `+`/`-` volume · `v` visualizer · `?` help · `q` quit

---

## Repository layout

```
flow                 the application (single script — the source of truth)
install.sh           installs the flow script to ~/.local/bin from a checkout
pyproject.toml       pip / PyPI metadata
setup.py             installs the `flow` script via pip
tools/               byte-compile + render smoke tests
.github/workflows/   CI (syntax check)
```

## License

MIT — see [`LICENSE`](LICENSE). Bundled ambient recordings are CC0/public-domain.

[Releases]: https://github.com/thepathless/flow/releases
