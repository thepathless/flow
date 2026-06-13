# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`flow` is a single-file terminal (curses) focus app: Pomodoro timer + nested todo list + daily habit tracker + ambient/lofi audio + an app blocker, with a mouse-first TUI. The **entire application is one ~2800-line Python script** (`./flow`) with **zero Python dependencies** (pure stdlib + `curses`). All persisted state lives under `~/.config/flow/` (`config.json`, `tasks.json`, `habits.json`, plus synthesized/downloaded WAVs in `sounds/`).

There is no build step, no test suite, and no package manifest. `IMPLEMENTATION_PLAN.md` is a handoff doc describing past changes with root cause + exact line locations — read it for historical context on completed tasks, but verify line numbers against the current file since they drift.

## Running & installing

```bash
./flow                 # run directly (shebang: /usr/bin/env python3)
./install.sh           # chmod +x and copy to ~/.local/bin (or /usr/local/bin if root)
```

External tools are runtime-optional and degrade gracefully (see `install.sh` for the dependency check):
- **mpv** — audio engine; flow drives it over a JSON-IPC unix socket at `/tmp/flow_mpv_<pid>`. No mpv → no ambient/lofi sound.
- **paplay** — transition chimes; falls back to terminal bell.
- **pacman / flatpak / snap** — used to enumerate installed apps for the blocker's fuzzy search.

Because there are no tests, **verify changes by running `./flow` in a real terminal** and exercising the affected view. Curses UIs cannot be meaningfully checked by reading output alone.

## Architecture

Everything is in `flow`, organized into manager classes plus one large UI class. Approximate line anchors (will drift — grep for `^class ` / `    def `):

- **`ConfigManager`** — every persisted setting is an attribute set in `__init__`; `.save()` dumps `self.__dict__` to `config.json` and `.load()` does `self.__dict__.update(data)`. **To add a persisted field: add a default in `__init__`.** `load()` also strips known legacy keys before merging.
- **`TodoManager`** (`tasks.json`) — unlimited nested subtasks. `get_visible_tasks` flattens the tree honoring collapse state; this is the pattern `HabitManager` was copied from.
- **`HabitManager`** (`habits.json`) — daily habits with streaks.
- **`AudioSynthesizer`** — offline WAV generation (white/pink/brown noise, etc.) written into `sounds/`.
- **Sound downloads** — module-level `SOUND_DOWNLOADS` (CC0/PD recordings) + `download_sounds()` fetch real ambient audio on first run (retry/timeout); `_install_krishna_flute()` copies the bundled Krishna MP3. The `self.sounds` entries carry a `files` fallback list resolved by `AudioEngine.resolve_path` (recording first, synth WAV second) so the app is never silent. Startup `bootstrap()` (in `curses_main`) runs synth + download behind the SYNTH screen.
- **`AudioEngine`** — a **multi-sound mixer**: one mpv process per active sound, kept in `self.instances` (idx → {proc, sock, type}), each with its own IPC socket `MPV_SOCKET_<idx>`. `toggle_sound(idx)` adds/removes a sound from the simultaneous mix (idx 0 = "None" clears all); `play()` is a back-compat alias. `set_volume`/`toggle` (mute) apply to every instance; `is_active(idx)`, `active_count()`, `status_label()` drive the UI. A **watchdog thread** reloads any dropped network-stream instance. A `threading.Lock` guards socket sends. Audio keeps playing across timer/session boundaries — do not add `stop()` on session end. Each instance launches with stream caching + ffmpeg reconnect flags via `_spawn_mpv`.
- **`Visualizer` / `CavaEngine`** — the bottom spectrum strip. `CavaEngine` drives bars from real audio via `cava` (reads the default-sink monitor, so it visualizes whatever mpv plays) when `cava` is installed; `_draw_visualizer` falls back to the procedural `Visualizer` otherwise. Config: `vis_bars`, `vis_amplitude`, `visualizer_rows` (clamped 1–4).
- **`BlockerEngine`** — a daemon thread (`_loop`, 0.5s tick) that scans `/proc/*/comm` + `argv0` and kills matches. Matching is **token-subset** via module-level `name_tokens` (splits on any non-alphanumeric incl. `/`, drops packaging noise like `bin/git/debug/stable/real`): a blocked entry matches when all its tokens are present in the process tokens. This is path-safe — `google-chrome` matches `/opt/google/chrome/chrome` (the earlier substring approach broke here, which is why blocking regressed). `clean_proc_name` is kept as a back-compat display helper. Kills the whole **process group** (`os.killpg`, SIGTERM→SIGKILL on later passes) to take down `bwrap` sandboxes + children, guarding `pgid != my_pgid` to never kill itself. It is the **single source of truth**: started once at `FlowTUI.__init__`, and runs whenever `config.block_apps and not is_break`. The timer only calls `set_break(...)`; it must never start/stop the thread. Best-effort — re-launched apps die within ~1s, not instantly.
- **`FlowTUI`** — the whole interface and main loop. Everything below is here.

### FlowTUI conventions

- **Views** are integer constants on the class: `HOME, TIMER, SOUNDS, SETTINGS, APPS, STATS, SYNTH, APPS_SEARCH`. Two panels: `LEFT` (todo/habits) and `RIGHT` (the active view). `switch_view` changes the right panel.
- **Main loop** `curses_main` runs at ~20 FPS (`stdscr.timeout(50)`). `_alloc` builds the left/right curses windows and the optional bottom spectrum-visualizer strip.
- **Rendering** is split: `_draw` paints the top tab bar + footer; `_draw_todo`/`_draw_habits` paint the left panel; `_draw_right` dispatches to a per-view `_v_<name>` renderer (`_v_home`, `_v_timer`, `_v_sounds`, `_v_settings`, `_v_stats`, `_v_blocklist`, `_v_app_search`).
- **Stats** (`_v_stats`) has four sub-views switched by `1/2/3/4` or clicking the sub-tabs: Daily, Habits (`_stats_habits`, per-habit 7-day ●/○ grid), Month (`_stats_calendar`, goal-based progress circles ○◔◑◕● via `_circle`), Year (`_stats_year`, monthly circles). Month/Year scale against `cfg.daily_goal_seconds` (the **Daily Focus Goal** setting; edits go through module-level `parse_duration_to_seconds`).
- **Input** is routed by `_key` (keyboard) with per-context handlers (`_key_todo`, `_key_habits`, `_key_right`), and `_handle_mouse` (clicks).
- **Mouse-first pattern:** during draw, register every clickable region via `register_btn(name, row, x, text, action)` into `self.buttons` using absolute screen coords, then resolve clicks generically. When a view computes geometry (e.g. the timer ring radius), the **same geometry must be used in both the renderer and the mouse handler** — duplicated/divergent geometry math is the classic source of "button can't be clicked" bugs here.
- **Mouse event classes:** `_handle_mouse` distinguishes **press** (button1 → run actions / `register_btn` hits), **scroll** (BUTTON4/5 → move cursor), and **hover/motion** (`REPORT_MOUSE_POSITION` → focus-follow only, never an action). This is why a scroll or a mouse-move over a habit no longer toggles it, and focus follows the pointer. Any new list/button must select on hover and act only on `is_click`.
- **Settings are a single source of truth:** `_build_settings()` returns `(label, value, action)` rows; rendering, keyboard, and mouse all index into it, so there is no fragile numeric idx→action map. Add a setting by adding one row there (+ a `_save_input` branch if it prompts for input). The Settings view scrolls (`rscroll`).
- **Persisted fields added this round** (all in `ConfigManager.__init__`): `auto_start`, `pomodoro_target`, `countdown_name`, `countdown_date`. Stats export (`_export_stats`) writes `flow_stats.json` + `flow_focus.csv` + `flow_habits.csv` to a user path. The top bar shows a named countdown (`_countdown_label`); the footer shows transient flashes (`_flash`/`_active_flash`).
- **Always draw with `saddstr`**, never raw `win.addstr` — `saddstr` clips at window boundaries so a write near the edge can't crash curses.

### Things that bite

- Adding a config field requires only the `__init__` default — but anything reading it must tolerate it being absent from an older on-disk `config.json` (handled by load-merge, but old files won't have new keys until next save).
- `get_user_home()` resolves `SUDO_USER` so config lands in the real user's home even under `sudo`/`pkexec`.
- The blocker skips its own PID; be careful not to add substrings that match common system processes.
