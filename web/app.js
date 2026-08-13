const $ = (id) => document.getElementById(id);
const els = {
  q: $("q"), qClear: $("qclear"), filters: $("filters"),
  results: $("results"), more: $("more"),
  hint: $("hint"), footer: $("footer"), tagline: $("tagline"),
  reindex: $("reindex"), dlg: $("indexdlg"), log: $("indexlog"),
  indexBar: $("indexbar"), indexCount: $("indexcount"),
  cartBtn: $("cartbtn"), cartCount: $("cartcount"), cartDlg: $("cartdlg"),
  cartItems: $("cartitems"), cartTotal: $("carttotal"), cartHint: $("carthint"),
  cartDl: $("cartdl"), cartCopy: $("cartcopy"), cartSave: $("cartsave"),
  cartClear: $("cartclear"), cartCompact: $("cartcompact"),
  cartConsole: $("cartconsole"), cartSort: $("cartsort"),
  acctBtn: $("acctbtn"), acctDlg: $("acctdlg"), acctForm: $("acctform"),
  acctEmail: $("acctemail"), acctPass: $("acctpass"), acctError: $("accterror"),
  acctSubmit: $("acctsubmit"), acctSigned: $("acctsigned"), acctWho: $("acctwho"),
  acctWhere: $("acctwhere"), acctReason: $("acctreason"),
  dlBtn: $("dlbtn"), dlCount: $("dlcount"), dlDlg: $("dldlg"),
  dlJobs: $("dljobs"), dlSummary: $("dlsummary"), dlClear: $("dlclear"),
  dlFolder: $("dlfolder"), dlWorkers: $("dlworkers"),
  dlSaved: $("dlsaved"), dlBrowse: $("dlbrowse"), dlExtract: $("dlextract"),
  dlExtractMode: $("dlextractmode"),
  dlDelete: $("dldelete"), dlWorkerInfo: $("dlworkerinfo"),
  dlPauseAll: $("dlpauseall"), dlRemoveAll: $("dlremoveall"),
  dlFolders: $("dlfolders"), folderList: $("folderlist"),
  foldersBase: $("foldersbase"), foldersHint: $("foldershint"), perConsole: $("perconsole"),
  foldersSaved: $("folderssaved"), foldersReset: $("foldersreset"),
  libBtn: $("libbtn"), libView: $("libraryview"), libBody: $("libbody"),
  libStats: $("libstats"), libGrid: $("libgrid"), libList: $("liblist"),
  libTitles: $("libtitles"), libSize: $("libsize"), libRefresh: $("librefresh"),
  libTitlesWrap: $("libtitleswrap"), libSizeWrap: $("libsizewrap"),
  libConsole: $("libconsole"), libSelect: $("libselect"), libRemove: $("libremove"),
  libSelectAll: $("libselectall"),
  libSort: $("libsort"),
  searchBtn: $("searchbtn"), homeBtn: $("homebtn"), titleBtn: $("titlebtn"),
  verBtn: $("verbtn"),
  libQ: $("libq"), libQClear: $("libqclear"),
  header: document.querySelector(".topbar"), padHints: $("padhints"),
  libMenu: $("libmenu"), libMenuClear: $("libmenuclear"),
  libMenuSave: $("libmenusave"), libMenuRemoveSel: $("libmenuremovesel"),
  libMenuPlay: $("libmenuplay"), libMenuDelCover: $("libmenudelcover"),
  libMenuGet: $("libmenuget"), libMenuCart: $("libmenucart"),
  libMenuAddTo: $("libmenuaddto"), libMenuRmPl: $("libmenurmpl"),
  libMenuSelect: $("libmenuselect"), libMenuConsole: $("libmenuconsole"),
  libMenuSetCover: $("libmenusetcover"), libMenuOpen: $("libmenuopen"),
  libMenuDelete: $("libmenudelete"),
  coverMenu: $("covermenu"), addMenu: $("addmenu"),
  libShelves: $("libshelves"), libNewPl: $("libnewpl"),
  libPlActions: $("libplactions"), libPlGet: $("libplget"),
  libPlCart: $("libplcart"), libPlRename: $("libplrename"),
  libPlDelete: $("libpldelete"),
  libAddPl: $("libaddpl"), libPlRemove: $("libplremove"),
  nameDlg: $("namedlg"), nameForm: $("nameform"), nameInput: $("nameinput"),
  nameTitle: $("nametitle"), nameOk: $("nameok"), nameCancel: $("namecancel"),
  searchbar: document.querySelector(".searchbar"),
  searchStick: $("searchstick"), homeCards: $("homecards"),
  cartSelAll: $("cartselall"), cartDlSel: $("cartdlsel"), cartRmSel: $("cartrmsel"),
  cartClrDone: $("cartclrdone"),
  settingsBtn: $("settingsbtn"), settingsDlg: $("settingsdlg"),
  setTabs: $("settabs"),
  libSettings: $("libsettings"), cartSettings: $("cartsettings"),
  toneRow: $("tonerow"), accentRow: $("accentrow"), langRow: $("langrow"),
  askDlg: $("askdlg"), askBody: $("askbody"), askOk: $("askok"),
  askCancel: $("askcancel"),
  updateBar: $("updatebar"), upMsg: $("upmsg"), upGet: $("upget"),
  upNotes: $("upnotes"), upLater: $("uplater"),
  upDlg: $("updlg"), upWhat: $("upwhat"), upDlgGet: $("updlgget"),
  upDlgNotes: $("updlgnotes"), upDlgLater: $("updlglater"),
  foldersDetect: $("foldersdetect"), notifyDone: $("notifydone"),
  dlMute: $("dlmute"),
  consBtn: $("consbtn"), consMenu: $("consmenu"),
  consSearch: $("conssearch"), consItems: $("consitems"),
  backupSave: $("backupsave"), backupLoad: $("backupload"),
};

/* Anything that has to appear over an open dialog has to be a popover.
   A modal <dialog> paints in the top layer, where no amount of z-index can
   reach it - an ordinary element positioned on top of one is drawn behind it
   and is simply not there as far as the user is concerned. Popovers join the
   same layer, and are positioned against the viewport rather than against any
   transformed ancestor. */
const CAN_POPOVER = typeof HTMLElement.prototype.showPopover === "function";

/** Promote an element to the top layer. The `hidden` attribute has to go:
 *  our own `[hidden]` rule is `!important`, so it would outlast the popover
 *  being opened and keep the thing invisible. */
function asPopover(el) {
  if (!CAN_POPOVER) return el;
  el.popover = "manual";
  el.hidden = false;      // `:popover-open` decides visibility from here on
  return el;
}

const isShown = (el) => CAN_POPOVER ? el.matches(":popover-open") : !el.hidden;

function showTop(el) {
  if (!CAN_POPOVER) { el.hidden = false; return; }
  if (!el.matches(":popover-open")) el.showPopover();
}

function hideTop(el) {
  if (!CAN_POPOVER) { el.hidden = true; return; }
  if (el.matches(":popover-open")) el.hidePopover();
}

/* The browser's own confirm() and alert() label themselves with the address
   of the local server - "127.0.0.1:52012 says" - which is both meaningless
   and alarming. These are the same thing wearing the app's own clothes. */
let askSettle = null;

function askClose(answer) {
  const settle = askSettle;
  askSettle = null;
  if (els.askDlg.open) els.askDlg.close();
  if (settle) settle(answer);
}

/** Resolves true if they went ahead, false if they backed out.
 *
 *  `notes` widens the box. A question is one line and reads best narrow; a
 *  release note is several paragraphs, and at question width it becomes a
 *  column of five-word lines you have to scroll through. */
function ask(message, { confirm = false, danger = false, ok = "OK",
                        notes = false } = {}) {
  askClose(false);                 // never leave an earlier question hanging
  els.askBody.textContent = message;
  els.askCancel.hidden = !confirm;
  els.askOk.textContent = ok;
  els.askOk.classList.toggle("danger", danger);
  els.askDlg.classList.toggle("notes", notes);
  els.askDlg.showModal();
  /* Focused without scrolling, then wound back to the top. The button sits
     below the message, so focusing it normally scrolls it into view - which
     nobody notices on a one-line question, but opens a long set of release
     notes at the very end of them. */
  els.askOk.focus({ preventScroll: true });
  els.askDlg.scrollTop = 0;
  return new Promise((resolve) => { askSettle = resolve; });
}

/** Just tells them something; there is nothing to decide. Options are passed
 *  along - `notes` is the one that matters here, for a box of prose. */
const say = (message, options) => ask(message, options);

/* The same box with somewhere to type, for naming a playlist. Resolves to the
   trimmed text, or null if they backed out - so an empty name and a cancel
   are the same answer, which is the only reading that doesn't create a list
   called nothing. */
let nameSettle = null;

function nameClose(answer) {
  const settle = nameSettle;
  nameSettle = null;
  if (els.nameDlg.open) els.nameDlg.close();
  if (settle) settle(answer);
}

function promptText({ title, value = "", ok = "OK" }) {
  nameClose(null);
  els.nameTitle.textContent = title;
  els.nameInput.value = value;
  els.nameOk.textContent = ok;
  els.nameDlg.showModal();
  els.nameInput.focus();
  els.nameInput.select();
  return new Promise((resolve) => { nameSettle = resolve; });
}

els.nameForm.addEventListener("submit", (ev) => {
  ev.preventDefault();
  nameClose(els.nameInput.value.trim() || null);
});

/* Enter is taken here rather than left to the form's own implicit submission,
   which doesn't fire for every kind of keypress the app can receive - the
   on-screen keyboard's included. Typing a name and pressing Enter has to be
   enough, whatever produced the Enter. */
els.nameInput.addEventListener("keydown", (ev) => {
  if (ev.key !== "Enter") return;
  ev.preventDefault();
  nameClose(els.nameInput.value.trim() || null);
});
els.nameCancel.addEventListener("click", () => nameClose(null));
// Esc and the backdrop both close a <dialog> without going through the form.
els.nameDlg.addEventListener("close", () => nameClose(null));

/* For news that isn't worth stopping for. A cover that saved itself into a
   folder you configured needs confirming - silence looks like nothing
   happened - but not with a box you have to dismiss every single time. */
const toastEl = asPopover(document.createElement("div"));
toastEl.id = "toast";
document.body.append(toastEl);
let toastTimer = null;

function toast(text) {
  toastEl.textContent = text;
  showTop(toastEl);
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => hideTop(toastEl), 3600);
}

/* ---------- info bubbles ----------

   The little "i" beside a setting. The bubble used to be an ::after on the
   icon itself, which put it inside the dialog's scrolling box: any icon near
   an edge - and in a dialog as tall as Settings that is most of them - had
   its bubble clipped by that box and came out half a sentence.

   One bubble, in the top layer, positioned against the viewport instead. It
   goes below the icon where there is room and above it where there isn't, and
   is nudged sideways to stay on screen. */
const infoTip = asPopover(document.createElement("div"));
infoTip.className = "infotip";
if (!CAN_POPOVER) infoTip.hidden = true;
document.body.append(infoTip);

const TIP_GAP = 9;    // between icon and bubble
const TIP_EDGE = 10;  // smallest gap left to the window edge
let tipIcon = null;   // the icon the bubble is currently showing for

function showInfoTip(icon) {
  const text = icon.dataset.tip;
  if (!text) return;
  tipIcon = icon;
  infoTip.textContent = t(text);
  // Shown before measuring: a hidden element has no size to measure.
  showTop(infoTip);

  const at = icon.getBoundingClientRect();
  const box = infoTip.getBoundingClientRect();
  // Right edges aligned, as the old bubble was, then pulled back inside the
  // window if that would hang it off either side.
  let left = at.right - box.width;
  left = Math.min(left, window.innerWidth - box.width - TIP_EDGE);
  left = Math.max(TIP_EDGE, left);

  let top = at.bottom + TIP_GAP;
  if (top + box.height > window.innerHeight - TIP_EDGE) {
    const above = at.top - TIP_GAP - box.height;
    top = above >= TIP_EDGE
      ? above
      : Math.max(TIP_EDGE, window.innerHeight - box.height - TIP_EDGE);
  }

  infoTip.style.left = `${left}px`;
  infoTip.style.top = `${top}px`;
}

function hideInfoTip() {
  if (!tipIcon) return;
  tipIcon = null;
  hideTop(infoTip);
}

const iconAt = (target) =>
  target instanceof Element ? target.closest(".infoicon") : null;

document.addEventListener("pointerover", (ev) => {
  const icon = iconAt(ev.target);
  if (icon) { if (icon !== tipIcon) showInfoTip(icon); }
  else hideInfoTip();
});
// Keyboard and gamepad reach these by focus, never by pointer.
document.addEventListener("focusin", (ev) => {
  const icon = iconAt(ev.target);
  if (icon) showInfoTip(icon); else hideInfoTip();
});
/* Anchored to where the icon was, so it has to go the moment the icon moves.
   Capturing, because the scroll is the dialog's own and doesn't bubble. */
document.addEventListener("scroll", hideInfoTip, true);
window.addEventListener("resize", hideInfoTip);
// A dialog's `close` doesn't bubble, so this one has to be caught on the way
// down - otherwise a bubble outlives the panel it was explaining.
document.addEventListener("close", hideInfoTip, true);
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") hideInfoTip();
});

const PAGE = 40;
const DIMENSIONS = [["console", "Console"], ["region", "Region"], ["ext", "Type"]];

// View preferences, stored server-side so they survive a restart, a different
// port, or reinstalling the app.
const prefs = {
  cartCompact: false, libView: "grid", libTitles: true,
  libSize: 160, libSort: "name", cartSort: "added-desc",
  tone: "default", accent: "blue", lang: "en",
  libPinned: [], libShut: [], libShelf: "",
  cartWide: false, dlWide: false,
  notifyDone: true, muteDone: false,
};

async function loadPrefs() {
  try {
    Object.assign(prefs, await fetch("/api/prefs").then((r) => r.json()));
  } catch { /* defaults are fine */ }
}

function savePrefs(changes) {
  Object.assign(prefs, changes);
  fetch("/api/prefs", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  }).catch(() => { /* a lost preference isn't worth an error */ });
}

/** Store something the user built, and say so if it didn't store.
 *
 *  The line between this and savePrefs above is what the user would lose. A
 *  cover size that goes back to its old value is a shrug; a list they spent
 *  ten minutes assembling is not, and the page is the worst possible witness
 *  to its own failure - it keeps the change in memory either way, so the list
 *  reads back correctly for as long as the window is open and is simply gone
 *  the next time the app starts. Nothing here can put that right on its own,
 *  so the one useful thing is to say it out loud while the window is still
 *  open and the work is still recoverable. */
function saveState(route, body, warning) {
  return fetch(route, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
    .then((res) => { if (!res.ok) throw new Error(String(res.status)); })
    .catch(() => toast(t(warning)));
}

// Box art comes from the libretro thumbnail server - the same one RetroArch
// uses. Nothing is stored locally; the browser fetches each cover directly.
// Its filenames follow No-Intro/Redump naming, which is exactly what our
// indexed filenames already are, so no fuzzy matching is needed.
const THUMB_BASE = "https://thumbnails.libretro.com";
const LIBRETRO = {
  "PlayStation": "Sony - PlayStation",
  "PlayStation 2": "Sony - PlayStation 2",
  "PSP": "Sony - PlayStation Portable",
  "GameCube": "Nintendo - GameCube",
  "Nintendo DS": "Nintendo - Nintendo DS",
  "Nintendo DSi": "Nintendo - Nintendo DSi",
  "Nintendo Wii": "Nintendo - Wii",
  "Nintendo 3DS": "Nintendo - Nintendo 3DS",
  "NES/Famicom": "Nintendo - Nintendo Entertainment System",
  "Famicom Disk System": "Nintendo - Family Computer Disk System",
  "SNES/Super Famicom": "Nintendo - Super Nintendo Entertainment System",
  "Nintendo 64": "Nintendo - Nintendo 64",
  "Game Boy": "Nintendo - Game Boy",
  "Game Boy Color": "Nintendo - Game Boy Color",
  "Game Boy Advance": "Nintendo - Game Boy Advance",
  "Pokemon Mini": "Nintendo - Pokemon Mini",
  "Virtual Boy": "Nintendo - Virtual Boy",
  "Atari 2600": "Atari - 2600",
  "Atari 7800": "Atari - 7800",
  "Atari Jaguar": "Atari - Jaguar",
  "Atari Jaguar CD": "Atari - Jaguar",
  "Atari Lynx": "Atari - Lynx",
  "SG-1000": "Sega - SG-1000",
  "Master System": "Sega - Master System - Mark III",
  "Genesis/Mega Drive": "Sega - Mega Drive - Genesis",
  "Sega CD": "Sega - Mega-CD - Sega CD",
  "32X": "Sega - 32X",
  "Game Gear": "Sega - Game Gear",
  "Sega Saturn": "Sega - Saturn",
  "Sega Dreamcast": "Sega - Dreamcast",
  "PC-8000/8800": "NEC - PC-8001 - PC-8801",
  "PC Engine/TurboGrafx-16": "NEC - PC Engine - TurboGrafx 16",
  "PC Engine CD/TurboGrafx-CD": "NEC - PC Engine CD - TurboGrafx-CD",
  "PC-FX": "NEC - PC-FX",
  "Neo Geo CD": "SNK - Neo Geo CD",
  "Neo Geo Pocket": "SNK - Neo Geo Pocket",
};
// Consoles whose sets mix two thumbnail folders get a second chance.
const LIBRETRO_ALT = {
  "Neo Geo Pocket": "SNK - Neo Geo Pocket Color",
  "PC Engine/TurboGrafx-16": "NEC - PC Engine SuperGrafx",
};
// Each miss is a 404, and a screen of results asks for a lot of them at once,
// so the search is bounded: a few filenames per kind of art, a few kinds.
// With one kind of art there is room to try more of a game's filenames, and
// more simplified forms of each - which is where the real hits come from.
const FILES_PER_KIND = 4;
const NAME_TRIES = 2;          // the filename, plus this many simpler forms
const MAX_COVER_TRIES = 10;
const CONSOLE_PREVIEW = 4; // console badges shown before the "+N" toggle
const SEARCHABLE_AT = 12; // menus longer than this get their own filter box

// Active filter selections. Multiple values within a dimension are OR'd.
const active = { console: new Set(), region: new Set(), ext: new Set() };
const menuQuery = { console: "", region: "", ext: "" };
let raOnly = false;     // show only files from RetroAchievements sets
let lastFacets = null;  // facets from the most recent search
let openDim = null;     // which dropdown is open, if any
let refocusMenu = false;
let offset = 0;
let total = 0;
let seq = 0; // guards against out-of-order responses

const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function humanSize(bytes) {
  if (!bytes) return "";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let n = bytes, i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${i === 0 ? n : n.toFixed(n < 10 ? 2 : 1)} ${units[i]}`;
}

function params(extra = {}) {
  const p = new URLSearchParams();
  const q = els.q.value.trim();
  if (q) p.set("q", q);
  for (const dim of ["console", "region", "ext"]) {
    if (active[dim].size) p.set(dim, [...active[dim]].join(","));
  }
  if (raOnly) p.set("ra", "1");
  p.set("limit", PAGE);
  for (const [k, v] of Object.entries(extra)) p.set(k, v);
  return p;
}

/* ---------- filter chips ---------- */

function menuItem(dim, entry) {
  const on = active[dim].has(entry.value);
  return `<button class="fitem${on ? " on" : ""}" data-act="pick"
    data-dim="${dim}" data-value="${esc(entry.value)}">
    <span class="box">${on ? "&#10003;" : ""}</span>
    <span class="fval">${esc(entry.value)}</span>
    <span class="n">${entry.count.toLocaleString()}</span></button>`;
}

function dropdown(dim, label, items) {
  const chosen = active[dim];
  const needle = menuQuery[dim].toLowerCase();
  const shown = needle
    ? items.filter((i) => i.value.toLowerCase().includes(needle))
    : items;

  // Summarise the selection on the button so the bar stays one line.
  let tail = "";
  if (chosen.size === 1) tail = `<span class="fpick">${esc([...chosen][0])}</span>`;
  else if (chosen.size > 1) tail = `<span class="fnum">${chosen.size}</span>`;

  const searchBox = items.length > SEARCHABLE_AT
    ? `<input class="fsearch" data-dim="${dim}" value="${esc(menuQuery[dim])}"
        placeholder="${esc(t("Filter"))} ${label.toLowerCase()}…" autocomplete="off">`
    : "";

  return `
    <div class="fdrop">
      <button class="fbtn${chosen.size ? " on" : ""}" data-act="open" data-dim="${dim}"
        ${items.length ? "" : "disabled"}>${label}${tail}<span class="fcaret">&#9662;</span></button>
      <div class="fmenu"${openDim === dim ? "" : " hidden"}>
        ${searchBox}
        <div class="fitems">${shown.length
          ? shown.map((i) => menuItem(dim, i)).join("")
          : `<div class="fempty">${esc(t("No matches"))}</div>`}</div>
      </div>
    </div>`;
}

/** RetroAchievements is a property of the source a file came from rather than
 *  of the game, so it isn't one of the dropdown dimensions - it's a toggle of
 *  its own, parked at the far right of the bar. The label stands in for the
 *  logo if the image isn't there. */
function raToggle() {
  return `
    <button class="rafilter${raOnly ? " on" : ""}" data-act="ra"
      aria-pressed="${raOnly}" title="${raOnly
        ? "Showing only RetroAchievements sets — click to show everything"
        : "Show only games from RetroAchievements sets"}">
      <img src="/ra.png" alt="RetroAchievements" onerror="raLogoFail(this)">
      <span class="ralabel">RA</span>
    </button>`;
}

window.raLogoFail = (img) => {
  img.closest(".rafilter")?.classList.add("nologo");
  img.remove();
};

/* ---------- the front page ----------

   Opening on every game in the index, alphabetically, meant opening on a
   scroll bar: forty thousand rows starting at "0-ji no Kane to Cinderella"
   tell you nothing about what is here. A console is the first choice anybody
   actually makes, so that is what the front page offers - with the whole list
   still one click away for people who would rather browse it. */
let browsingAll = false;   // "All consoles" was picked, so show the list

/** Home is the state with nothing chosen: no words typed, no filter set. */
const atHome = () => !browsingAll && !els.q.value.trim() && !raOnly
  && !active.console.size && !active.region.size && !active.ext.size;

const consoleCard = (value, count, label) => `
  <button class="ccard${value ? "" : " ccall"}" data-console="${esc(value)}">
    <span class="ccname">${esc(label ?? value)}</span>
    <span class="ccn">${count.toLocaleString()} ${esc(t(count === 1 ? "game" : "games"))}</span>
  </button>`;

function renderHome() {
  const list = lastFacets?.consoles || [];
  if (!list.length) { els.homeCards.innerHTML = ""; return; }
  // The search's own count, not the sum of the cards: a game released on
  // three consoles is counted by three of them and is still one game.
  const everything = total || list.reduce((n, c) => n + (c.count || 0), 0);
  els.homeCards.innerHTML = `
    <p class="homehint">${esc(t("Pick a console, or search for a game."))}</p>
    <div class="ccgrid">
      ${consoleCard("", everything, t("All consoles"))}
      ${list.map((c) => consoleCard(c.value, c.count || 0)).join("")}
    </div>`;
}

/** Cards or results, never both. Called wherever either could have changed. */
function paintHome() {
  const home = !libraryOpen && atHome();
  els.homeCards.hidden = !home;
  if (home) renderHome();
  els.results.hidden = libraryOpen || home;
  if (home) els.more.hidden = true;
}

els.homeCards.addEventListener("click", (ev) => {
  const card = ev.target.closest(".ccard");
  if (!card) return;
  // The blank one is "All consoles": no filter, just show me everything.
  if (card.dataset.console) active.console.add(card.dataset.console);
  else browsingAll = true;
  search(false);
});

/** Back to the cards: the logo and the app name both mean home. */
function goHome() {
  showLibrary(false);
  browsingAll = false;
  els.q.value = "";
  els.qClear.hidden = true;
  for (const set of Object.values(active)) set.clear();
  raOnly = false;
  openDim = null;
  search(false);
}

function renderFilters(facets) {
  if (facets) lastFacets = facets;
  if (!lastFacets) return;

  const sets = { console: lastFacets.consoles, region: lastFacets.regions,
                 ext: lastFacets.extensions };
  const chosen = [...active.console, ...active.region, ...active.ext].length
    + (raOnly ? 1 : 0);

  els.filters.innerHTML =
    DIMENSIONS.map(([dim, label]) => dropdown(dim, t(label), sets[dim])).join("") +
    (chosen
      ? `<button class="fclear" data-act="clear">&times; ${esc(t("Clear"))}${
          chosen > 1 ? ` (${chosen})` : ""}</button>`
      : "")
    + raToggle();

  // A re-render replaces the DOM, so put the cursor back in the open menu.
  if (refocusMenu && openDim) {
    const input = els.filters.querySelector(`.fsearch[data-dim="${openDim}"]`);
    if (input) {
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);
    }
  }
  refocusMenu = false;
}

els.filters.addEventListener("click", (ev) => {
  const btn = ev.target.closest("button");
  if (!btn) return;
  const { act, dim, value } = btn.dataset;

  if (act === "open") {
    openDim = openDim === dim ? null : dim;
    renderFilters();
  } else if (act === "clear") {
    for (const set of Object.values(active)) set.clear();
    raOnly = false;
    openDim = null;
    browsingAll = false;      // nothing chosen at all is the front page again
    search(false);
  } else if (act === "ra") {
    raOnly = !raOnly;
    openDim = null;
    search(false);
  } else if (act === "pick") {
    // Menu stays open so several values can be picked in one go.
    active[dim].has(value) ? active[dim].delete(value) : active[dim].add(value);
    search(false);
  }
});

els.filters.addEventListener("input", (ev) => {
  const input = ev.target.closest(".fsearch");
  if (!input) return;
  menuQuery[input.dataset.dim] = input.value;
  refocusMenu = true;
  renderFilters();
});

document.addEventListener("click", (ev) => {
  if (openDim && !ev.target.closest(".fdrop")) {
    openDim = null;
    renderFilters();
  }
});

document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape" && openDim) {
    openDim = null;
    renderFilters();
    els.q.focus();
  }
});

/* ---------- results ---------- */

function fileRow(f) {
  const bits = [f.source_name];
  if (f.disc) bits.push(`Disc ${f.disc}`);
  if (f.version) bits.push(f.version);
  if (f.languages.length) bits.push(f.languages.join(", "));
  if (f.tags.length) bits.push(f.tags.join(", "));

  const region = f.regions.length ? f.regions.join(", ") : "—";
  const locked = f.requires_login
    ? ` <span class="lock" title="${esc(t("archive.org serves this item only to signed-in accounts"))}">&#128274; ${esc(t("login"))}</span>`
    : "";
  // Console leads the detail line, tagged like the login marker beside it.
  const tag = `<span class="ctag">${esc(f.console)}</span>`;
  return `
    <div class="file">
      <div class="fname">
        <div>${esc(f.filename)}</div>
        <div class="fsub">${tag}${bits.map(esc).join(" &middot; ")}${locked}</div>
      </div>
      <span class="badge fregion">${esc(region)}</span>
      <span class="ftype">${esc(f.ext)}</span>
      <span class="fsize">${humanSize(f.size)}</span>
      <button class="dl" data-ext="${esc(f.ext || "")}"
        data-url="${esc(f.url)}" data-name="${esc(f.filename)}"
        data-size="${f.size || 0}" data-console="${esc(f.console)}"
        data-source="${esc(f.source_name)}" data-login="${f.requires_login ? 1 : 0}"
        title="${esc(t("Download now"))}">${esc(t("Download"))}</button>
      ${cartButton(f)}
    </div>`;
}

/* ---------- download list ---------- */

// Kept on the server rather than in browser storage: the app picks a free
// port at startup, and browser storage is tied to the exact origin - so a
// different port would silently lose the list. This survives that, plus
// reinstalls, since it lives in the user folder.
const cart = new Map();

function paintCartBadge() {
  els.cartCount.textContent = cart.size;
  els.cartCount.hidden = !cart.size;      // no "0" badge on an empty list
  els.cartBtn.classList.toggle("has", cart.size > 0);
}

async function loadCart() {
  try {
    const { items } = await fetch("/api/cart").then((r) => r.json());
    cart.clear();
    for (const item of items) if (item?.url) cart.set(item.url, item);
  } catch { /* server not up yet - the list stays empty this session */ }
  paintCartBadge();
}

function saveCart() {
  paintCartBadge();
  saveState("/api/cart", { items: [...cart.values()] },
    "Your download list could not be saved — is RomSrx still running? "
    + "Changes made now will be lost when this window is closed.");
}

const cartBytes = () => [...cart.values()].reduce((n, i) => n + (i.size || 0), 0);

/* The row carries everything the list needs, so the cart survives a new
   search without having to look anything up again.

   The + is a menu now rather than a single destination: the download list is
   the first entry in it, so what was one click is still one click and a
   second, and every shelf the user has made is reachable from the same
   place. Its state is painted on afterwards by paintAddButton(). */
function cartButton(f) {
  return `<button class="cartadd" data-url="${esc(f.url)}"
    data-name="${esc(f.filename)}" data-size="${f.size || 0}"
    data-console="${esc(f.console)}" data-source="${esc(f.source_name)}"
    data-ext="${esc(f.ext || "")}" data-login="${f.requires_login ? 1 : 0}"
    aria-haspopup="menu">+</button>`;
}

// "Download" on a result row queues that single file straight away.
els.results.addEventListener("click", async (ev) => {
  const go = ev.target.closest("button.dl");
  if (!go) return;
  ev.preventDefault();
  if (!await allowLoginOnly(go.dataset.login === "1", "That file")) return;
  const label = go.textContent;
  go.disabled = true;
  const added = await queueDownloads([{
    url: go.dataset.url, filename: go.dataset.name,
    size: Number(go.dataset.size) || 0,
    console: go.dataset.console, source: go.dataset.source,
    login: go.dataset.login === "1",
  }]);
  go.textContent = t(added > 0 ? "Queued" : (added === 0 ? "Already queued" : "Failed"));
  setTimeout(() => { go.textContent = label; go.disabled = false; }, 1800);
});

els.results.addEventListener("click", (ev) => {
  const btn = ev.target.closest(".cartadd");
  if (!btn) return;
  ev.preventDefault();
  const entry = entryFromData(btn.dataset);
  entry.art = shownCoverFor(btn);   // the cover you can see right now
  entry.alts = siblingNames(btn, entry.name, entry.console);  // ...and for later
  openAddMenu(ev, [entry]);
});

/** Thumbnail for a saved item. Entries added before the list stored an
 *  extension fall back to whatever follows the final dot. */
function cartCoverHtml(item) {
  const ext = item.ext ?? item.filename.split(".").pop();
  const urls = coverCandidates([{ ...item, ext }]);
  if (!urls.length) return `<span class="ci-art"></span>`;
  return `<span class="ci-art"><img src="${esc(urls[0])}"
    data-rest='${esc(JSON.stringify(urls.slice(1)))}' alt="" loading="lazy"
    decoding="async" onerror="coverFail(this)"></span>`;
}

// Which entries the list is currently showing, in the chosen order. Every
// bulk action works on this view, so "Download all" means "all of what you
// can see" once a console filter is on.
const SORTERS = {
  "added-desc": (a, b) => (b.added || 0) - (a.added || 0),
  "added-asc": (a, b) => (a.added || 0) - (b.added || 0),
  "name-asc": (a, b) =>
    a.filename.localeCompare(b.filename, undefined, { numeric: true }),
  "name-desc": (a, b) =>
    b.filename.localeCompare(a.filename, undefined, { numeric: true }),
  "size-desc": (a, b) => (b.size || 0) - (a.size || 0),
  "size-asc": (a, b) => (a.size || 0) - (b.size || 0),
};

const selected = new Set();

function visibleItems() {
  const wanted = els.cartConsole.value;
  const items = [...cart.values()]
    .filter((i) => !wanted || i.console === wanted);
  return items.sort(SORTERS[els.cartSort.value] || SORTERS["added-desc"]);
}

const selectedItems = () => visibleItems().filter((i) => selected.has(i.url));

function renderConsoleFilter() {
  const counts = new Map();
  for (const i of cart.values()) {
    counts.set(i.console, (counts.get(i.console) || 0) + 1);
  }
  const keep = els.cartConsole.value;
  els.cartConsole.innerHTML =
    `<option value="">${esc(t("All consoles"))} (${cart.size})</option>`
    + [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([name, n]) =>
        `<option value="${esc(name)}">${esc(name)} (${n})</option>`).join("");
  // Keep the choice if that console still has entries.
  els.cartConsole.value = counts.has(keep) ? keep : "";
}

function renderCart() {
  renderConsoleFilter();

  const items = visibleItems();
  for (const url of [...selected]) {          // drop stale selections
    if (!cart.has(url)) selected.delete(url);
  }
  const chosen = items.filter((i) => selected.has(i.url));
  const bytes = items.reduce((n, i) => n + (i.size || 0), 0);

  els.cartTotal.textContent = cart.size
    ? (items.length === cart.size
        ? `${items.length} file${items.length === 1 ? "" : "s"} · ${humanSize(bytes)}`
        : `${items.length} of ${cart.size} files · ${humanSize(bytes)}`)
    : "";

  els.cartItems.innerHTML = items.length
    ? items.map((i) => `
        <div class="cartitem${selected.has(i.url) ? " picked" : ""}">
          <input type="checkbox" class="ci-pick" data-url="${esc(i.url)}"
                 ${selected.has(i.url) ? "checked" : ""} aria-label="Select">
          ${cartCoverHtml(i)}
          <span class="ci-name">${esc(i.filename)}
            <span class="ci-sub"><span class="ctag">${esc(i.console)}</span>${
              esc(i.source)}${
              i.login ? ` <span class="lock">&#128274; ${esc(t("login"))}</span>` : ""}</span>
          </span>
          <span class="ci-size">${humanSize(i.size)}</span>
          <button class="ci-rm" data-url="${esc(i.url)}" title="Remove">&times;</button>
        </div>`).join("")
    : `<p class="empty">${cart.size
        ? t("No entries for this console.")
        : t("Nothing here yet — use the + button on any file.")}</p>`;

  const locked = items.filter((i) => i.login).length;
  els.cartHint.textContent = items.length
    ? (locked
        ? `${locked} of these need an archive.org account — you'll be asked to sign in.`
        : t("Downloads run inside the app, with resume and retry."))
    : "";

  els.cartDl.textContent = items.length
    ? `${t("Download all")} (${items.length})` : t("Download all");
  els.cartDl.disabled = !items.length;
  els.cartCopy.disabled = !items.length;
  els.cartSave.disabled = !items.length;

  els.cartSelAll.disabled = !items.length;
  updateSelectionUI();
}

/** Refresh only what selection affects. Ticking a box must not rebuild the
 *  list, or the scroll position jumps back to the top mid-way down. */
function updateSelectionUI() {
  const items = visibleItems();
  const chosen = items.filter((i) => selected.has(i.url)).length;

  for (const row of els.cartItems.querySelectorAll(".cartitem")) {
    const box = row.querySelector(".ci-pick");
    if (box) row.classList.toggle("picked", selected.has(box.dataset.url));
  }

  // Selection-only actions appear once something is ticked.
  els.cartDlSel.hidden = !chosen;
  els.cartRmSel.hidden = !chosen;
  els.cartDlSel.textContent = `${t("Download selected")} (${chosen})`;
  els.cartRmSel.textContent = `${t("Remove selected")} (${chosen})`;

  els.cartSelAll.checked = items.length > 0 && chosen === items.length;
  els.cartSelAll.indeterminate = chosen > 0 && chosen < items.length;
}

els.cartItems.addEventListener("click", (ev) => {
  const rm = ev.target.closest(".ci-rm");
  if (!rm) return;
  cart.delete(rm.dataset.url);
  selected.delete(rm.dataset.url);
  saveCart();
  renderCart();
  paintAddButtons();
});

function applyCompact(on) {
  if (!on) hideZoom();     // full-size tiles have nothing to enlarge
  els.cartItems.classList.toggle("compact", on);
  els.cartCompact.classList.toggle("on", on);
  els.cartCompact.title = on
    ? "Back to full-size covers"
    : "Show more entries at once";
}

els.cartCompact.addEventListener("click", () => {
  const on = !els.cartItems.classList.contains("compact");
  applyCompact(on);
  savePrefs({ cartCompact: on });
});

/* Hover preview, compact mode only - that's where the tiles get too small to
   read. It's a popover for the reason described up top; putting it inside the
   dialog doesn't work either, because the dialog is centred with a transform,
   which makes it the containing block for anything `fixed` within it and
   clips whatever reaches past its edge. */
const ZOOM = { max: 220, min: 120, ratio: 292 / 220, gap: 12, edge: 8 };

const zoom = asPopover(document.createElement("div"));
zoom.id = "coverzoom";
zoom.innerHTML = `<img alt="">`;
document.body.append(zoom);

function showZoom(tile) {
  if (!CAN_POPOVER || !els.cartItems.classList.contains("compact")) return;
  const img = tile.querySelector("img");
  if (!img || !img.currentSrc) return;   // nothing to enlarge

  zoom.querySelector("img").src = img.currentSrc;
  showTop(zoom);

  const panel = els.cartDlg.getBoundingClientRect();
  const row = tile.getBoundingClientRect();

  // Always parked in the gutter to the left of the list, so it turns up in
  // the same place every time. A window too narrow for the full-size preview
  // shrinks it rather than flipping it to the other side; below the minimum
  // it overlaps the list edge instead, which the top layer lets it do.
  const gutter = panel.left - ZOOM.gap - ZOOM.edge;
  const w = Math.max(ZOOM.min, Math.min(ZOOM.max, gutter));
  const h = w * ZOOM.ratio;
  zoom.style.width = `${w}px`;
  zoom.style.height = `${h}px`;

  zoom.style.left = `${Math.max(ZOOM.edge, panel.left - w - ZOOM.gap)}px`;
  zoom.style.top = `${Math.min(
    Math.max(ZOOM.edge, row.top + row.height / 2 - h / 2),
    window.innerHeight - h - ZOOM.edge,
  )}px`;
}

const hideZoom = () => hideTop(zoom);

els.cartItems.addEventListener("mouseover", (ev) => {
  const tile = ev.target.closest(".ci-art");
  if (tile) showZoom(tile);
});
els.cartItems.addEventListener("mouseout", (ev) => {
  if (!ev.relatedTarget?.closest?.(".ci-art")) hideZoom();
});
els.cartItems.addEventListener("scroll", hideZoom);
els.cartDlg.addEventListener("close", hideZoom);

els.cartBtn.addEventListener("click", async () => {
  renderCart();
  els.cartDlg.showModal();
  fitSorts();   // measure once visible, so fonts are settled
  await loadDownloadSettings();   // the "remove when downloaded" switch
});

// Dismissing on a backdrop click is handled once for every dialog by
// closeOnBackdrop(); a second copy here would ignore its maximised check.


els.cartClear.addEventListener("click", () => {
  cart.clear();
  selected.clear();
  saveCart();
  renderCart();
  paintAddButtons();
});

// Hand the files to the app's own downloader, then show the progress panel.
async function startDownloads(items, button) {
  if (!items.length) return;

  // A mixed batch is the common case. Signing in is offered first, since it
  // gets them everything they asked for; only if they decline is the batch
  // split and the locked ones left behind.
  const locked = items.filter((i) => i.login);
  if (locked.length && !signedInToArchive) {
    const rest = items.filter((i) => !i.login);
    const listed = locked.slice(0, 6).map((i) => `• ${i.filename}`).join("\n");
    const more = locked.length > 6 ? `\n…and ${locked.length - 6} more` : "";
    const signedIn = await promptArchiveLogin(
      `${locked.length} of these need an archive.org account:\n${listed}${more}`
      + (rest.length
          ? `\n\nSign in to get all ${items.length}, or close this to download `
            + `just the other ${rest.length}.`
          : "\n\nSign in here and they will download straight away."));

    if (!signedIn) {
      if (!rest.length) return;
      const go = await ask(
        `${locked.length} of these still need an account and would fail.`
        + `\n\nDownload the other ${rest.length} now?`,
        { confirm: true, ok: `Download ${rest.length}` });
      if (!go) return;
      items = rest;
    }
  }

  /* The button this was started from might be a word or might be an icon -
     the arrow on a playlist tile is one - so its markup is what gets put
     back, and only a button with words in it is given any to say. */
  const label = button.innerHTML;
  const wordy = !!button.textContent.trim();
  button.disabled = true;
  if (wordy) button.textContent = t("Queueing…");

  const added = await queueDownloads(items.map((i) => ({
    url: i.url, filename: i.filename, size: i.size,
    console: i.console, source: i.source, login: !!i.login,
  })));

  if (added < 0 && wordy) button.textContent = t("Server unreachable");
  else button.innerHTML = label;
  if (added < 0 && !wordy) toast(t("Server unreachable"));
  button.disabled = false;
  if (added >= 0) {
    els.cartDlg.close();
    await loadDownloadSettings();
    els.dlDlg.showModal();
    pollDownloads();
  }
}

els.cartDl.addEventListener("click", () =>
  startDownloads(visibleItems(), els.cartDl));

els.cartDlSel.addEventListener("click", () =>
  startDownloads(selectedItems(), els.cartDlSel));

els.cartRmSel.addEventListener("click", () => {
  for (const item of selectedItems()) cart.delete(item.url);
  selected.clear();
  saveCart();
  renderCart();
  paintAddButtons();
});

// Ticking a row, or the select-all box.
els.cartItems.addEventListener("change", (ev) => {
  const box = ev.target.closest(".ci-pick");
  if (!box) return;
  if (box.checked) selected.add(box.dataset.url);
  else selected.delete(box.dataset.url);
  updateSelectionUI();
});

els.cartSelAll.addEventListener("change", () => {
  const on = els.cartSelAll.checked;
  for (const i of visibleItems()) {
    if (on) selected.add(i.url); else selected.delete(i.url);
  }
  for (const box of els.cartItems.querySelectorAll(".ci-pick")) box.checked = on;
  updateSelectionUI();
});

// Changing the console clears the ticks, so "selected" never refers to rows
// that have scrolled out of the filter.
els.cartConsole.addEventListener("change", () => { selected.clear(); renderCart(); });

/* A <select> is as wide as its longest option, which left the outline much
   wider than the label showing. Measure the selected text and size to it. */
const sizer = document.createElement("span");
sizer.style.cssText = "position:absolute;visibility:hidden;white-space:pre;top:-999px";
document.body.append(sizer);

const ARROW_SPACE = 20;

function fitSelect(sel) {
  const cs = getComputedStyle(sel);
  Object.assign(sizer.style, {
    fontFamily: cs.fontFamily, fontSize: cs.fontSize,
    fontWeight: cs.fontWeight, fontStyle: cs.fontStyle,
    letterSpacing: cs.letterSpacing, textTransform: cs.textTransform,
  });
  sizer.textContent = sel.options[sel.selectedIndex]?.textContent ?? "";
  const chrome = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight)
    + parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth);
  sel.style.width = `${Math.ceil(sizer.getBoundingClientRect().width + chrome + ARROW_SPACE)}px`;
}

const fitSorts = () => fitSelect(els.cartSort);

els.cartSort.addEventListener("change", () => {
  savePrefs({ cartSort: els.cartSort.value });
  fitSorts();
  renderCart();
});

els.cartCopy.addEventListener("click", async () => {
  const text = visibleItems().map((i) => i.url).join("\n");
  try {
    await navigator.clipboard.writeText(text);
    els.cartCopy.textContent = "Copied";
  } catch {
    els.cartCopy.textContent = "Copy failed";
  }
  setTimeout(() => { els.cartCopy.textContent = "Copy URLs"; }, 1500);
});

els.cartSave.addEventListener("click", () => {
  const urls = visibleItems().map((i) => i.url).join("\n");
  const blob = new Blob([urls + "\n"], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "romsrx-downloads.txt";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
});

/* ---------- playlists ----------

   Lists the user makes themselves, kept on the server beside the download
   list and for the same reason.

   A playlist holds *games*, not files on disk, which is what lets one contain
   things that haven't been downloaded yet - the whole point of them. Each
   entry carries enough to be shown and enough to be fetched: the name and
   console so it can be drawn with its box art either way, and the URL it came
   from when it was added out of the search.

   `key` is what ties the two halves together. It is the same normalised stem
   the "In Library" markers already join on, so an entry added while the game
   was still a wishlist item quietly turns into the copy on disk the moment
   that download lands - no bookkeeping, and nothing to go stale. */

let playlists = [];

async function loadPlaylists() {
  try {
    const data = await fetch("/api/playlists").then((r) => r.json());
    playlists = Array.isArray(data.playlists) ? data.playlists : [];
  } catch { /* server not up yet - no lists this session */ }
}

function savePlaylists() {
  saveState("/api/playlists", { playlists },
    "Your playlists could not be saved — is RomSrx still running? "
    + "Changes made now will be lost when this window is closed.");
}

const playlistById = (id) => playlists.find((p) => p.id === id) || null;

/* A key names a game, not a file. `Zelda (USA).zip` and `Zelda (USA).7z`
   reduce to the same one deliberately: once an archive has been extracted the
   folder left behind cannot say which of the two produced it, so "do you have
   this game" is the only question that can be answered honestly.

   A + button is not that question. It sits on one file and was clicked on one
   file, and lighting up its neighbour says the app put something on a list
   that it didn't.

   The filename is not enough to tell them apart either. One game is mirrored
   across half a dozen archive.org items, so `Spider-Man 2 (USA).zip` appears
   once under Redump, once under a RetroAchievements collection and once under
   that year's Redump pack - same name, same size, same console, three rows.
   The URL is the one thing that differs, because it carries the item it came
   from; the source name is the readable half of the same fact.

   So: the URL where both sides have one, the filename and its source where
   they don't, and the key where either side is a whole game rather than a
   file - a game put on a shelf from your own library has no download to be
   named after. */
const fileTag = (e) => String(e?.file || "").toLowerCase();
const urlTag = (e) => String(e?.url || "").toLowerCase();
const sourceTag = (e) => String(e?.source || "").toLowerCase();

/** What tells one copy of a game apart from another. Empty means "the game
 *  itself", which matches any copy of it. */
const identity = (e) => {
  const url = urlTag(e);
  if (url) return `u:${url}`;
  const file = fileTag(e);
  return file ? `f:${file}|${sourceTag(e)}` : "";
};

const sameEntry = (item, entry) => {
  if (item.key !== entry.key) return false;
  const listed = identity(item);
  const asked = identity(entry);
  return !listed || !asked || listed === asked;
};

const inPlaylist = (pl, entry) => pl.items.some((i) => sameEntry(i, entry));

/** One game, however it was reached. Console is part of it because the same
 *  title on two systems is two games, and only one of them is the one you
 *  put on the shelf. */
const entryKey = (console_, name, ext) =>
  `${(console_ || "").toLowerCase()}|${installKey(installStem(name, ext))}`;

/** From a search result - the dataset of its + button, which already carries
 *  everything the download list needs. */
function entryFromData(d) {
  const ext = d.ext || "";
  return {
    key: entryKey(d.console, d.name, ext),
    name: installStem(d.name, ext),   // shown; the file's name minus its type
    file: d.name,                     // what to ask the downloader for
    console: d.console || "",
    url: d.url || "",
    size: Number(d.size) || 0,
    source: d.source || "",
    ext,
    login: d.login === "1" || d.login === true,
    added: Date.now(),
  };
}

/** The box art already on screen for the game this button belongs to.
 *
 *  Remembered on the entry, because the two lookups are not equally good and
 *  cannot be. A search result is a whole game, so its cover is hunted across
 *  every file in the group - `007 - Agent Under Fire.7z` carries no region in
 *  its name and has no art of its own, but the sibling named `(USA)` does, and
 *  that is the cover you were looking at when you pressed +. A playlist entry
 *  is one file and knows only its own name, so working it out again from
 *  scratch would come up empty and the game would arrive on the shelf as a
 *  blank tile. Taking the URL rather than re-deriving it means the shelf shows
 *  the picture you were promised.
 *
 *  coverSrc() is what decides this is really box art - it takes the thumbnail
 *  server and the user's own covers folder and nothing else. */
function shownCoverFor(el) {
  /* The console section's own art first - a game listed on three systems has
     one cover per section, and the one above the file being added is the one
     that belongs to it - then the game's own cover up in the header.

     Each is *tried*, not just the first one picked: a section whose art 404'd
     has had its image taken out of the page entirely, and stopping there would
     throw away the cover still sitting in plain sight at the top of the card. */
  for (const selector of [".consec", "details.game", "[data-key]"]) {
    const img = el.closest(selector)?.querySelector("img");
    // currentSrc is the candidate that actually loaded, after any 404s were
    // stepped past; src is only the one being tried right now, and on a lazy
    // image below the fold it may not have been requested at all.
    const url = img && (isCoverUrl(img.currentSrc) ? img.currentSrc
      : isCoverUrl(img.getAttribute("src")) ? img.getAttribute("src") : "");
    if (url) return url;
  }
  return "";
}

/** The other filenames this same game goes by, on this same console.
 *
 *  This is the durable half of the answer, and `art` above is only the quick
 *  one. A remembered URL is a snapshot: it depends on which covers had
 *  finished loading at the instant the + was pressed, and it says nothing at
 *  all for an entry saved before any of this existed. Names don't expire.
 *  Handing the shelf the same set of names the search had lets it do the same
 *  search - which is the whole reason the search finds art that a lone
 *  filename cannot, `007 - Agent Under Fire.7z` having none of its own and
 *  its `(USA)` sibling having plenty.
 *
 *  Same console only: a game's Game Boy cover is not its GameCube one. */
function siblingNames(el, own, console_) {
  const card = el.closest("details.game");
  if (!card) return [];
  const names = [];
  for (const button of card.querySelectorAll(".cartadd")) {
    if (button.dataset.console !== console_) continue;
    const stem = installStem(button.dataset.name, button.dataset.ext || "");
    if (stem && stem !== own && !names.includes(stem)) names.push(stem);
    if (names.length >= SIBLING_NAMES) break;
  }
  return names;
}

// Enough for the region that has the art without carrying half a Redump set
// around in a JSON file for every game on every shelf.
const SIBLING_NAMES = 3;

/** From a game already on disk. There is no URL - it came from the folder,
 *  not from a search - so it can't be re-downloaded from this alone. Adding
 *  the same game from the search later fills that in. */
function entryFromGame(game) {
  return {
    key: entryKey(game.console, game.name, ""),
    name: game.name, file: "", console: game.console || "",
    url: "", size: game.size || 0, source: "", ext: "",
    login: false, path: game.path, added: Date.now(),
  };
}

/** Fill in what an entry is missing from a fresh copy of the same game.
 *
 *  This is what makes a list built out of the library still useful after the
 *  files are gone: add the game again from the search and the entry gains the
 *  URL, so "Download missing" can act on it. Nothing already known is
 *  overwritten - the entry that is there is the one the user made. */
function mergeEntry(existing, fresh) {
  let changed = false;
  for (const field of ["url", "file", "source", "ext", "path", "art"]) {
    if (!existing[field] && fresh[field]) {
      existing[field] = fresh[field];
      changed = true;
    }
  }
  if (!existing.size && fresh.size) { existing.size = fresh.size; changed = true; }
  if (fresh.login && !existing.login) { existing.login = true; changed = true; }
  if (fresh.alts?.length && !existing.alts?.length) {
    existing.alts = fresh.alts;
    changed = true;
  }
  return changed;
}

/** Give the shelves whatever this game has just told us about itself.
 *
 *  An entry only learns where to find its cover at the moment it is added, so
 *  one saved before that was worked out - or added while its artwork was still
 *  loading - would stay a blank tile for good, and the only way out would be
 *  to take the game off the shelf and put it back. Opening this menu on a
 *  game in the search is the natural thing to do when you notice its tile is
 *  empty, so that is where the repair happens. Membership is never touched:
 *  this fills in blanks and nothing else. */
function refreshShelfCopies(entries) {
  let changed = false;
  for (const pl of playlists) {
    for (const entry of entries) {
      const existing = pl.items.find((i) => i.key === entry.key);
      if (existing && mergeEntry(existing, entry)) changed = true;
    }
  }
  if (!changed) return;
  savePlaylists();
  if (libraryOpen && currentPlaylist()) renderLibrary();
}

function addEntries(pl, entries) {
  let added = 0;
  for (const entry of entries) {
    const existing = pl.items.find((i) => i.key === entry.key);
    if (existing) {
      mergeEntry(existing, entry);
      /* A shelf holds one entry per game, so adding the .7z of something
         already on it as a .zip cannot make a second row. Left at that, the
         click would do nothing at all: the + you pressed would stay unlit and
         the one next to it would stay lit. Pointing the entry at the file you
         just chose is the reading that matches the button - the game is on the
         shelf once, as the copy you last asked for. */
      if (identity(entry) && identity(entry) !== identity(existing)) {
        Object.assign(existing, {
          file: entry.file, url: entry.url, ext: entry.ext,
          size: entry.size || existing.size, source: entry.source,
          login: entry.login,
        });
        added++;
      }
      continue;
    }
    pl.items.push({ ...entry });
    added++;
  }
  return added;
}

function removeEntries(pl, keys) {
  const drop = new Set(keys);
  const before = pl.items.length;
  pl.items = pl.items.filter((i) => !drop.has(i.key));
  return before - pl.items.length;
}

function createPlaylist(name) {
  const pl = {
    id: `pl${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`,
    name, created: Date.now(), items: [],
  };
  playlists.push(pl);
  return pl;
}

/** The download-list shape for an entry. Only ever called for entries that
 *  came from a search, since those are the only ones with a URL. */
const cartItemFromEntry = (e) => ({
  url: e.url, filename: e.file || e.name, size: e.size || 0,
  console: e.console, source: e.source, ext: e.ext,
  login: !!e.login, added: Date.now(),
});

const downloadItemFromEntry = (e) => ({
  url: e.url, filename: e.file || e.name, size: e.size || 0,
  console: e.console, source: e.source, login: !!e.login,
});

/* ---------- the + menu ----------

   One menu, opened from the + on a search result and from the + on a library
   tile alike, so "where does this game go" is answered the same way wherever
   it is asked. It stays open after a pick: putting a game on three shelves is
   one gesture, not three trips through the same menu. */

asPopover(els.addMenu);

let addTargets = [];      // the entries the menu is currently acting on

const menuRow = (act, label, on, count, attrs = "") => `
  <button data-act="${act}" ${attrs} class="mrow${on ? " on" : ""}">
    <span class="mtick">${on ? "&#10003;" : ""}</span>
    <span class="mlabel">${esc(label)}</span>
    <span class="mcount">${count}</span>
  </button>`;

function renderAddMenu() {
  if (!addTargets.length) return;
  const n = addTargets.length;
  const gettable = addTargets.filter((e) => e.url);

  const rows = [`<div class="menuhead">${esc(n > 1
    ? t("Add {n} games to…", { n }) : t("Add to…"))}</div>`];

  // Only where it can do something: a game that came off your own disk has no
  // URL, so there is nothing for the downloader to be given.
  if (gettable.length) {
    rows.push(menuRow("cart", t("Download list"),
                      gettable.every((e) => cart.has(e.url)), cart.size));
  }
  for (const pl of playlists) {
    rows.push(menuRow("pl", pl.name,
                      addTargets.every((e) => inPlaylist(pl, e)),
                      pl.items.length, `data-id="${esc(pl.id)}"`));
  }
  rows.push(`<button data-act="new" class="mnew">${esc(t("New playlist…"))}</button>`);
  els.addMenu.innerHTML = rows.join("");
}

function openAddMenu(ev, entries) {
  if (!entries.length) return;
  refreshShelfCopies(entries);   // an older copy may be missing its artwork
  addTargets = entries;
  renderAddMenu();
  openMenu(els.addMenu, ev);
}

els.addMenu.addEventListener("click", async (ev) => {
  const button = ev.target.closest("button");
  if (!button || !addTargets.length) return;
  /* Redrawing the menu below takes the clicked node out of the page, and the
     "did this land outside a menu" test upstairs would then say yes about a
     click that plainly didn't. */
  ev.romsrxMenu = true;
  const entries = addTargets;

  if (button.dataset.act === "cart") {
    const gettable = entries.filter((e) => e.url);
    if (gettable.every((e) => cart.has(e.url))) {
      for (const entry of gettable) cart.delete(entry.url);
    } else {
      // Adding something you can't download would only fail later, well away
      // from the click that caused it.
      const locked = gettable.some((e) => e.login);
      if (!await allowLoginOnly(locked, t("That file"))) return;
      for (const entry of gettable) {
        if (!cart.has(entry.url)) cart.set(entry.url, cartItemFromEntry(entry));
      }
    }
    saveCart();
  } else if (button.dataset.act === "pl") {
    const pl = playlistById(button.dataset.id);
    if (!pl) return;
    if (entries.every((e) => inPlaylist(pl, e))) {
      removeEntries(pl, entries.map((e) => e.key));
    } else {
      addEntries(pl, entries);
    }
    savePlaylists();
  } else if (button.dataset.act === "new") {
    // The box is a modal dialog, so the menu goes first - it would otherwise
    // sit over the thing asking for the name.
    closeMenus();
    const name = await promptText({
      title: t("New playlist"), ok: t("Create"),
      value: suggestPlaylistName(),
    });
    if (!name) return;
    addEntries(createPlaylist(name), entries);
    savePlaylists();
    afterListsChanged();
    toast(t("Added to {name}.", { name }));
    return;
  } else {
    return;
  }

  afterListsChanged();
  renderAddMenu();     // stays open, showing what just changed
});

/** "Playlist 2", "Playlist 3"… - a name to accept rather than one to think
 *  of, which is all most lists need. */
function suggestPlaylistName() {
  const base = t("Playlist");
  const taken = new Set(playlists.map((p) => p.name.toLowerCase()));
  if (!taken.has(base.toLowerCase())) return base;
  for (let n = 2; n < 500; n++) {
    if (!taken.has(`${base} ${n}`.toLowerCase())) return `${base} ${n}`;
  }
  return base;
}

/** Everything that shows what is in a list has to be told when one changes -
 *  the + buttons, the shelf counts, and the shelf itself when it is the one
 *  on screen. */
function afterListsChanged() {
  paintAddButtons();
  if (els.cartDlg.open) renderCart();
  if (!libraryOpen) return;
  if (currentPlaylist()) renderLibrary(); else renderShelves();
}

/** The state of a + button: a tick for the download list, an accent ring for
 *  a game that is on a shelf somewhere. Painted rather than baked in, because
 *  both answers change without the row being redrawn. */
function paintAddButton(button, entry, listed_) {
  const inCart = !!entry.url && cart.has(entry.url);
  const listed = listed_
    ? isListed(listed_, entry)
    : playlists.some((pl) => inPlaylist(pl, entry));
  button.classList.toggle("in", inCart);
  button.classList.toggle("listed", listed);
  button.innerHTML = inCart ? "&#10003;" : "+";
  button.title = t(inCart
    ? "In your download list — click to change where this goes"
    : (listed
        ? "In a playlist — click to change where this goes"
        : "Add to the download list or a playlist"));
}

/** Every copy on a shelf, grouped by the game it belongs to.
 *
 *  Asked once for the whole page rather than walking every list again for
 *  every button - a wall of covers multiplies that by a thousand. An empty
 *  string in the set is an entry that names no particular copy, which stands
 *  for any of them; see sameEntry(). */
function listedFiles() {
  const index = new Map();
  for (const pl of playlists) {
    for (const item of pl.items) {
      let copies = index.get(item.key);
      if (!copies) index.set(item.key, copies = new Set());
      copies.add(identity(item));
    }
  }
  return index;
}

const isListed = (index, entry) => {
  const copies = index.get(entry.key);
  if (!copies) return false;
  const own = identity(entry);
  return !own || copies.has("") || copies.has(own);
};

/* Only three things decide how a + button looks: the game's key, the file it
   sits on, and the URL that would put it in the download list. Building the
   whole entry for each one meant reading the DOM and searching the library per
   button, on every repaint. */
function paintAddButtons() {
  const listed = listedFiles();

  for (const button of els.results.querySelectorAll(".cartadd")) {
    paintAddButton(button, {
      key: entryKey(button.dataset.console, button.dataset.name,
                    button.dataset.ext || ""),
      // All three, because one game is mirrored across several archive.org
      // items under the same filename: only the URL - or failing that the
      // name together with the source - says which row this is.
      file: button.dataset.name,
      source: button.dataset.source,
      url: button.dataset.url,
    }, listed);
  }

  const onShelf = new Map((currentPlaylist()?.items || []).map((i) => [i.key, i]));
  for (const button of els.libBody.querySelectorAll(".libadd")) {
    const key = button.closest("[data-key]")?.dataset.key;
    if (!key) continue;
    // A game that came off your own folders has no URL, so the download list
    // is not one of its answers; one on a playlist may have arrived with one.
    // No filename either: the tile is a game, not one of the files behind it.
    paintAddButton(button, { key, url: onShelf.get(key)?.url || "" }, listed);
  }
  paintCartBadge();
}

/* ---------- box art ---------- */

// The thumbnail server substitutes these characters in its filenames.
const coverName = (s) => s.replace(/[&*/:`<>?\\|]/g, "_");

/* Box art only.
 *
 * The thumbnail server also keeps Named_Titles and Named_Snaps under the same
 * filenames, and falling back to those did fill some empty tiles - but with
 * title screens and gameplay screenshots, which read as wrong next to real
 * covers. A game with no box art is better served by its name on a plain
 * tile, which is what the library now shows.
 *
 * RetroAchievements was the obvious second source, since it covers the
 * homebrew and hacks libretro misses, but it can't be used: its API returns
 * 401 without a key, and while the images are public they are addressable
 * only by numeric game id - which only the API will tell you. Shipping a key
 * in a public app would leak it. */
const ART_KINDS = ["Named_Boxarts"];

/** The filename, then progressively simpler forms of it.
 *
 *  Plenty of misses are not missing art at all - the file just carries tags
 *  the thumbnail server's copy doesn't. `Crimewave (Europe) (Demo)` has no
 *  cover; `Crimewave (Europe)` does. Trailing bracketed groups come off one
 *  at a time, nearest the end first, since those are the least significant. */
function nameVariants(stem) {
  const out = [stem];
  let current = stem;
  while (out.length <= NAME_TRIES) {
    const trimmed = current.replace(/\s*\([^()]*\)\s*$/, "").trim();
    if (!trimmed || trimmed === current) break;
    current = trimmed;
    out.push(current);
  }
  return out;
}

function coverUrl(system, stem, kind) {
  return `${THUMB_BASE}/${encodeURIComponent(system)}/${kind}/${
    encodeURIComponent(coverName(stem))}.png`;
}

/** Candidate cover URLs for a set of files, best match first.
 *  Files are already sorted USA-first, so the first hit is usually the
 *  cover you'd expect; later files act as fallbacks for odd variants.
 *
 *  Every file's box art is tried before falling back to title screens,
 *  otherwise a Japanese release's screenshot would outrank the US box. */
function coverCandidates(files) {
  const urls = [];
  const seen = new Set();
  // Kind is the outer loop: box art of a slightly-simplified name beats a
  // screenshot of the exact one.
  for (const kind of ART_KINDS) {
    for (const file of files.slice(0, FILES_PER_KIND)) {
      const systems = [LIBRETRO[file.console], LIBRETRO_ALT[file.console]];
      const stem = file.ext
        ? file.filename.slice(0, -(file.ext.length + 1))
        : file.filename;
      if (!stem) continue;
      for (const name of nameVariants(stem)) {
        for (const system of systems) {
          if (!system) continue;
          const url = coverUrl(system, name, kind);
          if (!seen.has(url)) { seen.add(url); urls.push(url); }
          if (urls.length >= MAX_COVER_TRIES) return urls;
        }
      }
    }
  }
  return urls;
}

// Step through the remaining candidates. When they are all gone, leave the
// name in place of the picture if one was supplied - somewhere like the
// library, where the tile is the only thing identifying the game. Elsewhere
// the title is already right next to it, so the image just goes.
window.coverFail = (img) => {
  const rest = JSON.parse(img.dataset.rest || "[]");
  if (rest.length) {
    img.dataset.rest = JSON.stringify(rest.slice(1));
    img.src = rest[0];
    return;
  }
  const title = img.dataset.title;
  if (!title) { img.remove(); return; }

  const placeholder = document.createElement("span");
  placeholder.className = `noart ${img.className}`;   // keeps `libhit`
  placeholder.textContent = title;
  placeholder.title = title;
  img.replaceWith(placeholder);
};

function coverHtml(files) {
  const urls = coverCandidates(files);
  if (!urls.length) return `<span class="coverbox"></span>`;
  return `<span class="coverbox"><img class="cover" src="${esc(urls[0])}"
    data-rest='${esc(JSON.stringify(urls.slice(1)))}' alt="" loading="lazy"
    decoding="async" onerror="coverFail(this)"></span>`;
}

/** One console's box art, shown large beside that console's downloads.
 *  The console name sits underneath as a fallback for games with no art. */
function consoleArtHtml(console_, files) {
  const urls = coverCandidates(files);
  const img = urls.length
    ? `<img class="cover-lg" src="${esc(urls[0])}"
         data-rest='${esc(JSON.stringify(urls.slice(1)))}' alt="" loading="lazy"
         decoding="async" onerror="coverFail(this)">`
    : "";
  return `<div class="conart" title="${esc(console_)}">
    <span class="conart-name">${esc(console_)}</span>${img}</div>`;
}

/** Split a game's files into per-console sections, preserving sort order. */
function consoleSections(files) {
  const order = [];
  const byConsole = new Map();
  for (const file of files) {
    if (!byConsole.has(file.console)) {
      byConsole.set(file.console, []);
      order.push(file.console);
    }
    byConsole.get(file.console).push(file);
  }
  return order.map((name) => [name, byConsole.get(name)]);
}

/** Console badges, capped so a game on a dozen systems can't wrap the card
 *  onto several lines. The overflow sits hidden behind a "+N" toggle. */
function consoleBadges(consoles) {
  const badge = (c) => `<span class="badge console">${esc(c)}</span>`;
  if (consoles.length <= CONSOLE_PREVIEW) return consoles.map(badge).join("");

  const rest = consoles.slice(CONSOLE_PREVIEW);
  return consoles.slice(0, CONSOLE_PREVIEW).map(badge).join("")
    + rest.map((c) => `<span class="badge console extra" hidden>${esc(c)}</span>`).join("")
    + `<span class="badge console morecon" role="button" data-count="${rest.length}"
         data-open="0" title="Show ${rest.length} more console${rest.length === 1 ? "" : "s"}"
         >+${rest.length}<span class="morecaret">&#9662;</span></span>`;
}

function gameCard(g, open = false) {
  // Console leads the row so you can see what a result is at a glance.
  const consoles = consoleBadges(g.consoles);
  const regions = g.regions.slice(0, 4)
    .map((r) => `<span class="badge">${esc(r)}</span>`).join("");
  const n = g.files.length;
  const s = g.sources.length;

  return `
    <details class="game"${open ? " open" : ""}>
      <summary>
        <span class="caret">&#9654;</span>
        ${coverHtml(g.files)}
        <span class="ginfo">
          <span class="gtop">
            <span class="title">${esc(g.title)}</span>
            ${regions}
            <span class="count">${n} ${t(n === 1 ? "file" : "files")} &middot;
              ${s} ${t(s === 1 ? "source" : "sources")}</span>
          </span>
          <span class="gconsoles">${consoles}</span>
        </span>
      </summary>
      <div class="sections">${consoleSections(g.files).map(
        ([name, files]) => `
        <div class="consec">
          ${consoleArtHtml(name, files)}
          <div class="conbody">
            <div class="conhead">
              <button class="finst" hidden></button>
            </div>
            <div class="files">${files.map(fileRow).join("")}</div>
          </div>
        </div>`).join("")}</div>
    </details>`;
}

async function search(append = false) {
  const mine = ++seq;
  if (!append) offset = 0;

  els.hint.textContent = t("searching…");
  const res = await fetch(`/api/search?${params({ offset })}`);
  const data = await res.json();
  if (mine !== seq) return; // a newer keystroke already won

  total = data.total;
  if (!append) renderFilters(data.facets);

  // Cards always start collapsed - expanding is the user's call.
  const html = data.groups.map((g) => gameCard(g)).join("");

  if (append) {
    els.results.insertAdjacentHTML("beforeend", html);
  } else if (html) {
    els.results.innerHTML = html;
  } else if (indexEmpty) {
    // Nothing has ever been indexed, so "no matches" would be misleading -
    // there is nothing to match against yet.
    els.results.innerHTML = firstRunHtml();
  } else {
    els.results.innerHTML = `<p class="empty">${esc(t("No matches."))}${
      els.q.value.trim() ? " " + esc(t("Try a shorter or differently spelled title.")) : ""}</p>`;
  }

  paintInstalled();     // fresh rows, so the "In Library" markers go back on
  paintAddButtons();    // ...and the + buttons say where each file already is

  offset += data.groups.length;
  // Never over the library: a search can be re-run while the shelf is on
  // screen - switching language does exactly that - and "Load more" would
  // then turn up underneath a list it has nothing to do with.
  els.more.hidden = libraryOpen || offset >= total;
  // ...nor over the front page, which is showing consoles rather than games.
  paintHome();
  els.hint.textContent = total
    ? `${total.toLocaleString()} ${t(total === 1 ? "game" : "games")}`
    : "";
}

const debounce = (fn, ms) => {
  let t;
  return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
};
const debouncedSearch = debounce(() => search(false), 180);

/* A fresh install has no index, and the app can't do anything until it does.
   Rather than an empty results list, say what to press. */
let indexEmpty = false;

function firstRunHtml() {
  return `
    <div class="firstrun">
      <h2>Nothing indexed yet</h2>
      <p>RomSrx searches its own local copy of what archive.org holds.
         Building that copy takes a couple of minutes and only has to happen
         once — everything after it is offline and instant.</p>
      <button id="firstindex" class="bigbtn">Build the index</button>
      <p class="firstnote">You can rebuild it any time with the
         <span class="inlineicon">&#8635;</span> button in the corner.</p>
    </div>`;
}

/* Until an index exists there is nothing to search, nothing to filter and
   nothing to download, so every other control is turned off and the only
   thing on screen is the button that builds it. Reindex stays live, and so
   does the theme - being stuck on a colour you can't read would be worse. */
function lockUntilIndexed() {
  const usable = !indexEmpty;
  for (const el of [els.libBtn, els.searchBtn, els.homeBtn, els.titleBtn,
                    els.cartBtn, els.dlBtn, els.acctBtn, els.q]) {
    if (el) el.disabled = !usable;
  }
  document.body.classList.toggle("noindex", indexEmpty);
}

async function loadStats() {
  const stats = await fetch("/api/stats").then((r) => r.json());
  indexEmpty = !stats.games;
  lockUntilIndexed();
  els.tagline.textContent = indexEmpty
    ? t("no index yet")
    : `${stats.games.toLocaleString()} ${t("games")} · `
      + `${stats.files.toLocaleString()} ${t("files")} · ${humanSize(stats.bytes)}`;

  const failed = stats.sources.filter((s) => s.last_error);
  els.footer.innerHTML =
    `${stats.sources.length} ${esc(t("sources indexed"))}` +
    (failed.length ? ` &middot; <span style="color:#e0714f">${failed.length} ${
      esc(t("failed"))}: ${failed.map((s) => esc(s.name)).join(", ")}</span>` : "") +
    (stats.sources[0]?.last_indexed
      ? ` &middot; ${esc(t("last updated"))} ${
          esc(stats.sources[0].last_indexed.replace("T", " "))}`
      : "") +
    ` &middot; <span class="ver">RomSrx <span id="vernum"></span></span>` +
    ` &middot; <button class="linkbtn" id="checkupdates">${
        esc(t("Check for updates"))}</button>`;
  paintVersion();
}

/* ---------- updates ---------- */

/* Only ever a link. A running app can't replace its own files on Windows, so
   installing the new version is the user's move, not ours. */
let latestUpdate = null;

function paintVersion() {
  const span = $("vernum");
  if (span) span.textContent = latestUpdate?.current || "";
  // Beside the title too, where it doubles as a way into that version's notes.
  const version = latestUpdate?.current || "";
  els.verBtn.textContent = version ? `v${version}` : "";
  els.verBtn.hidden = !version;
}

/* What changed in the copy you are actually running - which is not the same
   question the update banner answers. That one only ever knows about the
   newest release, so once you are a version behind it would show you notes for
   something you haven't got. This asks for the exact tag. */
els.verBtn.addEventListener("click", async () => {
  const version = latestUpdate?.current;
  if (!version) return;
  els.verBtn.disabled = true;
  try {
    const res = await fetch(`/api/release?version=${encodeURIComponent(version)}`)
      .then((r) => r.json());
    await say(res.error
      || plainNotes(res.notes)
      || `RomSrx ${version} — no notes were published for this version.`);
  } catch {
    await say(t("Could not reach GitHub to fetch the release notes."));
  } finally {
    els.verBtn.disabled = false;
  }
});

function showUpdate(info) {
  latestUpdate = info;
  paintVersion();
  if (!info?.update) return;
  // Skipped once, stays skipped until a newer one than that turns up.
  let skipped = "";
  try { skipped = localStorage.getItem("romsrx.skipUpdate") || ""; } catch { }
  if (skipped === info.latest) return;

  els.upMsg.textContent =
    `RomSrx ${info.latest} is available — you have ${info.current}.`;
  els.upGet.href = info.asset?.url || info.page;
  els.upGet.textContent = info.asset
    ? `Download (${humanSize(info.asset.size)})` : "Open release page";
  els.upNotes.hidden = !info.notes;
  els.updateBar.hidden = false;
}

async function checkUpdates(force = false) {
  try {
    const info = await fetch(`/api/update${force ? "?force=1" : ""}`)
      .then((r) => r.json());
    showUpdate(info);
    return info;
  } catch {
    return null;
  }
}

/* ---------- downloads ---------- */

const STATUS_LABEL = () => ({
  queued: t("Queued"), running: t("Downloading"), extracting: t("Extracting…"),
  paused: t("Paused"), done: t("Finished"), error: t("Failed"),
  cancelled: t("Cancelled"),
});

const speedText = (bps) => (bps > 0 ? `${humanSize(bps)}/s` : "");

function etaText(seconds) {
  if (!seconds || seconds <= 0) return "";
  if (seconds < 60) return `${Math.round(seconds)}s left`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m left`;
  return `${(seconds / 3600).toFixed(1)}h left`;
}

/** Send files to the app's own downloader instead of the browser. */
async function queueDownloads(items) {
  if (!items.length) return 0;
  try {
    const res = await fetch("/api/downloads", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items }),
    });
    const data = await res.json();
    pollDownloads();
    return data.added || 0;
  } catch {
    return -1;   // server unreachable
  }
}

function jobMeta(job) {
  const meta = [STATUS_LABEL()[job.status] || job.status];
  if (job.status === "running") {
    meta.push(`${humanSize(job.done)} of ${humanSize(job.total)}`);
    if (job.speed) meta.push(speedText(job.speed));
    const eta = etaText(job.eta);
    if (eta) meta.push(eta);
  } else if (job.status === "done") {
    meta.push(humanSize(job.total));
    if (job.extracted) meta.push(t("extracted"));
    if (job.error) meta.push(job.error);
  } else if (job.status === "error") {
    meta.push(job.error || t("unknown error"));
  } else if (job.status === "queued" && job.place) {
    // Where it sits in the wait list, so reordering visibly does something.
    meta.push(job.place === 1 ? t("next up") : `#${job.place}`);
    if (job.done) meta.push(`${humanSize(job.done)} of ${humanSize(job.total)} so far`);
  }
  if (job.attempts > 1 && job.status !== "done") meta.push(`try ${job.attempts}`);
  // Why a 🔒 download won't budge. Without this a paused row just says
  // "Paused", and pressing play looks like it does nothing.
  if (job.login && !signedInToArchive && job.status !== "done") {
    return meta.map(esc).join(" &middot; ")
      + ` &middot; <span class="lock">&#128274; ${esc(t("sign in to resume"))}</span>`;
  }
  return meta.map(esc).join(" &middot; ");
}

function jobRow(job) {
  const pct = Math.min(job.percent, 100);

  // Cover art, matched the same way as the search results.
  const ext = job.filename.includes(".") ? job.filename.split(".").pop() : "";
  const urls = coverCandidates([{ console: job.console, filename: job.filename, ext }]);
  const art = urls.length
    ? `<span class="dj-art"><img src="${esc(urls[0])}"
         data-rest='${esc(JSON.stringify(urls.slice(1)))}' alt="" loading="lazy"
         decoding="async" onerror="coverFail(this)"></span>`
    : `<span class="dj-art"></span>`;

  const finished = job.status === "done";
  const busy = job.status === "queued" || job.status === "running"
    || job.status === "extracting";
  const resumable = job.status === "paused" || job.status === "cancelled"
    || job.status === "error";

  // Pause keeps the .part file, so resuming picks up where it stopped.
  let control = "";
  if (busy) {
    control = `<button class="dj-ctl" data-act="pause" data-id="${job.id}"
      title="${esc(t("Pause"))}">&#10074;&#10074;</button>`;
  } else if (resumable) {
    control = `<button class="dj-ctl" data-act="resume" data-id="${job.id}"
      title="${esc(t("Resume"))}">&#9654;</button>`;
  }

  // Swapping places in the wait list: send a running one back to make room,
  // then move the one you actually want to the front. Both keep their .part
  // file, so nothing restarts from zero.
  let order = "";
  if (job.status === "running") {
    order = `<button class="dj-ctl" data-act="requeue" data-id="${job.id}"
      title="Send back to the queue and let the next one start"
      >&#8681;</button>`;
  } else if (job.status === "queued" && job.place > 1) {
    order = `<button class="dj-ctl" data-act="startnext" data-id="${job.id}"
      title="Move to the front of the queue">&#8679;</button>`;
  }

  const shown = shownProgress(job);
  return `
    <div class="dljob ${esc(job.status)}" data-id="${job.id}">
      ${art}
      <div class="dj-body">
        <div class="dj-top">
          <span class="dj-name">${esc(job.filename)}${job.login
            ? ` <span class="lock">&#128274; ${esc(t("login"))}</span>` : ""}</span>
          <span class="dj-pct">${esc(shown.text)}</span>
          ${finished ? `<button class="dj-open" data-id="${job.id}"
                          title="${esc(t("Open containing folder"))}">&#128193;</button>` : ""}
          ${order}
          ${control}
          ${busy ? "" : `<button class="dj-forget" data-id="${job.id}"
            title="${esc(t("Take off this list and keep the files"))}">&times;</button>`}
          <button class="dj-trash" data-id="${job.id}"
            title="${esc(t("Delete this download and its files from your PC"))}">&#128465;</button>
        </div>
        <div class="dj-bar${shown.extracting ? " unpacking" : ""}${
             shown.guessing ? " guessing" : ""}"><span
             style="width:${shown.pct}%"></span></div>
        <div class="dj-meta">${job.console
          ? `<span class="ctag">${esc(job.console)}</span>` : ""}${jobMeta(job)}</div>
      </div>
    </div>`;
}

/** What the bar and the number should say right now.
 *
 *  Downloading and unpacking are two separate waits, and a bar that sat at
 *  100% through several minutes of extraction looked like the app had
 *  finished and then hung. While unpacking, the bar restarts and measures
 *  that instead - in a different colour, so it is plainly a second stage
 *  rather than the first one going backwards. Both .zip and .7z report how
 *  far through they are; an archive whose listing can't be read reports
 *  nothing, and that one keeps the word and a bar that crawls on the spot.
 */
function shownProgress(job) {
  if (job.status === "extracting") {
    const pct = Number(job.extractPercent) || 0;
    return {
      pct: pct || 100,          // no number to show: fill it and stripe it
      extracting: true,
      guessing: !pct,
      text: pct ? `${pct.toFixed(0)}%` : t("Extracting…"),
    };
  }
  const pct = Math.min(job.percent, 100);
  return { pct, extracting: false, guessing: false,
           text: job.status === "done" ? "100%" : `${pct.toFixed(0)}%` };
}

function renderDownloads(state) {
  const all = state.jobs || [];
  // Anything the user has already removed stays gone, even while the server
  // is still finishing the job of removing it. Ids the server no longer
  // mentions are dropped from the set - the removal is done, and holding
  // them would hide a future download that reused the id.
  const known = new Set(all.map((j) => j.id));
  for (const id of dropped) if (!known.has(id)) dropped.delete(id);
  const jobs = dropped.size ? all.filter((j) => !dropped.has(j.id)) : all;

  const busy = state.active + state.queued;

  els.dlCount.textContent = busy;
  els.dlCount.hidden = !busy;
  els.dlBtn.classList.toggle("has", busy > 0);
  els.dlSummary.textContent = busy
    ? `${state.active} ${t("running")} · ${state.queued} ${t("queued")}${
        state.speed ? " · " + speedText(state.speed) : ""}`
    : (jobs.length ? `${jobs.length} ${t("finished")}` : "");

  /* One button that flips: pause everything running, or restart everything
     that's stopped. Hidden when neither applies.

     `stopping` is what makes this behave. A running download only becomes
     "paused" once its worker reaches the next chunk and notices, and a stalled
     transfer can sit there for a long time - so counting it as still active
     left the button saying "Pause all" after you had already pressed it, with
     further presses doing nothing visible. A job that has been told to stop
     counts as stopped here, whatever it still says it is. */
  const RUNNING = ["running", "queued", "extracting"];
  const STOPPED = ["paused", "cancelled", "error"];
  const live = jobs.filter((j) => RUNNING.includes(j.status) && !j.stopping).length;
  const stopped = jobs.filter((j) =>
    STOPPED.includes(j.status) || (j.stopping && RUNNING.includes(j.status))).length;
  els.dlPauseAll.hidden = !live && !stopped;
  els.dlPauseAll.dataset.act = live ? "pauseall" : "resumeall";
  els.dlPauseAll.textContent = live ? t("Pause all")
    : `${t("Resume all")} (${stopped})`;
  els.dlRemoveAll.hidden = !jobs.length;

  // Rebuilding the list every poll destroys the buttons mid-click - a press
  // that starts before a refresh and ends after it never becomes a click.
  // So only rebuild when the rows or their states actually change; otherwise
  // update the moving parts in place.
  // Queue position is in here too: reordering changes which row carries the
  // "move up" button, and that only lives in freshly built markup.
  const signature = jobs.map((j) => `${j.id}:${j.status}:${j.place}`).join("|");
  if (signature === renderedJobs && els.dlJobs.querySelector(".dljob")) {
    for (const job of jobs) {
      const row = els.dlJobs.querySelector(`.dljob[data-id="${job.id}"]`);
      if (!row) continue;
      const shown = shownProgress(job);
      row.querySelector(".dj-pct").textContent = shown.text;
      const bar = row.querySelector(".dj-bar");
      bar.classList.toggle("unpacking", shown.extracting);
      bar.classList.toggle("guessing", shown.guessing);
      bar.querySelector("span").style.width = `${shown.pct}%`;
      row.querySelector(".dj-meta").innerHTML = (job.console
        ? `<span class="ctag">${esc(job.console)}</span>` : "") + jobMeta(job);
    }
    return;
  }
  renderedJobs = signature;

  els.dlJobs.innerHTML = jobs.length
    ? jobSections(jobs)
    : `<p class="empty">${esc(t("Nothing downloading. Add files from your list."))}</p>`;
}

/* What is happening now, what is waiting its turn, and what is over with.
   Split up so the queue reads as a queue - the order things will start in -
   rather than as one undifferentiated list. */
const JOB_SECTIONS = [
  ["Downloading", ["running", "extracting"]],
  ["Queued", ["queued"]],
  ["Paused", ["paused"]],
  ["Failed", ["cancelled", "error"]],
  ["Finished", ["done"]],
];

function jobSections(jobs) {
  return JOB_SECTIONS.map(([title, statuses]) => {
    const mine = jobs.filter((j) => statuses.includes(j.status));
    if (!mine.length) return "";
    // Waiting downloads go in the order they will actually start; everything
    // else keeps the order it was added in.
    mine.sort(title === "Queued"
      ? (a, b) => a.place - b.place
      : (a, b) => a.id - b.id);
    return `
      <div class="djgroup">
        <h3 class="djhead">${title}<span class="djn">${mine.length}</span></h3>
        ${mine.map(jobRow).join("")}
      </div>`;
  }).join("");
}

let dlTimer = null;
let renderedJobs = "";   // job ids + statuses currently drawn

const finishedJobs = new Set();
let sawFirstPoll = false;

/** The server is what takes a finished download off the list, so the page has
 *  to pick that change up instead of trusting its own copy. Only jobs that
 *  finish while we're watching count - on the first poll the queue is full of
 *  downloads that finished in some earlier session. */
/* ---------- "it's done" ----------

   A download that takes twenty minutes finishes while you are somewhere else,
   and the only sign of it was a number quietly changing in the header. Two
   ways of saying so: the app's own toast for when you are looking at it, and
   the desktop's notification for when you are not.

   The desktop one is asked for rather than assumed. Permission is requested
   the first time something finishes - not at launch, where a browser prompt
   before you have done anything is just noise - and if it is refused or the
   engine has no notifications at all, the toast still happens. */
/* ---------- the chime ----------

   A download that takes twenty minutes finishes while you are in another
   window, and a desktop notification only helps if you happen to be looking
   at the corner it appears in. A sound reaches you when nothing on screen
   can. Two short notes, a rising interval - long enough to notice, short
   enough not to be an event.

   Synthesised rather than shipped as a file. A .wav or .mp3 in web/ is
   another asset to bundle and a mismatch waiting to happen between the
   packaged app and the source tree; a few oscillator nodes are neither. */
let audioCtx = null;

function chime() {
  if (prefs.muteDone) return;
  const Ctx = window.AudioContext || window.webkitAudioContext;
  if (!Ctx) return;                       // no audio engine; the toast stands
  try {
    audioCtx = audioCtx || new Ctx();
    // Browsers suspend audio until the page has been interacted with. By the
    // time a download finishes something has always been clicked, but a
    // resume costs nothing and covers the case where it hasn't.
    if (audioCtx.state === "suspended") audioCtx.resume();

    const now = audioCtx.currentTime;
    for (const [at, freq] of [[0, 660], [0.16, 990]]) {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      // Shaped rather than switched: an oscillator started and stopped at
      // full volume clicks at both ends, which sounds like a fault.
      gain.gain.setValueAtTime(0, now + at);
      gain.gain.linearRampToValueAtTime(0.18, now + at + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + at + 0.22);
      osc.connect(gain).connect(audioCtx.destination);
      osc.start(now + at);
      osc.stop(now + at + 0.24);
    }
  } catch { /* an engine that refuses to make noise is not an error */ }
}

function paintMute() {
  const muted = !!prefs.muteDone;
  els.dlMute.classList.toggle("muted", muted);
  els.dlMute.setAttribute("aria-pressed", String(muted));
  const label = muted ? t("Download sound is off — click to turn it on")
                      : t("Mute the download-finished sound");
  els.dlMute.title = label;
  els.dlMute.setAttribute("aria-label", label);
}

els.dlMute.addEventListener("click", () => {
  savePrefs({ muteDone: !prefs.muteDone });
  paintMute();
  // Play the thing you just switched on, so the button demonstrates itself
  // rather than leaving you to wait for a download to find out.
  if (!prefs.muteDone) chime();
});

function desktopNotice(title, body) {
  if (!prefs.notifyDone) return;
  if (typeof Notification === "undefined") return;
  // Only worth telling the desktop when the window isn't the thing you are
  // looking at; on screen, the toast has already said it.
  if (document.visibilityState === "visible" && document.hasFocus()) return;

  const show = () => {
    try { new Notification(title, { body, icon: "/icon.png", tag: "romsrx-dl" }); }
    catch { /* some engines refuse from a non-secure origin; the toast stands */ }
  };
  if (Notification.permission === "granted") show();
  else if (Notification.permission !== "denied") {
    Notification.requestPermission().then((p) => { if (p === "granted") show(); })
      .catch(() => { /* older engines take a callback instead; not worth it */ });
  }
}

/* ---------- covers, fetched as games land ----------

   Where a console has a cover folder and the toggle on, the box art is
   fetched the moment its game finishes rather than being right-clicked for
   later. The candidates are resolved in the page first - the same list the
   shelf draws from - so the server is only asked to save a URL already known
   to exist, and a game the thumbnail server has never heard of quietly gets
   nothing rather than an error. */
function firstLoadable(urls) {
  return new Promise((resolve) => {
    let at = 0;
    const tryNext = () => {
      if (at >= urls.length) { resolve(""); return; }
      const url = urls[at++];
      const probe = new Image();
      probe.onload = () => resolve(url);
      probe.onerror = tryNext;
      probe.src = url;
    };
    tryNext();
  });
}

async function autoSaveCover(job) {
  const setup = consoleSetup.get(job.console || "");
  if (!setup?.cover || !setup.coverAuto) return;

  const ext = job.filename.includes(".") ? job.filename.split(".").pop() : "";
  const url = await firstLoadable(
    coverCandidates([{ console: job.console, filename: job.filename, ext }]));
  if (!url) return;             // no art for this one; nothing to save

  try {
    await fetch("/api/cover/save", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, console: job.console,
                             name: `${installStem(job.filename, ext)}.png` }),
    });
  } catch { /* the cover is a nicety; the game already downloaded fine */ }
}

function announceFinished(jobs) {
  if (!jobs.length) return;
  /* The chime answers to the mute button and to nothing else. It is a
     separate control in a separate place from "Tell me when a download
     finishes", and a mute button that silently does nothing because of a
     switch two panels away would be worse than no mute button. */
  chime();
  if (!prefs.notifyDone) return;
  const first = jobs[0].filename;
  const message = jobs.length === 1
    ? t("Downloaded {name}", { name: first })
    : t("Downloaded {name} and {n} more", { name: first, n: jobs.length - 1 });
  toast(message);
  desktopNotice(t("Download finished"), message);
}

async function syncCartWithFinished(jobs) {
  const done = (jobs || []).filter((j) => j.status === "done").map((j) => j.id);
  const fresh = done.filter((id) => !finishedJobs.has(id));
  for (const id of done) finishedJobs.add(id);

  if (!sawFirstPoll) { sawFirstPoll = true; return; }
  if (!fresh.length) return;

  const landed = fresh.map((id) => (jobs || []).find((j) => j.id === id))
                      .filter(Boolean);
  announceFinished(landed);
  for (const job of landed) autoSaveCover(job);

  // Something just landed on disk, so the search's "In Library" markers are
  // out of date. This happens whatever the tidy-the-list setting says.
  fetchLibrary()
    .then(() => { if (libraryOpen) renderLibrary(); })
    .catch(() => { /* the folder will be read again on Refresh */ });

  if (!els.cartClrDone.checked) return;
  await loadCart();
  if (els.cartDlg.open) renderCart();
}

async function pollDownloads() {
  clearTimeout(dlTimer);
  let busy = 0;
  try {
    const state = await fetch("/api/downloads").then((r) => r.json());
    renderDownloads(state);
    busy = state.active + state.queued;
    await syncCartWithFinished(state.jobs);
  } catch { /* server restarting - try again on the next tick */ }
  // Poll briskly while something is happening or the panel is open.
  const open = els.dlDlg.open;
  dlTimer = setTimeout(pollDownloads, busy ? (open ? 700 : 2000) : (open ? 1500 : 8000));
}

// Opened first, filled in after - both so it appears the moment you click,
// and so Back/Forward can tell that a panel opened without waiting on a fetch.
els.dlBtn.addEventListener("click", async () => {
  els.dlDlg.showModal();
  pollDownloads();
  await loadDownloadSettings();
});

/* ---------- taking a row off the list ----------

   Removing a download used to sit there for a second or more before the row
   went, and on a running one for as long as six: `discard` has to tell the
   worker to stop and then wait for it to let go of the file before it can
   delete anything, and the page was waiting for all of that, and then for the
   next poll, before it took the row away. All of that work is real and none of
   it is a reason to keep showing a row the user has already dealt with.

   So the row goes at once and the server catches up behind it. `dropped`
   keeps the poll from putting it back in the meantime - the job is still in
   the server's list until the worker notices - and entries are forgotten
   again as soon as the server stops reporting them, so nothing accumulates
   and a removal that genuinely failed reappears rather than vanishing. */
const dropped = new Set();

function dropJobRow(el) {
  const row = el.closest(".dljob");
  const id = Number(el.dataset.id);
  if (id) dropped.add(id);
  if (!row) return;
  const group = row.closest(".djgroup");
  row.remove();
  // A heading with nothing under it reads as a list that failed to load.
  if (group && !group.querySelector(".dljob")) group.remove();
  if (!els.dlJobs.querySelector(".dljob")) {
    els.dlJobs.innerHTML =
      `<p class="empty">${esc(t("Nothing downloading. Add files from your list."))}</p>`;
  }
  renderedJobs = "";      // the drawn list no longer matches the last signature
}

els.dlJobs.addEventListener("click", async (ev) => {
  const open = ev.target.closest(".dj-open");
  if (open) {
    await fetch("/api/downloads/reveal", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: Number(open.dataset.id) }),
    });
    return;
  }
  // Off the list, files untouched. No confirmation: nothing is destroyed, and
  // the download can be found again by searching for it.
  const forget = ev.target.closest(".dj-forget");
  if (forget) {
    forget.disabled = true;
    dropJobRow(forget);
    await fetch("/api/downloads/forget", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: Number(forget.dataset.id) }),
    });
    pollDownloads();
    return;
  }
  const bin = ev.target.closest(".dj-trash");
  if (bin) {
    // This deletes what is on disk, not just the row, so it gets asked about.
    const row = bin.closest(".dljob");
    const name = row?.querySelector(".dj-name")?.textContent || "this download";
    const go = await ask(
      t('Delete "{name}" from your PC?\n\nThe file is removed from disk, along '
        + "with any part-download. This can't be undone.", { name }),
      { confirm: true, danger: true, ok: t("Delete") });
    if (!go) return;

    bin.disabled = true;
    dropJobRow(bin);
    await fetch("/api/downloads/discard", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: Number(bin.dataset.id) }),
    });
    pollDownloads();
    return;
  }
  const ctl = ev.target.closest(".dj-ctl");
  if (!ctl) return;
  ctl.disabled = true;
  const id = Number(ctl.dataset.id);
  const res = await fetch(`/api/downloads/${ctl.dataset.act}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  }).then((r) => r.json()).catch(() => ({}));
  ctl.disabled = false;
  pollDownloads();

  // Refused because the account it needs is gone. Offer the sign-in, and if
  // they take it, do the resume they actually asked for.
  if (res.needs_login) {
    const row = ctl.closest(".dljob");
    const name = row?.querySelector(".dj-name")?.textContent || "That download";
    if (await promptArchiveLogin(
      `"${name}" comes from a 🔒 login source, and you are signed out.\n`
      + "It kept everything it had already downloaded — sign in here and it "
      + "picks up from where it stopped.")) {
      await fetch("/api/downloads/resume", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      pollDownloads();
    }
  }
});

els.dlBrowse.addEventListener("click", async () => {
  const label = els.dlBrowse.textContent;
  els.dlBrowse.disabled = true;
  els.dlBrowse.textContent = "Choosing…";
  try {
    const res = await fetch("/api/downloads/browse", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start: els.dlFolder.value.trim() }),
    }).then((r) => r.json());
    if (res.folder) {
      els.dlFolder.value = res.folder;    // null when cancelled
      await saveDownloadSettings();       // browsing must persist on its own
    }
  } catch { /* leave the typed path alone */ }
  els.dlBrowse.textContent = label;
  els.dlBrowse.disabled = false;
});

els.dlClear.addEventListener("click", async () => {
  // Same reasoning as a single row: these are already-finished jobs, the
  // server will agree, and waiting for it to say so just makes the button
  // feel broken.
  // The row carries the id as well as the buttons inside it do.
  for (const row of els.dlJobs.querySelectorAll(
    ".dljob.done, .dljob.cancelled, .dljob.error")) dropJobRow(row);
  await fetch("/api/downloads/clear", { method: "POST" });
  pollDownloads();
});

els.dlPauseAll.addEventListener("click", async () => {
  els.dlPauseAll.disabled = true;
  const res = await fetch(`/api/downloads/${els.dlPauseAll.dataset.act}`,
    { method: "POST" }).then((r) => r.json()).catch(() => ({}));
  els.dlPauseAll.disabled = false;
  pollDownloads();

  // Some of the batch needs the account we no longer have. One sign-in
  // unblocks the lot, so it is offered once rather than per download.
  if (res.blocked > 0 && await promptArchiveLogin(
    `${res.blocked} of these come from 🔒 login sources, and you are signed `
    + "out.\nSign in here and they will resume from where they stopped.")) {
    await fetch("/api/downloads/resumeall", { method: "POST" });
    pollDownloads();
  }
});

// Deletes files, so make sure it was meant.
els.dlRemoveAll.addEventListener("click", async () => {
  const total = els.dlJobs.querySelectorAll(".dljob").length;
  const go = await ask(
    t("Remove all {n} downloads and delete their files from your PC?\n\n"
      + "Finished files and part-downloads are both deleted.", { n: total }),
    { confirm: true, danger: true, ok: t("Remove all") });
  if (!go) return;
  els.dlRemoveAll.disabled = true;
  els.dlRemoveAll.textContent = t("Removing…");
  // Emptied on screen straight away. Deleting the files takes as long as it
  // takes - a running download has to be stopped and released first - but
  // none of that is a reason to keep the list on screen while it happens.
  for (const row of els.dlJobs.querySelectorAll(".dljob")) dropJobRow(row);
  await fetch("/api/downloads/discardall", { method: "POST" });
  els.dlRemoveAll.textContent = t("Remove all");
  els.dlRemoveAll.disabled = false;
  pollDownloads();
});

async function loadDownloadSettings() {
  try {
    const s = await fetch("/api/downloads/settings").then((r) => r.json());
    els.dlFolder.value = s.folder || "";
    // 0 is the stored value for "Unlimited", so don't fall back on it.
    els.dlWorkers.value = String(s.workers ?? 3);
    els.dlExtract.checked = !!s.extract;
    els.dlExtractMode.value = s.extract_mode === "here" ? "here" : "folder";
    els.dlExtractMode.disabled = !s.extract;
    els.dlDelete.checked = !!s.delete_archive;
    els.dlDelete.disabled = !s.extract;
    els.perConsole.checked = !!s.per_console;
    els.cartClrDone.checked = !!s.clear_when_done;
    els.notifyDone.checked = !!prefs.notifyDone;
    syncWorkerInfo();
    } catch { /* leave whatever is on screen */ }
}

/* Taking finished downloads off the list is the server's job - it has to
   happen for things that finish while this dialog, or the whole window, is
   shut. All the page does is set the switch and pick the change up again. */
els.notifyDone.addEventListener("change", () => {
  savePrefs({ notifyDone: els.notifyDone.checked });
});

els.cartClrDone.addEventListener("change", async () => {
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ clear_when_done: els.cartClrDone.checked }),
  });
});

// The caveat only matters when Unlimited is chosen, so only show it then.
// The warning only earns its place once the number is high enough for
// archive.org to start pushing back.
function syncWorkerInfo() {
  els.dlWorkerInfo.hidden = Number(els.dlWorkers.value) < 4;
}

els.dlWorkers.addEventListener("change", syncWorkerInfo);

els.dlExtract.addEventListener("change", () => {
  els.dlDelete.disabled = !els.dlExtract.checked;
  els.dlExtractMode.disabled = !els.dlExtract.checked;
});

// Settings save themselves - there's no Save button to forget.
async function saveDownloadSettings() {
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      folder: els.dlFolder.value.trim(),
      workers: Number(els.dlWorkers.value),
      extract: els.dlExtract.checked,
      extract_mode: els.dlExtractMode.value,
      delete_archive: els.dlDelete.checked,
      per_console: els.perConsole.checked,
    }),
  });
  els.dlSaved.hidden = false;
  clearTimeout(saveDownloadSettings.timer);
  saveDownloadSettings.timer = setTimeout(() => { els.dlSaved.hidden = true; }, 1400);
}

// Typing waits for a pause; the rest apply on the spot.
const saveSettingsSoon = debounce(saveDownloadSettings, 700);
els.dlFolder.addEventListener("input", saveSettingsSoon);
for (const control of [els.dlWorkers, els.dlExtract, els.dlExtractMode,
                       els.dlDelete]) {
  control.addEventListener("change", saveDownloadSettings);
}

// Backdrop dismissal: see closeOnBackdrop(), which covers every dialog.

/* ---------- library ---------- */

let libraryData = null;
let libraryOpen = false;
let libSelectMode = false;
const libSelected = new Set();

/* ---------- tiles ----------

   What the shelf draws, whichever shelf it is. The whole library is a list of
   games on disk; a playlist is a list of entries, each of which may or may not
   have a game on disk behind it yet. Both become the same shape here, so one
   set of renderers covers both and a playlist looks like the library rather
   than like a second, lesser thing. */

/** The copy on disk for a playlist entry, or null when it isn't downloaded.
 *
 *  The path is tried first for an entry that came out of the library, then
 *  the same name-join the "In Library" markers use - which is what picks the
 *  game up once it finally lands, without the entry having been touched. */
function resolveEntry(entry) {
  if (entry.path) {
    const exact = gameAt(entry.path);
    if (exact) return exact;
  }
  const hits = installedIndex.get(installKey(installStem(entry.name, entry.ext)));
  if (!hits?.length) return null;
  return hits.find((g) => (g.console || "") === (entry.console || ""))
    || hits.find((g) => !g.console) || null;
}

/** A readable title for a game that isn't here yet. The library gets its
 *  titles from the indexer; a playlist entry only has the filename, so the
 *  bracketed groups come off the end the same way. */
function looseTitle(stem) {
  let out = stem;
  for (;;) {
    const trimmed = out.replace(/\s*[([][^()[\]]*[)\]]\s*$/, "").trim();
    if (!trimmed || trimmed === out) return out;
    out = trimmed;
  }
}

function tileFromGame(game) {
  return {
    game, entry: null, key: entryKey(game.console, game.name, ""),
    console: game.console || "", name: game.name, title: game.title,
    size: game.size, path: game.path, cover: game.cover || "",
  };
}

function tileFromEntry(entry) {
  const game = resolveEntry(entry);
  return {
    game, entry, key: entry.key,
    console: game?.console || entry.console || "",
    name: game?.name || entry.name,
    title: game?.title || looseTitle(entry.name),
    size: game?.size ?? entry.size ?? 0,
    path: game?.path || "",
    cover: game?.cover || "",
    art: entry.art || "",       // the cover this game was wearing when added
    alts: entry.alts || [],     // ...and the other names to look under
  };
}

/** The playlist entry a tile stands for. In the library proper there is no
 *  entry yet, so one is made from the game - which is exactly what gets put
 *  on a shelf when the + is used there. */
function entryForCard(card) {
  if (!card) return null;
  const pl = currentPlaylist();
  const found = pl?.items.find((i) => i.key === card.dataset.key);
  if (found) return found;
  const game = gameAt(card.dataset.path);
  if (!game) return null;
  const entry = entryFromGame(game);
  // Keep the artwork with the entry, so a game put on a shelf and later
  // deleted from disk is still recognisable there.
  entry.art = shownCoverFor(card);
  return entry;
}

/** Library names are already No-Intro stems, so they feed the cover lookup
 *  directly with no extension to strip.
 *
 *  Order is the order of confidence: a cover the user chose themselves, then
 *  the one this game was actually wearing when it went onto a shelf, then the
 *  names worked out from the filename. The middle one is why a playlist tile
 *  shows the same picture the search did even when the file's own name has no
 *  art of its own - and it is still only a first guess, so a URL that has
 *  since gone stale falls through to the rest. */
function libCovers(tile) {
  const urls = [tile.cover, tile.art].filter(isCoverUrl);
  // Its own name first, then the other names the same game answers to, which
  // is exactly the list a search result gets to work with.
  const files = [tile.name, ...(tile.alts || [])]
    .map((filename) => ({ console: tile.console, filename, ext: "" }));
  for (const url of coverCandidates(files)) {
    if (!urls.includes(url)) urls.push(url);
  }
  return urls;
}

/** The image itself carries `libhit`, so only the artwork is clickable -
 *  not the empty space a narrower cover leaves in its tile. A game that isn't
 *  downloaded has nothing to open, so it doesn't get the class at all.
 *
 *  `data-title` is what the tile falls back to once every candidate has
 *  404'd. Without it the tile ends up genuinely blank, which in a wall of
 *  covers reads as a broken row rather than a game with no art. The list view
 *  gets the console instead - its thumbnail is far too small for a title, and
 *  the name is already spelled out beside it. */
function libCoverHtml(tile, big, extra = "") {
  const urls = libCovers(tile);
  const cls = big ? "libart" : "librowart";
  const hit = tile.game ? " libhit" : "";
  const label = big ? (tile.title || tile.name) : (tile.console || "?");
  /* The artwork sits inside a wrapper that shrinks to the picture rather than
     to the tile. Consoles have different case shapes, and a row that mixes
     them - Continue playing does, by definition - gives every tile the same
     box, so a squarer cover floats in it with a band of empty space. The
     wrapper is what the tile centres, and it is also what the hover controls
     are positioned against, so they stay on the picture instead of drifting
     off the bottom of it. */
  if (!urls.length) {
    return `<span class="${cls}"><span class="artwrap artfill"><span
      class="noart${hit}">${esc(label)}</span>${extra}</span></span>`;
  }
  return `<span class="${cls}"><span class="artwrap"><img class="${hit.trim()}"
    src="${esc(urls[0])}"
    data-rest='${esc(JSON.stringify(urls.slice(1)))}'
    data-title="${esc(label)}" alt="" loading="lazy"
    decoding="async" onerror="coverFail(this)">${extra}</span></span>`;
}

/* One arrow, matching the header's Downloads icon, for the button that
   fetches a game a playlist is still waiting on. */
const GET_ICON = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v10"/><path d="M8 10.5l4 4 4-4"/><path d="M5 19h14"/></svg>`;

/** Where this game goes, and - for one that isn't here yet - fetching it.
 *
 *  They live along the bottom edge of the artwork rather than in a corner of
 *  the tile: box art is not all one shape, and a control pinned to the tile
 *  ends up floating in the empty space beside a narrow cover instead of on
 *  the game it belongs to. Centred, so they stay on the picture whatever its
 *  width. Hidden while selecting, where the whole tile is a target and a
 *  button inside it would only steal the click. */
function tileActions(tile) {
  const get = (!tile.game && tile.entry?.url)
    ? `<button class="plget" title="${esc(t("Download now"))}"
        aria-label="${esc(t("Download now"))}">${GET_ICON}</button>`
    : "";
  return `<span class="libadds">${get}<button class="libadd"
    aria-haspopup="menu" aria-label="${esc(t("Add to…"))}">+</button></span>`;
}

const tileAttrs = (tile) => `data-key="${esc(tile.key)}"${
  tile.path ? ` data-path="${esc(tile.path)}"` : ""}`;

// Picked state is painted on afterwards by paintSelection(), never baked in
// here - re-rendering the markup for a tick would reload every cover image.
/* A game that isn't downloaded is drained of colour and says so in as many
   words. Both, because neither is enough on its own: grey artwork reads at a
   glance across a shelf, but a game with no box art has only a plain
   placeholder to grey, and greying that says nothing at all.
   The label rides at the top of the artwork and the buttons along the bottom,
   so the two never have to share an edge whatever shape the cover is. */
function libGridCard(tile) {
  const hit = tile.game ? " libhit" : "";
  const badge = tile.game ? ""
    : `<span class="plmiss">${esc(t("Not downloaded"))}</span>`;
  return `
    <div class="libcard${tile.game ? "" : " missing"}" ${tileAttrs(tile)}
         title="${esc(tile.game ? tile.name : `${tile.name} — ${t("Not downloaded")}`)}">
      ${libCoverHtml(tile, true, badge + tileActions(tile))}
      <span class="libtick"></span>
      <span class="libname${hit}">${esc(tile.title)}</span>
    </div>`;
}

function libListRow(tile) {
  const game = tile.game;
  const bits = [];
  if (game) {
    if (game.regions.length) bits.push(game.regions.join(", "));
    if (game.languages.length) bits.push(game.languages.join(", "));
    if (game.version) bits.push(game.version);
    if (game.disc) bits.push(`Disc ${game.disc}`);
    if (game.tags.length) bits.push(game.tags.join(", "));
    bits.push(game.extracted ? `folder · ${game.files} file${game.files === 1 ? "" : "s"}`
                             : (game.ext || "file").toUpperCase());
  } else {
    bits.push(t("Not downloaded"));
    if (tile.entry?.source) bits.push(tile.entry.source);
  }
  const hit = game ? " libhit" : "";
  return `
    <div class="librow${game ? "" : " missing"}" ${tileAttrs(tile)}>
      <span class="libtick"></span>
      ${libCoverHtml(tile, false)}
      <span class="librowname${hit}">${esc(tile.name)}
        <span class="librowsub">${bits.map(esc).join(" &middot; ")}</span>
      </span>
      <span class="librowsize">${tile.size ? humanSize(tile.size) : ""}</span>
      ${tileActions(tile)}
    </div>`;
}

/** The console menu, counted from whatever shelf is on screen - so a playlist
 *  offers its own consoles rather than every console you own. */
function renderLibraryConsoles(tiles) {
  const counts = new Map();
  for (const tile of tiles) {
    const key = tile.console || "Unsorted";
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  const keep = els.libConsole.value;
  els.libConsole.innerHTML =
    `<option value="">${esc(t("All consoles"))} (${tiles.length})</option>`
    + [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([name, n]) =>
        `<option value="${esc(name)}">${esc(name)} (${n})</option>`).join("");
  els.libConsole.value = counts.has(keep) ? keep : "";
}

/* ---------- shelves ----------
   The whole library, then one chip per playlist. Which one is showing is a
   preference, so the shelf you were last on is the one you come back to. */

function currentPlaylist() {
  return prefs.libShelf ? playlistById(prefs.libShelf) : null;
}

function shelfChip(id, name, count, on) {
  return `<button class="shelf${on ? " on" : ""}" data-id="${esc(id)}">
    <span class="shelfname">${esc(name)}</span>
    <span class="shelfn">${count}</span></button>`;
}

function renderShelves() {
  const here = currentPlaylist();
  els.libShelves.innerHTML =
    shelfChip("", t("All games"), libraryData?.total ?? 0, !here)
    + playlists.map((pl) =>
        shelfChip(pl.id, pl.name, pl.items.length, here?.id === pl.id)).join("");
}

/** The per-playlist controls. The two that act on games you haven't got carry
 *  their own count, and disappear when there are none - a playlist you have
 *  every game for shouldn't be offering to fetch them. */
function paintPlaylistActions(pl) {
  els.libPlActions.hidden = !pl;
  if (!pl) return;
  const missing = pl.items.filter((e) => e.url && !resolveEntry(e));
  els.libPlGet.hidden = !missing.length;
  els.libPlCart.hidden = !missing.length;
  els.libPlGet.textContent = `${t("Download missing")} (${missing.length})`;
  els.libPlCart.textContent = `${t("Add missing to list")} (${missing.length})`;
}

/** Does this tile answer to what was typed in the library's search box?
 *
 *  Every word has to appear somewhere, in any order - "kart mario" finds Mario
 *  Kart just as "mario kart" does, which matters when you half-remember a
 *  title. The console is searchable too, so "gba zelda" narrows in one go. */
function tileMatches(tile, needle) {
  const hay = `${tile.title} ${tile.name} ${tile.console || ""}`.toLowerCase();
  return needle.split(/\s+/).every((word) => hay.includes(word));
}

/* ---------- continue playing ----------

   The games you actually opened, newest first, above everything else. A
   library sorted by console and then alphabetically is a filing cabinet: it
   is very good at "where is X" and no use at all for "what was I playing".

   On a playlist it is filtered to that playlist, because a shelf you made is
   a context - what you played on it, not what you played anywhere. A shelf
   with nothing played on it gets no row rather than an empty one. */
let recentlyPlayed = [];
/* Everything you have played, not a top eight. The row scrolls sideways, so a
   long history costs nothing on screen - and the games you want are at the
   front of it anyway. The cap is only here so that a library where every game
   has been opened can't put four thousand tiles in the DOM. */
const RECENT_SHOWN = 200;

async function loadRecent() {
  try {
    const data = await fetch("/api/recent").then((r) => r.json());
    recentlyPlayed = data.recent || [];
  } catch { /* the shelf is still perfectly usable without it */ }
}

/* Two sources, one row.

   The stored list is what this app launched, and it is the better witness:
   it knows the exact moment and it cannot be wrong about it. The scan's
   `playedAt` is what the filesystem says about games opened from the
   emulator directly - the only way to see a session this app had no part in.

   Merged on the path, newest wins. A game played both ways keeps whichever
   was later, so launching from here doesn't push a more recent outside
   session down the row, and vice versa. */
function playHistory() {
  // Keyed on the path where there is one, since that is what both sources
  // agree on. A stored entry from a playlist may only have a `key`, so it
  // keeps that as a second way to find its tile.
  const seen = new Map();
  const note = (id, when, alt) => {
    if (!id) return;
    const had = seen.get(id);
    if (had) had.at = Math.max(had.at, when);
    else seen.set(id, { path: id, key: alt || "", at: when });
  };
  for (const entry of recentlyPlayed) {
    note(entry.path || entry.key, Number(entry.at) || 0, entry.key);
  }
  for (const game of libraryData?.games || []) {
    if (game.playedAt) note(game.path, game.playedAt, "");
  }
  return [...seen.values()].sort((a, b) => b.at - a.at);
}

/** The recently played games that are on the shelf being shown, as tiles. */
function recentTiles(playlist, all) {
  const order = playHistory();
  if (!order.length) return [];
  const here = new Map();
  for (const tile of all) {
    if (tile.path) here.set(tile.path, tile);
    if (tile.key && !here.has(tile.key)) here.set(tile.key, tile);
  }
  const out = [];
  for (const entry of order) {
    // Matched on the path first: two consoles can hold a game of the same
    // name, and the file you launched is the one you were playing.
    const tile = here.get(entry.path) || here.get(entry.key);
    if (!tile || out.includes(tile)) continue;
    if (playlist && !inPlaylist(playlist, tile.entry || { key: tile.key })) continue;
    out.push(tile);
    if (out.length >= RECENT_SHOWN) break;
  }
  return out;
}

/** Show each arrow only where there is something that way to scroll to.
 *
 *  The markup ships them hidden, so a row that fits on screen never grows a
 *  pair of buttons that would do nothing. */
function paintRecentNav() {
  const rail = els.libBody.querySelector(".recentrail");
  if (!rail) return;
  const strip = rail.closest(".recentstrip");
  const prev = strip.querySelector(".recentnav.prev");
  const next = strip.querySelector(".recentnav.next");
  /* Several pixels of slack rather than one. Scroll snapping settles a few
     px off the true ends - back at the start it reads 2, not 0 - and a
     one-pixel threshold left the back arrow showing with nowhere to go. */
  const slack = 8;
  const room = rail.scrollWidth - rail.clientWidth;
  prev.hidden = rail.scrollLeft <= slack;
  next.hidden = rail.scrollLeft >= room - slack;
}

els.libBody.addEventListener("click", (ev) => {
  const button = ev.target.closest(".recentnav");
  if (!button) return;
  ev.stopPropagation();          // not a click on whatever tile is behind it
  const rail = button.closest(".recentstrip").querySelector(".recentrail");
  // Most of a screenful, so something stays in view to keep your place.
  const step = Math.max(200, rail.clientWidth * 0.8);
  rail.scrollBy({ left: step * Number(button.dataset.scroll), behavior: "smooth" });
});

els.libBody.addEventListener("scroll", (ev) => {
  if (ev.target.classList?.contains("recentrail")) paintRecentNav();
}, true);

window.addEventListener("resize", debounce(paintRecentNav, 200));

function renderLibrary() {
  if (!libraryData) return;
  // A playlist deleted in another window leaves the preference pointing at
  // nothing; fall back to the whole library rather than to an empty shelf.
  if (prefs.libShelf && !playlistById(prefs.libShelf)) savePrefs({ libShelf: "" });

  const pl = currentPlaylist();
  renderShelves();
  paintPlaylistActions(pl);

  const all = pl ? pl.items.map(tileFromEntry)
                 : libraryData.games.map(tileFromGame);
  renderLibraryConsoles(all);

  const total = all.length;
  const wanted = els.libConsole.value;
  const needle = els.libQ.value.trim().toLowerCase();
  let tiles = wanted ? all.filter((tile) => (tile.console || "Unsorted") === wanted) : all;
  if (needle) tiles = tiles.filter((tile) => tileMatches(tile, needle));
  const shownBytes = tiles.reduce((n, tile) => n + (tile.size || 0), 0);
  const narrowed = wanted || needle;

  // No folder path here - with per-console paths there isn't a single one.
  const missing = pl ? tiles.filter((tile) => !tile.game).length : 0;
  els.libStats.textContent = !total
    ? (pl ? t("This playlist is empty") : t("No games found"))
    : (narrowed
        ? `${tiles.length} of ${total} games · ${humanSize(shownBytes)}`
        : `${total.toLocaleString()} game${total === 1 ? "" : "s"} · ${humanSize(shownBytes)}`)
      + (missing ? ` · ${missing} ${t("not downloaded")}` : "");

  els.libGrid.classList.toggle("on", prefs.libView === "grid");
  els.libList.classList.toggle("on", prefs.libView === "list");
  els.libTitlesWrap.hidden = prefs.libView !== "grid";
  els.libSizeWrap.hidden = prefs.libView !== "grid";
  els.libBody.style.setProperty("--cover", `${prefs.libSize}px`);
  els.libBody.classList.toggle("notitles", !prefs.libTitles);

  if (!tiles.length) {
    els.libBody.innerHTML = total
      ? `<p class="empty">${needle
          ? `Nothing here matches “${esc(els.libQ.value.trim())}”.`
          : t("No games for that console.")}</p>`
      : (pl
          ? `<p class="empty">${esc(t("Nothing on this playlist yet — use the + "
              + "button on any game, in the search or in your library."))}</p>`
          : `<p class="empty">No games here yet. Anything you download lands in this
             folder and will show up on Refresh.</p>`);
    paintSelection();
    paintFound();
    return;
  }

  // Grouped by console, which is also how the folders are laid out. Sorting
  // happens inside each group, so titles never mix across consoles.
  const order = {
    "name": (a, b) => a.title.localeCompare(b.title, undefined, { numeric: true }),
    "name-desc": (a, b) => b.title.localeCompare(a.title, undefined, { numeric: true }),
    "size-desc": (a, b) => b.size - a.size,
    "size": (a, b) => a.size - b.size,
  }[prefs.libSort] || ((a, b) => a.title.localeCompare(b.title));

  const groups = new Map();
  for (const tile of tiles) {
    const key = tile.console || "Unsorted";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(tile);
  }
  for (const list of groups.values()) list.sort(order);

  // Pinned consoles rise to the top, in the order they were pinned - the
  // first one you star stays first. Only meaningful when every console is on
  // screen; with one selected there is nothing to order.
  const showingAll = !wanted;
  const pinnedList = prefs.libPinned || [];
  const order2 = [...groups.entries()];
  if (showingAll) {
    order2.sort(([a], [b]) => pinRank(a) - pinRank(b) || a.localeCompare(b));
  }

  const render = prefs.libView === "grid" ? libGridCard : libListRow;
  // Above every console, and only when there is something in it.
  const recent = recentTiles(pl, tiles);
  /* Games opened straight from an emulator are found by when their files
     were last read, and Windows can be told to stop recording that. Where it
     has been, the row can only ever show what this app launched itself - so
     it says so once, on the heading, rather than quietly being shorter than
     the user expects. */
  const blind = libraryData?.reads_tracked === false;
  /* Not a console, so it is deliberately not shaped like one: the heading sits
     in the middle of the row rather than hard left where every console name
     is, and it is larger. The whole history goes in - it scrolls sideways
     instead of stopping at the first handful - with a button at each end for
     anyone without a horizontal wheel or a trackpad. */
  const recentHtml = recent.length ? `
    <section class="libgroup librecent">
      <h3 class="libhead recenthead">
        <span class="badge console">${esc(t("Continue playing"))}</span>
        <span class="libcount">${recent.length}</span>${blind ? `
        <span class="infoicon" tabindex="0" data-tip="Only games launched from this app are listed. This PC is not recording when files are read, so games opened straight from an emulator cannot be spotted. Turn it back on with: fsutil behavior set DisableLastAccess 2">i</span>` : ""}</h3>
      <div class="recentstrip">
        <button class="recentnav prev" data-scroll="-1" aria-label="${esc(t("Scroll back"))}"
                title="${esc(t("Scroll back"))}" hidden>&#10094;</button>
        <div class="recentrail ${prefs.libView === "grid" ? "libgrid" : "liblist"}">
          ${recent.map(render).join("")}
        </div>
        <button class="recentnav next" data-scroll="1" aria-label="${esc(t("Scroll on"))}"
                title="${esc(t("Scroll on"))}" hidden>&#10095;</button>
      </div>
    </section>` : "";

  els.libBody.innerHTML = recentHtml + order2.map(([console_, items]) => {
    const at = pinnedList.indexOf(console_);
    const pinned = at >= 0;
    const shut = isCollapsed(console_);
    // Pinning is offered even with one console filtered - otherwise you'd
    // have to clear the filter and scroll to find it again just to star it.
    // Reordering, though, needs the whole list in view to make any sense.
    const canMove = showingAll && pinned && pinnedList.length > 1;
    const arrows = canMove ? `
      <button class="libmove" data-console="${esc(console_)}" data-move="-1"
        title="Move up"${at === 0 ? " hidden" : ""}>&#9650;</button>
      <button class="libmove" data-console="${esc(console_)}" data-move="1"
        title="Move down"${at === pinnedList.length - 1 ? " hidden" : ""}>&#9660;</button>` : "";
    return `
    <section class="libgroup${shut ? " shut" : ""}">
      <h3 class="libhead">
        <button class="libpickall" data-console="${esc(console_)}"
          title="Select every ${esc(console_)} game" aria-label="Select all"></button>
        <button class="libfold" data-console="${esc(console_)}"
          title="${shut ? "Show" : "Hide"} these games"
          aria-expanded="${!shut}">&#9662;</button>
        <button class="libname-btn" data-console="${esc(console_)}"
          title="${shut ? "Show" : "Hide"} these games">
          <span class="badge console">${esc(console_)}</span>
        </button>
        <span class="libcount">${items.length}</span>
        <span class="libpinctl">${arrows}
          <button class="libpin${pinned ? " on" : ""}"
            data-console="${esc(console_)}"
            title="${pinned ? "Unpin" : "Pin to the top"}"
            aria-pressed="${pinned}">&#9733;</button>
        </span>
      </h3>
      <div class="${prefs.libView === "grid" ? "libgrid" : "liblist"}">
        ${items.map(render).join("")}
      </div>
    </section>`;
  }).join("");

  paintSelection();
  // Fresh cards, so the highlight has to be put back on whichever one is lit.
  paintFound();
  paintRecentNav();
}

/* Shape a console's tiles like its actual covers.
 *
 *  Box art varies a lot by system - Game Boy boxes are nearly square, PSP
 *  cases are tall - and a fixed 3:4 tile letterboxes most of them. The first
 *  cover to load in each group decides the shape for that group, and it is
 *  then left alone: re-measuring on every image would have the grid twitching
 *  as covers trickle in.
 *
 *  `load` doesn't bubble, so this listens in the capture phase. */
function matchArtRatio(img) {
  const group = img.closest(".libgroup");
  if (!group || group.dataset.ratio || !img.naturalWidth || !img.naturalHeight) return;
  group.dataset.ratio = "1";
  group.style.setProperty("--artratio",
    `${img.naturalWidth} / ${img.naturalHeight}`);
}

/** Give the wrapper the shape of the picture inside it.
 *
 *  The tile is shaped like the group's covers; this is shaped like *this*
 *  cover. Where the two differ - a PlayStation case in a row that also holds
 *  PS2 cases - the wrapper ends up shorter than the tile and gets centred in
 *  it, and the buttons that hang off its bottom edge stay on the artwork.
 *  Where they agree, which is every single-console shelf, the wrapper fills
 *  the tile and nothing about the layout changes. */
function fitArtWrap(img) {
  const wrap = img.closest(".artwrap");
  if (!wrap || !img.naturalWidth || !img.naturalHeight) return;
  wrap.style.setProperty("--own", `${img.naturalWidth} / ${img.naturalHeight}`);
}

els.libBody.addEventListener("load", (ev) => {
  const img = ev.target;
  if (!(img instanceof HTMLImageElement) || !img.closest(".libart")) return;
  matchArtRatio(img);
  fitArtWrap(img);
}, true);

/* Pinned and collapsed consoles. Both are per-console and both survive a
   restart, so they live in prefs rather than in a variable.

   `libPinned` is a list in display order, not a set: pinning appends, so the
   first console you star stays at the top and later ones queue up beneath it.
   The arrows rearrange that list directly. */
const isPinned = (console_) => (prefs.libPinned || []).includes(console_);
const isCollapsed = (console_) => (prefs.libShut || []).includes(console_);

/** Sort key: pinned consoles by their place in the list, everything else
 *  after them. Equal ranks fall through to an alphabetical tiebreak, so this
 *  must be a real number rather than Infinity - subtracting two Infinities
 *  gives NaN, and a NaN comparator scrambles the order. */
function pinRank(console_) {
  const at = (prefs.libPinned || []).indexOf(console_);
  return at < 0 ? Number.MAX_SAFE_INTEGER : at;
}

function toggleInPref(key, value) {
  const list = [...(prefs[key] || [])];
  const at = list.indexOf(value);
  if (at >= 0) list.splice(at, 1); else list.push(value);
  savePrefs({ [key]: list });
}

/** Swap a pinned console with its neighbour. */
function movePinned(console_, delta) {
  const list = [...(prefs.libPinned || [])];
  const at = list.indexOf(console_);
  const to = at + delta;
  if (at < 0 || to < 0 || to >= list.length) return;
  [list[at], list[to]] = [list[to], list[at]];
  savePrefs({ libPinned: list });
}

/** Selection is painted onto the existing nodes instead of re-rendering the
 *  library: a full innerHTML rebuild drops every cover image and re-fetches
 *  it, which made ticking a game flicker and lose the scroll position. */
function paintSelection() {
  els.libSelect.classList.toggle("on", libSelectMode);
  els.libSelect.textContent = t(libSelectMode ? "Done" : "Select");
  els.libRemove.hidden = !libSelected.size;
  els.libRemove.textContent = `${t("Remove")} (${libSelected.size})`;
  els.libBody.classList.toggle("selecting", libSelectMode);

  // Putting a run of games on a shelf in one go, and - only on a playlist -
  // taking them off it. Off the shelf, not off the disk: the Remove beside
  // them is the one that deletes, and the two must never read as the same
  // button wearing different words.
  els.libAddPl.hidden = !libSelected.size;
  els.libAddPl.textContent = `${t("Add to playlist")} (${libSelected.size})`;
  els.libPlRemove.hidden = !libSelected.size || !currentPlaylist();
  els.libPlRemove.textContent = `${t("Remove from playlist")} (${libSelected.size})`;

  // The same button both ways round, so its label always says what pressing
  // it will do rather than what state you are in.
  const shown = shownPaths();
  const allShownPicked = shown.length > 0 && shown.every((p) => libSelected.has(p));
  els.libSelectAll.disabled = !shown.length;
  els.libSelectAll.classList.toggle("on", allShownPicked);
  els.libSelectAll.textContent =
    `${t(allShownPicked ? "Deselect all" : "Select all")} (${shown.length})`;

  for (const el of els.libBody.querySelectorAll("[data-path]")) {
    const on = libSelected.has(el.dataset.path);
    el.classList.toggle("picked", on);
    const tick = el.querySelector(".libtick");
    if (tick) tick.innerHTML = on ? "&#10003;" : "";
  }
  for (const button of els.libBody.querySelectorAll(".libpickall")) {
    const paths = groupPaths(button.closest(".libgroup"));
    const all = paths.length > 0 && paths.every((p) => libSelected.has(p));
    button.classList.toggle("on", all);
    button.innerHTML = all ? "&#10003;" : "";
  }
}

const groupPaths = (group) =>
  [...group.querySelectorAll("[data-path]")].map((el) => el.dataset.path);

/** Every visible game, top to bottom, so shift-click can span consoles. */
const shownPaths = () =>
  [...els.libBody.querySelectorAll("[data-path]")].map((el) => el.dataset.path);

function selectRange(from, to) {
  const paths = shownPaths();
  const a = paths.indexOf(from), b = paths.indexOf(to);
  if (a < 0 || b < 0) return false;
  for (const p of paths.slice(Math.min(a, b), Math.max(a, b) + 1)) libSelected.add(p);
  return true;
}

/* ---------- what you already have ----------

   The search lists what archive.org holds; the library is what is on this
   machine. Crossing the two means a result can say "you already have this"
   instead of letting you download a second copy and find out afterwards.

   The join is on the filename without its extension. That sounds fragile and
   isn't: both sides are No-Intro/Redump names, and the downloader writes the
   file under exactly the name the index gave it - so `Game (USA).zip` lands as
   either `Game (USA).zip` or, once extracted, a folder called `Game (USA)`,
   and the library reports the stem either way. */
const installedIndex = new Map();     // normalised stem -> games with that name

/* Games by their path, which is what every part of the page holds onto: a
   card, a menu and a tick all identify a game that way. Scanning the list for
   each one was fine when the only caller was a click; it is not once a repaint
   asks the same question of every tile on screen, which turns a big library
   into a quadratic amount of work on every keystroke in the search box. */
const gamesByPath = new Map();

const gameAt = (path) => (path ? gamesByPath.get(path) : undefined) || null;

const installKey = (name) =>
  String(name || "").toLowerCase().replace(/\s+/g, " ").trim();

function buildInstalledIndex() {
  installedIndex.clear();
  gamesByPath.clear();
  for (const game of libraryData?.games || []) {
    gamesByPath.set(game.path, game);
    const key = installKey(game.name);
    if (!key) continue;
    if (!installedIndex.has(key)) installedIndex.set(key, []);
    installedIndex.get(key).push(game);
  }
}

/** A filename with its extension taken off, matching how the library names
 *  what it found: a downloaded file keeps its name, and an extracted one
 *  becomes a folder called the same thing without the archive suffix. */
function installStem(name, ext) {
  const suffix = ext ? `.${ext.toLowerCase()}` : "";
  return suffix && name.toLowerCase().endsWith(suffix)
    ? name.slice(0, -suffix.length) : name;
}

/** The copy on disk for a whole console section, or null.
 *
 *  Deliberately per console rather than per file. Which exact file produced
 *  the copy on disk is not knowable once an archive has been extracted - the
 *  folder keeps the name and loses the extension, so a `.zip` and a `.7z` of
 *  the same game are indistinguishable afterwards. Answering "you have this
 *  game, on this console" is a question that can be answered honestly;
 *  "you have this exact file" cannot.
 *
 *  Console has to agree, unless the copy on disk is unsorted - which is what
 *  everything is when "folder per console" is off. */
function installedForSection(files, console_) {
  for (const { name, ext } of files) {
    const hits = installedIndex.get(installKey(installStem(name, ext)));
    if (!hits?.length) continue;
    const hit = hits.find((g) => g.console === console_)
      || hits.find((g) => !g.console);
    if (hit) return hit;
  }
  return null;
}

/* Painted onto the rendered rows rather than baked into them, because the two
   arrive in either order: the library scan reads the disk and can easily
   finish after the first search has already drawn, and a download finishing
   changes the answer for a page that is sitting there untouched. */
function paintInstalled() {
  for (const slot of els.results.querySelectorAll(".finst")) {
    // The section's own rows are the source of truth for what it lists, so
    // nothing has to be duplicated onto the marker itself.
    const rows = [...slot.closest(".consec").querySelectorAll("button.dl")];
    const files = rows.map((b) => ({ name: b.dataset.name, ext: b.dataset.ext }));
    const game = installedForSection(files, rows[0]?.dataset.console || "");

    slot.hidden = !game;
    if (!game) {
      delete slot.dataset.path;
      continue;
    }
    slot.dataset.path = game.path;
    slot.innerHTML = `<span class="finst-tick">&#10003;</span>${esc(t("In Library"))}`;
    slot.title = `Already in your library — click to show it\n${game.path}`;
  }
}

/** Read the library from disk and update anything that depends on it. Kept
 *  apart from loadLibrary() so the search can have this without the library
 *  view being drawn - at startup it usually isn't even on screen. */
/* Which consoles have a cover folder or an emulator set. Read alongside the
   library so the right-click menu can offer only what will actually work,
   rather than showing entries that answer with "nothing is configured". */
const consoleSetup = new Map();

async function loadConsoleSetup() {
  try {
    const { consoles } = await fetch("/api/downloads/folders").then((r) => r.json());
    consoleSetup.clear();
    for (const row of consoles || []) {
      consoleSetup.set(row.console, { cover: !!row.cover, emulator: !!row.emulator,
                                     coverAuto: !!row.coverAuto });
    }
  } catch { /* the menu simply offers less */ }
}

async function fetchLibrary() {
  await loadConsoleSetup();
  libraryData = await fetch("/api/library").then((r) => r.json());
  // Games that were deleted or renamed must not keep padding "Remove (n)".
  const alive = new Set(libraryData.games.map((g) => g.path));
  for (const p of libSelected) if (!alive.has(p)) libSelected.delete(p);
  buildInstalledIndex();
  paintInstalled();
}

/** Take deleted games off the shelf now, and re-read the disk quietly after.
 *
 *  `loadLibrary()` blanks the view to "Reading your folders…" and walks every
 *  download folder before anything reappears, which after a deletion means
 *  the whole library flickers away and comes back just to lose one card. The
 *  page already knows exactly which paths went, so it can say so immediately.
 *  The rescan still happens - it is what catches anything else that changed
 *  on disk - but in the background, with the shelf already correct. */
function forgetGames(paths) {
  const gone = new Set(paths);
  if (libraryData?.games) {
    libraryData.games = libraryData.games.filter((g) => !gone.has(g.path));
    libraryData.total = libraryData.games.length;
  }
  for (const p of gone) libSelected.delete(p);
  buildInstalledIndex();
  paintInstalled();
  if (libraryOpen) renderLibrary();

  fetchLibrary()
    .then(() => { if (libraryOpen) renderLibrary(); })
    .catch(() => { /* the folders get read again on Refresh */ });
}

async function loadLibrary() {
  els.libBody.innerHTML = `<p class="empty">Reading your folders…</p>`;
  try {
    await fetchLibrary();
    renderLibrary();
  } catch {
    els.libBody.innerHTML = `<p class="empty">Could not read the library.</p>`;
  }
}

/* ---------- the game you just jumped to ----------

   The highlight is a class on one card, and every redraw of the library
   rebuilds those cards from scratch - so anything that redraws while it is
   still flashing used to take it away mid-pulse. A download finishing, a
   playlist changing, the shelf being repainted: all of them wipe it, and from
   the other side of the screen that looks like the highlight giving up the
   moment you do anything.

   So the app remembers which game is lit rather than trusting the class to
   survive, and every redraw puts it back. Only the clock takes it away.

   Keep this in step with the beat count on .libfound in the stylesheet: six
   beats of 0.75s. Whichever of the two is shorter is what you actually see. */
const FOUND_MS = 4500;
let foundPath = "";
let foundTimer = null;

/** Put the highlight back on the lit card, if it is on screen at all.
 *
 *  `restart` replays the animation from its first beat, which is what a fresh
 *  click wants; a redraw settles for whatever is left of the six seconds. */
function paintFound(restart = false) {
  if (!foundPath) return null;
  const card = [...els.libBody.querySelectorAll("[data-path]")]
    .find((el) => el.dataset.path === foundPath);
  if (!card) return null;
  if (restart) {
    card.classList.remove("libfound");
    void card.offsetWidth;          // without this the animation just continues
  }
  card.classList.add("libfound");
  return card;
}

function markFound(path) {
  foundPath = path;
  clearTimeout(foundTimer);
  foundTimer = setTimeout(() => {
    foundPath = "";
    for (const el of els.libBody.querySelectorAll(".libfound")) {
      el.classList.remove("libfound");
    }
  }, FOUND_MS);
  return paintFound(true);
}

/** Jump from a search result to the copy you already have.
 *
 *  Any filter that would hide it is cleared first, and a folded-away console
 *  is opened - arriving at a library that doesn't visibly contain the game you
 *  just clicked would read as the link being broken. */
async function revealInLibrary(path) {
  showLibrary(true);
  if (!libraryData) await loadLibrary();

  const game = gameAt(path);
  if (!game) { await say(t("That game is no longer in your library.")); return; }

  // Back to the whole library first: a playlist is a subset, and the game
  // being pointed at needn't be on the one that happens to be showing.
  showShelf("");
  els.libConsole.value = "";
  els.libQ.value = "";
  els.libQClear.hidden = true;
  const group = game.console || "Unsorted";
  if (isCollapsed(group)) toggleInPref("libShut", group);
  renderLibrary();

  // Paths carry backslashes and brackets, so the lookup inside markFound is a
  // scan rather than an attribute selector - no escaping to get wrong.
  const card = markFound(path);
  if (!card) return;
  card.scrollIntoView({ block: "center", behavior: "smooth" });
}

els.results.addEventListener("click", (ev) => {
  const slot = ev.target.closest(".finst");
  if (!slot?.dataset.path) return;
  ev.preventDefault();
  revealInLibrary(slot.dataset.path);
});

function showLibrary(on) {
  libraryOpen = on;
  els.libView.hidden = !on;
  els.searchStick.hidden = on;   // the search box and its filters together
  els.results.hidden = on || atHome();
  els.homeCards.hidden = on || !atHome();
  els.more.hidden = on || els.more.hidden;
  els.libBtn.classList.toggle("on", on);
  els.searchBtn.classList.toggle("on", !on);
  if (!on) return;
  // The scan may already have run for the search's "In Library" markers, in
  // which case the data is here but was never drawn - so an empty body means
  // render, not rescan.
  if (!libraryData) { loadLibrary(); return; }
  if (!els.libBody.firstElementChild) renderLibrary();

  /* Then read the folders again behind what is already on screen. Games get
     added and deleted outside the app, and having to remember to press Refresh
     to see your own disk is a poor deal - but so is a blank "Reading your
     folders…" every time you glance at the tab, which is why the cached view
     is shown first and quietly replaced. */
  fetchLibrary().then(renderLibrary).catch(() => { /* Refresh still works */ });
}

els.libBtn.addEventListener("click", () => showLibrary(true));
// Pressing the search button means "I want to search", so put the cursor in
// the box ready to type. Selecting what's already there means a new query
// replaces the old one without having to clear it first.
function goToSearch() {
  showLibrary(false);
  els.q.focus();
  els.q.select();
}
els.searchBtn.addEventListener("click", goToSearch);
// The logo and the app name are both "home", and home here is the search box.
els.homeBtn.addEventListener("click", goHome);
els.titleBtn.addEventListener("click", goHome);
els.libRefresh.addEventListener("click", loadLibrary);

for (const [button, mode] of [[els.libGrid, "grid"], [els.libList, "list"]]) {
  button.addEventListener("click", () => {
    savePrefs({ libView: mode });
    renderLibrary();
  });
}

els.libTitles.addEventListener("change", () => {
  savePrefs({ libTitles: els.libTitles.checked });
  els.libBody.classList.toggle("notitles", !prefs.libTitles);
});

// Dragging updates live; the value is only stored when you let go.
els.libSize.addEventListener("input", () => {
  prefs.libSize = Number(els.libSize.value);
  els.libBody.style.setProperty("--cover", `${prefs.libSize}px`);
});
els.libSize.addEventListener("change", () =>
  savePrefs({ libSize: Number(els.libSize.value) }));

els.libSort.addEventListener("change", () => {
  savePrefs({ libSort: els.libSort.value });
  renderLibrary();
});

/* ---------- shelf controls ---------- */

/** Switching shelves drops the selection: the ticks refer to games on the
 *  shelf you were looking at, and carrying them across to another one means
 *  "Remove" would be aimed at games that are no longer in front of you. */
function showShelf(id) {
  if ((prefs.libShelf || "") === (id || "")) return;
  savePrefs({ libShelf: id || "" });
  libSelected.clear();
  libSelectMode = false;
  libAnchor = "";
  els.libConsole.value = "";
  renderLibrary();
}

els.libShelves.addEventListener("click", (ev) => {
  const chip = ev.target.closest(".shelf");
  if (chip) showShelf(chip.dataset.id);
});

els.libNewPl.addEventListener("click", async () => {
  const name = await promptText({
    title: t("New playlist"), ok: t("Create"), value: suggestPlaylistName(),
  });
  if (!name) return;
  const pl = createPlaylist(name);
  savePlaylists();
  savePrefs({ libShelf: pl.id });   // straight to the shelf you just made
  renderLibrary();
});

els.libPlRename.addEventListener("click", async () => {
  const pl = currentPlaylist();
  if (!pl) return;
  const name = await promptText({
    title: t("Rename playlist"), ok: t("Rename"), value: pl.name,
  });
  if (!name || name === pl.name) return;
  pl.name = name;
  savePlaylists();
  renderLibrary();
});

els.libPlDelete.addEventListener("click", async () => {
  const pl = currentPlaylist();
  if (!pl) return;
  const go = await ask(
    t('Delete the playlist "{name}"?\n\nOnly the list goes — the {n} games on '
      + "it are left exactly as they are, downloaded or not.",
      { name: pl.name, n: pl.items.length }),
    { confirm: true, danger: true, ok: t("Delete") });
  if (!go) return;
  playlists = playlists.filter((p) => p.id !== pl.id);
  savePlaylists();
  savePrefs({ libShelf: "" });
  renderLibrary();
});

/** Everything on this playlist that isn't here yet and could be fetched. */
function missingOf(pl) {
  return (pl?.items || []).filter((e) => e.url && !resolveEntry(e));
}

els.libPlGet.addEventListener("click", () => {
  const missing = missingOf(currentPlaylist());
  if (missing.length) startDownloads(missing.map(downloadItemFromEntry), els.libPlGet);
});

els.libPlCart.addEventListener("click", () => {
  const missing = missingOf(currentPlaylist());
  let added = 0;
  for (const entry of missing) {
    if (cart.has(entry.url)) continue;
    cart.set(entry.url, cartItemFromEntry(entry));
    added++;
  }
  saveCart();
  afterListsChanged();
  toast(added
    ? t("{n} added to your download list.", { n: added })
    : t("They are all on your download list already."));
});

/** The games currently ticked, as playlist entries. A tick can only ever
 *  land on a game that is on disk, so these all resolve. */
function selectedEntries() {
  const cards = new Map();
  for (const el of els.libBody.querySelectorAll("[data-path]")) {
    cards.set(el.dataset.path, el);
  }
  const pl = currentPlaylist();
  const entries = [];
  for (const path of libSelected) {
    const game = gameAt(path);
    if (!game) continue;
    // On a playlist, the entry that is already there carries where the game
    // came from - which a fresh one built from the folder would not.
    const key = entryKey(game.console, game.name, "");
    const existing = pl?.items.find((i) => i.key === key);
    if (existing) { entries.push(existing); continue; }
    const entry = entryFromGame(game);
    const card = cards.get(path);
    // No card means the game is ticked but scrolled out of this render; the
    // shelf works the cover out from the name, as it always did.
    entry.art = card ? shownCoverFor(card) : "";
    entries.push(entry);
  }
  return entries;
}

els.libAddPl.addEventListener("click", (ev) => openAddMenu(ev, selectedEntries()));

els.libPlRemove.addEventListener("click", () => {
  const pl = currentPlaylist();
  if (!pl) return;
  const gone = removeEntries(pl, selectedEntries().map((e) => e.key));
  if (!gone) return;
  savePlaylists();
  libSelected.clear();
  libAnchor = "";
  renderLibrary();
  toast(t("{n} taken off {name}.", { n: gone, name: pl.name }));
});

// Pin a console to the top, or fold its games away. Both re-render, so they
// run before the selection handlers below and stop there.
els.libBody.addEventListener("click", (ev) => {
  const move = ev.target.closest(".libmove");
  if (move) {
    ev.stopPropagation();
    movePinned(move.dataset.console, Number(move.dataset.move));
    renderLibrary();
    return;
  }
  const pin = ev.target.closest(".libpin");
  if (pin) {
    ev.stopPropagation();
    toggleInPref("libPinned", pin.dataset.console);
    renderLibrary();
    return;
  }
  const fold = ev.target.closest(".libfold, .libname-btn");
  if (fold) {
    ev.stopPropagation();
    toggleInPref("libShut", fold.dataset.console);
    renderLibrary();
  }
});

// Select every game under a console heading.
els.libBody.addEventListener("click", (ev) => {
  if (ev.target.closest(".libpin, .libfold, .libname-btn, .libmove")) return;
  const all = ev.target.closest(".libpickall");
  if (!all) return;
  const paths = groupPaths(all.closest(".libgroup"));
  const turnOn = !paths.every((p) => libSelected.has(p));
  for (const p of paths) {
    if (turnOn) libSelected.add(p); else libSelected.delete(p);
  }
  if (turnOn) libSelectMode = true;   // ticks would otherwise be invisible
  libAnchor = "";
  paintSelection();
});

// The last game ticked by hand - shift-click extends the run from there.
let libAnchor = "";

// While selecting, the whole tile is the hit area; otherwise only the artwork
// and the title open the game, so the gaps in the grid stay dead.
/* The tile's own buttons come first: they sit inside the card, so without
   this the click would carry on and start the game underneath them. */
els.libBody.addEventListener("click", async (ev) => {
  const add = ev.target.closest(".libadd");
  if (add) {
    ev.stopPropagation();
    const entry = entryForCard(add.closest("[data-key]"));
    if (entry) openAddMenu(ev, [entry]);
    return;
  }
  const get = ev.target.closest(".plget");
  if (!get) return;
  ev.stopPropagation();
  const entry = entryForCard(get.closest("[data-key]"));
  if (entry?.url) await startDownloads([downloadItemFromEntry(entry)], get);
});

els.libBody.addEventListener("click", async (ev) => {
  if (ev.target.closest(".libpickall, .libadds")) return;
  const card = ev.target.closest("[data-path]");
  if (!card) return;
  const path = card.dataset.path;
  const modifier = ev.shiftKey || ev.ctrlKey || ev.metaKey;

  if (!libSelectMode && !modifier && !ev.target.closest(".libhit")) return;

  if (libSelectMode || modifier) {
    libSelectMode = true;
    window.getSelection()?.removeAllRanges();   // shift-click highlights text
    if (ev.shiftKey && libAnchor && selectRange(libAnchor, path)) {
      // range added; the anchor stays put so you can keep widening it
    } else {
      libSelected.has(path) ? libSelected.delete(path) : libSelected.add(path);
      libAnchor = path;
    }
    paintSelection();
    return;
  }
  /* One click plays. The folder lives in the right-click menu instead, so
     nothing has to wait to find out whether a second click is coming. */
  playGame(path);
});

/** Hand a game to the program set for its console. */
async function playGame(path) {
  const game = gameAt(path);
  const console_ = game?.console || "";
  const res = await fetch("/api/library/play", {
    method: "POST", headers: { "Content-Type": "application/json" },
    // The key and the name go too: what gets played is remembered, and a
    // shelf has to be able to ask "which of my games have I played" without
    // going back to disk for the answer.
    body: JSON.stringify({ path, console: console_, name: game?.name || "",
                           key: entryKey(console_, game?.name || "", "") }),
  }).then((r) => r.json()).catch(() => ({ error: t("Could not reach the app.") }));

  if (res.noEmulator) {
    await say(t("No emulator is set for {console}.\n\nOpen Settings → Folders "
      + "and emulators and choose one in the Emulator column, then try again.",
      { console: console_ || "—" }));
    return;
  }
  if (res.error) { await say(res.error); return; }
  if (res.recent) { recentlyPlayed = res.recent; if (libraryOpen) renderLibrary(); }
}

function setSelectMode(on) {
  libSelectMode = on;
  if (!on) { libSelected.clear(); libAnchor = ""; }
  paintSelection();
}

els.libSelect.addEventListener("click", () => setSelectMode(!libSelectMode));

/* Every game on screen at once, and off again on a second press.
   Deliberately "shown" rather than "the whole library": with a console picked
   or something typed in the search, taking the filter at its word is the only
   reading that isn't a trap - selecting games you can't see, then deleting
   them, is not a mistake anyone recovers from. */
els.libSelectAll.addEventListener("click", () => {
  const shown = shownPaths();
  if (!shown.length) return;
  if (shown.every((p) => libSelected.has(p))) {
    for (const path of shown) libSelected.delete(path);
  } else {
    libSelectMode = true;      // otherwise the ticks would be invisible
    for (const path of shown) libSelected.add(path);
  }
  libAnchor = "";
  paintSelection();
});

// Esc leaves selection mode - the same key that closes the right-click menu,
// so only take it once the menu is already gone.
document.addEventListener("keydown", (ev) => {
  if (ev.key !== "Escape" || !libSelectMode) return;
  if (isShown(els.libMenu) || isShown(els.addMenu)) return;
  if (document.querySelector("dialog[open]")) return;
  setSelectMode(false);
});

els.libConsole.addEventListener("change", renderLibrary);

/* Typing re-renders, which reloads every visible cover - so it waits for a
   pause rather than firing per keystroke. The clear button is immediate,
   since that one is a decision, not a work in progress. */
const renderLibrarySoon = debounce(renderLibrary, 160);

els.libQ.addEventListener("input", () => {
  els.libQClear.hidden = !els.libQ.value;
  renderLibrarySoon();
});

els.libQClear.addEventListener("click", () => {
  els.libQ.value = "";
  els.libQClear.hidden = true;
  els.libQ.focus();
  renderLibrary();
});

/* Deleting a game leaves its box art behind, and on a console set to fetch
   covers automatically that art is a file this app put there without asking.
   So it goes out with the game - which is what the server needs the name and
   console of each path for, since a path on its own says neither.

   Only the consoles with the switch on: the server checks that too, and it is
   the one that decides. Sent for every deletion regardless, so the answer
   never depends on how fresh this page's copy of the settings is. */
const deleteInfo = (paths) => paths.map((path) => {
  const game = gameAt(path);
  return { path, name: game?.name || "", console: game?.console || "" };
});

/** Delete everything currently ticked, after asking. Shared by the toolbar's
 *  Remove button and the right-click menu, so both ask the same question and
 *  neither can drift into deleting on different terms from the other. */
async function removeSelectedGames() {
  const paths = [...libSelected];
  if (!paths.length) return;
  const go = await ask(
    t("Delete {n} games from your PC?\n\nThe files are removed from disk, not "
      + "just the list.\n\nThis can't be undone.", { n: paths.length }),
    { confirm: true, danger: true, ok: `${t("Delete")} ${paths.length}` });
  if (!go) return;

  els.libRemove.disabled = true;
  const res = await fetch("/api/library/delete", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paths, covers: true, games: deleteInfo(paths) }),
  }).then((r) => r.json()).catch(() => ({ failed: [{ error: "Could not reach the app." }] }));
  els.libRemove.disabled = false;
  libSelected.clear();
  // Only the ones that really went, so a failure leaves its card on screen
  // rather than hiding a game that is still on disk.
  forgetGames(res.removedPaths || (res.failed?.length ? [] : paths));
  if (res.failed?.length) {
    await say(t("Removed {done}. Could not remove {failed}:",
      { done: res.removed ?? 0, failed: res.failed.length })
      + "\n" + res.failed.map((f) => `• ${f.error}`).join("\n"));
  } else if (res.coversRemoved) {
    toast(t("Deleted {n} games and their covers.",
            { n: res.removed ?? paths.length }));
  }
}

els.libRemove.addEventListener("click", removeSelectedGames);

/* ---------- right-click menus ---------- */

let menuPath = "";
let menuKey = "";          // ...and which playlist entry, when it is one
let menuCover = "";        // artwork under the pointer, for either menu
let menuConsole = "";      // ...and which console it belongs to

/** Which console the artwork under the pointer belongs to.
 *
 *  Read from wherever the image happens to be rather than stamped onto every
 *  cover in the app: the console is already spelled out beside each one, in a
 *  different shape in each place. An empty answer simply means the save falls
 *  back to asking, which is the old behaviour and never wrong. */
function coverConsole(img) {
  const card = img.closest?.("[data-path]");
  if (card) {
    return gameAt(card.dataset.path)?.console || "";
  }
  // Search results: one section per console, and its rows carry the name.
  const section = img.closest?.(".consec") || img.closest?.("details.game");
  const fromRow = section?.querySelector("button.dl")?.dataset.console;
  if (fromRow) return fromRow;
  // The download list and the downloads panel both tag their rows.
  const row = img.closest?.(".cartitem, .dljob");
  return row?.querySelector(".ctag")?.textContent.trim() || "";
}

// Both menus go in the top layer: covers are shown inside the download list
// and the downloads panel, which are modal dialogs, and a menu that isn't in
// that layer opens behind them where nobody can see or click it.
asPopover(els.libMenu);
asPopover(els.coverMenu);

function closeLibMenu() { hideTop(els.libMenu); menuPath = ""; menuKey = ""; }

/* addTargets is deliberately left alone: openMenu() closes whatever else is
   open as its first move, and the + menu sets its targets before that runs.
   A hidden menu can't be clicked, so what it last pointed at is harmless. */
function closeMenus() {
  closeLibMenu();
  hideTop(els.coverMenu);
  hideTop(els.addMenu);
}

/** Opened at the pointer, pulled back when it would run off the edge.
 *
 *  The menu is moved into whatever dialog it was opened from. A modal dialog
 *  makes everything outside its own subtree inert, so a menu parked elsewhere
 *  in the page is drawn over the dialog but silently refuses every click.
 *  Being a popover is what keeps it positioned against the viewport once it
 *  is in there, instead of against the dialog's own transformed box. */
function openMenu(menu, ev) {
  /* The click that opened this is still on its way up to the document, where
     "clicked outside a menu" would close it again before anyone saw it. The
     event is marked instead of listing every button that can open one, so a
     new opener can't forget to add itself to that list. */
  ev.romsrxMenu = true;
  closeMenus();
  const host = ev.target.closest("dialog") || document.body;
  if (menu.parentElement !== host) host.append(menu);

  showTop(menu);
  const { offsetWidth: w, offsetHeight: h } = menu;
  menu.style.left = `${Math.min(ev.clientX, window.innerWidth - w - 8)}px`;
  menu.style.top = `${Math.min(ev.clientY, window.innerHeight - h - 8)}px`;
}

// A dialog closing takes its menu off-screen with it, so drop it explicitly.
for (const dialog of document.querySelectorAll("dialog")) {
  dialog.addEventListener("close", () => { closeMenus(); hideZoom(); });
}

els.libBody.addEventListener("contextmenu", (ev) => {
  const card = ev.target.closest("[data-path], [data-key]");
  if (!card) return;
  ev.preventDefault();

  const game = gameAt(card.dataset.path);
  const pl = currentPlaylist();
  const entry = entryForCard(card);
  // A playlist entry with nothing behind it yet: half this menu is about a
  // copy on disk, and there isn't one.
  const here = !!game;

  // A game whose art never loaded has no image left to save.
  menuCover = coverSrc(card.querySelector("img"));
  els.libMenuSave.hidden = !menuCover;
  els.libMenuClear.hidden = !game?.cover;
  els.libMenuSetCover.hidden = !here;
  els.libMenuOpen.hidden = !here;
  els.libMenuDelete.hidden = !here;
  els.libMenuSelect.hidden = !here;
  els.libMenuConsole.hidden = !here;

  // The two ways to get a game a playlist is still waiting for.
  const gettable = !here && !!entry?.url;
  els.libMenuGet.hidden = !gettable;
  els.libMenuCart.hidden = !gettable;
  if (gettable) {
    els.libMenuCart.textContent = t(cart.has(entry.url)
      ? "Remove from download list" : "Add to download list");
  }

  els.libMenuAddTo.hidden = !entry;
  els.libMenuRmPl.hidden = !pl;
  if (pl) els.libMenuRmPl.textContent = t("Remove from {name}", { name: pl.name });

  /* Clearing a whole selection from here saves going back up to the toolbar
     for it. Offered only when the game under the pointer is itself one of the
     selected ones - right-clicking outside the selection means you are talking
     about that game, and "all" would quietly take out several others. A
     selection of one already has "Delete game from PC" above it. */
  const bulk = libSelected.size > 1 && libSelected.has(card.dataset.path);
  els.libMenuRemoveSel.hidden = !bulk;
  if (bulk) els.libMenuRemoveSel.textContent = `${t("Remove all")} (${libSelected.size})`;

  // Both of these depend on something being configured for the console, so
  // they only appear where they can actually do anything.
  const setup = consoleSetup.get(game?.console || "") || {};
  els.libMenuPlay.hidden = !here || !setup.emulator;
  els.libMenuDelCover.hidden = !(setup.cover && menuCover);

  openMenu(els.libMenu, ev);
  menuPath = card.dataset.path || "";   // openMenu clears it
  menuKey = card.dataset.key || "";
});

/* Saving a cover, anywhere one is shown. The app window has no browser
   context menu of its own, so this is the one piece of it worth rebuilding -
   box art is useful outside the app, as emulator thumbnails. */

/** Box art comes from the thumbnail server, or from /covers/ when the user
 *  set one themselves. Anything else on the page is some other picture. */
const isCoverUrl = (url) =>
  !!url && (url.startsWith(THUMB_BASE) || url.startsWith("/covers/"));

/** The src of an image only if it is box art. */
function coverSrc(img) {
  const raw = img?.tagName === "IMG" ? img.getAttribute("src") || "" : "";
  return isCoverUrl(raw) ? raw : "";
}

/** The thumbnail server names its files the way emulators expect them, so
 *  its own name is the right suggestion. Covers the user supplied are stored
 *  under a hash, so those fall back to the game's name. */
function coverFileName(url, fallback = "cover") {
  const base = decodeURIComponent(url.split("?")[0].split("/").pop() || "");
  if (!url.startsWith("/covers/")) return base || `${fallback}.png`;
  return fallback + (base.includes(".") ? base.slice(base.lastIndexOf(".")) : ".png");
}

async function saveCover(url, name, console_ = "") {
  const res = await fetch("/api/cover/save", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, name, console: console_ }),
  }).then((r) => r.json()).catch(() => ({ error: "Could not reach the app." }));
  if (res.error) { await say(res.error); return; }
  // Saved without a picker, so say where it went - otherwise a cover set to
  // save silently looks like nothing happened at all.
  if (res.saved && res.asked === false) toast(t("Cover saved to {path}", { path: res.saved }));
}

// Everywhere except the library, which offers the same entry on its own menu.
document.addEventListener("contextmenu", (ev) => {
  const url = coverSrc(ev.target);
  if (!url || ev.target.closest("#libbody")) return;
  ev.preventDefault();
  menuCover = url;
  menuConsole = coverConsole(ev.target);
  openMenu(els.coverMenu, ev);
});

els.coverMenu.addEventListener("click", (ev) => {
  if (!ev.target.closest("button") || !menuCover) return;
  const url = menuCover;
  const console_ = menuConsole;
  closeMenus();
  saveCover(url, coverFileName(url), console_);
});

document.addEventListener("click", (ev) => {
  if (ev.romsrxMenu) return;   // this click opened a menu, or happened in one
  if (!ev.target.closest("#libmenu, #covermenu, #addmenu")) closeMenus();
});
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") closeMenus();
});

els.libMenu.addEventListener("click", async (ev) => {
  const action = ev.target.closest("button")?.dataset.act;
  if (!action || (!menuPath && !menuKey)) return;
  const path = menuPath;
  const key = menuKey;
  const art = menuCover;
  const game = gameAt(path);
  const pl = currentPlaylist();
  // Read before the menu closes, since closing is what forgets which card
  // this was about.
  const entry = pl?.items.find((i) => i.key === key)
    || (game ? entryFromGame(game) : null);
  closeLibMenu();

  if (action === "addto") {
    if (entry) openAddMenu(ev, [entry]);
    return;
  }
  if (action === "removefrompl") {
    if (!pl || !removeEntries(pl, [key])) return;
    savePlaylists();
    renderLibrary();
    toast(t("Taken off {name}.", { name: pl.name }));
    return;
  }
  if (action === "getnow") {
    // The menu it was chosen from is already gone, so the progress goes to a
    // button nobody can see - which is what the toast is for.
    if (entry?.url) {
      await startDownloads([downloadItemFromEntry(entry)],
                           document.createElement("button"));
    }
    return;
  }
  if (action === "tocart") {
    if (!entry?.url) return;
    if (cart.has(entry.url)) cart.delete(entry.url);
    else if (await allowLoginOnly(!!entry.login, t("That file"))) {
      cart.set(entry.url, cartItemFromEntry(entry));
    }
    saveCart();
    afterListsChanged();
    return;
  }

  if (action === "play") {
    await playGame(path);
  } else if (action === "savecover") {
    if (art) {
      await saveCover(art, coverFileName(art, game?.name || "cover"),
                      game?.console || "");
    }
  } else if (action === "deletecoverfile") {
    const name = coverFileName(art, game?.name || "cover");
    const go = await ask(
      t('Delete the cover file "{name}" from your PC?\n\nThis removes the image '
        + "saved in this console's cover folder. The game itself is not "
        + "touched.", { name }),
      { confirm: true, danger: true, ok: t("Delete") });
    if (!go) return;

    const res = await fetch("/api/cover/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, console: game?.console || "" }),
    }).then((r) => r.json()).catch(() => ({ error: t("Could not reach the app.") }));

    if (res.error) await say(res.error);
    else if (res.missing) {
      await say(t("There is no cover file to delete at {path}.", { path: res.path }));
    }
    else if (res.deleted) toast(t("Cover file deleted: {path}", { path: res.deleted }));
  } else if (action === "open") {
    await fetch("/api/library/reveal", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
  } else if (action === "cover") {
    const res = await fetch("/api/library/cover", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    }).then((r) => r.json());
    if (res.error) await say(res.error);
    if (res.ok) await loadLibrary();
  } else if (action === "clearcover") {
    await fetch("/api/library/cover/clear", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    await loadLibrary();
  } else if (action === "select") {
    libSelectMode = true;
    libSelected.add(path);
    libAnchor = path;
    paintSelection();
  } else if (action === "selectconsole") {
    const key = game?.console || "";
    libSelectMode = true;
    for (const g of libraryData?.games || []) {
      if ((g.console || "Unsorted") === (key || "Unsorted")) libSelected.add(g.path);
    }
    libAnchor = "";
    paintSelection();
  } else if (action === "removeselected") {
    await removeSelectedGames();
  } else if (action === "delete") {
    const go = await ask(
      t('Delete "{name}" from your PC?\n\nThe files are removed from disk, '
        + "not just the list.", { name: game ? game.name : path }),
      { confirm: true, danger: true, ok: t("Delete") });
    if (!go) return;
    const res = await fetch("/api/library/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths: [path], covers: true,
                             games: deleteInfo([path]) }),
    }).then((r) => r.json());
    forgetGames(res.removedPaths || (res.failed?.length ? [] : [path]));
    if (res.failed?.length) await say(res.failed[0].error);
    else if (res.coversRemoved) toast(t("Deleted the game and its cover."));
  }
});

/* ---------- folder per console ---------- */

let folderState = { base: "", consoles: [] };

/** Paths under the base folder show only the part that differs - otherwise
 *  every row repeats the same long prefix and they all look identical. */
function shortPath(full, base) {
  if (!base || !full) return full || "";
  // Whichever separator this machine uses - the paths come from the server,
  // so they are backslashes on Windows and forward slashes everywhere else.
  const sep = full.includes("\\") ? "\\" : "/";
  const b = base.replace(/[\\/]+$/, "").toLowerCase();
  const f = full.toLowerCase();
  if (f === b) return "(main folder)";
  if (f.startsWith(b + sep)) return `…${sep}${full.slice(base.replace(/[\\/]+$/, "").length + 1)}`;
  return full;
}

/* One labelled block: what it is, an info bubble saying why you would set it,
   then the box and its buttons. Every field in the panel is this shape, so
   the whole thing reads as a form rather than as a grid of anonymous paths. */
/* Both strings stay in English here and are translated where they are used:
   the label by applyLanguage, which is re-run on every language change and
   would otherwise be re-translating its own output; the tip by showInfoTip,
   which looks `data-tip` up when the bubble opens. Baking either one in at
   build time leaves it stuck in whichever language was on when the row was
   drawn. */
const frField = (label, tip, body) => `
  <div class="fr-field">
    <span class="fr-label" data-i18n>${esc(label)}<span class="infoicon"
      tabindex="0" data-tip="${esc(tip)}">i</span></span>
    <span class="fr-cell">${body}</span>
  </div>`;

function folderRow(entry) {
  // The effective path is the placeholder, so you can always see where a
  // console will land even without an override set.
  const hint = shortPath(entry.effective, folderState.base);
  // Both cover toggles are meaningless without somewhere to keep the images,
  // so they follow the cover folder rather than standing on their own.
  const noCover = entry.cover ? "" : " disabled";
  return `
    <div class="folderrow" data-console="${esc(entry.console)}">
      <h4 class="fr-name">${esc(entry.console)}</h4>

      ${frField("Games folder",
        "Where this console's games are saved. Blank uses the main folder.", `
        <input class="fr-path" type="text" spellcheck="false" title="${esc(entry.effective)}"
               value="${esc(entry.override ? entry.effective : "")}"
               placeholder="${esc(hint)}">
        <button class="fr-browse ghost small" title="${esc(t("Choose a folder"))}">&hellip;</button>
        <button class="fr-clear ghost small" title="${esc(t("Use the default"))}">&times;</button>`)}

      ${frField("Covers",
        "Where Save cover image puts box art. Blank asks each time. Your emulator's thumbnails folder works here.", `
        <input class="fr-cover" type="text" spellcheck="false"
               value="${esc(entry.cover || "")}"
               placeholder="${esc(t("ask every time"))}"
               title="${esc(t("Covers for this console are saved here without asking"))}">
        <button class="fr-coverbrowse ghost small" title="${esc(t("Choose a folder"))}">&hellip;</button>
        <button class="fr-coverclear ghost small" title="${esc(t("ask every time"))}">&times;</button>`)}

      <div class="fr-toggles">
        <label class="fr-autocover">
          <input type="checkbox" class="fr-coverauto"${
            entry.coverAuto ? " checked" : ""}${noCover}>
          <span data-i18n>Get covers automatically</span>
          <span class="infoicon" tabindex="0" data-i18n
                data-tip="As each game for this console finishes downloading, its box art is fetched and saved into the covers folder above. Needs that folder set.">i</span>
        </label>
        <!-- Deliberately not implied by the switch above. Downloading art for
             you is not the same permission as deleting art, and a covers
             folder is very often an emulator's shared thumbnails folder full
             of images this app never put there. -->
        <label class="fr-autocover">
          <input type="checkbox" class="fr-coverdelete"${
            entry.coverDelete ? " checked" : ""}${noCover}>
          <span data-i18n>Delete covers with the game</span>
          <span class="infoicon" tabindex="0" data-i18n
                data-tip="When you remove a game from your PC through this app, its cover in the folder above goes too. Off, the image is left alone. Nothing else in that folder is ever touched.">i</span>
        </label>
      </div>

      ${frField("Emulator",
        "The program that plays this console's games.", `
        <input class="fr-emu" type="text" spellcheck="false"
               value="${esc(entry.emulator || "")}"
               placeholder="${esc(t("none"))}"
               title="${esc(t("Games for this console open in this program"))}">
        <button class="fr-emubrowse ghost small" title="${esc(t("Choose a program"))}">&hellip;</button>
        <button class="fr-emuclear ghost small" title="${esc(t("Clear"))}">&times;</button>`)}

      ${frField("Core",
        "RetroArch cannot open anything without a core. Pick the one for this console. Every other emulator leaves this blank.", `
        <input class="fr-emucore" type="text" spellcheck="false"
               value="${esc(entry.emulatorCore || "")}"
               placeholder="${esc(t("core — only RetroArch needs one"))}"
               title="${esc(t("RetroArch cannot open anything without a core. Pick the one for this console."))}">
        <button class="fr-corebrowse ghost small" title="${esc(t("Choose a core"))}">&hellip;</button>
        <button class="fr-coreclear ghost small" title="${esc(t("Clear"))}">&times;</button>`)}

      ${frField("Arguments",
        "Anything else the program wants, typed as you would type it. The game is added at the end unless you write {game} yourself.", `
        <input class="fr-emuargs" type="text" spellcheck="false"
               value="${esc(entry.emulatorArgs || "")}"
               placeholder="${esc(t("extra arguments, if the program needs any"))}">`)}
    </div>`;
}

/* Which console's settings are on screen. Kept across a reload of the folder
   data so saving a path doesn't bounce you back to "Choose console…". */
let folderConsole = "";

const folderEntry = (name) =>
  folderState.consoles.find((c) => c.console === name) || null;

function renderFolders() {
  els.foldersBase.textContent = folderState.base;
  /* Says where things stand before it says what you can change, because the
     answer to "where did my game go" is the first line, not the third. */
  els.foldersHint.textContent = t(folderState.per_console
    ? "Each console downloads to its own subfolder of the folder above. Pick a console to override that, and to choose where its covers are saved and what plays the games."
    : "Every console downloads to the folder above. Pick a console to give it a folder of its own, and to choose where its covers are saved and what plays the games.");

  // A console that is set up already says so in the list, so you can see what
  // you have configured without opening each one in turn.
  const configured = (c) => c.override || c.cover || c.emulator;
  /* Typing narrows the list to what matches, anywhere in the name - "mega"
     finds Genesis/Mega Drive, which a native menu's type-to-jump never would,
     since that only ever matches from the first letter. */
  const needle = (els.consSearch.value || "").trim().toLowerCase();
  const shown = needle
    ? folderState.consoles.filter((c) => c.console.toLowerCase().includes(needle))
    : folderState.consoles;

  els.consBtn.textContent = folderConsole || t("Choose console…");
  els.consBtn.classList.toggle("on", !!folderConsole);
  els.consBtn.insertAdjacentHTML("beforeend", '<span class="fcaret">&#9662;</span>');

  els.consItems.innerHTML = shown.length
    ? shown.map((c) => `<button class="fitem consitem${
        c.console === folderConsole ? " on" : ""}" data-console="${esc(c.console)}">
        <span class="mlabel">${esc(c.console)}</span>${
        configured(c) ? '<span class="consdone">&#10003;</span>' : ""}</button>`).join("")
    : `<div class="fempty">${esc(t("No matches"))}</div>`;

  const entry = folderEntry(folderConsole);
  els.folderList.innerHTML = entry ? folderRow(entry) : "";
  applyLanguage(prefs.lang);
}


async function loadFolders() {
  try {
    folderState = await fetch("/api/downloads/folders").then((r) => r.json());
    renderFolders();
  } catch { /* server restarting */ }
}

/* Four ways in, one dialog - but a gear should answer for the panel it sits
   in and nothing else. Opened from a panel, Settings shows only the group
   that panel actually obeys: hunting for the two switches that change the
   downloads panel in a list that also holds the language and the theme is
   the sort of thing a gear on the panel itself is supposed to spare you.
   The header's gear is the whole dialog, and stays the way to everything. */
/* The per-console paths belong to two panels at once: they are where the
   downloads land, and they are what the library plays from. Both gears show
   them - the downloads one alongside the settings that decide the main
   folder, the library's on its own. */
const SETTINGS_SCOPES = {
  downloads: ["setdownloads", "setconsoles"],
  cart: ["setcart"],
  consoles: ["setconsoles"],
};

/* The subtabs, for the header's gear - which opens the lot and so is the one
   that needed narrowing down. "All" is the old behaviour, kept because a
   setting you can't name is easier to find by scrolling past it than by
   guessing which tab it lives on.

   Downloads, the download list and the per-console folders are one tab: they
   are the same subject asked three ways - what goes on the list, where it
   lands, and where each console puts it. Splitting them would mean setting a
   folder on one tab and the switch that decides whether it is used on
   another. */
const SETTINGS_TABS = {
  all: null,                                       // null = show everything
  appearance: ["setlanguage", "settheme"],
  paths: ["setcart", "setdownloads", "setconsoles"],
  backup: ["setbackup"],
};

let settingsTab = "all";

/** Show one tab's groups, or - when a panel's gear asked for a scope - only
 *  that scope, with the tabs out of the way. */
function paintSettings(scope = "") {
  const only = scope ? (SETTINGS_SCOPES[scope] || null) : SETTINGS_TABS[settingsTab];
  els.setTabs.hidden = !!scope;
  for (const group of els.settingsDlg.querySelectorAll(".setgroup")) {
    group.hidden = !!only && !only.includes(group.id);
  }
  for (const button of els.setTabs.querySelectorAll("button")) {
    button.classList.toggle("on", button.dataset.tab === settingsTab);
  }
}

let settingsScope = "";

async function openSettings(scope = "") {
  settingsScope = scope;
  paintSettings(scope);
  els.settingsDlg.showModal();
  els.settingsDlg.scrollTop = 0;
  await Promise.all([loadDownloadSettings(), loadFolders()]);
}

els.setTabs.addEventListener("click", (ev) => {
  const tab = ev.target.closest("button")?.dataset.tab;
  if (!tab || !(tab in SETTINGS_TABS)) return;
  settingsTab = tab;
  paintSettings(settingsScope);
  // A tab is a fresh page, not a place in the one you were reading.
  els.settingsDlg.scrollTop = 0;
});

els.settingsBtn.addEventListener("click", () => openSettings());
// Where each console's downloads, covers and emulator live - the library is
// what those paths fill, so this is the gear that owns them.
els.libSettings.addEventListener("click", () => openSettings("consoles"));
els.cartSettings.addEventListener("click", () => openSettings("cart"));
els.dlFolders.addEventListener("click", () => openSettings("downloads"));

// Applies straight away rather than waiting for Save, since the preview
// beside it is claiming it already has.
els.perConsole.addEventListener("change", async () => {
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ per_console: els.perConsole.checked }),
  });
  if (els.settingsDlg.open) await loadFolders();
});


/* Both columns behave the same way, so they share one handler: which input a
   button belongs to is decided by the class it carries, not by a second copy
   of all of this. */
const FOLDER_COLUMNS = [
  { browse: ".fr-browse", clear: ".fr-clear", input: ".fr-path" },
  { browse: ".fr-coverbrowse", clear: ".fr-coverclear", input: ".fr-cover" },
  // The emulator is a program, not a folder, so it needs the other picker.
  { browse: ".fr-emubrowse", clear: ".fr-emuclear", input: ".fr-emu",
    pick: "/api/downloads/browse-exe", field: "file" },
  // Same picker, filtered to shared libraries - .dll here, .so or .dylib
  // elsewhere - since that is what a libretro core is.
  { browse: ".fr-corebrowse", clear: ".fr-coreclear", input: ".fr-emucore",
    pick: "/api/downloads/browse-exe", field: "file", kind: "core" },
];

els.folderList.addEventListener("click", async (ev) => {
  const row = ev.target.closest(".folderrow");
  if (!row) return;

  for (const col of FOLDER_COLUMNS) {
    const input = row.querySelector(col.input);

    if (ev.target.closest(col.clear)) {
      input.value = "";
      await saveFolders(false);    // saves itself - no Save button to forget
      await loadFolders();
      return;
    }
    const btn = ev.target.closest(col.browse);
    if (!btn) continue;

    btn.disabled = true;
    try {
      const res = await fetch(col.pick || "/api/downloads/browse", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: input.value || folderState.base,
                               kind: col.kind }),
      }).then((r) => r.json());
      const chosen = res[col.field || "folder"];
      if (chosen) {
        input.value = chosen;
        await saveFolders(false);
        await loadFolders();
      }
    } catch { /* keep what was typed */ }
    btn.disabled = false;
    return;
  }
});

// Typed paths save themselves once you pause.
els.folderList.addEventListener("input", debounce(async (ev) => {
  if (!ev.target.closest(
    ".fr-path, .fr-cover, .fr-emu, .fr-emucore, .fr-emuargs")) return;
  await saveFolders(false);
}, 800));

/* A tick is a decision, not a phrase being typed, so it saves at once rather
   than 800ms later - long enough for the dialog to be closed in between. */
els.folderList.addEventListener("change", async (ev) => {
  if (!ev.target.closest(".fr-coverauto, .fr-coverdelete")) return;
  await saveFolders(false);
});

/* ---------- the console picker ---------- */
function openConsoleMenu(on) {
  els.consMenu.hidden = !on;
  els.consBtn.setAttribute("aria-expanded", String(on));
  if (!on) return;
  // Straight into the box: opening this menu is nearly always the first half
  // of typing a name.
  els.consSearch.focus();
  els.consSearch.select();
}

els.consBtn.addEventListener("click", (ev) => {
  ev.stopPropagation();
  openConsoleMenu(els.consMenu.hidden);
});

els.consSearch.addEventListener("input", renderFolders);
els.consSearch.addEventListener("click", (ev) => ev.stopPropagation());

els.consItems.addEventListener("click", (ev) => {
  const item = ev.target.closest(".consitem");
  if (!item) return;
  ev.stopPropagation();
  folderConsole = item.dataset.console;
  els.consSearch.value = "";      // next time it opens on the whole list
  openConsoleMenu(false);
  renderFolders();
});

// Enter takes the only thing left, which is what typing a name is for.
els.consSearch.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") { openConsoleMenu(false); els.consBtn.focus(); return; }
  if (ev.key !== "Enter") return;
  const first = els.consItems.querySelector(".consitem");
  if (first) first.click();
});

document.addEventListener("click", (ev) => {
  if (!els.consMenu.hidden && !ev.target.closest(".consdrop")) openConsoleMenu(false);
});

/** Fold what is on screen back into our copy of every console's settings.
 *
 *  Load-bearing now that only one console is shown at a time. The server
 *  replaces each of these maps wholesale, so building them from the visible
 *  rows - which is what this did when every console had a row - would send a
 *  map containing one console and wipe the settings of all the others. The
 *  page's own copy is the full picture; the row on screen only updates its
 *  own entry in it. */
function readFolderRow() {
  const row = els.folderList.querySelector(".folderrow");
  if (!row) return;
  const entry = folderEntry(row.dataset.console);
  if (!entry) return;

  const value = (sel) => row.querySelector(sel).value.trim();
  const cover = value(".fr-cover");
  entry.override = value(".fr-path");
  entry.cover = cover;
  entry.emulator = value(".fr-emu");
  entry.emulatorCore = value(".fr-emucore");
  entry.emulatorArgs = value(".fr-emuargs");

  // Neither toggle means anything without somewhere to keep the images, so
  // both follow the cover folder.
  for (const [sel, key] of [[".fr-coverauto", "coverAuto"],
                            [".fr-coverdelete", "coverDelete"]]) {
    const box = row.querySelector(sel);
    box.disabled = !cover;
    entry[key] = !!cover && box.checked;
  }
}

async function saveFolders(showTick = true) {
  readFolderRow();

  const folders = {};
  const covers = {};
  const coverAuto = {};
  const coverDelete = {};
  const emulators = {};
  const emulatorCores = {};
  const emulatorArgs = {};
  for (const entry of folderState.consoles) {
    const name = entry.console;
    if (entry.override) folders[name] = entry.override;
    if (entry.cover) covers[name] = entry.cover;
    if (entry.cover && entry.coverAuto) coverAuto[name] = true;
    if (entry.cover && entry.coverDelete) coverDelete[name] = true;
    if (entry.emulator) emulators[name] = entry.emulator;
    if (entry.emulatorCore) emulatorCores[name] = entry.emulatorCore;
    if (entry.emulatorArgs) emulatorArgs[name] = entry.emulatorArgs;
  }
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ per_console: els.perConsole.checked,
                           console_folders: folders,
                           cover_folders: covers,
                           cover_auto: coverAuto,
                           cover_delete: coverDelete,
                           emulators,
                           emulator_cores: emulatorCores,
                           emulator_args: emulatorArgs }),
  });
  if (showTick) {
    els.foldersSaved.hidden = false;
    setTimeout(() => { els.foldersSaved.hidden = true; }, 1600);
  }
}

/* Finds per-console folders that are already on disk and writes down where
   they are. The library reads the folders the app knows about, so a collection
   sorted by a version that kept no record of it - or by hand - arrives as one
   big "Unsorted" pile until someone says where each console lives. */
els.foldersDetect.addEventListener("click", async () => {
  const button = els.foldersDetect;
  const label = button.textContent;
  button.disabled = true;
  button.textContent = t("Looking…");
  try {
    const res = await fetch("/api/downloads/relink", { method: "POST" })
      .then((r) => r.json());
    await loadFolders();
    if (res.error) { await say(res.error); }
    else if (!res.linked && !res.repaired) {
      // Says where it looked, because "found nothing" is only useful with
      // that: the answer is usually that the collection is somewhere else.
      await say(t("Nothing to change.\n\n{kept} consoles already point at a "
                  + "folder that is still there, and no folder named after any "
                  + "of the others turned up in:\n\n{roots}",
                  { kept: res.kept, roots: (res.roots || []).join("\n") }));
    } else {
      const lines = [];
      if (res.linked) {
        lines.push(t("Linked {n}: {list}",
                     { n: res.linked, list: res.consoles.join(", ") }));
      }
      // A path that had gone stale - a moved or renamed folder, or a drive
      // that came back with a different letter.
      if (res.repaired) {
        lines.push(t("Re-pointed {n} whose folder had moved: {list}",
                     { n: res.repaired, list: res.repairedConsoles.join(", ") }));
      }
      if (res.kept) lines.push(t("Left {n} already-working ones alone.", { n: res.kept }));
      await say(`${lines.join("\n")}\n\n${t("Press Refresh in the library to see them sorted.")}`);
      if (libraryOpen) loadLibrary();
    }
  } catch {
    await say(t("Could not reach the app."));
  }
  button.textContent = label;
  button.disabled = false;
});

/* Every console, not just the one on screen.
   Blanking the visible inputs was the whole job when every console had a row;
   with one shown at a time that would quietly turn "Clear all" into "clear
   this one". It works on our copy of the settings instead - and asks first,
   because the damage is now entirely off screen: thirty-nine consoles you
   cannot see losing their paths on one click. */
els.foldersReset.addEventListener("click", async () => {
  const set = folderState.consoles.filter(
    (c) => c.override || c.cover || c.emulator || c.emulatorCore || c.emulatorArgs);
  if (!set.length) return;

  const go = await ask(
    t("Clear the folders, covers and emulators set for all {n} consoles?\n\n"
      + "Only the settings are cleared — no files are moved or deleted.",
      { n: set.length }),
    { confirm: true, danger: true, ok: t("Clear all") });
  if (!go) return;

  for (const entry of folderState.consoles) {
    entry.override = entry.cover = "";
    entry.emulator = entry.emulatorCore = entry.emulatorArgs = "";
    entry.coverAuto = entry.coverDelete = false;
  }
  // Straight to the server: reading the row back first would put the values
  // still sitting in the boxes on screen back over what was just cleared.
  els.folderList.innerHTML = "";
  await saveFolders();
  await loadFolders();
});

// Backdrop dismissal: see closeOnBackdrop().

/* ---------- archive.org account ---------- */

/* Whether archive.org will actually serve the restricted sources. Kept here
   so the download list and the queue can refuse politely rather than letting
   a download start and fail with a 403 nobody can interpret. */
let signedInToArchive = false;

/* Being told to "sign in from the header" and then having to find the button,
   sign in, and start over is three steps too many when the thing you wanted is
   one click behind it. So the account dialog itself is what comes up, carrying
   the reason - sign in there and whatever you were doing carries on. */
let loginPromptOpen = false;

/** Opens the account dialog with a reason on it. Resolves true once they are
 *  signed in, false if they closed it without. */
function promptArchiveLogin(reason) {
  return new Promise((resolve) => {
    loginPromptOpen = true;
    els.acctReason.textContent = reason;
    els.acctReason.hidden = false;
    showAccountError("");
    els.acctDlg.addEventListener("close", () => {
      loginPromptOpen = false;
      els.acctReason.hidden = true;
      els.acctReason.textContent = "";
      resolve(signedInToArchive);
    }, { once: true });
    els.acctDlg.showModal();
    loadAccount();
    if (!signedInToArchive) els.acctEmail.focus();
  });
}

/** True if this can go ahead. Offers the sign-in when it can't, so saying yes
 *  to it is enough to let the caller continue. */
async function allowLoginOnly(needsLogin, what) {
  if (!needsLogin || signedInToArchive) return true;
  return promptArchiveLogin(
    `${what} needs an archive.org account.\n`
    + "This source is marked 🔒 login: archive.org refuses it to anyone who "
    + "isn't signed in. Sign in here and the download will go ahead.");
}

function showAccount(state) {
  const signedIn = !!state.signed_in;
  signedInToArchive = signedIn;
  // Icon-only button - setting text here would wipe the SVG inside it.
  els.acctBtn.classList.toggle("on", signedIn);
  els.acctBtn.title = signedIn
    ? `Signed in as ${state.email || "your account"}`
    : "Sign in to unlock login-only sources";

  els.acctForm.hidden = signedIn;
  els.acctSigned.hidden = !signedIn;
  if (signedIn) {
    els.acctWho.textContent = state.email || "your account";
    els.acctWhere.textContent = state.config
      ? `Session stored at ${state.config}`
      : "";
  }
  if (state.error && !signedIn) showAccountError(state.error);
}

function showAccountError(message) {
  els.acctError.textContent = message;
  els.acctError.hidden = !message;
}

async function loadAccount() {
  try {
    showAccount(await fetch("/api/account").then((r) => r.json()));
  } catch { /* offline or server restarting - leave the button as-is */ }
}

els.acctBtn.addEventListener("click", async () => {
  showAccountError("");
  els.acctDlg.showModal();
  await loadAccount();
});

els.acctForm.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  showAccountError("");
  els.acctSubmit.disabled = true;
  els.acctSubmit.textContent = "Signing in…";

  const body = JSON.stringify({
    email: els.acctEmail.value,
    password: els.acctPass.value,
  });
  els.acctPass.value = "";   // don't leave it sitting in the field

  try {
    const res = await fetch("/api/account/login", {
      method: "POST", headers: { "Content-Type": "application/json" }, body,
    });
    const state = await res.json();
    if (!res.ok || state.error) {
      showAccountError(state.error || "Sign-in failed.");
    } else {
      showAccount(state);
      search(false);   // 🔒 rows are now reachable
      // Opened to unblock something, so get out of the way and let it happen.
      if (loginPromptOpen) els.acctDlg.close();
    }
  } catch (err) {
    showAccountError(t("Could not reach the local server."));
  } finally {
    els.acctSubmit.disabled = false;
    els.acctSubmit.textContent = "Sign in";
  }
});

for (const id of ["acctlogout", "acctlogout2"]) {
  $(id).addEventListener("click", async () => {
    try {
      const state = await fetch("/api/account/logout", { method: "POST" })
        .then((r) => r.json());
      showAccount(state);
      search(false);           // 🔒 rows are out of reach again
      // Anything 🔒 that was mid-flight has just been stopped by the server.
      // Saying so beats leaving them to find it paused on their own.
      if (state.paused > 0) {
        pollDownloads();
        await say(t("{n} downloads need an archive.org account, so they have "
          + "been paused.\n\nNothing is lost — sign back in and resume, and "
          + "they pick up from where they stopped.", { n: state.paused }));
      }
    } catch { showAccountError(t("Could not reach the local server.")); }
  });
}

// Every dialog closes from its own corner X.
for (const x of document.querySelectorAll("dialog [data-close]")) {
  x.addEventListener("click", () => x.closest("dialog").close());
}

// Same backdrop-dismiss rule as the download list.
// Backdrop dismissal: see closeOnBackdrop().

/* ---------- reindex ---------- */

/** Time left, worked out from how long the sources so far actually took.
 *
 *  Held back until a few are done: the first source carries the cost of
 *  opening connections, so extrapolating from it produces a wild number that
 *  then visibly collapses - which reads as the app not knowing what it is
 *  doing. `elapsed` comes from the server so this is right even when the panel
 *  was opened halfway through. */
function indexEta(done, total, elapsed) {
  if (done < 3 || elapsed < 4) return "";
  const left = etaText((elapsed / done) * (total - done));
  return left ? ` · about ${left}` : "";
}

async function pollIndex() {
  const s = await fetch("/api/index/status").then((r) => r.json());
  els.log.textContent = s.log.join("\n");
  els.log.scrollTop = els.log.scrollHeight;

  // How far along, so it's obvious whether this is seconds or minutes away.
  const { done = 0, total = 0, elapsed = 0 } = s;
  els.indexBar.style.width = total ? `${(done / total) * 100}%` : "0%";
  els.indexCount.textContent = total
    ? `${done} of ${total} sources${done < total
        ? indexEta(done, total, elapsed) : " — finishing up"}`
    : "starting…";

  if (s.running) {
    setTimeout(pollIndex, 1000);
    return;
  }

  els.indexBar.style.width = "100%";
  els.indexCount.textContent = total ? `Done — ${total} sources` : "Done";
  restoreReindexButton();
  loadStats();
  search(false);
}

/* The button carries an icon, not a label; swapping in "Indexing…" replaces
   the SVG, so it has to be put back rather than just re-enabled. */
const REINDEX_ICON = els.reindex.innerHTML;

function restoreReindexButton() {
  indexing = false;
  els.reindex.disabled = false;
  els.reindex.innerHTML = REINDEX_ICON;
  els.reindex.classList.remove("working");
  els.reindex.title = "Re-fetch file lists from archive.org";
}

/* An index already running when the app opens - because it was closed
   mid-run, or a second window is open - has to be picked up, or the button
   would sit idle while work happens in the background. */
async function resumeIndexIfRunning() {
  try {
    const s = await fetch("/api/index/status").then((r) => r.json());
    if (!s.running) return;
    indexing = true;
    els.reindex.classList.add("working");
    els.reindex.title = "Indexing… (click to watch)";
    pollIndex();
  } catch { /* server not up yet */ }
}

let indexing = false;

async function startReindex() {
  // Closing the progress window doesn't stop the indexing - it carries on in
  // the background. Pressing the button again while that is happening has to
  // show the progress again rather than doing nothing, or there is no way
  // back in and the app looks stuck.
  if (indexing) {
    if (!els.dlg.open) els.dlg.showModal();
    return;
  }

  indexing = true;
  els.reindex.classList.add("working");
  els.reindex.title = "Indexing… (click to watch)";
  els.log.textContent = "starting…";
  els.indexBar.style.width = "0%";
  els.indexCount.textContent = "starting…";
  els.dlg.showModal();
  await fetch("/api/index", { method: "POST" });
  pollIndex();
}

els.reindex.addEventListener("click", startReindex);

// The first-run card is rebuilt by every search, so catch its button on the way up.
els.results.addEventListener("click", (ev) => {
  if (ev.target.closest("#firstindex")) startReindex();
});

/* ---------- wiring ---------- */

els.q.addEventListener("input", () => {
  els.qClear.hidden = !els.q.value;
  debouncedSearch();
});
els.qClear.addEventListener("click", () => {
  els.q.value = "";
  els.qClear.hidden = true;
  els.q.focus();
  search();
});
els.more.addEventListener("click", () => search(true));

// The "+N" badge lives inside <summary>, so we have to cancel the click in
// the capture phase - by the time it reaches <summary> the card has already
// been told to expand.
els.results.addEventListener("click", (ev) => {
  const toggle = ev.target.closest(".morecon");
  if (!toggle) return;
  ev.preventDefault();
  ev.stopPropagation();

  const wasOpen = toggle.dataset.open === "1";
  for (const badge of toggle.parentElement.querySelectorAll(".badge.extra")) {
    badge.hidden = wasOpen;
  }

  const count = toggle.dataset.count;
  const plural = count === "1" ? "" : "s";
  toggle.dataset.open = wasOpen ? "0" : "1";
  toggle.title = wasOpen
    ? `Show ${count} more console${plural}`
    : `Hide ${count} console${plural}`;
  toggle.innerHTML = `${wasOpen ? "+" : "&minus;"}${count}`
    + `<span class="morecaret">${wasOpen ? "&#9662;" : "&#9652;"}</span>`;
}, true);

// The library toolbar sticks below the header, so it needs the real height.
/* A maximised panel is positioned just under the header, so this number has
   to be right at all times. Measuring only on load and on window resize was
   not enough: the header wraps to two rows when the window is narrow, and
   nothing fires a resize when its *contents* change - leaving a maximised
   panel sitting underneath it with its close button out of reach. */
function measureHeader() {
  document.documentElement.style.setProperty(
    "--headerh", `${Math.round(els.header.getBoundingClientRect().height)}px`);
}

if (typeof ResizeObserver === "function") {
  new ResizeObserver(measureHeader).observe(els.header);
}
/* ---------- filling the window ----------
   One button per dialog that flips between a panel and the whole window, with
   the icon showing what pressing it will do. The choice is remembered per
   dialog, so a panel you like full-size comes back that way. */
/* The familiar pair: brackets in all four corners, opening outwards to grow
   and folding inwards to shrink. Each corner is one stroke so the join stays
   clean at 15px, and the two are mirror images of each other - which is what
   makes it read at a glance which one you are looking at. */
const WIDE_ICONS = {
  grow: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4H4v5M15 4h5v5M9 20H4v-5M15 20h5v-5"/></svg>`,
  shrink: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h5V4M20 9h-5V4M4 15h5v5M20 15h-5v5"/></svg>`,
};

function paintWide(button) {
  const key = button.dataset.wide;
  const dialog = button.closest("dialog");
  const on = !!prefs[key];
  dialog.classList.toggle("wide", on);
  button.innerHTML = on ? WIDE_ICONS.shrink : WIDE_ICONS.grow;
  button.title = on ? "Shrink back to a panel" : "Fill the window";
  button.setAttribute("aria-pressed", String(on));
}

const wideButtons = () => document.querySelectorAll(".dlgwide");

function applyWide() { wideButtons().forEach(paintWide); }

for (const button of wideButtons()) {
  button.addEventListener("click", () => {
    savePrefs({ [button.dataset.wide]: !prefs[button.dataset.wide] });
    paintWide(button);
  });
}

/* ---------- theme ---------- */

// Named rather than raw colours, so the stylesheet stays the one place that
// decides what "green" actually looks like on each tone.
const ACCENTS = [
  ["blue", "Blue"], ["cyan", "Cyan"], ["teal", "Teal"], ["green", "Green"],
  ["gold", "Gold"], ["orange", "Orange"], ["red", "Red"], ["pink", "Pink"],
  ["purple", "Purple"],
];
const TONES = ["default", "dark", "light"];

function applyTheme() {
  const root = document.documentElement;
  root.dataset.tone = TONES.includes(prefs.tone) ? prefs.tone : "default";
  root.dataset.accent = ACCENTS.some(([v]) => v === prefs.accent)
    ? prefs.accent : "blue";
  // Mirrored into the page's own storage so the next launch can paint the
  // right colours before /api/prefs has answered.
  try {
    localStorage.setItem("romsrx.tone", root.dataset.tone);
    localStorage.setItem("romsrx.accent", root.dataset.accent);
  } catch { /* storage disabled - the server copy still holds */ }
  paintThemePicker();
}

function paintThemePicker() {
  for (const button of els.toneRow.querySelectorAll("button")) {
    button.classList.toggle("on", button.dataset.tone === prefs.tone);
  }
  for (const button of els.accentRow.querySelectorAll(".swatch")) {
    button.classList.toggle("on", button.dataset.accent === prefs.accent);
  }
}

// Each swatch carries its own colour, so the list reads as colours rather
// than as words. `--swatch` is the same hue the stylesheet would apply.
els.accentRow.innerHTML = ACCENTS.map(([value, label]) => `
  <button class="swatch" data-accent="${value}" title="${label}"
    aria-label="${label}" style="--swatch: var(--hue-${value})"></button>`).join("");

els.toneRow.addEventListener("click", (ev) => {
  const tone = ev.target.closest("button")?.dataset.tone;
  if (!tone) return;
  savePrefs({ tone });
  applyTheme();
});

els.accentRow.addEventListener("click", (ev) => {
  const accent = ev.target.closest(".swatch")?.dataset.accent;
  if (!accent) return;
  savePrefs({ accent });
  applyTheme();
});

/* ---------- language ---------- */

els.langRow.innerHTML = Object.entries(LANGUAGES).map(([code, name]) => `
  <button data-lang="${code}">${esc(name)}</button>`).join("");

function paintLanguagePicker() {
  for (const button of els.langRow.querySelectorAll("button")) {
    button.classList.toggle("on", button.dataset.lang === prefs.lang);
  }
}

/** Switch language and redraw everything that holds words.
 *
 *  The marked-up markup is handled by applyLanguage; everything built from
 *  JavaScript has to be asked to draw itself again, which is why each renderer
 *  is called rather than reloading the page. Reloading would be simpler and
 *  would throw away the search you had typed. */
function setLanguage(code) {
  savePrefs({ lang: code });
  applyLanguage(code);
  paintLanguagePicker();

  loadStats();                       // tagline and footer
  search(false);                     // result rows and filter menus
  if (libraryData) renderLibrary();
  renderCart();
  pollDownloads();
  paintVersion();
  measureHeader();
}

els.langRow.addEventListener("click", (ev) => {
  const code = ev.target.closest("button")?.dataset.lang;
  if (code && code !== prefs.lang) setLanguage(code);
});



/* Click the backdrop to dismiss. Both checks are needed:
     target === dialog  - a <select> popup is drawn outside the dialog's box,
                          so choosing an option would otherwise read as a
                          backdrop click and close the whole thing.
     outside the box    - the dialog's own padding still belongs to it. */
/** Whether a pointer event landed beyond the dialog's own box.
 *
 *  The backdrop is not an element, so a press on it is reported against the
 *  dialog - as is a press on the dialog's own padding. Only the coordinates
 *  can tell those two apart. */
function beyondDialog(dialog, ev) {
  const box = dialog.getBoundingClientRect();
  return ev.clientX < box.left || ev.clientX > box.right
    || ev.clientY < box.top || ev.clientY > box.bottom;
}

function closeOnBackdrop(dialog) {
  /* Where the press began, not where it ended.

     A click event fires on the nearest ancestor of both the press and the
     release, so dragging out of a text box inside the dialog and letting go
     past its edge - which is exactly what selecting a long path to replace it
     looks like - delivers a click whose target is the dialog. Judged on the
     release alone, that shut the window and threw the edit away.

     Dismissing is a gesture that has to start on the backdrop. Releasing
     there is not enough, and neither is a press that began outside the window
     altogether: no pointerdown ever reaches us for that, so the flag stays
     down and nothing closes. */
  let fromBackdrop = false;

  dialog.addEventListener("pointerdown", (ev) => {
    fromBackdrop = ev.target === dialog && beyondDialog(dialog, ev);
  });
  // A drag the system took over - a window-manager gesture, a lost pointer -
  // never became a click, so it must not leave the flag armed for the next one.
  dialog.addEventListener("pointercancel", () => { fromBackdrop = false; });

  dialog.addEventListener("click", (ev) => {
    const started = fromBackdrop;
    fromBackdrop = false;
    if (!started) return;
    if (ev.target !== dialog || !ev.detail) return;
    const box = dialog.getBoundingClientRect();
    if (!beyondDialog(dialog, ev)) return;

    // A maximised panel fills everything below the header, so the only real
    // estate left to click is the header itself - and that is what dismisses
    // it. The 12px slivers down the sides and along the bottom are ignored:
    // they are too easy to clip while aiming at the edge of the list.
    if (dialog.classList.contains("wide")) {
      if (ev.clientY < box.top) dialog.close();
      return;
    }
    dialog.close();
  });
}

/* Every dialog, the question box included. Clicking away from a question
   settles it as "no", which is what Esc already did and the safe answer in
   every case - the alternative is a box you can only escape from with the
   keyboard. */
for (const dialog of document.querySelectorAll("dialog")) closeOnBackdrop(dialog);

els.askOk.addEventListener("click", () => askClose(true));
els.askCancel.addEventListener("click", () => askClose(false));
// Esc and the backdrop both close a <dialog> without touching our buttons.
els.askDlg.addEventListener("close", () => askClose(false));

/* ---------- mouse back / forward ---------- */

/* One page, so there is no browser history worth moving through - what these
   step through is the panels you have open. The buttons are handled here
   rather than through the History API precisely because nothing is pushed
   onto it: whatever the engine does with them natively then has nowhere to
   go, and can't take the app off its own page.

   The question dialog is left out - it is an interruption, not somewhere you
   navigated to. */
const navOpen = [];      // panels open, oldest first
const navClosed = [];    // what Back took away, for Forward to bring back

// Which button reopens a given dialog. Going through the button reloads
// whatever it shows, so a panel restored by Forward isn't showing stale data.
const NAV_REOPEN = {
  cartdlg: "cartBtn", dldlg: "dlBtn", acctdlg: "acctBtn",
  settingsdlg: "settingsBtn",
};
const NAV_SKIP = new Set(["askdlg", "namedlg"]);

let navMoving = false;   // suppresses the usual "new place, forget forward"

for (const dialog of document.querySelectorAll("dialog")) {
  if (NAV_SKIP.has(dialog.id)) continue;
  const showModal = dialog.showModal.bind(dialog);
  dialog.showModal = () => {
    showModal();
    if (!navOpen.includes(dialog)) navOpen.push(dialog);
    if (!navMoving) navClosed.length = 0;
  };
  dialog.addEventListener("close", () => {
    const at = navOpen.indexOf(dialog);
    if (at >= 0) navOpen.splice(at, 1);
  });
}

function navBack() {
  // A question on screen is waiting for an answer, not somewhere you can
  // step back from - stepping would close the panel behind it instead. The
  // same goes for the box asking what to call a playlist.
  if (els.askDlg.open || els.nameDlg.open) return;
  const dialog = navOpen[navOpen.length - 1];
  if (dialog) {
    dialog.close();
    navClosed.push(dialog);
  } else if (libraryOpen) {
    showLibrary(false);
    navClosed.push("library");
  }
}

function navForward() {
  if (els.askDlg.open || els.nameDlg.open) return;
  const last = navClosed.pop();
  if (!last) return;
  navMoving = true;
  try {
    if (last === "library") {
      showLibrary(true);
    } else {
      const button = els[NAV_REOPEN[last.id]];
      if (button) button.click(); else last.showModal();
    }
  } finally {
    navMoving = false;
  }
}

// Buttons 3 and 4 are the thumb pair. preventDefault on both press and
// release so the engine doesn't also try to navigate.
for (const type of ["mousedown", "mouseup", "auxclick"]) {
  addEventListener(type, (ev) => {
    if (ev.button !== 3 && ev.button !== 4) return;
    ev.preventDefault();
    if (type !== "mouseup") return;
    ev.button === 3 ? navBack() : navForward();
  });
}

measureHeader();
addEventListener("resize", measureHeader);

/* Everything the user set last time comes back before the first render. */
(async () => {
  await loadPrefs();
  // Language first: everything drawn after this should already be in it.
  applyLanguage(prefs.lang);
  paintLanguagePicker();
  applyTheme();
  applyWide();
  paintMute();
  els.libTitles.checked = prefs.libTitles;
  els.libSize.value = String(prefs.libSize);
  els.libSort.value = prefs.libSort;
  els.cartSort.value = prefs.cartSort;
  applyCompact(prefs.cartCompact);
  await Promise.all([loadCart(), loadPlaylists(), loadRecent()]);
  paintAddButtons();     // the first search may have drawn before these landed
})();

els.upLater.addEventListener("click", () => {
  try { localStorage.setItem("romsrx.skipUpdate", latestUpdate?.latest || ""); } catch { }
  els.updateBar.hidden = true;
});

/* Release notes are written in Markdown, for the GitHub page that also shows
   them; this box is plain text. Only the two markers that actually turn up get
   stripped - headings and bold - so "## Fixed" reads as a heading rather than
   as two stray hashes. */
const plainNotes = (text) => String(text || "")
  .replace(/^#{1,6}\s*/gm, "")
  .replace(/\*\*(.+?)\*\*/g, "$1");

/* Release notes are a page of prose, not a one-line question, so they get a
   wider box than the yes/no it shares. */
const showNotes = () => say(
  plainNotes(latestUpdate?.notes) || t("No notes for this release."),
  { notes: true });

els.upNotes.addEventListener("click", showNotes);
els.upDlgNotes.addEventListener("click", showNotes);

/** The same offer as the bar, in front of you, for when you went looking. */
function openUpdateDialog(info) {
  if (!info?.update) return;
  els.upWhat.textContent =
    `RomSrx ${info.latest} is available — you have ${info.current}.`;
  els.upDlgGet.href = info.asset?.url || info.page;
  els.upDlgGet.textContent = info.asset
    ? `${t("Download")} (${humanSize(info.asset.size)})`
    : t("Open release page");
  els.upDlgNotes.hidden = !info.notes;
  els.upDlg.showModal();
}

els.upDlgLater.addEventListener("click", () => els.upDlg.close());

// The footer is rebuilt by loadStats, so the button is caught as it bubbles.
els.footer.addEventListener("click", async (ev) => {
  if (!ev.target.closest("#checkupdates")) return;
  const button = ev.target.closest("#checkupdates");
  button.textContent = t("Checking…");
  const info = await checkUpdates(true);
  button.textContent = t("Check for updates");
  if (!info) await say(t("Could not reach GitHub to check for updates."));
  else if (info.error) await say(t("Could not check for updates - no connection."));
  else if (!info.update) await say(t("You're up to date. RomSrx {version} is the latest.", { version: info.current }));
  else {
    // Asking again un-skips: you went looking for this one.
    try { localStorage.removeItem("romsrx.skipUpdate"); } catch { }
    showUpdate(info);        // the bar stays, for the next launch
    openUpdateDialog(info);  // ...and the answer appears where you asked
  }
});

loadAccount();
pollDownloads();   // keeps the header badge live even with the panel closed
loadStats();
search(false);
checkUpdates();
resumeIndexIfRunning();

/* Read the download folders once at startup so search results can say what is
   already here. It reads the disk, so it goes last and its result is painted
   onto whatever has rendered by the time it lands. */
fetchLibrary().catch(() => { /* the Library tab will try again */ });

/* ---------- backup ----------
   Both sides go through the system's own file picker, so the user says where
   it lands and where it comes from - the app never writes anywhere it wasn't
   pointed at. */
async function runBackup(button, route, busyText) {
  const label = button.textContent;
  button.disabled = true;
  button.textContent = busyText;
  try {
    const res = await fetch(route, { method: "POST" }).then((r) => r.json());
    if (res.cancelled) { /* they closed the picker; say nothing */ }
    else if (res.error) await say(res.error);
    else if (route === "/api/backup") {
      await say(t("Backup saved to {path}\n\n{n} items.",
                  { path: res.path, n: res.files }));
    } else {
      await say(t("Restored {n} items.\n\nRomSrx needs to be restarted "
                  + "for all of it to take effect.", { n: res.files }));
    }
  } catch {
    await say(t("Could not reach the app."));
  }
  button.textContent = label;
  button.disabled = false;
}

els.backupSave.addEventListener("click", () =>
  runBackup(els.backupSave, "/api/backup", t("Choosing…")));

els.backupLoad.addEventListener("click", async () => {
  // Restoring replaces what is here now, which is worth one question.
  const go = await ask(
    t("Restore from a backup?\n\nYour current settings, download list and "
      + "playlists on this machine are replaced by the ones in the file."),
    { confirm: true, ok: t("Restore") });
  if (go) await runBackup(els.backupLoad, "/api/restore", t("Choosing…"));
});

