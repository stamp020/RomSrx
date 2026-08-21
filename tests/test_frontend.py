"""Two ways the page and the server quietly stop agreeing.

**Preferences.** The page saves a setting by POSTing it to /api/prefs, and the
server keeps an allow-list - anything not in state.DEFAULT_PREFS is dropped.
That is the right shape for a public endpoint and a miserable failure to
diagnose: the switch works all session, and is back where it started after a
restart, with nothing logged anywhere. It has happened twice. So every key the
page writes is checked against the list here, where the answer costs nothing.

**Using a `const` before the line that declares it.** JavaScript hoists a
`function` and does not hoist a `const`, so a top-level line that calls one
declared further down the file throws at load - and everything after it in
that file never runs. The app comes up with the header still saying "loading
index…" and no button doing anything, which reads as the whole app being
broken rather than as one line in the wrong place. `node --check` cannot see
it: it is not a syntax error, it is a perfectly well-formed program that
happens to be wrong.

**Characters that should not be in a source file.** A stray U+0081 sat in
style.css for a whole release, drawn as an empty box beside the achievement
count, because a control character is invisible in an editor and nothing reads
CSS looking for one. U+FFFD is the same story from the other end - it is what a
character looks like after an encoding went wrong, so finding one means a
string has already been damaged. Neither has any business in this codebase.

Nothing here runs the app or touches the network.
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import state  # noqa: E402

WEB = ROOT / "web"
# Found rather than listed, so a new script is covered the day it appears.
SCRIPTS = sorted(p.name for p in WEB.glob("*.js"))

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def report(label, bad, note):
    global ok, fail  # noqa: PLW0603
    if not bad:
        ok += 1
        print(f"  pass  {label}")
        return
    fail += 1
    print(f"  FAIL  {label}\n          {note}")
    for line in sorted(bad)[:30]:
        print(f"            {line}")
    if len(bad) > 30:
        print(f"            …and {len(bad) - 30} more")


# -- what the page saves ----------------------------------------------------

def object_at(src: str, at: int):
    """The text inside the {...} starting at `at`, brackets balanced and
    strings respected. A regex cannot do this: the objects hold ternaries with
    braces and strings holding braces of their own."""
    depth, i, start = 0, at, at + 1
    while i < len(src):
        ch = src[i]
        if ch in "\"'`":
            quote, i = ch, i + 1
            while i < len(src) and src[i] != quote:
                i += 2 if src[i] == "\\" else 1
            i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return src[start:i], i
        i += 1
    return "", i


def top_level_keys(body: str) -> set[str]:
    """The names on the left of a colon, at the top level of one object.

    Walked a character at a time rather than matched, because everything
    simpler gets this wrong. `{ webTarget: x === "browser" ? "browser" : "app" }`
    has three colons and one key, and a pattern looking for `"word":` happily
    reports "browser" as a preference that the server is throwing away.

    So a name only counts where a key could actually start - at the beginning,
    or after a comma - and only at depth zero, since the keys of a nested
    object are values rather than preference names.
    """
    keys: set[str] = set()
    depth, i, may_start = 0, 0, True

    def after(j):
        while j < len(body) and body[j] in " \t\r\n":
            j += 1
        return j

    while i < len(body):
        ch = body[i]
        if ch in "\"'`":
            quote, j = ch, i + 1
            while j < len(body) and body[j] != quote:
                j += 2 if body[j] == "\\" else 1
            text, j = body[i + 1:j], j + 1
            if may_start and depth == 0 and body[after(j):after(j) + 1] == ":":
                keys.add(text)
            i, may_start = j, False
            continue
        if ch in "{[(":
            depth, i, may_start = depth + 1, i + 1, True
            continue
        if ch in "}])":
            depth, i, may_start = depth - 1, i + 1, False
            continue
        if ch == ",":
            i, may_start = i + 1, depth == 0
            continue
        if ch in " \t\r\n":
            i += 1
            continue
        word = re.match(r"[A-Za-z_$][\w$]*", body[i:])
        if word:
            j = i + len(word.group(0))
            if may_start and depth == 0 and body[after(j):after(j) + 1] == ":":
                keys.add(word.group(0))
            i, may_start = j, False
            continue
        i, may_start = i + 1, False
    return keys


def written_keys(src: str):
    """Preference names the page writes, and a count of the ones it works out
    at run time - which no reading of the source can check."""
    fixed, computed = set(), 0
    for m in re.finditer(r"\bsavePrefs?\(\s*(?=\{)", src):
        body, _ = object_at(src, m.end())
        fixed |= top_level_keys(body)
        computed += len(re.findall(r"\[\s*\w+\s*\]\s*:", body))
    return fixed, computed


def strip_noise(src: str) -> str:
    """The file with strings, template literals, comments and regexes blanked.

    Blanked rather than removed, so every line number and every brace outside
    them stays exactly where it was.

    Two things made the first attempts at this useless, and both are worth
    naming because both made the check pass everything instead of failing.

    Regexes carry unbalanced brackets - `/[^)]/` is one - and a few dozen of
    those leave the brace count permanently adrift. A slash starts a regex
    when the last significant character was an operator or an opening bracket
    rather than a value, which is the usual rule and enough for this file.

    Template literals nest. `${rows.map((r) => `<td>${r}</td>`)}` is routine
    here, and a scanner that stops at the next backtick loses its place for
    everything after it. So the state is a stack: inside a template it is text
    until `${`, and inside that it is code again - which may hold another
    template - until the brace that matches.
    """
    out = list(src)
    i, n = 0, len(src)
    prev = ""                       # last significant character in code
    # ["tpl", 0] is template text; ["expr", depth] is the code inside a
    # ${...}, with depth counting its own nested braces.
    stack: list[list] = []

    def blank(at, upto):
        for k in range(at, min(upto, n)):
            if src[k] != "\n":
                out[k] = " "

    while i < n:
        ch = src[i]

        if stack and stack[-1][0] == "tpl":
            if ch == "\\":
                blank(i, i + 2)
                i += 2
                continue
            if src[i:i + 2] == "${":
                blank(i, i + 2)
                stack.append(["expr", 0])
                i += 2
                prev = ""
                continue
            if ch == "`":
                blank(i, i + 1)
                stack.pop()
                i += 1
                prev = "x"
                continue
            if ch != "\n":
                out[i] = " "
            i += 1
            continue

        # Code: the file itself, or the inside of a ${...}.
        if stack and stack[-1][0] == "expr" and ch in "{}":
            if ch == "{":
                stack[-1][1] += 1
            elif stack[-1][1] == 0:
                blank(i, i + 1)     # the } that closes the ${
                stack.pop()
                i += 1
                prev = "x"
                continue
            else:
                stack[-1][1] -= 1

        if src[i:i + 2] == "//":
            j = src.find("\n", i)
            blank(i, n if j < 0 else j)
            i = n if j < 0 else j
            continue
        if src[i:i + 2] == "/*":
            j = src.find("*/", i)
            j = n if j < 0 else j + 2
            blank(i, j)
            i = j
            continue

        if ch == "/" and prev in "=(,:[!&|?{};+-*%~^<>":
            j, in_class, closed = i + 1, False, False
            while j < n:
                c = src[j]
                if c == "\\":
                    j += 2
                    continue
                if c == "\n":
                    break           # a regex does not span lines
                if c == "[":
                    in_class = True
                elif c == "]":
                    in_class = False
                elif c == "/" and not in_class:
                    closed = True
                    break
                j += 1
            if closed:
                blank(i, j + 1)
                i = j + 1
                prev = "x"
                continue
            # Not a regex after all: fall through and treat it as division.

        if ch == "`":
            blank(i, i + 1)
            stack.append(["tpl", 0])
            i += 1
            continue

        if ch in "\"'":
            quote, j = ch, i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == quote or src[j] == "\n":
                    break
                j += 1
            blank(i, j + 1)
            i = j + 1
            prev = "x"
            continue

        if not ch.isspace():
            prev = ch
        i += 1
    return "".join(out)


def late_const_uses(src: str) -> list[str]:
    """Top-level code that calls a `const` declared further down.

    Deliberately narrow: only a call, only at the top level, and only of a
    name this file declares later with const or let. A function declaration
    hoists and is fine; a name used inside a function body is fine, because
    that body does not run at load. Anything cleverer than this starts
    reporting things that work.

    Nesting is counted in braces alone. Parentheses would be more precise and
    are not worth it: a call whose arguments run over several lines is still
    one top-level statement, and every line of it is code that runs now.
    """
    clean = strip_noise(src)
    lines = clean.splitlines()

    declared: dict[str, int] = {}
    depth = 0
    for at, line in enumerate(lines, 1):
        m = re.match(r"(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=", line)
        if depth == 0 and m:
            declared.setdefault(m.group(1), at)
        depth = max(0, depth + line.count("{") - line.count("}"))

    bad, depth = [], 0
    for at, line in enumerate(lines, 1):
        if depth == 0:
            for m in re.finditer(r"(?:^|=\s*)([A-Za-z_$][\w$]*)\s*\(", line):
                name = m.group(1)
                first = declared.get(name)
                if first and first > at:
                    bad.append(f"line {at} calls {name}(), "
                               f"which is declared on line {first}")
        depth = max(0, depth + line.count("{") - line.count("}"))
    return bad


def main():
    allowed = set(state.DEFAULT_PREFS)

    print("what the page saves, and what the server keeps")
    written, computed = set(), 0
    for name in SCRIPTS:
        got, n = written_keys((WEB / name).read_text(encoding="utf-8"))
        written |= got
        computed += n

    dropped = sorted(k for k in written if k not in allowed)
    report("every preference the page writes is one the server keeps", dropped,
           "these are POSTed to /api/prefs and dropped on the floor:")

    read = set()
    for name in SCRIPTS:
        read.update(re.findall(r"\bprefs\.([A-Za-z_]\w*)",
                               (WEB / name).read_text(encoding="utf-8")))
    unknown = sorted(k for k in read if k not in allowed)
    report("...and every preference it reads is one the server sends", unknown,
           "read from prefs, but never sent, so always undefined:")

    check("the page does save something", len(written) > 20, True)
    # Not a failure - a computed key cannot be checked from the source, and
    # saying how many there are is the honest version of "all of them".
    print(f"  note  {computed} key(s) worked out at run time, not checkable here")

    print("\nusing something before the line that declares it")
    early = []
    for name in SCRIPTS:
        for note in late_const_uses((WEB / name).read_text(encoding="utf-8")):
            early.append(f"{name}: {note}")
    report("no top-level call runs before its const exists", early,
           "these throw at load, and everything after them in the file "
           "never runs:")

    print("\ncharacters that should not be in a source file")
    files = (sorted(p for p in WEB.iterdir() if p.suffix in (".js", ".html", ".css"))
             + sorted((ROOT / "romsrx").glob("*.py")))
    control, replacement, nul, bom = [], [], [], []
    for path in files:
        # utf-8-sig so a byte-order mark is reported below rather than read as
        # part of the first line - which is how one sat at the top of a source
        # file long enough for ast.parse to be the thing that found it.
        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            bom.append(path.relative_to(ROOT).as_posix())
        text = path.read_text(encoding="utf-8-sig")
        for n, line in enumerate(text.splitlines(), 1):
            where = f"{path.relative_to(ROOT).as_posix()}:{n}"
            if any(0x80 <= ord(c) <= 0x9F for c in line):
                control.append(f"{where}  {line.strip()[:70]!r}")
            if "�" in line:
                replacement.append(f"{where}  {line.strip()[:70]!r}")
            if "\0" in line:
                nul.append(f"{where}  {line.strip()[:70]!r}")

    report("no C1 control characters", control,
           "invisible in an editor, drawn as an empty box on screen:")
    report("no U+FFFD", replacement,
           "the mark of a string that has already been through a bad decode:")
    report("no raw NUL bytes", nul,
           "write \\u0000 instead - a typed one is invisible and travels badly:")
    report("no byte-order marks", bom,
           "nothing here is UTF-16, and a BOM is a syntax error to some readers:")

    print(f"\n{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)


main()
