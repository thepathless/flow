# Flow — Implementation Plan & Handoff Doc

Single-file app: `/workspace/flow` (~2100 lines, pure-Python + `curses`, zero deps, audio via external `mpv` over a JSON-IPC unix socket). Config/state live in `~/.config/flow/` (`config.json`, `tasks.json`, synthesized + downloaded sounds under `sounds/`).

This doc lists every requested change with **root cause**, **exact location**, and **how to implement**. Tasks are ordered by priority. **All tasks are now implemented (`[x]`)** — see the Status log at the bottom for what changed and where. The per-task detail below is kept so any item can be re-derived or handed to another model.

## Architecture cheat-sheet (where things live)
- `ConfigManager` (line ~93) — all persisted settings; `.save()` writes `config.json`. Add new persisted fields here + in `__init__` defaults.
- `TodoManager` (~134) — nested tasks; pattern to copy for habits.
- `AudioSynthesizer` (~311) — offline WAV generation (white/pink/brown/etc.).
- `AudioEngine` (~474) — wraps mpv. `_start_mpv`, `_cmd` (IPC send), `play/stop/toggle/set_volume`. **Audio fixes go here.**
- `BlockerEngine` (~612) — kills blocked apps in a daemon thread. **Blocker fix goes here + in FlowTUI startup.**
- `FlowTUI` (~677) — the whole UI. Views enum at top (`HOME/TIMER/SOUNDS/SETTINGS/APPS/SYNTH/APPS_SEARCH`). Main loop `curses_main` (~844), 20 FPS (`stdscr.timeout(50)`). `_alloc` (~923) builds the left/right windows. `_draw` (~1554) top bar + footer; `_draw_todo` left; `_draw_right` dispatches per-view `_v_*` renderers. Input: `_key` (~1335) routes; `_handle_mouse` (~1130) for clicks.
- Clickable top-bar tabs use `register_btn`/`self.buttons` (absolute screen coords). **The clean pattern for mouse-first UI is to register every button this way during draw and resolve clicks generically** (see Task 4).

---

## Task 1 — Audio resilience: never pause, never buffer  `[x]`
**Symptoms:** lofi radio plays then pauses/resumes, then stops entirely. Should play continuously regardless of focus state; same guarantee for all sounds.

**Root causes:**
1. `_timer_done()` (line ~1013) calls `self.audio.stop()` → ambient/lofi audio is paused every time a focus session ends.
2. mpv is launched (`_start_mpv`, ~502) with no network cache and no reconnect → any HTTP stream hiccup stalls forever.
3. No watchdog: when a stream EOFs/drops, mpv goes idle and nothing reloads it.

**Implement:**
- In `_start_mpv`, add args:
  `--cache=yes --cache-secs=60 --demuxer-readahead-secs=60 --demuxer-max-bytes=64MiB --demuxer-max-back-bytes=32MiB`
  and ffmpeg reconnect for streams:
  `--stream-lavf-o-append=reconnect=1 --stream-lavf-o-append=reconnect_streamed=1 --stream-lavf-o-append=reconnect_on_network_error=1 --stream-lavf-o-append=reconnect_delay_max=60`
  plus `--network-timeout=0`.
- Remove the `self.audio.stop()` in `_timer_done()` (keep playing across session boundaries). The transition *chimes* (`one_shot`) still fire.
- Add a watchdog thread in `AudioEngine` (`_watchdog`, started in `__init__`): every ~2s, if `self.is_playing` and current sound is a `stream`, query mpv `core-idle`/`eof-reached` via IPC (use a request-capable `_get(prop)` that reads the socket reply). If idle/eof while we expect playback → re-`play(current_sound_idx)`.
- Keep a `_lock` (threading.Lock) around socket sends since watchdog + UI thread both call `_cmd`.

**Done when:** lofi plays for 30+ min without stopping; finishing a pomodoro doesn't cut the music.

---

## Task 2 — App blocker actually blocks  `[x]`
**Symptom:** added `audacity`, enabled "App Blocker: active", but audacity still opens.

**Root cause:** `BlockerEngine.start()` is called **only** from `_start_timer()` (line ~989). Toggling `block_apps` in Settings never starts the thread, and `_pause_timer`/`_reset_timer` call `blocker.stop()`. So blocking only happens during a live focus timer.

**Implement:**
- Start the blocker once at startup: in `FlowTUI.__init__` after creating `self.blocker`, call `self.blocker.start()`. Make `_loop` the single source of truth — it already checks `self.config.block_apps`.
- Change kill condition in `_loop` to block whenever `config.block_apps and not self.is_break`. With no timer running `is_break=False`, so a manually-enabled blocker blocks immediately (matches user expectation).
- Timer start/done should only call `self.blocker.set_break(is_break)`, NOT start/stop the thread. Remove `blocker.stop()` from `_pause_timer`/`_reset_timer`.
- Escalate kills: SIGTERM, and on the next loop if still alive, SIGKILL.
- Note in UI: blocking is best-effort (kills processes); it can't stop a re-launch instantly but will kill within ~1.5s.

**Done when:** enable blocker in Settings with audacity listed → launching audacity gets killed within ~2s, no timer needed.

---

## Task 3 — Mouse-first UI (fix Focus pause/reset clicks)  `[x]`
**Symptom:** in Focus view, pause/reset can't be clicked.

**Root cause:** geometry computed twice and differently. `_v_timer` (~1858) uses `R = max(7, min(cy-2,(mx-4)//4,14))` and `info_y = min(my-4, cy+R+2)`; `_handle_mouse` TIMER branch (~1226) uses `R = max(3, min(cy-2,(rw-4)//4,8))` and `info_y = min(std_my-4, ...)`. Button row never matches.

**Implement (preferred, fixes ALL mouse gaps):** adopt the top-bar pattern everywhere. During each `_v_*` render, call `self.register_btn(name, abs_row, abs_x, text, action)` with **absolute stdscr coords** (add window origin: left win origin col 0 row 1; right win origin col `left_w` row 1). Then `_handle_mouse` becomes: iterate `self.buttons`, if click within rect → call action. Delete the per-view geometry math in `_handle_mouse`. This makes pause/reset/volume/settings rows/sound rows/blocklist buttons all clickable with one code path.
- Minimal fallback if short on time: extract `_timer_geom(my,mx)` returning the button rects, call it from both `_v_timer` and the mouse handler so they agree.
- Also ensure list rows (sounds, settings, blocklist, todo, habits) register click → select/activate.

**Done when:** every visible `[ button ]` and list row responds to a single click; Focus pause/reset work.

---

## Task 4 — Minimal bottom spectrum visualizer (cliamp style)  `[x]`
**Reference:** `bjarneo/cliamp` `ui/visualizer.go` + `ui/vis_bars.go`. We replicate the *look* (cliamp uses real FFT; we drive bands procedurally since mpv owns the audio).

**Exact look to copy:**
- 10 bands. Fractional block chars: `[" ", "▁","▂","▃","▄","▅","▆","▇","█"]`.
- Per row, `rowBottom=(rows-1-row)/rows`, `rowTop=(rows-row)/rows`; a band fills `█` if `level>=rowTop`, a fractional block if between, else space (`fracBlock`).
- Color tiers by level: `<0.3` low (cyan/blue), `0.3–0.6` mid (green), `>0.6` high (yellow/red).
- Smoothing: fast attack / slow decay — `if target>cur: cur=target*0.6+cur*0.4 else cur=target*0.25+cur*0.75` per analysis tick, eased per frame.

**Implement:**
- New `Visualizer` class: holds `bands=[0]*10`, `smoothed=[0]*10`, `rows` (default 1, configurable 1–3), `enabled`. Method `tick(playing, volume, frame)`:
  - if not playing → targets decay to 0.
  - else generate organic targets: per band `base = volume/100`, modulate with cheap pseudo-noise (sines at different freqs per band + a little randomness seeded by frame) so low bands pulse slower/taller than highs. No real audio needed.
  - apply fast-attack/slow-decay toward targets.
- Render method returns per-row strings; draw on `stdscr` full width at the bottom.
- **Layout:** in `_alloc`, reduce window height by `vis_h` when `cfg.visualizer and audio.is_playing`: windows are rows `1..my-2-vis_h`, visualizer rows `my-1-vis_h..my-2`, footer `my-1`. Recompute on toggle and on play/stop (`self.dirty=True`).
- Call `vis.tick(...)` each loop iteration in `curses_main`; draw in `_draw` before footer.
- Keybind `v` to toggle, and a Settings entry "Visualizer on/off" + persisted `cfg.visualizer=True`, `cfg.visualizer_rows=1`. Optional: `V` cycles a couple of styles (Bars vs Columns) — store `cfg.vis_style`.

**Done when:** a thin dancing equalizer appears full-width at the bottom while audio plays, matching cliamp's block aesthetic; `v` toggles it; it never steals panel space when off.

---

## Task 5 — Discoverability  `[x]`
**Symptom:** features exist (e.g. `[`/`]` column-width resize) but users don't know.

**Implement:**
- Enrich `_footer()` (~1623): HOME/all views should surface `[ ]:width`, `v:viz`, `Tab:panel`, and a `?:help` hint.
- Add a `?` help overlay (modal drawn over everything, dismiss any key): list all keybinds grouped (Navigation, Todo, Habits, Timer, Sounds, Stats). Add `register_btn` for a `[?]` in the top bar.
- In the left panel near the buttons, the resize affordance: show `‹ [ ] ›` mini hint or make the panel border draggable (stretch goal: detect drag on the divider column `left_w` and set `left_w` to mouse x).

**Done when:** a new user can see, without docs, how to resize columns, toggle the visualizer, and open help.

---

## Task 6 — Habits section (lower-left, under todo)  `[x]`
**Design (researched against common TUI habit trackers / dotfiles):** a habit = `{id, name, history: {"YYYY-MM-DD": true}}`. Show name, today's check `[✓]/[ ]`, current streak, and a mini last-7-days grid `▪▪▫▪▪▪▫`. Persist to `~/.config/flow/habits.json` via a `HabitManager` mirroring `TodoManager`.

**Layout:** split the left window into two stacked cards in `_alloc`: top `todo` (≈60%), bottom `habits` (≈40%). Add a left-panel sub-focus toggle (e.g. `Tab` cycles todo→habits→right, or a dedicated key). Track `self.left_section in (TODO, HABITS)`.

**Keys/mouse:** `a` add, `space/click` toggle today, `d` delete, `e` edit. Streak = consecutive days up to today with a check.

**Done when:** habits render under the todo list, today can be toggled by click or space, streaks update, persisted across runs.

---

## Task 7 — Stats section (top bar: daily / weekly / calendar)  `[x]`
**Data:** today the app only keeps cumulative `cfg.study_total`. Add per-day tracking: `cfg.daily_study = {"YYYY-MM-DD": seconds}` (or separate `stats.json`). Everywhere study seconds are flushed (the stopwatch accumulator in `curses_main` ~890, `_timer_done`, `_cleanup`), also add to today's bucket via a helper `add_study(seconds)` that writes both `study_total` and `daily_study[today]`.

**UI:** add a `STATS` view + a top-bar tab "📊 stats". Three sub-views (toggle with `1/2/3` or clickable sub-tabs):
- **Daily:** today's total big, plus a list of recent days.
- **Weekly:** 7 vertical bars (Mon–Sun) using the same block chars as the visualizer, scaled to the week's max; label hours under each.
- **Calendar:** GitHub-style month heatmap — a grid of day cells shaded by minutes studied (use shade chars `·░▒▓█` or color intensity). Show month name, navigable with `←/→`.

**Done when:** Stats tab shows real per-day study time in daily, weekly, and monthly calendar views.

---

## Testing notes
- No `mpv` in the dev sandbox — audio paths can't be run here; syntax-check with `python3 -m py_compile flow` and review logic. The user has mpv installed.
- Curses can't run headless here either; keep changes incremental and verify by reading. The user runs `flow` in a real terminal.
- Persisted config gains new keys; `ConfigManager.load()` does `self.__dict__.update(data)` so old configs stay compatible (new fields keep their defaults).

## Status log — all tasks implemented (2026-06-13)
Every task below is **DONE** and the changes are live in `/workspace/flow`. Verified by
`python3 -m py_compile`, unit tests of the pure logic (Visualizer, HabitManager streaks,
calendar math), and a pty render harness that drew every view (home/timer/sounds/stats×3/
settings/habits) + the visualizer strip with seeded data — no tracebacks.

- **Task 1 Audio resilience — DONE.** `_start_mpv` now launches with cache + ffmpeg
  reconnect flags; added `_get()` IPC reader + `_watchdog()` thread that reloads a dropped
  stream; `_timer_done()` no longer pauses audio (music plays across focus/break). `_cmd`
  serialized with a lock.
- **Task 2 Blocker — DONE.** `self.blocker.start()` now runs at startup; `_loop` blocks
  whenever `block_apps and not is_break`, escalates SIGTERM→SIGKILL; timer pause/reset only
  set break-state (pausing is not a bypass).
- **Task 3 Mouse-first — DONE.** Generic `register_btn` hit-test at top of `_handle_mouse`;
  Home + Focus (pause/reset) + Help + Stats sub-tabs + calendar arrows all register absolute
  coords. Stale per-view geometry for Home/Timer removed. (The old code even called an
  unhandled `p` key — that's why pause never worked by mouse.)
- **Task 4 Visualizer — DONE.** New `Visualizer` class (cliamp look: `" ▁▂▃▄▅▆▇█"`, per-row
  colour tiers, fast-attack/slow-decay). Strip drawn full-width above the footer; `_alloc`
  reserves rows only while playing + enabled; `v` toggles + Settings entry + persisted
  `cfg.visualizer`/`visualizer_rows`.
- **Task 5 Discoverability — DONE.** Footers surface `[ ]:width`, `v:viz`, `?:help`; new
  modal help overlay (`?` key / `[ ? ]` top-bar button) lists all keybinds + "everything is
  mouse-first".
- **Task 6 Habits — DONE.** `HabitManager` + `habits.json`; left column splits into todo
  (top) / habits (bottom) when tall enough; Tab cycles todo→habits→right; add/edit/delete/
  toggle by key or click; shows ✓, current streak (🔥), and a 7-day `▪▫` grid.
- **Task 7 Stats — DONE.** Per-day tracking via `_add_study` → `cfg.daily_study`; new
  📊 stats tab with Daily / Weekly (block bar chart) / Calendar (month heatmap, `←/→` to
  change month) sub-views, switchable by `1/2/3` or clicking the sub-tabs.

---

## Production-readiness work order (HANDOFF.md) — status log (2026-06-13)
Second pass, tracked in `HANDOFF.md`. Each item below was verified with the command noted.

- **Task 1 Habits card never disappears — DONE & verified.** `_alloc` threshold lowered to
  `ch >= 9`; habits render down to an 11-row terminal. (Applied in the prior session.)
- **Task 2 Real sound recordings + Krishna + never-silent fallback — DONE & verified.**
  `SOUND_DOWNLOADS`/`download_sounds`/`_install_krishna_flute`; `self.sounds` carry a `files`
  fallback list resolved by `resolve_path`; startup `bootstrap()` downloads on first run with
  a 3-attempt retry. All 8 recordings ffprobe-validated. Optional offline synth fallbacks for
  ocean/fire/wind (2.7) intentionally skipped — downloads cover the normal case.
- **Task 3 CAVA visualizer (procedural fallback) — DONE & verified.** `CavaEngine` drives the
  spectrum from real audio when `cava` is installed (PulseAudio/PipeWire default-sink monitor);
  falls back to the procedural `Visualizer` otherwise. Added `vis_bars`/`vis_amplitude` config,
  Settings rows (Height/Bars/Amplitude) with working `_save_input` branches (these were missing
  and silently no-op'd until this session), `_vis_h` clamp raised to 4 rows. **cava is not
  installed on this machine**, so the real-audio reactivity path was reviewed/reasoned, not run
  live; the procedural fallback path is what the render harness exercised. Verified:
  `py_compile` + `tools/render_test.py --all-sizes` clean.
- **Task 4 Flatpak/sandbox-aware app blocking — DONE & verified (static).** `clean_proc_name`
  normalizes punctuation + strips `-bin/-git/-debug/-stable/-real`; `_find_pids` matches on the
  normalized name; `_loop` now SIGTERMs→SIGKILLs the whole **process group** (`os.killpg`) so a
  `bwrap`/flatpak sandbox dies with its children, while guarding `pgid != my_pgid` so it never
  kills itself. Tick tightened to 0.5s. Functional kill test requires a real desktop app —
  verified compile + render harness here; behaviour reasoned through.
- **Task 5 Daily Focus Goal + app-list dedup — DONE & verified.** `parse_duration_to_seconds`
  (`21h3m23s`/`2h`/`30m`/`90`-as-minutes); `cfg.daily_goal_seconds` (default 2h) with a Settings
  row + edit. App dedup now collapses `-bin/-git/-debug/-stable` variants to a base name. Parser
  asserts pass; harness clean.
- **Task 6 Stats overhaul — DONE & verified.** Sub-tabs are now Daily / Habits / Month / Year
  (`1/2/3/4` or click). New `_stats_habits` (per-habit 7-day ●/○ grid), `_stats_year` (monthly
  ○◔◑◕● scaled to goal), and the monthly calendar switched from a shade ramp to goal-based
  circles via `_circle`. Verified with `tools/stats_test.py` (drives all four sub-views against a
  real curses window at 10/16/24/40 rows — no tracebacks).
- **Task 7 Final verify + docs/install — DONE.** `install.sh` now checks for `cava` and
  pre-seeds the bundled Krishna MP3 into `~/.config/flow/sounds/`. `CLAUDE.md` and this log
  updated.

### Things that still need a real desktop to confirm
- **cava reactivity** — needs cava + PipeWire/PulseAudio + audio playing.
- **App blocker kills** — add a flatpak app to the block list, enable the blocker, launch it,
  confirm it dies within ~1s and that flow never kills its own group.

---

## User test round — 16 reported items (2026-06-13, 3rd pass)

After hands-on testing the user filed 16 items. Status (✅ = code-complete + verified by the
test harnesses noted; 🎧 = code-complete but needs a real terminal **with audio** to confirm
perceptually). New harnesses live in `tools/`: `blocker_test.py`, `help_test.py`,
`view_test.py`, `feature_test.py` (+ existing `render_test.py`, `stats_test.py`).

1. ✅ **Habits scroll** — added `hscroll` (mirrors todo `lscroll`); list scrolls with the cursor + ▲/▼.
2. 🎧 **White/pink/brown noise = static** — white noise *is* broadband by nature; smoothed the
   synth (1-pole low-pass on white, softer pink/brown) and lengthened loops 10s→20s to kill the
   seam. Version-gated regen (`.noise_version`) so existing installs rebuild. Verify by ear.
3. 🎧 **Wind ≈ Ocean** — swapped Ocean to `Adriatic_Sea_waves.ogg` (clear swell) so it differs
   from the forest-wind recording. Reachability verified; timbre needs ears.
4. ✅ **Multiple simultaneous sounds** — `AudioEngine` is now a mixer (one mpv per active sound,
   `toggle_sound`); Sounds view marks every active ▶ and shows "N playing".
5. ✅ **Volume hitboxes** — bigger forgiving ±/bar zones in the Sounds mouse handler.
6. 🎧 **Rain had thunder** — swapped to `Rain_against_the_window.ogg` (pure rain, no thunder,
   1m22s). Saved under a new filename so it re-downloads. Verify by ear.
7. ✅ **Export stats** — Settings → "Export Stats →" prompts for a path; writes JSON + 2 CSVs.
8. ✅ **Richer stats** — Daily now shows 7-day total/avg, this-week-vs-last trend, goal streak
   (current/best), best day; Habits shows 30-day completion % + streak per habit.
9. ✅ **Scroll/hover toggled habits + fire emoji** — mouse events now split into press/scroll/
   hover; scroll & hover never toggle (only a real click/space does). Removed the 🔥/streak from
   the habit row for a minimal look.
10. ✅ **Auto-start + session target** — Settings "Auto-start Sessions" + "Session Target";
    `_timer_done` auto-chains focus/break only when on and the target isn't reached (0 = unlimited).
11. ✅ **Help overlay overflow** — `_draw_help` lays out key/desc in box-relative columns and
    clips every line; `help_test.py` asserts nothing draws outside the box at 4 sizes.
12. ✅ **Countdown** — Settings "Countdown Name" + "Countdown Date"; top bar always shows
    "⏳ name: Nd / today! / passed".
13. ✅ **App blocker broken (regression)** — root cause: normalization didn't split `/`, so a
    deduped `google-chrome` no longer substring-matched `/opt/google/chrome/chrome`. Replaced with
    token-subset matching (`name_tokens`). `blocker_test.py` covers 10 real cases.
14. ✅ **Mouse-first gaps** — Settings mouse handler capped clickable rows at idx<8 (now uses
    `_settings_n` + scroll); list rows select on hover; everything actionable is clickable.
15. ✅ **Hover-follow focus** — motion events move panel/cursor under the pointer (no click needed).
16. ✅ **Production polish / anti-flicker** — fixed the help-overlay flicker (it painted onto
    stdscr *after* `noutrefresh`, so `doupdate` never flushed it — now re-flushed last). Settings
    scroll + config migration safe (`__dict__.update` keeps new defaults). Full harness suite green.

### Known limitations / future polish (for a future session)
- Visualizer bands are **procedural**, not real FFT (mpv owns the PCM). For true reactivity,
  add an mpv audio tap (e.g. `--ao=pcm` to a fifo, or `af=ebur128` + `af-metadata` loudness
  over IPC) and feed amplitude into `Visualizer.tick`. Look is already cliamp-accurate.
- SOUNDS and STATS tabs are reachable by click (matching the app's existing pattern) but not
  by a dedicated key; consider a view-cycle hotkey for full keyboard parity.
- Habits list doesn't scroll (caps at the visible rows); add scrolling if a user keeps >10.
- `mpv` is required for audio; not present in the dev sandbox, so audio paths were reviewed +
  reconnect logic reasoned through rather than run live. Test on the target machine.
