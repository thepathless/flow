#!/usr/bin/env python3
"""Render-test harness for flow: launches it in a pseudo-terminal at given sizes,
optionally sends keystrokes, and reports any Python traceback. No mpv/cava needed."""
import os, pty, time, select, struct, fcntl, termios, signal, sys

FLOW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flow")


def run(rows, cols, keys=b"", seconds=2.5):
    pid, fd = pty.fork()
    if pid == 0:
        os.environ["TERM"] = "xterm-256color"
        os.execvp("python3", ["python3", FLOW])
        os._exit(1)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    out, t0, sent = b"", time.time(), False
    while time.time() - t0 < seconds:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                d = os.read(fd, 65536)
            except OSError:
                break
            if not d:
                break
            out += d
        if keys and not sent and time.time() - t0 > 0.9:
            try:
                os.write(fd, keys)
            except OSError:
                pass
            sent = True
    try:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
    except OSError:
        pass
    return out.decode("utf-8", "replace")


def check(rows, cols, keys=b""):
    t = run(rows, cols, keys)
    tb = "Traceback" in t
    print(f"{rows}x{cols}: {'TRACEBACK!' if tb else 'ok'}  habits={'habits' in t}")
    if tb:
        i = t.find("Traceback")
        print(t[i:i + 1200])
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
