/* ---------- the keyboard ----------

   This app could already be driven end to end with a controller - the stick
   moves focus, A presses what it lands on, and there is an on-screen keyboard
   for typing. It could not be driven with a keyboard at all. Nine key
   handlers between them, every global one doing nothing but Escape.

   Which is the wrong way round. The thing somebody does forty times an
   evening here is type a game's name, at a desk, with both hands already on
   the keys, and reaching for the mouse to put the cursor back in the search
   box is the smallest possible annoyance repeated the largest number of
   times.

   Nothing here reimplements navigation. The arrows move the browser's own
   focus between elements that were already focusable - which the controller
   work proved every control in this app is - so anything added later is
   reachable without being told about it, exactly as the pad is.

   Loaded after app.js, like gamepad.js: top-level `const`/`let` in a classic
   script share one global scope, so `els`, `showLibrary` and friends are all
   in hand.

   Two rules keep it out of the way, and both matter more than any shortcut:
   a key pressed while typing is text, and a key pressed while a dialog is up
   belongs to the dialog. */

const KEY_SHEET_ID = "keysheet";

/** Is the keystroke going into a field? Then it is not a shortcut.
 *
 *  `isContentEditable` is in here for the search box's own kind and for
 *  anything a future panel adds; `closest` rather than a tag check because
 *  the target of a keypress inside a field can be a node within it. */
function typingInto(target) {
  const el = target instanceof Element ? target : null;
  if (!el) return false;
  if (el.closest("input, textarea, select, [contenteditable='']," +
                 " [contenteditable='true']")) return true;
  return false;
}

/** The dialog currently in front, if any. */
const openDialog = () => document.querySelector("dialog[open]");

/* ---------- moving through what is on screen ---------- */

/** The rows the arrows walk, in the order they are drawn.
 *
 *  Whichever half of the app is showing: the cards in a search, or the games
 *  on the shelf. Both are lists of one thing, which is why one pair of arrow
 *  keys can serve them - and why this asks the page what is on it rather than
 *  keeping a list of its own that could go stale behind a re-render. */
function walkable() {
  if (libraryOpen) {
    return [...els.libBody.querySelectorAll(
      ".libcard, .librow, [data-path], [data-key]")]
      .filter((el) => el.offsetParent !== null);
  }
  return [...els.results.querySelectorAll(".game > summary")]
    .filter((el) => el.offsetParent !== null);
}

/** Move the focus one step, and bring it into view.
 *
 *  From nothing, both directions start at the top: pressing Down on a fresh
 *  page means "start here", and so does pressing Up, because there is nothing
 *  above the first row to be at. */
function step(by) {
  const rows = walkable();
  if (!rows.length) return false;
  const at = rows.indexOf(document.activeElement?.closest?.(
    ".libcard, .librow, [data-path], [data-key], summary") ?? null);
  const next = at < 0 ? 0 : Math.min(rows.length - 1, Math.max(0, at + by));
  const row = rows[next];
  if (!row) return false;
  // Focusable whether or not the markup thought to say so: a library tile is
  // a div, and the arrows have to be able to land on it.
  if (!row.hasAttribute("tabindex") && row.tagName !== "SUMMARY") {
    row.tabIndex = -1;
  }
  row.focus({ preventScroll: true });
  row.scrollIntoView({ block: "nearest", behavior: "smooth" });
  return true;
}

/** The card the arrows are on, whichever half of the app is showing. */
const focusedRow = () => document.activeElement?.closest?.(
  ".game, .libcard, .librow, [data-path], [data-key]") || null;

/* ---------- the sheet ---------- */

/** Every shortcut, from one list so the sheet cannot fall out of step with
 *  what the keys actually do.
 *
 *  A function rather than a constant, and each label written as a literal
 *  inside t(), for two reasons that turn out to be the same reason: the sheet
 *  has to be in whatever language is current when it opens rather than
 *  whichever was set when the file loaded, and a string handed to t() through
 *  a variable is invisible to the check that every visible string has a
 *  translation. Written out, it is caught the day it is added. */
const shortcuts = () => [
  ["/", t("Jump to the search box")],
  ["Ctrl K", t("Jump to the search box")],
  ["Esc", t("Clear the search, or close what is open")],
  ["↑ ↓", t("Move through the results")],
  ["Enter", t("Open the one you are on")],
  ["Ctrl D", t("Add it to the download list")],
  ["S", t("Search")],
  ["L", t("Library")],
  ["D", t("Downloads")],
  ["C", t("Download list")],
  ["?", t("This list")],
];

function keySheet() {
  let sheet = document.getElementById(KEY_SHEET_ID);
  if (sheet) return sheet;
  sheet = document.createElement("dialog");
  sheet.id = KEY_SHEET_ID;
  sheet.className = "keysheet";
  document.body.append(sheet);
  // Clicking the backdrop closes it, the same way every other panel here
  // behaves - the check is that the press landed on the dialog itself rather
  // than on anything inside it.
  sheet.addEventListener("click", (ev) => {
    if (ev.target === sheet) sheet.close();
  });
  return sheet;
}

function showKeySheet() {
  const sheet = keySheet();
  if (sheet.open) { sheet.close(); return; }
  sheet.innerHTML = `
    <h2>${esc(t("Keyboard shortcuts"))}</h2>
    <dl class="keylist">
      ${shortcuts().map(([key, what]) => `
        <div class="keyrow">
          <dt>${key.split(" ").map((k) => `<kbd>${esc(k)}</kbd>`).join("")}</dt>
          <dd>${esc(what)}</dd>
        </div>`).join("")}
    </dl>
    <p class="keynote">${esc(t("A key pressed while you are typing is just "
      + "typing — these only work outside a text box."))}</p>`;
  sheet.showModal();
}

/* ---------- the one handler ---------- */

document.addEventListener("keydown", (ev) => {
  if (ev.altKey || ev.metaKey) return;          // somebody else's shortcut

  const dialog = openDialog();
  const typing = typingInto(ev.target);

  // Escape in the search box empties it. The browser does this for a
  // type="search" input on some platforms and not others, and "it depends" is
  // not a behaviour - so it is done here for all of them.
  if (ev.key === "Escape" && ev.target === els.q && els.q.value) {
    ev.preventDefault();
    els.q.value = "";
    els.q.dispatchEvent(new Event("input", { bubbles: true }));
    return;
  }

  // Ctrl+K reaches the search box from anywhere, including out of a field and
  // out from behind a panel, because that is the whole point of it.
  if (ev.key.toLowerCase() === "k" && ev.ctrlKey) {
    ev.preventDefault();
    dialog?.close();
    focusSearch();
    return;
  }

  if (typing || dialog) return;

  switch (ev.key) {
    case "/":
      ev.preventDefault();
      focusSearch();
      return;
    case "?":
      ev.preventDefault();
      showKeySheet();
      return;
    case "ArrowDown":
      if (step(1)) ev.preventDefault();
      return;
    case "ArrowUp":
      if (step(-1)) ev.preventDefault();
      return;
    case "Enter": {
      const row = focusedRow();
      if (!row) return;
      ev.preventDefault();
      // A search card opens; a library tile does whatever clicking it does,
      // which is a setting the reader already chose.
      if (row.matches(".game")) row.open = !row.open;
      else row.click();
      return;
    }
    default:
      break;
  }

  if (ev.ctrlKey) {
    // The top copy of the card you are on. Deliberately the top one: the
    // rows are already in the order this app would have chosen, region
    // preference and all, so "the first one" is "the one it recommends".
    if (ev.key.toLowerCase() === "d") {
      const card = focusedRow()?.closest?.(".game");
      const add = card?.querySelector(".cartadd");
      if (!add) return;
      ev.preventDefault();
      if (!card.open) card.open = true;
      add.click();
    }
    return;
  }

  // Single letters, which are only ever letters when nothing is being typed
  // into - checked above.
  switch (ev.key.toLowerCase()) {
    case "s": ev.preventDefault(); showLibrary(false); break;
    case "l": ev.preventDefault(); showLibrary(true); break;
    case "d": ev.preventDefault(); els.dlBtn.click(); break;
    case "c": ev.preventDefault(); els.cartBtn.click(); break;
    default: break;
  }
});

/** Put the cursor in the search box, leaving the library if that is where we
 *  are. Selected rather than just focused: the usual reason for going back to
 *  the box is to look for something else. */
function focusSearch() {
  if (libraryOpen) showLibrary(false);
  els.q.focus();
  els.q.select();
}
