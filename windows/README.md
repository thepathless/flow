# Windows

`flow` is built around a Unix terminal. There are two ways to run it on Windows;
**WSL is strongly recommended** because every feature works there unchanged.

## Option A — WSL (recommended, full features)

[WSL] gives you a real Linux environment. Inside it, flow behaves exactly like
on Linux (audio, app-blocker, visualizer, everything).

```powershell
wsl --install                # one-time, then reboot
```

Then, inside the Ubuntu/WSL shell:

```sh
pip install flow-tui
flow
```

Run it in **Windows Terminal** for proper colors, Unicode and mouse support.

## Option B — Native pip (core features only)

```powershell
pip install "flow-tui[windows]"
flow
```

The `[windows]` extra pulls in `windows-curses` (the curses backend Windows
needs). Run flow inside **Windows Terminal**, not the legacy `console`.

### What works natively vs. what needs WSL

| Feature | Native Windows | WSL |
| --- | --- | --- |
| Pomodoro timer, stopwatch | ✅ | ✅ |
| To-dos & subtasks | ✅ | ✅ |
| Habit tracker & stats | ✅ | ✅ |
| Countdown, settings, export | ✅ | ✅ |
| Simulated visualizer | ✅ | ✅ |
| Ambient/lofi audio (`mpv`) | ❌ (Linux IPC) | ✅ |
| App blocker (`/proc`) | ❌ (no-op) | ✅ |

flow degrades gracefully: the audio and app-blocker features are simply inactive
on native Windows — nothing crashes.

> Bottom line: for the complete experience on Windows, use **WSL**. For a quick
> timer/todo/habit setup with no Linux layer, native pip is fine.

[WSL]: https://learn.microsoft.com/windows/wsl/install
