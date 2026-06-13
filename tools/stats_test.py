#!/usr/bin/env python3
"""Exercise the Stats sub-views (daily/habits/month/year) directly against a
real curses window, without launching the full app. Reports any exception.
Run inside a terminal: python3 tools/stats_test.py
"""
import os, sys, types, curses
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "flow")).read().split("if __name__")[0]
mod = types.ModuleType("flowmod")
mod.__file__ = os.path.join(ROOT, "flow")
exec(compile(src, "flow", "exec"), mod.__dict__)

FlowTUI = mod.FlowTUI


class Cfg:
    daily_goal_seconds = 7200
    study_total = 5400
    def __init__(self):
        today = datetime.now()
        self.daily_study = {
            today.strftime("%Y-%m-%d"): 3600,
            (today - timedelta(days=1)).strftime("%Y-%m-%d"): 9000,
            (today - timedelta(days=40)).strftime("%Y-%m-%d"): 1200,
        }


class Habits:
    def streak(self, h):
        return len(h.get("history", {}))

    def __init__(self):
        today = datetime.now().date()
        self.habits = [
            {"name": "Read", "history": {today.strftime("%Y-%m-%d"): True,
                                          (today - timedelta(days=2)).strftime("%Y-%m-%d"): True}},
            {"name": "Exercise daily long name here", "history": {}},
        ]


def build():
    t = FlowTUI.__new__(FlowTUI)
    t.cfg = Cfg()
    t.habits = Habits()
    t.study_session = 120
    t.cal_offset = 0
    t.left_w = 30
    t.buttons = {}
    t.register_btn = lambda *a, **k: None
    return t


def main(stdscr):
    curses.start_color()
    for i in range(1, 8):
        try:
            curses.init_pair(i, i, -1)
        except curses.error:
            pass
    t = build()
    results = []
    for rows in (10, 16, 24, 40):
        w = curses.newwin(rows, 90, 0, 0)
        my, mx = rows, 90
        for name, fn in (("daily", t._stats_daily), ("habits", t._stats_habits),
                          ("month", t._stats_calendar), ("year", t._stats_year)):
            try:
                w.erase()
                fn(w, my, mx)
                results.append((rows, name, "ok"))
            except Exception as e:
                import traceback
                results.append((rows, name, "FAIL: " + repr(e) + "\n" + traceback.format_exc()))
    return results


if __name__ == "__main__":
    try:
        curses.set_escdelay(25)
    except Exception:
        pass
    res = curses.wrapper(lambda s: (curses.use_default_colors(), main(s))[1])
    bad = [r for r in res if r[2] != "ok"]
    for rows, name, status in res:
        print(f"{rows}x90 {name:7s}: {status if status == 'ok' else 'TRACEBACK'}")
    for rows, name, status in bad:
        print(f"\n--- {rows}x90 {name} ---\n{status}")
    sys.exit(1 if bad else 0)
