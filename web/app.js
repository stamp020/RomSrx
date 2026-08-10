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
  dlFolders: $("dlfolders"), foldersDlg: $("foldersdlg"), folderList: $("folderlist"),
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
  coverMenu: $("covermenu"),
  searchbar: document.querySelector(".searchbar"),
  searchStick: $("searchstick"),
  cartSelAll: $("cartselall"), cartDlSel: $("cartdlsel"), cartRmSel: $("cartrmsel"),
  cartClrDone: $("cartclrdone"),
  themeBtn: $("themebtn"), themeDlg: $("themedlg"),
  toneRow: $("tonerow"), accentRow: $("accentrow"), langRow: $("langrow"),
  askDlg: $("askdlg"), askBody: $("askbody"), askOk: $("askok"),
  askCancel: $("askcancel"),
  updateBar: $("updatebar"), upMsg: $("upmsg"), upGet: $("upget"),
  upNotes: $("upnotes"), upLater: $("uplater"),
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

/** Resolves true if they went ahead, false if they backed out. */
function ask(message, { confirm = false, danger = false, ok = "OK" } = {}) {
  askClose(false);                 // never leave an earlier question hanging
  els.askBody.textContent = message;
  els.askCancel.hidden = !confirm;
  els.askOk.textContent = ok;
  els.askOk.classList.toggle("danger", danger);
  els.askDlg.showModal();
  /* Focused without scrolling, then wound back to the top. The button sits
     below the message, so focusing it normally scrolls it into view - which
     nobody notices on a one-line question, but opens a long set of release
     notes at the very end of them. */
  els.askOk.focus({ preventScroll: true });
  els.askDlg.scrollTop = 0;
  return new Promise((resolve) => { askSettle = resolve; });
}

/** Just tells them something; there is nothing to decide. */
const say = (message) => ask(message);

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

const PAGE = 40;
const DIMENSIONS = [["console", "Console"], ["region", "Region"], ["ext", "Type"]];

// View preferences, stored server-side so they survive a restart, a different
// port, or reinstalling the app.
const prefs = {
  cartCompact: false, libView: "grid", libTitles: true,
  libSize: 160, libSort: "name", cartSort: "added-desc",
  tone: "default", accent: "blue", lang: "en",
  libPinned: [], libShut: [],
  cartWide: false, dlWide: false,
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
  fetch("/api/cart", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items: [...cart.values()] }),
  }).catch(() => { /* keep working even if the write fails */ });
}

const cartBytes = () => [...cart.values()].reduce((n, i) => n + (i.size || 0), 0);

// The row carries everything the list needs, so the cart survives a new
// search without having to look anything up again.
function cartButton(f) {
  const inList = cart.has(f.url);
  return `<button class="cartadd${inList ? " in" : ""}" data-url="${esc(f.url)}"
    data-name="${esc(f.filename)}" data-size="${f.size || 0}"
    data-console="${esc(f.console)}" data-source="${esc(f.source_name)}"
    data-ext="${esc(f.ext || "")}" data-login="${f.requires_login ? 1 : 0}"
    title="${esc(t(inList ? "Remove from list" : "Add to download list"))}"
    >${inList ? "&#10003;" : "+"}</button>`;
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

els.results.addEventListener("click", async (ev) => {
  const btn = ev.target.closest(".cartadd");
  if (!btn) return;
  ev.preventDefault();

  const url = btn.dataset.url;
  if (cart.has(url)) {
    cart.delete(url);
  } else {
    // Adding something you can't download would only fail later, well away
    // from the click that caused it.
    if (!await allowLoginOnly(btn.dataset.login === "1", "That file")) return;
    cart.set(url, {
      url, filename: btn.dataset.name, size: Number(btn.dataset.size) || 0,
      console: btn.dataset.console, source: btn.dataset.source,
      ext: btn.dataset.ext, login: btn.dataset.login === "1",
      added: Date.now(),
    });
  }
  const inList = cart.has(url);
  btn.classList.toggle("in", inList);
  btn.innerHTML = inList ? "&#10003;" : "+";
  btn.title = t(inList ? "Remove from list" : "Add to download list");
  saveCart();
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

// Put any result row that is no longer in the list back to its "+" state.
function syncRowButtons() {
  for (const btn of els.results.querySelectorAll(".cartadd.in")) {
    if (!cart.has(btn.dataset.url)) {
      btn.classList.remove("in");
      btn.innerHTML = "+";
      btn.title = t("Add to download list");
    }
  }
}

els.cartItems.addEventListener("click", (ev) => {
  const rm = ev.target.closest(".ci-rm");
  if (!rm) return;
  cart.delete(rm.dataset.url);
  selected.delete(rm.dataset.url);
  saveCart();
  renderCart();
  syncRowButtons();
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
  syncRowButtons();
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

  const label = button.textContent;
  button.disabled = true;
  button.textContent = t("Queueing…");

  const added = await queueDownloads(items.map((i) => ({
    url: i.url, filename: i.filename, size: i.size,
    console: i.console, source: i.source, login: !!i.login,
  })));

  button.textContent = added < 0 ? t("Server unreachable") : label;
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
  syncRowButtons();
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

  offset += data.groups.length;
  els.more.hidden = offset >= total;
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
    await say("Could not reach GitHub to fetch the release notes.");
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

  return `
    <div class="dljob ${esc(job.status)}" data-id="${job.id}">
      ${art}
      <div class="dj-body">
        <div class="dj-top">
          <span class="dj-name">${esc(job.filename)}${job.login
            ? ` <span class="lock">&#128274; ${esc(t("login"))}</span>` : ""}</span>
          <span class="dj-pct">${finished ? "100%" : pct.toFixed(0) + "%"}</span>
          ${finished ? `<button class="dj-open" data-id="${job.id}"
                          title="${esc(t("Open containing folder"))}">&#128193;</button>` : ""}
          ${order}
          ${control}
          <button class="dj-trash" data-id="${job.id}"
            title="${esc(t("Delete this download and its files from your PC"))}">&#128465;</button>
        </div>
        <div class="dj-bar"><span style="width:${pct}%"></span></div>
        <div class="dj-meta">${job.console
          ? `<span class="ctag">${esc(job.console)}</span>` : ""}${jobMeta(job)}</div>
      </div>
    </div>`;
}

function renderDownloads(state) {
  const jobs = state.jobs || [];
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
      const pct = Math.min(job.percent, 100);
      row.querySelector(".dj-pct").textContent =
        job.status === "done" ? "100%" : `${pct.toFixed(0)}%`;
      row.querySelector(".dj-bar span").style.width = `${pct}%`;
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
async function syncCartWithFinished(jobs) {
  const done = (jobs || []).filter((j) => j.status === "done").map((j) => j.id);
  const fresh = done.filter((id) => !finishedJobs.has(id));
  for (const id of done) finishedJobs.add(id);

  if (!sawFirstPoll) { sawFirstPoll = true; return; }
  if (!fresh.length) return;

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

els.dlJobs.addEventListener("click", async (ev) => {
  const open = ev.target.closest(".dj-open");
  if (open) {
    await fetch("/api/downloads/reveal", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: Number(open.dataset.id) }),
    });
    return;
  }
  const bin = ev.target.closest(".dj-trash");
  if (bin) {
    // This deletes what is on disk, not just the row, so it gets asked about.
    const row = bin.closest(".dljob");
    const name = row?.querySelector(".dj-name")?.textContent || "this download";
    const go = await ask(
      `Delete "${name}" from your PC?`
      + "\n\nThe file is removed from disk, along with any part-download."
      + " This can't be undone.",
      { confirm: true, danger: true, ok: "Delete" });
    if (!go) return;

    bin.disabled = true;
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
    `Remove all ${total} download${total === 1 ? "" : "s"} and delete their `
    + "files from your PC?\n\nFinished files and part-downloads are both deleted.",
    { confirm: true, danger: true, ok: "Remove all" });
  if (!go) return;
  els.dlRemoveAll.disabled = true;
  els.dlRemoveAll.textContent = "Removing…";
  await fetch("/api/downloads/discardall", { method: "POST" });
  els.dlRemoveAll.textContent = "Remove all";
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
    syncWorkerInfo();
    } catch { /* leave whatever is on screen */ }
}

/* Taking finished downloads off the list is the server's job - it has to
   happen for things that finish while this dialog, or the whole window, is
   shut. All the page does is set the switch and pick the change up again. */
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

/** Library entries are already No-Intro stems, so they feed the cover
 *  lookup directly with no extension to strip. A cover the user set
 *  themselves always wins. */
const libCovers = (game) => (game.cover ? [game.cover] : [])
  .concat(coverCandidates([{ console: game.console, filename: game.name, ext: "" }]));

/** The image itself carries `libhit`, so only the artwork is clickable -
 *  not the empty space a narrower cover leaves in its tile.
 *
 *  `data-title` is what the tile falls back to once every candidate has
 *  404'd. Without it the tile ends up genuinely blank, which in a wall of
 *  covers reads as a broken row rather than a game with no art. The list view
 *  gets the console instead - its thumbnail is far too small for a title, and
 *  the name is already spelled out beside it. */
function libCoverHtml(game, big) {
  const urls = libCovers(game);
  const cls = big ? "libart" : "librowart";
  const label = big ? (game.title || game.name) : (game.console || "?");
  if (!urls.length) {
    return `<span class="${cls}"><span class="noart libhit">${esc(label)}</span></span>`;
  }
  return `<span class="${cls}"><img class="libhit" src="${esc(urls[0])}"
    data-rest='${esc(JSON.stringify(urls.slice(1)))}'
    data-title="${esc(label)}" alt="" loading="lazy"
    decoding="async" onerror="coverFail(this)"></span>`;
}

// Picked state is painted on afterwards by paintSelection(), never baked in
// here - re-rendering the markup for a tick would reload every cover image.
function libGridCard(game) {
  return `
    <div class="libcard" data-path="${esc(game.path)}" title="${esc(game.name)}">
      ${libCoverHtml(game, true)}
      <span class="libtick"></span>
      <span class="libname libhit">${esc(game.title)}</span>
    </div>`;
}

function libListRow(game) {
  const bits = [];
  if (game.regions.length) bits.push(game.regions.join(", "));
  if (game.languages.length) bits.push(game.languages.join(", "));
  if (game.version) bits.push(game.version);
  if (game.disc) bits.push(`Disc ${game.disc}`);
  if (game.tags.length) bits.push(game.tags.join(", "));
  bits.push(game.extracted ? `folder · ${game.files} file${game.files === 1 ? "" : "s"}`
                           : (game.ext || "file").toUpperCase());
  return `
    <div class="librow" data-path="${esc(game.path)}">
      <span class="libtick"></span>
      ${libCoverHtml(game, false)}
      <span class="librowname libhit">${esc(game.name)}
        <span class="librowsub">${bits.map(esc).join(" &middot; ")}</span>
      </span>
      <span class="librowsize">${humanSize(game.size)}</span>
    </div>`;
}

/** Does this game answer to what was typed in the library's search box?
 *
 *  Every word has to appear somewhere, in any order - "kart mario" finds Mario
 *  Kart just as "mario kart" does, which matters when you half-remember a
 *  title. The console is searchable too, so "gba zelda" narrows in one go. */
function libMatches(game, needle) {
  const hay = `${game.title} ${game.name} ${game.console || ""}`.toLowerCase();
  return needle.split(/\s+/).every((word) => hay.includes(word));
}

function renderLibraryConsoles() {
  const keep = els.libConsole.value;
  els.libConsole.innerHTML =
    `<option value="">${esc(t("All consoles"))} (${libraryData.total})</option>`
    + libraryData.consoles.map((c) =>
        `<option value="${esc(c.console)}">${esc(c.console)} (${c.count})</option>`).join("");
  els.libConsole.value =
    libraryData.consoles.some((c) => c.console === keep) ? keep : "";
}

function renderLibrary() {
  if (!libraryData) return;
  renderLibraryConsoles();

  const { total, bytes, base } = libraryData;
  const wanted = els.libConsole.value;
  const needle = els.libQ.value.trim().toLowerCase();
  let games = wanted
    ? libraryData.games.filter((g) => (g.console || "Unsorted") === wanted)
    : libraryData.games;
  if (needle) games = games.filter((g) => libMatches(g, needle));
  const shownBytes = games.reduce((n, g) => n + g.size, 0);
  const narrowed = wanted || needle;

  // No folder path here - with per-console paths there isn't a single one.
  els.libStats.textContent = !total
    ? t("No games found")
    : (narrowed
        ? `${games.length} of ${total} games · ${humanSize(shownBytes)}`
        : `${total.toLocaleString()} game${total === 1 ? "" : "s"} · ${humanSize(bytes)}`);

  els.libGrid.classList.toggle("on", prefs.libView === "grid");
  els.libList.classList.toggle("on", prefs.libView === "list");
  els.libTitlesWrap.hidden = prefs.libView !== "grid";
  els.libSizeWrap.hidden = prefs.libView !== "grid";
  els.libBody.style.setProperty("--cover", `${prefs.libSize}px`);
  els.libBody.classList.toggle("notitles", !prefs.libTitles);

  if (!games.length) {
    els.libBody.innerHTML = total
      ? `<p class="empty">${needle
          ? `Nothing here matches “${esc(els.libQ.value.trim())}”.`
          : t("No games for that console.")}</p>`
      : `<p class="empty">No games here yet. Anything you download lands in this
         folder and will show up on Refresh.</p>`;
    paintSelection();
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
  for (const game of games) {
    const key = game.console || "Unsorted";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(game);
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
  els.libBody.innerHTML = order2.map(([console_, items]) => {
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

els.libBody.addEventListener("load", (ev) => {
  const img = ev.target;
  if (img instanceof HTMLImageElement && img.closest(".libart")) matchArtRatio(img);
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

const installKey = (name) =>
  String(name || "").toLowerCase().replace(/\s+/g, " ").trim();

function buildInstalledIndex() {
  installedIndex.clear();
  for (const game of libraryData?.games || []) {
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
async function fetchLibrary() {
  libraryData = await fetch("/api/library").then((r) => r.json());
  // Games that were deleted or renamed must not keep padding "Remove (n)".
  const alive = new Set(libraryData.games.map((g) => g.path));
  for (const p of libSelected) if (!alive.has(p)) libSelected.delete(p);
  buildInstalledIndex();
  paintInstalled();
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

/** Jump from a search result to the copy you already have.
 *
 *  Any filter that would hide it is cleared first, and a folded-away console
 *  is opened - arriving at a library that doesn't visibly contain the game you
 *  just clicked would read as the link being broken. */
async function revealInLibrary(path) {
  showLibrary(true);
  if (!libraryData) await loadLibrary();

  const game = libraryData?.games.find((g) => g.path === path);
  if (!game) { await say("That game is no longer in your library."); return; }

  els.libConsole.value = "";
  els.libQ.value = "";
  els.libQClear.hidden = true;
  const group = game.console || "Unsorted";
  if (isCollapsed(group)) toggleInPref("libShut", group);
  renderLibrary();

  // Paths carry backslashes and brackets, so this is a scan rather than an
  // attribute selector - no escaping to get wrong.
  const card = [...els.libBody.querySelectorAll("[data-path]")]
    .find((el) => el.dataset.path === path);
  if (!card) return;
  card.scrollIntoView({ block: "center", behavior: "smooth" });
  card.classList.remove("libfound");
  void card.offsetWidth;            // restart the animation on a repeat click
  card.classList.add("libfound");
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
  els.results.hidden = on;
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
els.homeBtn.addEventListener("click", goToSearch);
els.titleBtn.addEventListener("click", goToSearch);
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
els.libBody.addEventListener("click", async (ev) => {
  if (ev.target.closest(".libpickall")) return;
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
  await fetch("/api/library/reveal", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
});

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
  if (ev.key !== "Escape" || !libSelectMode || isShown(els.libMenu)) return;
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

/** Delete everything currently ticked, after asking. Shared by the toolbar's
 *  Remove button and the right-click menu, so both ask the same question and
 *  neither can drift into deleting on different terms from the other. */
async function removeSelectedGames() {
  const paths = [...libSelected];
  if (!paths.length) return;
  const go = await ask(
    `Delete ${paths.length} game${paths.length === 1 ? "" : "s"} from your PC?`
    + "\n\nThe files are removed from disk, not just the list."
    + "\n\nThis can't be undone.",
    { confirm: true, danger: true, ok: `Delete ${paths.length}` });
  if (!go) return;

  els.libRemove.disabled = true;
  const res = await fetch("/api/library/delete", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paths }),
  }).then((r) => r.json()).catch(() => ({ failed: [{ error: "Could not reach the app." }] }));
  els.libRemove.disabled = false;
  libSelected.clear();
  if (res.failed?.length) {
    await say(`Removed ${res.removed ?? 0}. Could not remove ${res.failed.length}:\n`
      + res.failed.map((f) => `• ${f.error}`).join("\n"));
  }
  await loadLibrary();
}

els.libRemove.addEventListener("click", removeSelectedGames);

/* ---------- right-click menus ---------- */

let menuPath = "";
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
    return libraryData?.games.find((g) => g.path === card.dataset.path)?.console || "";
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

function closeLibMenu() { hideTop(els.libMenu); menuPath = ""; }
function closeMenus() { closeLibMenu(); hideTop(els.coverMenu); }

/** Opened at the pointer, pulled back when it would run off the edge.
 *
 *  The menu is moved into whatever dialog it was opened from. A modal dialog
 *  makes everything outside its own subtree inert, so a menu parked elsewhere
 *  in the page is drawn over the dialog but silently refuses every click.
 *  Being a popover is what keeps it positioned against the viewport once it
 *  is in there, instead of against the dialog's own transformed box. */
function openMenu(menu, ev) {
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
  const card = ev.target.closest("[data-path]");
  if (!card) return;
  ev.preventDefault();

  const game = libraryData?.games.find((g) => g.path === card.dataset.path);
  // A game whose art never loaded has no image left to save.
  menuCover = coverSrc(card.querySelector("img"));
  els.libMenuSave.hidden = !menuCover;
  els.libMenuClear.hidden = !game?.cover;

  /* Clearing a whole selection from here saves going back up to the toolbar
     for it. Offered only when the game under the pointer is itself one of the
     selected ones - right-clicking outside the selection means you are talking
     about that game, and "all" would quietly take out several others. A
     selection of one already has "Delete game from PC" above it. */
  const bulk = libSelected.size > 1 && libSelected.has(card.dataset.path);
  els.libMenuRemoveSel.hidden = !bulk;
  if (bulk) els.libMenuRemoveSel.textContent = `Remove all (${libSelected.size})`;

  openMenu(els.libMenu, ev);
  menuPath = card.dataset.path;   // openMenu clears it
});

/* Saving a cover, anywhere one is shown. The app window has no browser
   context menu of its own, so this is the one piece of it worth rebuilding -
   box art is useful outside the app, as emulator thumbnails. */

/** The src of an image only if it is box art - covers come from the
 *  thumbnail server, or from /covers/ when the user set one themselves. */
function coverSrc(img) {
  const raw = img?.tagName === "IMG" ? img.getAttribute("src") || "" : "";
  return raw.startsWith(THUMB_BASE) || raw.startsWith("/covers/") ? raw : "";
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
  if (res.saved && res.asked === false) toast(`Cover saved to ${res.saved}`);
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
  if (!ev.target.closest("#libmenu, #covermenu")) closeMenus();
});
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") closeMenus();
});

els.libMenu.addEventListener("click", async (ev) => {
  const action = ev.target.closest("button")?.dataset.act;
  if (!action || !menuPath) return;
  const path = menuPath;
  const art = menuCover;
  const game = libraryData?.games.find((g) => g.path === path);
  closeLibMenu();

  if (action === "savecover") {
    if (art) {
      await saveCover(art, coverFileName(art, game?.name || "cover"),
                      game?.console || "");
    }
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
      `Delete "${game ? game.name : path}" from your PC?`
      + "\n\nThe files are removed from disk, not just the list.",
      { confirm: true, danger: true, ok: "Delete" });
    if (!go) return;
    const res = await fetch("/api/library/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths: [path] }),
    }).then((r) => r.json());
    if (res.failed?.length) await say(res.failed[0].error);
    await loadLibrary();
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

function folderRow(entry) {
  // The effective path is the placeholder, so you can always see where a
  // console will land even without an override set.
  const hint = shortPath(entry.effective, folderState.base);
  return `
    <div class="folderrow" data-console="${esc(entry.console)}">
      <span class="fr-name">${esc(entry.console)}</span>

      <span class="fr-cell">
        <input class="fr-path" type="text" spellcheck="false" title="${esc(entry.effective)}"
               value="${esc(entry.override ? entry.effective : "")}"
               placeholder="${esc(hint)}">
        <button class="fr-browse ghost small" title="${esc(t("Choose a folder"))}">&hellip;</button>
        <button class="fr-clear ghost small" title="${esc(t("Use the default"))}">&times;</button>
      </span>

      <span class="fr-cell">
        <input class="fr-cover" type="text" spellcheck="false"
               value="${esc(entry.cover || "")}"
               placeholder="${esc(t("ask every time"))}"
               title="${esc(t("Covers for this console are saved here without asking"))}">
        <button class="fr-coverbrowse ghost small" title="${esc(t("Choose a folder"))}">&hellip;</button>
        <button class="fr-coverclear ghost small" title="${esc(t("ask every time"))}">&times;</button>
      </span>
    </div>`;
}

function renderFolders() {
  els.foldersBase.textContent = folderState.base;
  els.foldersHint.textContent = t(folderState.per_console
    ? "Each console has its own subfolder. Give one a different path to send it elsewhere — a folder inside the main one is remembered relative to it, so it moves if you change the main folder."
    : "Everything shares the main folder. Give a console its own path here to split it out.");
  els.folderList.innerHTML = folderState.consoles.map(folderRow).join("");
}


async function loadFolders() {
  try {
    folderState = await fetch("/api/downloads/folders").then((r) => r.json());
    renderFolders();
  } catch { /* server restarting */ }
}

els.dlFolders.addEventListener("click", async () => {
  els.foldersDlg.showModal();
  await loadFolders();
});

// Applies straight away rather than waiting for Save, since the preview
// beside it is claiming it already has.
els.perConsole.addEventListener("change", async () => {
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ per_console: els.perConsole.checked }),
  });
  if (els.foldersDlg.open) await loadFolders();
});


/* Both columns behave the same way, so they share one handler: which input a
   button belongs to is decided by the class it carries, not by a second copy
   of all of this. */
const FOLDER_COLUMNS = [
  { browse: ".fr-browse", clear: ".fr-clear", input: ".fr-path" },
  { browse: ".fr-coverbrowse", clear: ".fr-coverclear", input: ".fr-cover" },
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
      const res = await fetch("/api/downloads/browse", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: input.value || folderState.base }),
      }).then((r) => r.json());
      if (res.folder) {
        input.value = res.folder;
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
  if (!ev.target.closest(".fr-path, .fr-cover")) return;
  await saveFolders(false);
}, 800));

async function saveFolders(showTick = true) {
  const folders = {};
  const covers = {};
  for (const row of els.folderList.querySelectorAll(".folderrow")) {
    const path = row.querySelector(".fr-path").value.trim();
    if (path) folders[row.dataset.console] = path;
    const cover = row.querySelector(".fr-cover").value.trim();
    if (cover) covers[row.dataset.console] = cover;
  }
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ per_console: els.perConsole.checked,
                           console_folders: folders,
                           cover_folders: covers }),
  });
  if (showTick) {
    els.foldersSaved.hidden = false;
    setTimeout(() => { els.foldersSaved.hidden = true; }, 1600);
  }
}

els.foldersReset.addEventListener("click", async () => {
  for (const input of els.folderList.querySelectorAll(".fr-path, .fr-cover")) {
    input.value = "";
  }
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
    showAccountError("Could not reach the local server.");
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
        await say(`${state.paused} download${state.paused === 1 ? "" : "s"} `
          + `need${state.paused === 1 ? "s" : ""} an archive.org account, so `
          + (state.paused === 1 ? "it has" : "they have") + " been paused.\n\n"
          + "Nothing is lost — sign back in and resume, and "
          + (state.paused === 1 ? "it picks" : "they pick")
          + " up from where they stopped.");
      }
    } catch { showAccountError("Could not reach the local server."); }
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

els.themeBtn.addEventListener("click", () => els.themeDlg.showModal());

/* Click the backdrop to dismiss. Both checks are needed:
     target === dialog  - a <select> popup is drawn outside the dialog's box,
                          so choosing an option would otherwise read as a
                          backdrop click and close the whole thing.
     outside the box    - the dialog's own padding still belongs to it. */
function closeOnBackdrop(dialog) {
  dialog.addEventListener("click", (ev) => {
    if (ev.target !== dialog || !ev.detail) return;
    const box = dialog.getBoundingClientRect();
    const outside = ev.clientX < box.left || ev.clientX > box.right
      || ev.clientY < box.top || ev.clientY > box.bottom;
    if (!outside) return;

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
  themedlg: "themeBtn", foldersdlg: "dlFolders",
};
const NAV_SKIP = new Set(["askdlg"]);

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
  // step back from - stepping would close the panel behind it instead.
  if (els.askDlg.open) return;
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
  if (els.askDlg.open) return;
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
  els.libTitles.checked = prefs.libTitles;
  els.libSize.value = String(prefs.libSize);
  els.libSort.value = prefs.libSort;
  els.cartSort.value = prefs.cartSort;
  applyCompact(prefs.cartCompact);
  await loadCart();
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

els.upNotes.addEventListener("click", () =>
  say(plainNotes(latestUpdate?.notes) || "No notes for this release."));

// The footer is rebuilt by loadStats, so the button is caught as it bubbles.
els.footer.addEventListener("click", async (ev) => {
  if (!ev.target.closest("#checkupdates")) return;
  const button = ev.target.closest("#checkupdates");
  button.textContent = "Checking…";
  const info = await checkUpdates(true);
  button.textContent = "Check for updates";
  if (!info) await say("Could not reach GitHub to check for updates.");
  else if (info.error) await say("Could not check for updates - no connection.");
  else if (!info.update) await say(`You're up to date. RomSrx ${info.current} is the latest.`);
  else { try { localStorage.removeItem("romsrx.skipUpdate"); } catch { } showUpdate(info); }
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
