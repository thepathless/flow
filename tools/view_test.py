#!/usr/bin/env python3
"""Render the new Settings view + countdown label under a real curses window
to catch runtime/curses errors the HOME-only render harness can't reach."""
import os, sys, types, curses, datetime, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "flow")).read().split("if __name__")[0]
mod = types.ModuleType("flowmod"); mod.__file__ = os.path.join(ROOT, "flow")
exec(compile(src, "flow", "exec"), mod.__dict__)
F = mod.FlowTUI


class Cfg:
    work_dur = 25; short_break_dur = 5; long_break_dur = 15
    daily_goal_seconds = 7200; auto_start = True; pomodoro_target = 4
    countdown_name = "Exam"; countdown_date = ""
    sound_enabled = True; notifications = True; visualizer = True
    visualizer_rows = 2; vis_bars = 60; vis_amplitude = 100
    block_apps = False; blocked_apps = ["steam", "discord"]
    study_total = 3600


class H:
    habits = [{"name": "Read", "history": {}}]


def main(stdscr):
    curses.use_default_colors()
    for i in range(1, 8):
        try:
            curses.init_pair(i, i, -1)
        except curses.error:
            pass
    t = F.__new__(F)
    t.cfg = Cfg(); t.habits = H()
    t.panel = F.RIGHT
    results = []
    for rows in (10, 16, 24, 40):
        # Settings view at this height (exercises scroll + all 17 rows)
        for rcur in (0, 8, 16):
            t.rcur = rcur; t.rscroll = 0
            w = curses.newwin(rows, 70, 0, 0)
            try:
                w.erase(); t._v_settings(w, rows, 70)
                results.append((rows, f"settings rcur={rcur}", "ok"))
            except Exception as e:
                results.append((rows, f"settings rcur={rcur}", "FAIL " + repr(e) + "\n" + traceback.format_exc()))
    # countdown label states (colored path needs curses)
    for ds, want in (("", True), ((datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), False),
                     (datetime.date.today().strftime("%Y-%m-%d"), False),
                     ((datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"), False)):
        t.cfg.countdown_date = ds
        try:
            lbl = t._countdown_label()
            results.append(("cd", ds or "(off)", "ok" if (lbl is None) == want else "FAIL wrong-none"))
        except Exception as e:
            results.append(("cd", ds or "(off)", "FAIL " + repr(e)))
    return results


if __name__ == "__main__":
    res = curses.wrapper(main)
    bad = [r for r in res if not r[2].startswith("ok")]
    for a, b, st in res:
        print(f"{a} {b}: {st if st == 'ok' else 'FAIL'}")
    for a, b, st in bad:
        print(f"\n--- {a} {b} ---\n{st}")
    sys.exit(1 if bad else 0)
