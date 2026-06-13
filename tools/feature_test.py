import types, os, sys, tempfile, json
src = open("flow").read().split("if __name__")[0]
m = types.ModuleType("m"); m.__file__ = os.path.abspath("flow")
exec(compile(src, "flow", "exec"), m.__dict__)
F = m.FlowTUI
ok = True


def check(name, cond):
    global ok
    print(("OK  " if cond else "FAIL") + " " + name)
    if not cond:
        ok = False


# _parse_date
check("date valid", F._parse_date("2026-12-31") == "2026-12-31")
check("date slash", F._parse_date("2026/12/31") == "2026-12-31")
check("date clear", F._parse_date("none") == "")
check("date junk", F._parse_date("abc") == "")

# bare instance for export + settings + countdown
t = F.__new__(F)


class Cfg:
    pass


t.cfg = Cfg()
c = t.cfg
c.work_dur = 25; c.short_break_dur = 5; c.long_break_dur = 15
c.daily_goal_seconds = 7200; c.auto_start = True; c.pomodoro_target = 0
c.countdown_name = "Exam"; c.countdown_date = ""
c.sound_enabled = True; c.notifications = True; c.visualizer = True
c.visualizer_rows = 2; c.vis_bars = 60; c.vis_amplitude = 100
c.block_apps = False; c.blocked_apps = ["steam"]
c.study_total = 3600
c.daily_study = {"2026-06-13": 3600, "2026-06-12": 1800}


class H:
    habits = [{"name": "Read", "history": {"2026-06-13": True, "2026-06-10": True}}]


t.habits = H()

items = t._build_settings()
check("settings has 17 rows", len(items) == 17)
check("every row is (label,val,callable)", all(len(r) == 3 and callable(r[2]) for r in items))
labels = [r[0] for r in items]
check("has Auto-start", "Auto-start Sessions" in labels)
check("has Session Target", "Session Target" in labels)
check("has Countdown Name", "Countdown Name" in labels)
check("has Export", any("Export" in l for l in labels))

# countdown label (color_pair needs curses; only check the no-curses paths)
c.countdown_date = ""
check("countdown disabled -> None", t._countdown_label() is None)
c.countdown_date = "not-a-date"
check("countdown invalid -> None", t._countdown_label() is None)

# export
d = tempfile.mkdtemp()
t._flash_msg = ""; t._flash_t = 0
import time as _time
m.time = m.time  # ensure time available
t._export_stats(d)
jp = os.path.join(d, "flow_stats.json")
fp = os.path.join(d, "flow_focus.csv")
hp = os.path.join(d, "flow_habits.csv")
check("json written", os.path.exists(jp))
check("focus csv written", os.path.exists(fp))
check("habits csv written", os.path.exists(hp))
if os.path.exists(jp):
    data = json.load(open(jp))
    check("json has daily_study", data["daily_study_seconds"]["2026-06-13"] == 3600)
    check("json has habits", data["habits"][0]["name"] == "Read")
if os.path.exists(fp):
    csv = open(fp).read()
    check("focus csv has rows", "2026-06-13,3600" in csv)

print("\nALL", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
