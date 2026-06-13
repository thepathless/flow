#!/usr/bin/env python3
"""Render the help overlay at several sizes against a real curses window and
assert no glyph is drawn outside the box borders (catches text overflow)."""
import os, sys, types, curses

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "flow")).read().split("if __name__")[0]
mod = types.ModuleType("flowmod"); mod.__file__ = os.path.join(ROOT, "flow")
exec(compile(src, "flow", "exec"), mod.__dict__)
FlowTUI = mod.FlowTUI


def main(stdscr):
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass
    for i in range(1, 8):
        try:
            curses.init_pair(i, i, -1)
        except curses.error:
            pass
    t = FlowTUI.__new__(FlowTUI)
    results = []
    for rows, cols in ((24, 80), (30, 100), (16, 60), (40, 120)):
        win = curses.newwin(rows, cols, 0, 0)
        t.stdscr = win
        win.erase()
        t._draw_help(rows, cols)
        bw = max(34, min(cols - 4, 60))
        x0 = (cols - bw) // 2
        right = x0 + bw  # first column to the RIGHT of the box
        overflow = False
        for y in range(rows):
            # left of box
            for x in range(0, x0):
                try:
                    ch = win.inch(y, x) & 0xFF
                except curses.error:
                    ch = 0x20
                if ch not in (0x20, 0):
                    overflow = True
            # right of box (avoid last cell which can't be written)
            for x in range(right, cols - 1):
                try:
                    ch = win.inch(y, x) & 0xFF
                except curses.error:
                    ch = 0x20
                if ch not in (0x20, 0):
                    overflow = True
        results.append((rows, cols, "OVERFLOW" if overflow else "ok"))
    return results


if __name__ == "__main__":
    res = curses.wrapper(lambda s: (curses.use_default_colors(), main(s))[1])
    bad = [r for r in res if r[2] != "ok"]
    for rows, cols, st in res:
        print(f"{rows}x{cols}: {st}")
    sys.exit(1 if bad else 0)
