# HANDOFF.md — Flow TUI production-readiness work order

**Audience:** a coding agent (likely a smaller/free model running in [opencode](https://opencode.ai)) that will finish this project task‑by‑task. Read this whole file once, then do **one task per session** in order. Each task is self‑contained: it tells you exactly where to edit, gives complete copy‑paste code, and ends with a verification command you must run before declaring it done.

**The app:** `flow` is a single ~2850‑line Python file (`/workspace/flow`), curses TUI, no Python deps. State lives in `~/.config/flow/` (`config.json`, `tasks.json`, `habits.json`, `sounds/`). Audio plays through external `mpv` over a JSON‑IPC unix socket. See `CLAUDE.md` for architecture.

---

## 0. Golden rules (read first — these prevent the mistakes the last session made)

1. **Never claim a task is done without running its verify command.** The previous session marked everything "DONE" in `IMPLEMENTATION_PLAN.md` while shipping broken sound paths. Do not repeat that.
2. **The file must always compile.** After every edit run `python3 -m py_compile flow`. If it fails, fix it before doing anything else.
3. **Draw with `saddstr(win, y, x, text, attr)`**, never raw `win.addstr` — `saddstr` clips at the window edge so it can't crash curses.
4. **Add a persisted setting** = add a default attribute in `ConfigManager.__init__` (it saves/loads via `self.__dict__`). Old config files stay compatible because new keys keep their default until next save.
5. **Don't invent line numbers.** Locate code by grepping for the anchor strings given in each task (`grep -n "anchor" flow`). The file changes as you edit, so line numbers drift.
6. **Do exactly one task per session if you are rate‑limited.** Tasks are ordered by priority and dependency. Tasks 2,3,4,5 are independent of each other. Task 6 depends on Task 5. Task 7 is last.
7. **Test rendering with the harness in Appendix A** (`tools/render_test.py`). curses can't be eyeballed from code review alone.
8. If something in this doc contradicts the actual code, **trust the code** and note the discrepancy in your final message.

---

## 1. Recommended free models (opencode)

Researched June 2026. Free offerings are promos and change without notice — if one is gone, pick the next.

| Where | Model | Why / use it for | Caveats |
|-------|-------|------------------|---------|
| **OpenCode Zen** (`opencode auth login` → Zen) | **Grok Code Fast 1** | Fast agentic edits; good default driver for most tasks here | Free during feedback period; xAI may use data to improve the model |
| **OpenCode Zen** | **GLM 4.7** | Strong reasoning; use for the hard tasks (3 CAVA, 6 stats) | Free for limited time, zero‑retention |
| **OpenCode Zen** | MiniMax M2.1 / DeepSeek V4 Flash Free | Backups if the above are busy | Limited‑time free |
| **OpenRouter free** (`:free` suffix) | **Qwen3 Coder** (`qwen/qwen3-coder:free`) | **1M context — fits this whole 2850‑line file at once.** Best for tasks needing broad context (3, 6) | ~20 req/min, ~200 req/day; may vanish |
| **OpenRouter free** | DeepSeek V4 Flash, Llama 3.3 70B, GPT‑OSS 120B | General/mechanical tasks (4, 5) | Same rate limits |

**Suggested assignment (strongest models for the riskiest work):**
- Tasks **2 (sounds)**, **3 (CAVA)**, **6 (stats)** → GLM 4.7 or Qwen3 Coder (more context + reasoning).
- Tasks **4 (blocker)**, **5 (goal + dedup)**, **7 (verify/docs)** → Grok Code Fast 1 is plenty.

How to set up: install opencode, run `opencode` in this directory, `/login` to OpenCode Zen (or add an OpenRouter key), then `/models` to pick one. Because all are free/cheap, switch models freely if one stalls.

> Rate‑limit tip: each task below is scoped to a handful of edits + one verify run. If you hit a limit mid‑task, the file still compiles (golden rule 2), so you can resume next session from the same task.

---

## 2. Current status

> **PROGRESS LOG** (newest first) — the driver updates this after every step.
> - **2026-06-13:** Tasks **3, 4, 5, 6, 7 all DONE & verified** in one session — project is feature-complete per this work order. Notes/deviations: **Task 3** was found half-applied from a prior session (CavaEngine + config + render path + Settings rows existed, but the `_save_input` branches for `vis_rows`/`vis_bars`/`vis_amp` were **missing**, so editing those settings silently did nothing) — added the branches; `_vis_h` clamp was already 4. **cava is not installed here**, so real-audio reactivity is reasoned, not run live; procedural fallback verified. **Task 4** blocker now process-group-kills (`os.killpg`, guarded `pgid != my_pgid`) with `clean_proc_name` normalization; tick 0.5s; functional kill needs a real desktop app. **Task 5** parser + daily goal + dedup all in; parser asserts pass. **Task 6** four stats sub-views (Daily/Habits/Month/Year) with goal circles — verified by new `tools/stats_test.py` which drives all four against a real curses window at 10/16/24/40 rows (no tracebacks). **Task 7** install.sh checks cava + seeds Krishna MP3; CLAUDE.md + IMPLEMENTATION_PLAN.md updated. All passes: `py_compile`, `render_test.py --all-sizes`, `stats_test.py`, parser asserts, `bash -n install.sh`.
> - **2026-06-13:** Task 2 (sounds) **DONE & verified**. All 8 recordings downloaded into `~/.config/flow/sounds/` and `ffprobe`-validated (rain.ogg/thunder.ogg/ocean.mp3/fireplace.mp3/birds.ogg/cafe.mp3/wind.ogg all decode; krishna_flute.mp3 copied from bundle). Imports, `SOUND_DOWNLOADS`/`download_sounds`/`_install_krishna_flute`, `self.sounds` rewrite, `resolve_path`, `play()` loop condition, and startup `bootstrap()` all applied. **Deviation from plan:** added a 3-attempt retry + 60s timeout in `download_sounds` because archive.org cold-cache nodes intermittently exceeded 30s (café failed once, succeeded on retry). Optional 2.6 (grey-out unavailable rows) and 2.7 (offline synth fallbacks for ocean/fire/wind) **NOT done** — left as nice-to-haves. `tools/render_test.py` created; clean at 12/16/24/40 rows, habits visible.
> - **2026-06-13:** Task 1 (habits visibility) done & verified.
> - Next up: **nothing in this work order — all 7 done.** Remaining checks need a real desktop: cava reactivity (cava + PipeWire/PulseAudio) and a live app-blocker kill test (see IMPLEMENTATION_PLAN.md "Things that still need a real desktop").

| Task | State |
|------|-------|
| 1. Habits card never disappears | ✅ **DONE** (already applied & verified — see below; do not redo) |
| 2. Sounds: real recordings + Krishna + fallback | ✅ **DONE & verified** (see progress log; retry added; optional 2.6/2.7 skipped) |
| 3. Real CAVA visualizer + controls (procedural fallback) | ✅ **DONE & verified** (added missing `_save_input` branches; cava-reactivity needs a real desktop) |
| 4. Flatpak/sandbox‑aware app blocking | ✅ **DONE** (process-group kill; live kill test needs a desktop) |
| 5. Daily Focus Goal + app‑list dedup | ✅ **DONE & verified** (parser asserts pass) |
| 6. Stats overhaul (habits heatmap, month circles, year) | ✅ **DONE & verified** (`tools/stats_test.py`) |
| 7. Verify everything + update docs/install | ✅ **DONE** (install.sh cava check + Krishna seed; docs updated) |

### Task 1 — already done (reference only)
**Problem:** the habits card was dropped whenever the left content height `ch < 12`, so on short/split terminals (or while the visualizer ate rows) the user saw **no habits card at all**.
**Fix applied** in `_alloc` (grep `Split the left column`): lowered the threshold to `ch >= 9` and size the card to its content. Verified habits renders down to an 11‑row terminal. Nothing further needed.

---

## TASK 2 — Fix the sounds (real recordings + Krishna flute + never‑silent fallback)

### Why
The sound list points at MP3 files that were **never created** (`rain.mp3`, `thunder.mp3`, `ocean.mp3`, `fireplace.mp3`, `birds.mp3`, `cafe.mp3`, `wind.mp3`, `krishna_flute.mp3`). Only the old synthesized WAVs exist (`rain.wav`, `storm.wav`, `white/pink/brown/alpha.wav`). So every nicely‑named sound is silent. The Krishna flute MP3 is sitting in the project dir, never copied in.

### Decision (already made by the user)
Download **real CC0/public‑domain recordings** on first run. Copy the bundled Krishna MP3. Resolve each sound to whatever file actually exists, falling back to the synth WAV when present, so the app is **never silent again**.

### Verified download URLs (all returned HTTP 200 + audio on 2026‑06‑13)
| key | URL | save as |
|-----|-----|---------|
| rain | `https://upload.wikimedia.org/wikipedia/commons/1/15/Sound_of_light_rainfall.ogg` | `rain.ogg` |
| thunder | `https://upload.wikimedia.org/wikipedia/commons/b/b1/Thunderstorm_after_hot_summer_day_17_minutes_02_of_04.ogg` | `thunder.ogg` |
| ocean | `https://archive.org/download/EXT_BeachBehindChrysalis/EXT_BeachBehindChrysalis_64kb.mp3` | `ocean.mp3` |
| fireplace | `https://archive.org/download/ronkoster2023-fireplace-with-crackling-sounds-2-min-rk-178392/ronkoster2023-fireplace-with-crackling-sounds-2-min-rk-178392.mp3` | `fireplace.mp3` |
| birds | `https://upload.wikimedia.org/wikipedia/commons/e/e7/Birdsong_morning_01.ogg` | `birds.ogg` |
| cafe | `https://archive.org/download/453074-c-rogers-370973-waweee-coffee-shop-ambience-remastered/453074__c_rogers__370973__waweee__coffee-shop-ambience_remastered.mp3` | `cafe.mp3` |
| wind | `https://upload.wikimedia.org/wikipedia/commons/f/f3/Wind_in_Swedish_pine_forest_at_25_mps.ogg` | `wind.ogg` |

### Step 2.1 — add imports
At the top of `flow` (grep `^import subprocess`), ensure `shutil` and `urllib.request` are imported. Add these two lines near the other imports:
```python
import shutil
import urllib.request
```

### Step 2.2 — add the downloader (module‑level, right above `class AudioEngine:`)
Grep `# AUDIO ENGINE` to find the spot; paste this block just before `class AudioEngine:`.
```python
# Real ambient recordings (CC0 / public-domain / CC-BY), fetched on first run.
# Verified reachable 2026-06-13. key -> (url, local filename)
SOUND_DOWNLOADS = {
    "rain":      ("https://upload.wikimedia.org/wikipedia/commons/1/15/Sound_of_light_rainfall.ogg", "rain.ogg"),
    "thunder":   ("https://upload.wikimedia.org/wikipedia/commons/b/b1/Thunderstorm_after_hot_summer_day_17_minutes_02_of_04.ogg", "thunder.ogg"),
    "ocean":     ("https://archive.org/download/EXT_BeachBehindChrysalis/EXT_BeachBehindChrysalis_64kb.mp3", "ocean.mp3"),
    "fireplace": ("https://archive.org/download/ronkoster2023-fireplace-with-crackling-sounds-2-min-rk-178392/ronkoster2023-fireplace-with-crackling-sounds-2-min-rk-178392.mp3", "fireplace.mp3"),
    "birds":     ("https://upload.wikimedia.org/wikipedia/commons/e/e7/Birdsong_morning_01.ogg", "birds.ogg"),
    "cafe":      ("https://archive.org/download/453074-c-rogers-370973-waweee-coffee-shop-ambience-remastered/453074__c_rogers__370973__waweee__coffee-shop-ambience_remastered.mp3", "cafe.mp3"),
    "wind":      ("https://upload.wikimedia.org/wikipedia/commons/f/f3/Wind_in_Swedish_pine_forest_at_25_mps.ogg", "wind.ogg"),
}


def _install_krishna_flute():
    """Copy the Krishna flute MP3 bundled next to this script into SOUNDS_DIR."""
    dest = os.path.join(SOUNDS_DIR, "krishna_flute.mp3")
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for cand in os.listdir(script_dir):
            if cand.lower().endswith(".mp3") and "krishna" in cand.lower():
                shutil.copyfile(os.path.join(script_dir, cand), dest)
                return
    except Exception:
        pass


def download_sounds(progress_cb=None):
    """Fetch real recordings on first run. Missing files are left missing so the
    AudioEngine can fall back to a synthesized WAV (never silent)."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    _install_krishna_flute()
    items = list(SOUND_DOWNLOADS.items())
    for i, (key, (url, fname)) in enumerate(items):
        dest = os.path.join(SOUNDS_DIR, fname)
        if os.path.exists(dest) and os.path.getsize(dest) > 1024:
            continue
        if progress_cb:
            progress_cb(f"Downloading {key}…", int(i / max(1, len(items)) * 100))
        tmp = dest + ".part"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "flow-tui/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(tmp, dest)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            # leave missing → falls back to synth/None
    if progress_cb:
        progress_cb("Ready!", 100)
```

### Step 2.3 — make the sound list resolve to files that exist
In `AudioEngine.__init__` (grep `self.sounds = [`), **replace the entire `self.sounds = [ ... ]` list** with the version below. Each local sound now carries a `files` list (preferred recording first, synth WAV fallback second); the actual path is resolved lazily in `play()`.
```python
        self.sounds = [
            {"name": "None", "type": "none", "files": []},
            {"name": "🌧 Rain",         "type": "local", "files": ["rain.ogg", "rain.wav"]},
            {"name": "⛈ Thunderstorm",  "type": "local", "files": ["thunder.ogg", "storm.wav"]},
            {"name": "🌊 Ocean Waves",  "type": "local", "files": ["ocean.mp3", "ocean.wav"]},
            {"name": "🔥 Fireplace",    "type": "local", "files": ["fireplace.mp3", "fire.wav"]},
            {"name": "🐦 Birds",        "type": "local", "files": ["birds.ogg", "birds.wav"]},
            {"name": "☕ Café",         "type": "local", "files": ["cafe.mp3", "cafe.wav"]},
            {"name": "💨 Wind",         "type": "local", "files": ["wind.ogg", "wind.wav"]},
            {"name": "🎵 Krishna Flute","type": "local", "files": ["krishna_flute.mp3"]},
            {"name": "〰 Alpha Waves",   "type": "local", "files": ["alpha.wav"]},
            {"name": "White Noise",     "type": "local", "files": ["white.wav"]},
            {"name": "Pink Noise",      "type": "local", "files": ["pink.wav"]},
            {"name": "Brown Noise",     "type": "local", "files": ["brown.wav"]},
            {"name": "📻 Lofi Radio",   "type": "stream", "path": "http://stream.zeno.fm/0r0xa792kwzuv"},
        ]
```

Add this helper method anywhere inside `class AudioEngine` (e.g. right after `__init__`):
```python
    def resolve_path(self, sound):
        """Return the first existing file for a sound, or None if unavailable."""
        if sound.get("type") == "stream":
            return sound.get("path")
        for fn in sound.get("files", []):
            p = os.path.join(SOUNDS_DIR, fn)
            if os.path.exists(p):
                return p
        return None
```

### Step 2.4 — use the resolved path in `play()`
In `AudioEngine.play` (grep `def play(self, idx)`), replace the body that reads `sound["path"]`. The new body:
```python
    def play(self, idx):
        if not self.config.sound_enabled:
            return
        self.current_sound_idx = idx
        sound = self.sounds[idx]
        if sound["type"] == "none":
            self.stop()
            return
        path = self.resolve_path(sound)
        if not path:
            # File not downloaded yet / unavailable — do nothing rather than error.
            return
        self._cmd("loadfile", path, "replace")
        time.sleep(0.05)
        if sound["type"] == "local" or path.endswith((".mp3", ".ogg", ".wav", ".oga")):
            self._cmd("set_property", "loop-file", "inf")
        else:
            self._cmd("set_property", "loop-file", "no")
        time.sleep(0.02)
        self._cmd("set_property", "volume", self.volume)
        time.sleep(0.02)
        self._cmd("set_property", "pause", False)
        self.is_playing = True
```
Also check the `_watchdog` method (grep `def _watchdog`): it indexes `sound["type"]` — that's fine, the new dicts still have `"type"`. No change needed there.

### Step 2.5 — kick off downloads at startup
In `curses_main` (grep `needs_synth = False`), the app already runs `synthesize_all` in a background thread when WAVs are missing. Extend it so it **also** downloads recordings and rebuilds the sound paths. Replace the whole `if needs_synth: ... else: self._alloc()` block with:
```python
        # Setup screen runs while we synthesize noise WAVs and download recordings.
        wav_missing = needs_synth
        dl_missing = any(
            not os.path.exists(os.path.join(SOUNDS_DIR, fn))
            for _, (_, fn) in SOUND_DOWNLOADS.items()
        ) or not os.path.exists(os.path.join(SOUNDS_DIR, "krishna_flute.mp3"))

        if wav_missing or dl_missing:
            self.view = self.SYNTH
            self._alloc()

            def cb(desc, pct):
                self.synth_desc = desc
                self.synth_pct = pct
                self.dirty = True

            def bootstrap():
                if wav_missing:
                    AudioSynthesizer.synthesize_all(cb)
                download_sounds(cb)
                self.dirty = True

            threading.Thread(target=bootstrap, daemon=True).start()
        else:
            self._alloc()
```
> Note: `synth_pct >= 100` (set by the `"Ready!"` callback at the end of `download_sounds`) is what flips the SYNTH screen back to HOME — that logic already exists in the loop just below.

### Step 2.6 — grey out unavailable sounds in the Sounds view (small polish)
In `_v_sounds` (grep `def _v_sounds`), when a row's sound has no resolvable file yet, show it dimmed with a "…" hint so the user knows it's still downloading. Find the loop that draws each sound name and, for `type == "local"`, compute `avail = self.audio.resolve_path(snd) is not None` and use `curses.A_DIM` + append `" (downloading…)"` when not available. Keep it minimal; if unsure, skip this step — it's cosmetic.

### Verify Task 2
```bash
cd /workspace
python3 -m py_compile flow && echo COMPILE_OK
# Fresh-state download smoke test (does NOT touch your real ~/.config):
python3 - <<'PY'
import importlib.util, tempfile, os
# load module-level funcs without launching curses
src = open("flow").read()
ns = {}
# pull just the pieces we need by execing in a guarded namespace
import types
mod = types.ModuleType("flowmod")
mod.__file__ = os.path.abspath("flow")
exec(compile(src.split('if __name__')[0], "flow", "exec"), mod.__dict__)
d = tempfile.mkdtemp()
mod.SOUNDS_DIR = d
ok = []
import urllib.request
for k,(u,fn) in mod.SOUND_DOWNLOADS.items():
    try:
        req=urllib.request.Request(u, headers={"User-Agent":"flow-tui/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            head=r.read(2048)
        ok.append((k, len(head)>0))
    except Exception as e:
        ok.append((k, False))
print("URL reachability:", ok)
PY
```
**Done when:** compile passes; every URL is reachable; after a real run (`./flow`) the setup screen shows "Downloading …", and Rain/Thunderstorm/Ocean/Fireplace/Birds/Café/Wind/Krishna all play. If offline, Rain still plays (falls back to `rain.wav`) and Thunderstorm falls back to `storm.wav`; the rest stay silent until a connected run — that's expected.

### Optional 2.7 — offline fallbacks for ocean/fireplace/wind (nice‑to‑have)
So those three are never silent even offline, add synth generators to `AudioSynthesizer` producing `ocean.wav`, `fire.wav`, `wind.wav` and append them to the `jobs` list in `synthesize_all`. Patterns: **ocean** = brown noise through a slow (~0.08 Hz) amplitude LFO for wave swells; **fire** = brown-noise bed + random short bright "crackle" bursts; **wind** = pink noise through a slow amplitude + light pitch LFO. Reuse the existing `_brown`/`_pink` structure. These are the `files[1]` fallbacks already referenced in Step 2.3. Skip if rate‑limited; downloads cover the normal case.

---

## TASK 3 — Real CAVA visualizer (with graceful procedural fallback)

### Why
The original ask was a **real, audio‑reactive** visualizer via [CAVA](https://github.com/karlstav/cava). The last session built a *fake* one that fabricates bars from the volume number. Keep the fake one as a fallback (cava is **not currently installed** on the target machine), but drive the bars from real audio when cava is present.

### How it captures mpv's audio
cava's default PulseAudio/PipeWire backend reads the **default sink monitor**, and mpv plays to the default sink — so cava with `source = auto` visualizes whatever mpv is playing. No FIFO plumbing needed.

### Step 3.1 — config constant
Near the other paths (grep `MPV_SOCKET =`), add:
```python
CAVA_CONFIG = f"/tmp/flow_cava_{os.getpid()}.conf"
```

### Step 3.2 — CavaEngine class (paste right after the existing `class Visualizer:` block, grep `class Visualizer`)
```python
class CavaEngine:
    """Drives the spectrum from real audio via cava. Falls back to nothing if
    cava is absent — the caller then uses the procedural Visualizer."""

    def __init__(self, bars=60):
        self.bars = max(8, min(200, bars))
        self.values = [0.0] * self.bars   # normalized 0..1, newest frame
        self.proc = None
        self.alive = False
        self._thread = None

    @staticmethod
    def available():
        return shutil.which("cava") is not None

    def _write_config(self):
        conf = (
            "[general]\n"
            "framerate = 30\n"
            f"bars = {self.bars}\n"
            "[input]\n"
            "method = pulse\n"
            "source = auto\n"
            "[output]\n"
            "method = raw\n"
            "raw_target = /dev/stdout\n"
            "data_format = ascii\n"
            "ascii_max_range = 1000\n"
            "bar_delimiter = 59\n"
            "frame_delimiter = 10\n"
        )
        with open(CAVA_CONFIG, "w") as f:
            f.write(conf)

    def start(self):
        if not self.available():
            return False
        try:
            self._write_config()
            self.proc = subprocess.Popen(
                ["cava", "-p", CAVA_CONFIG],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
        except Exception:
            self.proc = None
            return False
        self.alive = True
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()
        return True

    def _read(self):
        while self.alive and self.proc and self.proc.stdout:
            try:
                line = self.proc.stdout.readline()
            except Exception:
                break
            if not line:
                break
            try:
                parts = line.decode("ascii", "ignore").strip().split(";")
                vals = [int(x) for x in parts if x.strip().isdigit()]
                if vals:
                    self.values = [min(1.0, v / 1000.0) for v in vals]
            except Exception:
                pass

    def has_signal(self):
        return self.alive and self.proc is not None and self.proc.poll() is None

    def columns(self, width):
        """Interpolate cava bars to `width` columns (same contract as Visualizer.columns)."""
        vals = self.values
        n = len(vals)
        if width <= 0 or n == 0:
            return []
        if n == 1:
            return [vals[0]] * width
        out, last = [], n - 1
        for c in range(width):
            pos = (c / (width - 1) * last) if width > 1 else 0.0
            i = int(pos)
            frac = pos - i
            out.append(vals[i] * (1 - frac) + vals[min(i + 1, last)] * frac)
        return out

    def stop(self):
        self.alive = False
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=1)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        try:
            os.unlink(CAVA_CONFIG)
        except OSError:
            pass
```
Make sure `import shutil` exists (added in Task 2; add it if you're doing Task 3 first).

### Step 3.3 — config fields (in `ConfigManager.__init__`, grep `self.visualizer_rows`)
Add after `self.visualizer_rows = 2`:
```python
        self.vis_bars = 60        # cava bar count (20–100)
        self.vis_amplitude = 100  # height scaling percent (25–150)
```
Also bump the height clamp from 3 to 4 — in `_vis_h` (grep `def _vis_h`) change `min(3, self.cfg.visualizer_rows)` to `min(4, self.cfg.visualizer_rows)`.

### Step 3.4 — instantiate & start cava (in `FlowTUI.__init__`, grep `self.vis =`)
Where `self.vis` (the procedural Visualizer) is created, add right after it:
```python
        self.cava = CavaEngine(bars=self.cfg.vis_bars)
        self.cava_on = self.cava.start()  # False if cava not installed
```
And in cleanup (grep `def _cleanup`) add `if getattr(self, "cava", None): self.cava.stop()`.

### Step 3.5 — render from cava when available (in `_draw_visualizer`, grep `def _draw_visualizer`)
Replace the line `levels = self.vis.columns(mx)` with:
```python
        amp = max(0.25, min(1.5, self.cfg.vis_amplitude / 100.0))
        if getattr(self, "cava_on", False) and self.cava.has_signal():
            levels = [min(1.0, v * amp) for v in self.cava.columns(mx)]
        else:
            levels = [min(1.0, v * amp) for v in self.vis.columns(mx)]
```

### Step 3.6 — settings entries + editing
In `_v_settings` (grep `def _v_settings`) add three rows to the `items` list (after the `"Visualizer"` row):
```python
            ("Visualizer Height", f"{self.cfg.visualizer_rows} rows"),
            ("Visualizer Bars", f"{self.cfg.vis_bars}"),
            ("Visualizer Amplitude", f"{self.cfg.vis_amplitude}%"),
```
This shifts the indices of "App Blocker" and "Blocked Apps →". In `_settings_action` (grep `def _settings_action`), the `idx ==` numbers must match the new order. Re‑number so each label maps to the right action; for the three new ones call `self._begin_input("vis_rows")`, `self._begin_input("vis_bars")`, `self._begin_input("vis_amp")` respectively, and keep App Blocker / Blocked Apps as the last two indices. **Count the list carefully** — the order in `items` must equal the order in `_settings_action`.

In `_save_input` (grep `def _save_input`), add three branches alongside the existing `work_dur`/`short_dur` ones:
```python
        elif self.input_for == "vis_rows":
            if val.isdigit():
                self.cfg.visualizer_rows = max(1, min(4, int(val)))
                self.cfg.save(); self._alloc()
        elif self.input_for == "vis_bars":
            if val.isdigit():
                self.cfg.vis_bars = max(20, min(100, int(val)))
                self.cfg.save()
                if getattr(self, "cava", None):   # restart cava with new bar count
                    self.cava.stop(); self.cava = CavaEngine(bars=self.cfg.vis_bars); self.cava_on = self.cava.start()
        elif self.input_for == "vis_amp":
            if val.isdigit():
                self.cfg.vis_amplitude = max(25, min(150, int(val)))
                self.cfg.save()
```

### Verify Task 3
```bash
python3 -m py_compile flow && echo COMPILE_OK
python3 tools/render_test.py   # (Appendix A) — must show NO traceback at all sizes
command -v cava || echo "cava NOT installed → procedural fallback path is what runs here"
```
**Done when:** compiles; render harness shows no traceback whether or not cava exists; with cava installed + audio playing, bars react to the actual sound; settings show/edit Height, Bars, Amplitude. Real‑cava reactivity can only be confirmed on a machine with cava + PipeWire/PulseAudio — note that in your report if you can't test it here.

---

## TASK 4 — Flatpak / sandbox‑aware app blocking

### Why
`BlockerEngine._loop` polls every 1.5 s and sends a single `os.kill` to the matched PID. Flatpak apps run inside a `bwrap` sandbox (`bwrap … -- audacity` → child `audacity.bin`); killing the child alone lets bwrap respawn or the match miss. Names also vary (`audacity.bin`, `helium-browser-bin`).

### Step 4.1 — name normalizer (module‑level, above `class BlockerEngine`, grep `class BlockerEngine`)
```python
def clean_proc_name(name):
    n = name.lower().replace("-", " ").replace("_", " ").replace(".", " ")
    for suffix in (" bin", " git", " debug", " stable", " real"):
        if n.endswith(suffix):
            n = n[: -len(suffix)]
    return n.strip()
```

### Step 4.2 — use normalized matching in `_find_pids` (grep `def _find_pids`)
Replace the inner match test. Currently it does `if b in comm or b in cmdline`. Change the matching so both sides are normalized:
```python
                cl = clean_proc_name(comm) + " " + clean_proc_name(cmdline)
                for b in blocked:
                    if clean_proc_name(b) and clean_proc_name(b) in cl:
                        pids.append(pid)
                        break
```
(Keep the surrounding `/proc` reading exactly as it is.)

### Step 4.3 — process‑group kill + escalation in `_loop` (grep `def _loop`)
Replace the whole `_loop` method with:
```python
    def _loop(self):
        kill_attempts = {}  # pid -> attempts
        try:
            my_pgid = os.getpgrp()
        except Exception:
            my_pgid = -1
        while self.running:
            if self.config.block_apps and not self.is_break:
                alive = set()
                for pid in self._find_pids():
                    alive.add(pid)
                    attempts = kill_attempts.get(pid, 0)
                    sig = signal.SIGKILL if attempts >= 2 else signal.SIGTERM
                    try:
                        try:
                            pgid = os.getpgid(pid)
                        except Exception:
                            pgid = -1
                        if pgid > 0 and pgid != my_pgid:
                            os.killpg(pgid, sig)   # nukes bwrap + all children
                        else:
                            os.kill(pid, sig)
                    except Exception:
                        pass
                    kill_attempts[pid] = attempts + 1
                # forget pids that are gone so a relaunch restarts at SIGTERM
                for dead in [p for p in kill_attempts if p not in alive]:
                    del kill_attempts[dead]
            else:
                kill_attempts.clear()
            time.sleep(0.5)
```
Note this replaces the old `self._sigtermed` mechanism; you can delete the `self._sigtermed = set()` line in `__init__` (grep `_sigtermed`) since it's no longer used.

### Verify Task 4
```bash
python3 -m py_compile flow && echo COMPILE_OK
python3 tools/render_test.py   # no traceback
```
**Done when:** compiles; render harness clean. Functional test on a real machine: add `audacity` (or a Flatpak app) to the block list, enable App Blocker in Settings (no timer needed), launch the app → it dies within ~1 s. **Safety check:** confirm the app never kills its own process group (it guards `pgid != my_pgid`).

---

## TASK 5 — Daily Focus Goal + app‑list de‑duplication

Two small, independent items.

### 5A — Daily Focus Goal
**Step 5A.1** — duration parser (module‑level, near the top helpers, grep `def get_visible_tasks` and put it above that):
```python
def parse_duration_to_seconds(s):
    """'21h3m23s' / '2h' / '30m' / '90' (bare = minutes) -> seconds. 0 if invalid."""
    s = (s or "").strip().lower()
    if s.isdigit():
        return int(s) * 60
    total = 0
    for val, unit in re.findall(r"(\d+)\s*([hms])", s):
        total += int(val) * {"h": 3600, "m": 60, "s": 1}[unit]
    return total
```
**Step 5A.2** — config default (in `ConfigManager.__init__`, grep `self.daily_study`):
```python
        self.daily_goal_seconds = 7200  # 2h default daily focus goal
```
**Step 5A.3** — settings row + edit. In `_v_settings` add a row, e.g. after the durations:
```python
            ("Daily Focus Goal", self._fmt_hm(self.cfg.daily_goal_seconds)),
```
(Re‑number `_settings_action` to match — same caution as Task 3.6.) Its action: `self._begin_input("daily_goal")`. In `_save_input` add:
```python
        elif self.input_for == "daily_goal":
            secs = parse_duration_to_seconds(val)
            if secs > 0:
                self.cfg.daily_goal_seconds = secs
                self.cfg.save()
```
> If you are doing Task 5 before Task 3, just append your row(s) to `_v_settings`/`_settings_action` and keep the index mapping consistent. Whoever does both tasks must reconcile the final settings order — count the list.

### 5B — App‑list dedup
In `fetch_installed_apps` (grep `# Deduplicate: normalize names`), replace the dedup block with one that also strips packaging suffixes so `helium-browser-bin` collapses into `helium-browser`:
```python
            # Deduplicate: collapse -bin/-git/-debug variants, prefer the base name.
            def base(a):
                a = a.lower()
                for suf in ("-bin", "-git", "-debug", "-stable"):
                    if a.endswith(suf):
                        a = a[: -len(suf)]
                return a.replace("-", " ").replace("_", " ").strip()
            norm_map = {}
            for app in sorted(apps):
                k = base(app)
                # keep the shortest/prettiest representative for each base name
                if k not in norm_map or len(app) < len(norm_map[k]):
                    norm_map[k] = app
            self.installed_apps = sorted(norm_map.values())
            self.app_search_results = self.installed_apps[:]
            self.dirty = True
```

### Verify Task 5
```bash
python3 -m py_compile flow && echo COMPILE_OK
python3 - <<'PY'
import types,os
src=open("flow").read().split("if __name__")[0]
m=types.ModuleType("m"); m.__file__=os.path.abspath("flow")
exec(compile(src,"flow","exec"),m.__dict__)
p=m.parse_duration_to_seconds
assert p("21h3m23s")==21*3600+3*60+23, p("21h3m23s")
assert p("2h")==7200 and p("30m")==1800 and p("90")==5400 and p("junk")==0
print("parser OK")
PY
python3 tools/render_test.py   # no traceback
```
**Done when:** parser asserts pass; Settings shows/edits "Daily Focus Goal"; render harness clean.

---

## TASK 6 — Stats overhaul (depends on Task 5's daily goal)

### Why
Original ask: **weekly habits heatmap**, **monthly calendar with progress circles** ○◔◑◕●, and a **yearly overview**. Current Stats has daily / weekly(study bars) / calendar(shade ramp). Add the missing views and switch the monthly calendar to goal‑based circles.

### Step 6.1 — circle helper + a daily/monthly completion ratio (add inside `FlowTUI`, near `_fmt_hm`)
```python
    @staticmethod
    def _circle(pct):
        if pct <= 0.05: return "○"
        if pct <= 0.35: return "◔"
        if pct <= 0.65: return "◑"
        if pct <= 0.85: return "◕"
        return "●"
```

### Step 6.2 — expand the sub‑view tabs
In `_v_stats` (grep `modes = [`), change to:
```python
        modes = [("daily", "Daily"), ("habits", "Habits"), ("month", "Month"), ("year", "Year")]
```
and update the dispatch below it:
```python
        if self.stats_mode == 0:
            self._stats_daily(w, my, mx)
        elif self.stats_mode == 1:
            self._stats_habits(w, my, mx)
        elif self.stats_mode == 2:
            self._stats_calendar(w, my, mx)
        else:
            self._stats_year(w, my, mx)
```
The sub‑tabs are switched by clicking them or keys `1`/`2`/`3`/`4`. Check `_key_right` (grep `def _key_right`) handles digit keys for stats — if it only handles `1/2/3`, extend it to `4` (call `self._set_stats_mode(3)`).

### Step 6.3 — weekly HABITS heatmap (new method)
```python
    def _stats_habits(self, w, my, mx):
        habits = self.habits.habits
        today = datetime.now().date()
        days = [today - timedelta(days=(6 - i)) for i in range(7)]  # oldest→today
        saddstr(w, 3, 4, "Habits — last 7 days", curses.A_BOLD | curses.color_pair(5))
        # weekday headers
        hx = 22
        for i, d in enumerate(days):
            saddstr(w, 5, hx + i * 3, d.strftime("%a")[0], curses.A_DIM)
        if not habits:
            saddstr(w, 7, 4, "no habits yet — add them in the left panel", curses.A_DIM)
            return
        for r, h in enumerate(habits):
            y = 6 + r
            if y >= my - 2:
                break
            name = h["name"][:16]
            saddstr(w, y, 4, name, curses.color_pair(6))
            for i, d in enumerate(days):
                done = bool(h["history"].get(d.strftime("%Y-%m-%d")))
                mark = "●" if done else "○"
                a = curses.color_pair(1) if done else curses.A_DIM
                saddstr(w, y, hx + i * 3, mark, a)
```

### Step 6.4 — monthly calendar with goal circles (replace the shade ramp in `_stats_calendar`)
In `_stats_calendar` (grep `# Shade ramp by minutes studied`), replace the per‑day level/ramp logic with goal‑based circles. Keep the month nav (`‹ ›`) and headers as they are. The inner loop becomes:
```python
        goal = max(1, self.cfg.daily_goal_seconds)
        row = 6
        col = first_wd
        month_total = 0
        for day in range(1, days_in_month + 1):
            ds = f"{year:04d}-{month:02d}-{day:02d}"
            secs = self._study_for(ds)
            month_total += secs
            pct = secs / goal
            circ = self._circle(pct)
            x = 4 + col * cw
            is_today = (year == today.year and month == today.month and day == today.day)
            cell_a = curses.color_pair(1) | curses.A_BOLD if pct >= 0.86 else (
                curses.color_pair(1) if pct > 0.05 else curses.A_DIM)
            if is_today:
                cell_a = curses.color_pair(3) | curses.A_BOLD
            saddstr(w, row, x, f"{day:2d}", curses.A_DIM if not is_today else cell_a)
            saddstr(w, row, x + 2, circ, cell_a)
            col += 1
            if col > 6:
                col = 0
                row += 1
            if row >= my - 3:
                break
        saddstr(w, my - 3, 4, f"month total  {self._fmt_hm(month_total)}   goal/day {self._fmt_hm(goal)}",
                curses.A_BOLD | curses.color_pair(1))
```
(Delete the now‑unused `ramp = [...]` line and the `mins`/`lvl` block it replaces.)

### Step 6.5 — yearly overview (new method)
```python
    def _stats_year(self, w, my, mx):
        today = datetime.now()
        year = today.year
        goal = max(1, self.cfg.daily_goal_seconds)
        saddstr(w, 3, 4, f"{year} — monthly focus", curses.A_BOLD | curses.color_pair(5))
        year_total = 0
        for m in range(1, 13):
            days_in = _calendar.monthrange(year, m)[1]
            msecs = sum(self._study_for(f"{year:04d}-{m:02d}-{d:02d}") for d in range(1, days_in + 1))
            year_total += msecs
            pct = msecs / (goal * days_in)
            y = 5 + (m - 1)
            if y >= my - 2:
                break
            circ = self._circle(pct)
            a = curses.color_pair(1) | curses.A_BOLD if pct >= 0.86 else (
                curses.color_pair(1) if pct > 0.05 else curses.A_DIM)
            saddstr(w, y, 4, _calendar.month_name[m][:3], curses.color_pair(6))
            saddstr(w, y, 9, circ, a)
            saddstr(w, y, 12, self._fmt_hm(msecs), curses.A_DIM)
        saddstr(w, my - 2, 4, f"year total  {self._fmt_hm(year_total)}", curses.A_BOLD | curses.color_pair(1))
```

### Verify Task 6
```bash
python3 -m py_compile flow && echo COMPILE_OK
python3 tools/render_test.py --keys $'\x09'   # Tab into panels; just confirm no traceback
```
Then manually: run `./flow`, click the **stats** tab, click each sub‑tab (Daily / Habits / Month / Year). To see data, add a habit and check it, and let the stopwatch run a bit.
**Done when:** all four sub‑views render with no traceback; Month/Year use ○◔◑◕● scaled to the daily goal; Habits shows a per‑habit 7‑day ●/○ grid.

---

## TASK 7 — Final verification + docs/install

1. **Compile + render harness at multiple sizes** (Appendix A):
   ```bash
   python3 -m py_compile flow && python3 tools/render_test.py --all-sizes
   ```
   Zero tracebacks at 12, 16, 24, 40 rows.
2. **install.sh** (grep `Check pkexec` in `install.sh`): add a check recommending `cava` (for the real visualizer) and confirm the Krishna MP3 ships. Add, near the other dependency checks:
   ```bash
   if command -v cava &> /dev/null; then echo "  ✅ cava is installed (real audio visualizer)."; else echo "  ⚠️  cava NOT installed (visualizer falls back to a simulated one). Install: sudo pacman -S cava / sudo apt install cava"; fi
   ```
   Also copy the bundled Krishna MP3 into the user's sound dir during install (optional; the app also self‑copies on first run via `_install_krishna_flute`).
3. **IMPLEMENTATION_PLAN.md**: update the status log **honestly** — mark each task done only after its verify passed, and note anything you couldn't test live (e.g. real cava without PipeWire).
4. **CLAUDE.md**: add one line each for the new pieces — `download_sounds`/`SOUND_DOWNLOADS`, `CavaEngine`, `parse_duration_to_seconds`, daily goal, new stats sub‑views.

**Done when:** harness clean at all sizes; install.sh mentions cava; docs reflect reality.

---

## Appendix A — render test harness (`tools/render_test.py`)

Create this file once (Task 2 or earlier). It launches `flow` in a pseudo‑terminal at given sizes, optionally sends keystrokes, and reports any Python traceback. **No mpv/cava needed** — it just exercises the curses rendering.
```python
#!/usr/bin/env python3
import os, pty, time, select, struct, fcntl, termios, signal, sys

FLOW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flow")

def run(rows, cols, keys=b"", seconds=2.5):
    pid, fd = pty.fork()
    if pid == 0:
        os.environ["TERM"] = "xterm-256color"
        os.execvp("python3", ["python3", FLOW]); os._exit(1)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    out, t0, sent = b"", time.time(), False
    while time.time() - t0 < seconds:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try: d = os.read(fd, 65536)
            except OSError: break
            if not d: break
            out += d
        if keys and not sent and time.time() - t0 > 0.9:
            try: os.write(fd, keys)
            except OSError: pass
            sent = True
    try: os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0)
    except OSError: pass
    return out.decode("utf-8", "replace")

def check(rows, cols, keys=b""):
    t = run(rows, cols, keys)
    tb = "Traceback" in t
    print(f"{rows}x{cols}: {'TRACEBACK!' if tb else 'ok'}  habits={'habits' in t}")
    if tb:
        i = t.find("Traceback"); print(t[i:i+1200])
    return not tb

if __name__ == "__main__":
    keys = b""
    if "--keys" in sys.argv:
        keys = sys.argv[sys.argv.index("--keys") + 1].encode()
    sizes = [(24, 90)]
    if "--all-sizes" in sys.argv:
        sizes = [(12, 80), (16, 80), (24, 90), (40, 120)]
    ok = all(check(r, c, keys) for r, c in sizes)
    sys.exit(0 if ok else 1)
```
Run: `python3 tools/render_test.py --all-sizes`

## Appendix B — quick reference: where things live (grep anchors)
- Sound list / engine: `class AudioEngine`, `self.sounds = [`, `def play(self, idx)`, `def _watchdog`
- Synth + startup: `def synthesize_all`, `needs_synth = False`
- Visualizer: `class Visualizer`, `def _draw_visualizer`, `def _vis_h`
- Blocker: `class BlockerEngine`, `def _find_pids`, `def _loop`
- Apps: `def fetch_installed_apps`
- Settings: `def _v_settings`, `def _settings_action`, `def _save_input`, `def _begin_input`
- Stats: `def _v_stats`, `def _stats_daily`, `def _stats_weekly`, `def _stats_calendar`, `def _cal_nav`
- Config: `class ConfigManager`, `def __init__` (defaults)
- Layout: `def _alloc` (the left split — habits fix already here)

## Appendix C — what NOT to touch
- The mpv buffering/reconnect flags in `_start_mpv` and the `_watchdog` — Task 1 of the *previous* plan; they work, leave them.
- `_handle_mouse` generic button hit‑testing and `register_btn` — the mouse‑first pattern is correct; just make sure any new clickable thing registers a button there.
- Don't "optimize" the curses draw loop or change the 20 FPS timeout.
