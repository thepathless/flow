import types, os, sys
src = open("flow").read().split("if __name__")[0]
m = types.ModuleType("m"); m.__file__ = os.path.abspath("flow")
exec(compile(src, "flow", "exec"), m.__dict__)
nt = m.name_tokens


def match(blocked, comm, argv0):
    bt = nt(blocked); pt = nt(comm) | nt(argv0)
    return bool(bt) and bt <= pt


cases = [
    ("google-chrome", "chrome", "/opt/google/chrome/chrome", True),
    ("helium-browser", "helium-browser-", "/opt/helium/helium-browser-bin", True),
    ("steam", "steam", "/usr/bin/steam", True),
    ("audacity", "audacity.bin", "/app/bin/audacity.bin", True),
    ("discord", "Discord", "/opt/discord/Discord", True),
    ("firefox", "firefox", "/usr/lib/firefox/firefox", True),
    ("chrome", "code", "/usr/share/code/code", False),
    ("spotify", "spotify", "/usr/bin/spotify", True),
    ("obs studio", "obs", "/usr/bin/obs", False),
    ("obs", "obs", "/usr/bin/obs", True),
]
ok = True
for b, c, a, exp in cases:
    got = match(b, c, a)
    if got != exp:
        ok = False
    print(f"{'OK' if got==exp else 'FAIL'}: block={b!r} comm={c!r} argv0={a!r} -> {got} (exp {exp})")
print("ALL", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
