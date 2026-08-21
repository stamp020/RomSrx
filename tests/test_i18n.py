"""Every word the interface shows, and whether Portuguese can answer it.

The failure this exists to prevent is silent and slow. A translated app does
not break when somebody adds a button - it just shows that one button in
English, and nobody notices until a Portuguese reader hovers it. Over a few
features the interface drifts back into English one string at a time, and
finding them again means clicking through every window in the app.

So the strings are counted here instead. Text reaches the screen four ways
and all four are checked:

  * markup text and title/aria-label/placeholder/label attributes, which are
    translated by applyLanguage - and only on elements carrying data-i18n, so
    a missing marker is as bad as a missing translation;
  * data-tip, the info bubbles, which showInfoTip translates when the bubble
    opens whether or not the element is marked;
  * t("...") in the scripts, including the ones written as several literals
    joined with +, which JavaScript folds into one key before the call; and
  * frField(label, tip, ...), whose two arguments are deliberately left in
    English in the source and translated where they are used.

Brand names and bare domains are exempt: "RomSrx" is "RomSrx" everywhere.

Nothing here runs the app or touches the network - it reads the four files
the interface is made of.
"""
import io
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = ROOT / "web"

# Found rather than listed. A hardcoded list is a list somebody has to
# remember to add to, and the first thing that happened after this suite was
# written was a new script file that it silently did not read.
HTML = sorted(p.name for p in WEB.glob("*.html"))
JS = sorted(p.name for p in WEB.glob("*.js"))

# Attributes applyLanguage rewrites. data-tip is not among them - it is looked
# up when the bubble opens - so it is collected separately below.
ATTRS = ("title", "aria-label", "placeholder", "label")

# Tags with no words of their own, or whose words are not prose.
SKIP_TAGS = {"script", "style", "svg", "path", "circle", "rect", "line",
             "polyline", "polygon", "g", "defs", "use", "head", "meta",
             "link", "br", "hr"}

# The same in every language.
BRANDS = {"RomSrx", "RetroAchievements"}

# Text the page replaces before anybody reads it, so marking it would only
# cache a key that is never shown. Each is written by JavaScript on the first
# paint - see loadStats, askName, askPick and pollIndex.
PLACEHOLDERS = {"loading index…", "starting…", "New playlist", "Which patch?"}

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def report(label, missing, note):
    """Pass or fail on a list, naming what is on it.

    The names matter more than the count: "3 strings have no translation" is
    a puzzle, and printing them is the answer.
    """
    global ok, fail  # noqa: PLW0603
    if not missing:
        ok += 1
        print(f"  pass  {label}")
        return
    fail += 1
    print(f"  FAIL  {label}\n          {note}")
    for text in sorted(missing)[:40]:
        print(f"            {text!r}")
    if len(missing) > 40:
        print(f"            …and {len(missing) - 40} more")


# -- the table -------------------------------------------------------------

def pt_table() -> set[str]:
    """The English keys of the Portuguese table, as JavaScript wrote them."""
    src = (WEB / "i18n.js").read_text(encoding="utf-8")
    body = src[src.index("const PT = {"):src.index("\n};")]
    return {json.loads('"%s"' % m.group(1))
            for m in re.finditer(r'"((?:[^"\\]|\\.)*)"\s*:', body)}


# -- the markup ------------------------------------------------------------

class Markup(HTMLParser):
    """Every string an element shows, and whether it is marked for
    translation. Text belongs to the tag it sits directly inside, which is
    the same rule translateElement follows."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.found: list[tuple[str, str, bool]] = []   # kind, text, marked

    def handle_starttag(self, tag, attrs):
        got = dict(attrs)
        marked = "data-i18n" in got
        if tag not in SKIP_TAGS:
            for attr in ATTRS:
                if got.get(attr, "").strip():
                    self.found.append((attr, " ".join(got[attr].split()), marked))
            if got.get("data-tip", "").strip():
                # Translated at the moment the bubble opens, so the marker on
                # the element has nothing to do with it.
                self.found.append(("data-tip",
                                   " ".join(got["data-tip"].split()), True))
        if tag not in ("br", "hr", "img", "input", "meta", "link"):
            self.stack.append((tag, marked))

    def handle_endtag(self, tag):
        while self.stack:
            if self.stack.pop()[0] == tag:
                break

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text or not self.stack:
            return
        tag, marked = self.stack[-1]
        # Two letters in a row, so "&times;", "3" and "&#9650;" are not prose.
        if tag in SKIP_TAGS or not re.search(r"[A-Za-z]{2}", text):
            return
        self.found.append(("text", text, marked))


def markup_strings():
    out = []
    for name in HTML:
        scan = Markup()
        scan.feed((WEB / name).read_text(encoding="utf-8"))
        out.extend((name, *row) for row in scan.found)
    return out


# -- the scripts -----------------------------------------------------------

def read_literal(src: str, at: int):
    """The string literal starting at `at`, and where it ends.

    Returns None for a template literal holding ${...}: that is a sentence
    built at run time, and its fixed halves are not keys.
    """
    quote = src[at]
    if quote not in "\"'`":
        return None, at
    out, i = [], at + 1
    escapes = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\",
               '"': '"', "'": "'", "`": "`", "0": "\0"}
    while i < len(src):
        ch = src[i]
        if ch == "\\":
            out.append(escapes.get(src[i + 1], src[i + 1]))
            i += 2
            continue
        if ch == quote:
            return "".join(out), i + 1
        if quote == "`" and src.startswith("${", i):
            return None, at
        out.append(ch)
        i += 1
    return None, at


def t_keys(src: str):
    """Every t(...) whose first argument is fixed text.

    `t("one " + "two")` is one key, because JavaScript folds the concatenation
    before the call. An extractor that stopped at the first closing quote
    would report a key that does not exist and miss the one that does - which
    is exactly how a long sentence stays untranslated while looking handled.
    """
    found = []
    for m in re.finditer(r"(?<![A-Za-z0-9_$.])t\(\s*", src):
        i, parts = m.end(), []
        while True:
            text, end = read_literal(src, i)
            if text is None:
                parts = None
                break
            parts.append(text)
            j = end
            while j < len(src) and src[j] in " \t\r\n":
                j += 1
            if j < len(src) and src[j] == "+":
                j += 1
                while j < len(src) and src[j] in " \t\r\n":
                    j += 1
                i = j
                continue
            break
        if parts:
            found.append("".join(parts))
    return found


def script_strings():
    """Keys the scripts ask for, however they ask."""
    out = set()
    for name in JS:
        src = (WEB / name).read_text(encoding="utf-8")
        out.update(t_keys(src))
        # frField's label and tip: English in the source on purpose, so that
        # applyLanguage and showInfoTip can translate them where they land.
        for m in re.finditer(r'frField\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*\n?\s*'
                             r'"((?:[^"\\]|\\.)*)"', src):
            out.add(json.loads('"%s"' % m.group(1)))
            out.add(json.loads('"%s"' % m.group(2)))
        # Info bubbles written into markup the scripts build.
        for m in re.finditer(r'data-tip="([^"$]{4,})"', src):
            out.add(" ".join(m.group(1).split()))
    return out


# -- what a string has to be before it needs translating --------------------

def worth_translating(text: str) -> bool:
    if text in BRANDS or text in PLACEHOLDERS:
        return False
    # A bare domain or URL is not English.
    if re.fullmatch(r"[\w.-]+\.(com|org|tv|net|io|gg)(/\S*)?", text):
        return False
    return True


def main():
    have = pt_table()
    rows = markup_strings()

    print("the markup")
    unmarked = {text for _, kind, text, marked in rows
                if not marked and kind != "data-tip" and worth_translating(text)}
    report("every string in the markup is marked for translation", unmarked,
           "these carry no data-i18n, so applyLanguage never sees them:")

    untranslated = {text for _, _, text, marked in rows
                    if marked and worth_translating(text) and text not in have}
    report("...and every marked string has a Portuguese entry", untranslated,
           "marked up, but nothing in the PT table answers to them:")

    # A key with a newline in it can never match: translateElement collapses
    # runs of whitespace, and a wrapped attribute keeps its line break.
    wrapped = {text for _, kind, text, _ in rows
               if kind in ATTRS and "\n" in text}
    report("...and no attribute is wrapped across lines", wrapped,
           "the newline goes into the lookup key and nothing can match it:")

    print("\nthe scripts")
    asked = script_strings()
    missing = {text for text in asked if worth_translating(text) and text not in have}
    report("everything the scripts ask t() for has an entry", missing,
           "asked for at run time, with no PT entry:")

    print("\nthe table itself")
    # A placeholder is filled from `vars`, so one that appears on only one
    # side of a pair is a translation that will show a literal "{n}".
    holes = []
    src = (WEB / "i18n.js").read_text(encoding="utf-8")
    body = src[src.index("const PT = {"):src.index("\n};")]
    pairs = re.finditer(r'"((?:[^"\\]|\\.)*)"\s*:\s*\n?\s*"((?:[^"\\]|\\.)*)"', body)
    for m in pairs:
        key, value = (json.loads('"%s"' % g) for g in m.groups())
        if set(re.findall(r"\{(\w+)\}", key)) != set(re.findall(r"\{(\w+)\}", value)):
            holes.append(f"{key!r} -> {value!r}")
    report("every translation fills the same placeholders as its original",
           holes, "one side names a {placeholder} the other does not:")

    check("the table is not empty", len(have) > 500, True)

    print(f"\n{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)


main()
