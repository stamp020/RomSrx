"""Run every patcher test suite and report one number.

    python tests/run_all.py

These are plain scripts rather than pytest cases, so they run anywhere Python
does with nothing installed. Each prints its own results and ends with a count;
this collects those counts and fails the process if any suite did.

Nothing here touches the network - the suites build their own patches. The
scripts that check real patches from RetroAchievements are deliberately not
part of this, so a run means the same thing offline as on.
"""
import io
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = Path(__file__).resolve().parent
SUITES = ["test_patcher.py", "test_vcdiff.py", "test_naming.py",
          "test_patch_game.py", "test_indexer_retry.py", "test_index_store.py",
          "test_ppf.py", "test_replace.py", "test_artwork.py",
          "test_search.py", "test_rahash.py", "test_verify.py",
          "test_wanted.py", "test_hardcore.py", "test_rapi.py",
          "test_discs.py", "test_times.py", "test_emufind.py",
          "test_scope.py", "test_library.py", "test_i18n.py",
          "test_frontend.py", "test_portable.py", "test_spell.py",
          "test_throttle.py", "test_autosave.py", "test_minerva.py",
          "test_torrent.py", "test_webmenu.py", "test_hacks.py", "test_arcade.py", "test_resume.py"]

# The list above is written out rather than globbed, so that the order is the
# quick suites first and a new file cannot quietly change what a run means.
# The cost of that is a suite nobody added here never runs at all, and never
# says so - test_webmenu.py sat unlisted and green for exactly as long as it
# took to notice the suite count had not gone up. So the folder is checked
# against the list.
_listed = set(SUITES)
_present = {p.name for p in HERE.glob("test_*.py")}
_missing = sorted(_present - _listed)
if _missing:
    print("These suites exist but are not in SUITES, so they never run:")
    for _name in _missing:
        print(f"  {_name}")
    raise SystemExit(1)

total_ok = total_fail = 0
broken: list[str] = []
# What each failing suite actually said, kept so the report at the bottom can
# repeat it. A run on a machine that is not yours is read as the last few
# lines of a log, and "one suite failed" without naming it is a message that
# costs another whole run to act on.
detail: dict[str, list[str]] = {}

for name in SUITES:
    print(f"\n=== {name} " + "=" * (58 - len(name)))
    result = subprocess.run([sys.executable, str(HERE / name)],
                            capture_output=True, text=True, encoding="utf-8")
    output = (result.stdout or "") + (result.stderr or "")
    print(output.rstrip())

    lines = output.splitlines()
    bad: list[str] = []
    for at, line in enumerate(lines):
        if not line.lstrip().startswith("FAIL"):
            continue
        # The FAIL line and the got/want pair printed under it.
        bad.extend(x.rstrip() for x in lines[at:at + 3])

    tally = re.search(r"(\d+) passed, (\d+) failed", output)
    if not tally:
        # It never reached its own tally, so the end of the output is the
        # traceback and there is nothing else worth having.
        broken.append(f"{name} did not finish")
        detail[name] = lines[-25:] or ["(no output at all)"]
        continue
    total_ok += int(tally.group(1))
    total_fail += int(tally.group(2))
    if result.returncode != 0:
        broken.append(f"{name} exited with {result.returncode}")
    if bad:
        detail[name] = bad

print("\n" + "=" * 64)
print(f"{total_ok} passed, {total_fail} failed, across {len(SUITES)} suites")
for note in broken:
    print(f"  !! {note}")
for name, lines in detail.items():
    print(f"\n  !! {name}")
    for line in lines:
        print(f"     {line}")

# On a CI runner the same report goes to the job summary, which is the page
# somebody looks at when a build goes red. Reading the log means finding and
# expanding the right step in a browser; this puts the answer on the front.
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary and (total_fail or broken):
    try:
        with open(summary, "a", encoding="utf-8") as out:
            out.write(f"### Tests failed on {sys.platform}\n\n")
            for note in broken:
                out.write(f"- **{note}**\n")
            for name, lines in detail.items():
                out.write(f"\n**{name}**\n\n```\n"
                          + "\n".join(lines) + "\n```\n")
    except OSError:
        pass          # the summary is a convenience, not the result

sys.exit(1 if total_fail or broken else 0)
