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
          "test_discs.py", "test_times.py"]

total_ok = total_fail = 0
broken: list[str] = []

for name in SUITES:
    print(f"\n=== {name} " + "=" * (58 - len(name)))
    result = subprocess.run([sys.executable, str(HERE / name)],
                            capture_output=True, text=True, encoding="utf-8")
    output = (result.stdout or "") + (result.stderr or "")
    print(output.rstrip())

    tally = re.search(r"(\d+) passed, (\d+) failed", output)
    if not tally:
        broken.append(f"{name} did not finish")
        continue
    total_ok += int(tally.group(1))
    total_fail += int(tally.group(2))
    if result.returncode != 0:
        broken.append(f"{name} exited with {result.returncode}")

print("\n" + "=" * 64)
print(f"{total_ok} passed, {total_fail} failed, across {len(SUITES)} suites")
for note in broken:
    print(f"  !! {note}")

sys.exit(1 if total_fail or broken else 0)
