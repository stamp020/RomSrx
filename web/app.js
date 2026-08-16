const $ = (id) => document.getElementById(id);
const els = {
  q: $("q"), qClear: $("qclear"), filters: $("filters"),
  results: $("results"), more: $("more"),
  hint: $("hint"), footer: $("footer"), tagline: $("tagline"),
  reindex: $("reindex"), dlg: $("indexdlg"), log: $("indexlog"),
  indexBar: $("indexbar"), indexCount: $("indexcount"),
  indexAutoClose: $("indexautoclose"), wideLayout: $("widelayout"),
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
  patchFolder: $("patchfolder"), patchBrowse: $("patchbrowse"),
  patchReplace: $("patchreplace"),
  dlExtractMode: $("dlextractmode"),
  dlDelete: $("dldelete"), dlWorkerInfo: $("dlworkerinfo"),
  dlPauseAll: $("dlpauseall"), dlRemoveAll: $("dlremoveall"),
  dlFolders: $("dlfolders"), folderList: $("folderlist"),
  regionPref: $("regionpref"),
  foldersBase: $("foldersbase"), foldersHint: $("foldershint"), perConsole: $("perconsole"),
  foldersSaved: $("folderssaved"), foldersReset: $("foldersreset"),
  libBtn: $("libbtn"), libView: $("libraryview"), libBody: $("libbody"),
  libStats: $("libstats"), libGrid: $("libgrid"), libList: $("liblist"),
  libStorage: $("libstorage"), storageDlg: $("storagedlg"),
  libNext: $("libnext"), nextDlg: $("nextdlg"),
  raMe: $("rame"), raMeFace: $("rameface"), raMePic: $("ramepic"),
  raMeName: $("ramename"), raMePoints: $("ramepoints"), raMeGame: $("ramegame"),
  raMeGameIcon: $("ramegameicon"), raMeGameText: $("ramegametext"),
  coverMenuProfile: $("covermenuprofile"),
  profDlg: $("profdlg"), proFrame: $("proframe"), profPop: $("profpop"),
  libRecs: $("librecs"), recsDlg: $("recsdlg"), recsList: $("recslist"),
  recsHint: $("recshint"), recsNote: $("recsnote"),
  recsSort: $("recssort"), recsSortRow: $("recssortrow"),
  recsSortNote: $("recssortnote"), recsConsole: $("recsconsole"),
  recsOnlyRa: $("recsonlyra"), recsMore: $("recsmore"),
  recsMoreRow: $("recsmorerow"),
  nextList: $("nextlist"), nextNote: $("nextnote"),
  nextHint: $("nexthint"), nextSort: $("nextsort"),
  nextSortRow: $("nextorderwrap"), nextAll: $("nextall"),
  storageTop: $("storagetop"), storageConsoles: $("storageconsoles"),
  storageBiggest: $("storagebiggest"), storageNote: $("storagenote"),
  storageTidyRow: $("storagetidyrow"), storageStale: $("storagestale"),
  storageTidy: $("storagetidy"),
  libStray: $("libstray"), libStrayText: $("libstraytext"),
  libStrayFix: $("libstrayfix"), libStrayHide: $("libstrayhide"),
  libTitles: $("libtitles"), libSize: $("libsize"), libRefresh: $("librefresh"),
  libFoldAll: $("libfoldall"),
  libTitlesWrap: $("libtitleswrap"), libSizeWrap: $("libsizewrap"),
  libConsole: $("libconsole"), libSelect: $("libselect"), libRemove: $("libremove"),
  libSelectAll: $("libselectall"),
  libSort: $("libsort"),
  libMastered: $("libmastered"), libMasteredWrap: $("libmasteredwrap"),
  libTimesPick: $("libtimes"),
  libClick: $("libclick"), achOnPlay: $("achonplay"),
  timePop: $("timepop"), timePopRow: $("timepoprow"),
  achBlock: $("achblock"), timeAch: $("timeach"), prevAch: $("prevach"),
  achHead: $("achhead"), achLoad: $("achload"), achRefresh: $("achrefresh"),
  achCount: $("achcount"), achControls: $("achcontrols"),
  achFilter: $("achfilter"), achSort: $("achsort"),
  achList: $("achlist"), achNote: $("achnote"),
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
  libMenuRa: $("libmenura"), libMenuHash: $("libmenuhash"),
  libMenuPatch: $("libmenupatch"), libMenuApply: $("libmenuapply"),
  libMenuWeb: $("libmenuweb"), webPatchBtn: $("webpatchbtn"),
  patchBar: $("patchbar"), patchBarWhat: $("patchbarwhat"),
  patchBarFill: $("patchbarfill"), patchBarPct: $("patchbarpct"),
  patchDlg: $("patchdlg"), patchGame: $("patchgame"), patchFile: $("patchfile"),
  patchGamePick: $("patchgamepick"), patchFilePick: $("patchfilepick"),
  patchRun: $("patchrun"), patchOnline: $("patchonline"),
  patchClose: $("patchclose"), patchResult: $("patchresult"),
  patchDlgReplace: $("patchdlgreplace"),
  libMenuTool: $("libmenutool"), libMenuEmu: $("libmenuemu"),
  libMenuM3u: $("libmenum3u"),
  gameEmuDlg: $("gameemudlg"), gameEmuWhat: $("gameemuwhat"),
  gameEmuPath: $("gameemupath"), gameEmuPick: $("gameemupick"),
  gameEmuCore: $("gameemucore"), gameEmuCorePick: $("gameemucorepick"),
  gameEmuArgs: $("gameemuargs"), gameEmuSave: $("gameemusave"),
  gameEmuClear: $("gameemuclear"), gameEmuCancel: $("gameemucancel"),
  coverMenuHash: $("covermenuhash"), coverMenuPatch: $("covermenupatch"),
  coverMenu: $("covermenu"), addMenu: $("addmenu"),
  coverMenuRa: $("covermenura"), coverMenuSave: $("covermenusave"),
  raBtn: $("rabtn"), webTarget: $("webtarget"),
  coverDlg: $("coverdlg"), coverBig: $("coverbig"),
  coverBigSave: $("coverbigsave"), coverBigClose: $("coverbigclose"),
  libShelves: $("libshelves"), libNewPl: $("libnewpl"),
  libPlActions: $("libplactions"), libPlGet: $("libplget"),
  libPlCart: $("libplcart"), libPlRename: $("libplrename"),
  libPlDelete: $("libpldelete"),
  libAddPl: $("libaddpl"), libPlRemove: $("libplremove"),
  nameDlg: $("namedlg"), nameForm: $("nameform"), nameInput: $("nameinput"),
  nameTitle: $("nametitle"), nameOk: $("nameok"), nameCancel: $("namecancel"),
  pickDlg: $("pickdlg"), pickForm: $("pickform"), pickInput: $("pickinput"),
  pickTitle: $("picktitle"), pickCancel: $("pickcancel"),
  searchbar: document.querySelector(".searchbar"),
  searchSort: $("searchsort"), searchSortNote: $("searchsortnote"),
  searchStick: $("searchstick"), homeCards: $("homecards"),
  cartSelAll: $("cartselall"), cartDlSel: $("cartdlsel"), cartRmSel: $("cartrmsel"),
  cartClrDone: $("cartclrdone"),
  settingsBtn: $("settingsbtn"), settingsDlg: $("settingsdlg"),
  setTabs: $("settabs"),
  artRaOn: $("artraon"), artRaKey: $("artrakey"),
  artRaUser: $("artrauser"),
  artRaState: $("artrastate"), artRaTest: $("artratest"),
  artRaResult: $("artraresult"), artProvs: $("artprovs"),
  artIgdbOn: $("artigdbon"), artIgdbId: $("artigdbid"),
  artIgdbSecret: $("artigdbsecret"), artIgdbState: $("artigdbstate"),
  artIgdbTest: $("artigdbtest"), artIgdbResult: $("artigdbresult"),
  artSgdbOn: $("artsgdbon"), artSgdbKey: $("artsgdbkey"),
  artSgdbState: $("artsgdbstate"), artSgdbTest: $("artsgdbtest"),
  artSgdbResult: $("artsgdbresult"),
  artForget: $("artforget"), artCount: $("artcount"), artSaved: $("artsaved"),
  artMode: $("artmode"), artModeNote: $("artmodenote"),
  libSettings: $("libsettings"), cartSettings: $("cartsettings"),
  toneRow: $("tonerow"), accentRow: $("accentrow"), langRow: $("langrow"),
  prevDlg: $("prevdlg"), prevCover: $("prevcover"), prevName: $("prevname"),
  prevConsole: $("prevconsole"), prevPlay: $("prevplay"),
  prevRa: $("prevra"), prevSave: $("prevsave"), prevStats: $("prevstats"),
  prevTimes: $("prevtimes"), prevShots: $("prevshots"),
  prevSummary: $("prevsummary"), prevNote: $("prevnote"),
  coverPrev: $("coverprev"), coverNext: $("covernext"),
  coverCount: $("covercount"),
  timeDlg: $("timedlg"), timeGame: $("timegame"), timeBody: $("timebody"),
  timeNote: $("timenote"), timeOpen: $("timeopen"),
  coverMenuTime: $("covermenutime"), libMenuTime: $("libmenutime"),
  askDlg: $("askdlg"), askBody: $("askbody"),
  askOpt: $("askopt"), askOptBox: $("askoptbox"),
  askOptLabel: $("askoptlabel"), askOk: $("askok"),
  askCancel: $("askcancel"),
  updateBar: $("updatebar"), upMsg: $("upmsg"), upGet: $("upget"),
  upNotes: $("upnotes"), upLater: $("uplater"),
  upDlg: $("updlg"), upWhat: $("upwhat"), upDlgGet: $("updlgget"),
  upDlgNotes: $("updlgnotes"), upDlgLater: $("updlglater"),
  foldersDetect: $("foldersdetect"), notifyDone: $("notifydone"),
  dlMute: $("dlmute"),
  consBtn: $("consbtn"), consMenu: $("consmenu"), consClear: $("consclear"),
  consModeAll: $("consmodeall"),
  consAllDlg: $("consalldlg"), consAllGrid: $("consallgrid"),
  consAllBase: $("consallbase"),
  consBulk: $("consbulk"), consBulkCount: $("consbulkcount"),
  consBulkEmu: $("consbulkemu"), consBulkCore: $("consbulkcore"),
  consBulkNone: $("consbulknone"),
  consBulkGetCores: $("consbulkgetcores"),
  consRetroarch: $("consretroarch"), consRetroNote: $("consretronote"),
  consSearch: $("conssearch"), consItems: $("consitems"),
  backupSave: $("backupsave"), backupLoad: $("backupload"),
  backupDlg: $("backupdlg"), backupList: $("backuplist"),
  backupSaves: $("backupsaves"),
  backupGo: $("backupgo"), backupAll: $("backupall"),
  backupCancel: $("backupcancel"),
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

/* ---------- the page stays put while a window is open ----------

   A modal <dialog> stops the page behind it being clicked but not being
   scrolled: open Settings on top of a long list of search results and the
   wheel still moves the results underneath it, which reads as the window
   having come loose from the page.

   Driven by watching the `open` attribute rather than by the `close` event.
   That is not belt-and-braces: some builds this runs on - including the one
   these panels were tested in - never fire `close` at all, so anything hung
   off it would lock the page and never let go. The attribute cannot lie, and
   it also covers the ways a dialog closes without any script of ours running:
   Escape, or a form that submits with method="dialog".

   Asking whether *any* dialog is open, rather than counting them, is what
   makes stacking work: ask() opens a question over whichever panel asked it,
   and closing the question must not unlock the page while the panel behind it
   is still there. */
function lockPageScroll() {
  const anyOpen = !!document.querySelector("dialog[open]");
  document.documentElement.classList.toggle("modalopen", anyOpen);
}

new MutationObserver(lockPageScroll).observe(document.documentElement, {
  subtree: true, attributes: true, attributeFilter: ["open"],
});

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
                        cancel = "", notes = false, option = null } = {}) {
  askClose(false);                 // never leave an earlier question hanging
  els.askBody.textContent = message;
  els.askCancel.hidden = !confirm;
  // Set every time rather than only when asked for: this box is reused, and a
  // label left behind by one question would turn up on the next.
  els.askCancel.textContent = cancel || t("Cancel");
  // A tick box, when the question has one. Hidden again every time, or one
  // question's option would turn up under the next one.
  els.askOpt.hidden = !option;
  if (option) {
    els.askOptLabel.textContent = option.label;
    els.askOptBox.checked = !!option.checked;
  }
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

/** What the tick box on the last question was left at. */
const askOption = () => els.askOptBox.checked;

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

/* The same shape again, for choosing one of a list. Resolves to the chosen
   string, or null if they backed out. */
let pickSettle = null;

function pickClose(answer) {
  const settle = pickSettle;
  pickSettle = null;
  if (els.pickDlg.open) els.pickDlg.close();
  if (settle) settle(answer);
}

function pickOne(title, items) {
  pickClose(null);
  els.pickTitle.textContent = title;
  els.pickInput.innerHTML = "";
  for (const item of items) {
    const opt = document.createElement("option");
    opt.value = item;
    opt.textContent = item;
    els.pickInput.append(opt);
  }
  els.pickDlg.showModal();
  els.pickInput.focus();
  return new Promise((resolve) => { pickSettle = resolve; });
}

els.pickForm.addEventListener("submit", (ev) => {
  ev.preventDefault();
  pickClose(els.pickInput.value || null);
});
els.pickCancel.addEventListener("click", () => pickClose(null));
els.pickDlg.addEventListener("cancel", (ev) => {
  ev.preventDefault();
  pickClose(null);
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
  // Only ever applied while the shelf is ordered by what you have earned.
  libHideMastered: false,
  // Which of the two RetroAchievements medians ride on every tile, whatever
  // the shelf is ordered by: off | beat | master | both.
  libTimes: "off",
  // What a click on the artwork does: "play" the game, or open its "preview".
  libClick: "play",
  // What opens beside a game when it starts: "off", the app's own "app" list,
  // or the game's page on the "site" itself.
  achOnPlay: "off",
  // The parts the backup window had unticked, or null while it has never
  // been touched - see paintBackupParts.
  backupSkip: null,
  tone: "default", accent: "blue", lang: "en",
  libPinned: [], libShut: [], libShelf: "",
  libOrder: [],           // consoles in the order they were dragged into
  cartWide: false, dlWide: false,
  indexAutoClose: false, wideLayout: false,
  notifyDone: true, muteDone: false,
  // How many unplaced files the "not in any console" note was last
  // dismissed at; it stays hidden until more than that turn up.
  strayHidden: 0,
  // Where a game's page opens: "app" or "browser".
  webTarget: "app",
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
const MAX_COVER_TRIES = 10;
const CONSOLE_PREVIEW = 4; // console badges shown before the "+N" toggle
const SEARCHABLE_AT = 12; // menus longer than this get their own filter box

// Active filter selections. Multiple values within a dimension are OR'd.
const active = { console: new Set(), region: new Set(), ext: new Set() };
const menuQuery = { console: "", region: "", ext: "" };

/** Open one dropdown, closing whatever was open - and forgetting what was
 *  typed into it.
 *
 *  The forgetting is the point. What you type in a menu narrows the list of
 *  values, and it used to outlive the menu: type "nin", pick a console,
 *  search, then come back to change the console and the list is still only
 *  the ones matching "nin" - or empty, because searching changed which
 *  consoles have any results left and none of the survivors match. The box
 *  was still sitting there with the word in it, but off screen above a list
 *  that just said "No matches". A filter within a menu belongs to that
 *  opening of it, not to the session. */
function setOpenDim(next) {
  if (openDim && openDim !== next) menuQuery[openDim] = "";
  openDim = next;
}
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

/** How long a game has been played, said the way a person would say it.
 *
 *  Rounded down, and never to seconds: this is a total built up over weeks,
 *  and "6h 52m" is the answer to the question. Under a minute reads as "<1m"
 *  rather than "0m", because a game that was started and quit is not the same
 *  as one that was never opened - and one that was never opened shows nothing
 *  here at all. */
function humanPlaytime(seconds) {
  const total = Math.floor(Number(seconds) || 0);
  if (total <= 0) return "";
  if (total < 60) return t("<1m");
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  return hours ? `${hours}h ${String(minutes).padStart(2, "0")}m`
    : `${minutes}m`;
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
  // Both wear the logo: the filter in the bar and the per-game check on a
  // card. Either falls back to the letters when the file isn't there.
  img.closest(".rafilter, .racheck")?.classList.add("nologo");
  img.remove();
};

/* ---------- the front page ----------

   Opening on every game in the index, alphabetically, meant opening on a
   scroll bar: forty thousand rows starting at "0-ji no Kane to Cinderella"
   tell you nothing about what is here. A console is the first choice anybody
   actually makes, so that is what the front page offers - with the whole list
   still one click away for people who would rather browse it. */
let browsingAll = false;   // "All consoles" was picked, so show the list

/** Home is the state with no game chosen yet: no words typed, no console or
 *  region or type picked.
 *
 *  RetroAchievements is deliberately not in that list. It narrows *which*
 *  games exist rather than picking one, so pressing it on the front page is a
 *  question about the cards - "how many of these have achievement sets" - and
 *  the old answer was to throw the cards away and show a list of games on
 *  every console at once. The counts are recalculated with the filter on
 *  instead, and the front page stays the front page. */
const atHome = () => !browsingAll && !els.q.value.trim()
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
  // With the RetroAchievements filter on, every number on this page is a
  // count of achievement sets rather than of games. Saying so is the
  // difference between "the counts dropped" and "the counts dropped because
  // of the button I just pressed".
  const hint = raOnly
    ? t("Counting only RetroAchievements sets. Pick a console, or search for a game.")
    : t("Pick a console, or search for a game.");
  els.homeCards.innerHTML = `
    <p class="homehint">${esc(hint)}</p>
    <div class="ccgrid">
      ${consoleCard("", everything, t("All consoles"))}
      ${list.map((c) => consoleCard(c.value, c.count || 0)).join("")}
    </div>`;
}

/** Whether "Load more" belongs on screen, worked out fresh every time.
 *
 *  It used to be remembered instead - hidden on the way into the library and
 *  put back to whatever it had been on the way out - and that loses the one
 *  thing worth knowing. "Hidden" is the answer to two different questions:
 *  are there more results, and is something else covering them. Storing the
 *  answer forgets which question it was for, so the button hidden by opening
 *  the library was still hidden when the library closed, for the rest of the
 *  session. The search's own numbers always know. */
function paintMore() {
  els.more.hidden = libraryOpen || atHome() || offset >= total;
}

/** Cards or results, never both. Called wherever either could have changed. */
function paintHome() {
  /* With nothing indexed there is no third answer: the console cards are a
     list of consoles nobody has yet, and a result list has nothing to list.
     Both would be blank, which is what used to happen - the front page won
     because no search had been typed, drew no cards because there are no
     consoles, and hid the results underneath it, panel and all. So the panel
     that offers to build the index takes the page instead, and it does so
     whether this is a first run or an index someone has just deleted; the
     app cannot tell those apart and has no reason to. */
  if (indexEmpty) {
    els.homeCards.hidden = true;
    els.results.hidden = false;
    if (!els.results.querySelector(".firstrun")) {
      els.results.innerHTML = firstRunHtml();
    }
    paintMore();
    return;
  }

  const home = !libraryOpen && atHome();
  els.homeCards.hidden = !home;
  if (home) renderHome();
  els.results.hidden = libraryOpen || home;
  paintMore();
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
  setOpenDim(null);
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
    setOpenDim(openDim === dim ? null : dim);
    renderFilters();
  } else if (act === "clear") {
    for (const set of Object.values(active)) set.clear();
    raOnly = false;
    setOpenDim(null);
    browsingAll = false;      // nothing chosen at all is the front page again
    search(false);
  } else if (act === "ra") {
    raOnly = !raOnly;
    setOpenDim(null);
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
    setOpenDim(null);
    renderFilters();
  }
});

document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape" && openDim) {
    setOpenDim(null);
    renderFilters();
    els.q.focus();
  }
});

/* ---------- RetroAchievements pages ----------

   Which games have one is a question with a real answer, and a menu entry
   that opened a search results page for everything - including the four
   hundred Japanese pachinko discs RetroAchievements has never heard of -
   would be worse than no entry at all. So the answer is looked up.

   It is looked up in a batch, for everything on screen, as the screen is
   drawn: opening a menu then never has to wait, and the entry is either
   there or it isn't rather than appearing a moment after the menu does.
   The work is on the server (see retro.py) because that is where the list
   of games is cached; from here it is one request per screenful, and none
   at all once the answers are known. */

const raIds = new Map();      // "console\0filename" -> game id, 0 for "none"
const raPatches = new Map();  // game id -> every patch published for it
/* How much of each set you have earned, by game id. Empty unless a
   RetroAchievements username is set, which is why nothing about the library
   changes for somebody who only filled in a key for the artwork. */
const raProgress = new Map();
const patchExts_ = new Set();  // file types the built-in patcher can rewrite

const RA_HOME = "https://retroachievements.org/";

// Where the patches this app cannot apply go instead. Chosen because it does
// the work in the browser rather than on someone's server - the ROM never
// leaves this machine - and because it reads the formats this app does not:
// PPF, which is how disc patches are published, as well as the xdelta
// variants written with their own compression.
const WEB_PATCHER = "https://www.marcrobledo.com/RomPatcher.js/";
const RA_PAGE = `${RA_HOME}game/`;
const raKey = (console_, name) => `${console_}\u0000${name}`;

/** The id, if we have been told. Never waits: a menu opens with what is
 *  known right now, and an unresolved game is one without the entry. */
const raId = (console_, name) =>
  (console_ && name) ? (raIds.get(raKey(console_, name)) || 0) : 0;

/** A row that carries the two things a lookup needs. Search results, the
 *  download list and the downloads panel all stamp them on. */
const raIdOfRow = (row) =>
  row ? raId(row.dataset.raConsole || "", row.dataset.raName || "") : 0;

/** The page for whatever is under the pointer, row or not.
 *
 *  A row answers for itself. Artwork can't: a search result's cover sits in
 *  the card's header, above the rows it belongs to rather than inside one,
 *  and each console's art sits beside its own section. So when the pointer
 *  isn't on a row, whatever encloses it is asked on its behalf.
 *
 *  Nearest first, and that order is the point: a console's own artwork should
 *  open that console's page, not whichever of the card's consoles happens to
 *  be listed first. Only a cover that stands for the whole card falls back to
 *  the card, where the first file with a page is as good an answer as there
 *  is - they are all the same game. */
const raIdNear = (target) => {
  const row = target.closest(".file, .cartitem, .dljob, .nextrow, .recsrow");
  if (row) return raIdOfRow(row);

  const scope = target.closest(".consec") || target.closest(".game");
  if (!scope) return 0;
  for (const within of scope.querySelectorAll(".file")) {
    const found = raIdOfRow(within);
    if (found) return found;
  }
  return 0;
};

const raAttrs = (console_, name) =>
  `data-ra-console="${esc(console_ || "")}" data-ra-name="${esc(name || "")}"`;

/** Open a RetroAchievements page where Settings says it should go.
 *
 *  A window of this app's, where a sign-in is remembered between sessions and
 *  the page sits beside the library; or the browser the user already has,
 *  where they are quite possibly signed in already. Both are real top-level
 *  pages, which is the point - RetroAchievements sends X-Frame-Options and
 *  refuses to be embedded in anything, so there is no third way to show it.
 *
 *  Whichever is asked for, the other one covers for it: `python -m romsrx
 *  serve` in an ordinary browser has no app window to make a second of, and a
 *  machine with no browser configured has nothing to hand a page to. Better
 *  the page opens somewhere than nowhere. */
async function openWeb(url, title = "") {
  if (!url) return;
  const post = (route, body) =>
    fetch(route, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => r.json()).catch(() => ({}));

  // Named for what it is showing. This was fixed to RetroAchievements when
  // that was the only place a page could come from, which left every other
  // page opening in a window claiming to be that site.
  const inApp = () =>
    post("/api/browse/window", { url, title: title || t("RetroAchievements") });
  const outside = () => post("/api/browse/open", { url });

  const [first, second] = prefs.webTarget === "browser"
    ? [outside, inApp]
    : [inApp, outside];
  if ((await first()).opened) return;
  await second();
}

const openRa = (id) => openWeb(RA_PAGE + id);

/* How long each game takes, for the two time-based sorts. Filled in by the
   server a bounded number at a time - a time costs a request - so choosing one
   of those sorts settles over a few goes on a large shelf rather than hanging
   on the first. */
const libTimes = new Map();

/* The console and name a time is filed under.
 *
 * Taken from the copy on disk when there is one and from the playlist entry
 * when there isn't. A game you have not downloaded still has a name and a
 * console, which is all RetroAchievements needs to say how long it takes - so
 * the entry is a perfectly good thing to ask about, and asking means a shelf
 * ordered by how long things take is in that order all the way down instead of
 * dumping everything you haven't got yet at the end. */
const timeIdent = (tile) => ({
  console: tile.game?.console || tile.entry?.console || "",
  name: tile.game?.name || tile.entry?.name || "",
});
const timeKey = (tile) => {
  const it = timeIdent(tile);
  return `${it.console}	${it.name}`;
};

/* What you have earned in each game's set, for the shelf that is ordered by it
   and the toggle that hides the finished ones.
 *
 * Hardcore is the figure throughout, as everywhere else in this app: it is the
 * one RetroAchievements treats as real, and it is what the badge on the tile
 * already shows. A game with no set - or with a set you have never touched -
 * has nothing to report, which sorts it last rather than as a zero at the top.
 */
const earnedOf = (tile) => {
  const it = timeIdent(tile);
  return raProgress.get(raId(it.console, it.name)) || null;
};

const isMastered = (tile) => {
  const done = earnedOf(tile);
  return !!(done?.total && done.hardcore >= done.total);
};

function byEarned(a, b) {
  const mine = earnedOf(a)?.hardcore || 0;
  const theirs = earnedOf(b)?.hardcore || 0;
  if (mine !== theirs) return theirs - mine;
  return a.title.localeCompare(b.title, undefined, { numeric: true });
}

function byTime(a, b, which) {
  const mine = libTimes.get(timeKey(a))?.[which];
  const theirs = libTimes.get(timeKey(b))?.[which];
  if (mine && theirs) return mine - theirs;
  if (mine) return -1;
  if (theirs) return 1;
  return a.title.localeCompare(b.title, undefined, { numeric: true });
}

let pricing = false;

/** Every game on the shelf being looked at, as tiles.
 *
 *  The library is what is on disk; a playlist is what you meant to play,
 *  downloaded or not. Both come out of here in the same shape, which is what
 *  lets the things that work on "the shelf" - the ordering, the times, the
 *  suggestions - stop caring which of the two they are looking at. */
function shelfTiles() {
  const pl = currentPlaylist();
  return pl ? pl.items.map(tileFromEntry)
            : (libraryData?.games || []).map(tileFromGame);
}

/** Ask for times for everything on the shelf, then draw it again. */
async function priceLibrary() {
  if (pricing) return;
  pricing = true;
  try {
    // One ask per game, not per tile: a playlist can hold two entries that
    // resolve to the same game, and the second one costs a request to be told
    // what the first already said.
    const asking = new Map();
    for (const tile of shelfTiles()) {
      const it = timeIdent(tile);
      if (it.console && it.name) asking.set(`${it.console}	${it.name}`, it);
    }
    const found = await fetch("/api/times", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ games: [...asking.values()] }),
    }).then((r) => r.json());
    for (const [key, row] of Object.entries(found.times || {})) {
      libTimes.set(key, row);
    }
    renderLibrary();
    // More to price than one request allows: say so rather than leaving a
    // half-sorted shelf looking broken.
    if (found.waiting) {
      toast(t("{n} more still being timed — pick this sort again in a moment.",
              { n: found.waiting }));
    }
  } catch { /* the shelf simply stays in the order it was */ }
  pricing = false;
}

/** Price the shelf if it is ordered by time and something on it has none.
 *
 *  For arriving somewhere - opening the library, switching shelves - rather
 *  than for choosing the sort, which asks outright so that picking it again is
 *  how you retry the ones that were still being timed. A shelf whose games are
 *  all priced already asks for nothing, so this is free to call on the way in.
 *  Without it, a playlist opened with a time sort already chosen is drawn in
 *  an order the page has no numbers for: the games it has never priced are
 *  exactly the ones that aren't in the library, which is most of the point of
 *  a playlist. */
function priceShelfIfNeeded(force = false) {
  const wanted = force || prefs.libTimes !== "off"
    || prefs.libSort === "beat" || prefs.libSort === "master";
  if (!wanted) return;
  const unpriced = shelfTiles().some((tile) => {
    const it = timeIdent(tile);
    return it.console && it.name && !libTimes.has(`${it.console}	${it.name}`);
  });
  if (unpriced) priceLibrary();
}

/* ---------- where the space went ----------

   Worked out from the shelf the page is already holding rather than asked for,
   so opening this costs one render and no request. The three numbers people
   actually want are how much there is, how it splits by console, and which
   handful of games are eating most of it - a game you have never started that
   is taking eleven gigabytes is a decision waiting to be made. */
function paintStorage() {
  const games = (libraryData?.games || []).filter((g) => g.size > 0);
  const total = games.reduce((n, g) => n + g.size, 0);
  const unplayed = games.filter((g) => !g.playSeconds);
  const unplayedSize = unplayed.reduce((n, g) => n + g.size, 0);

  els.storageTop.innerHTML = [
    [humanSize(total), t("in total")],
    [games.length.toLocaleString(), t("games")],
    [unplayed.length.toLocaleString(), t("never started")],
    [humanSize(unplayedSize), t("never started")],
  ].map(([value, label], at) => `
      <div class="timestat"><span class="timestatval">${esc(value)}</span>
        <span class="timestatkey">${esc(at === 3 ? t("sitting unused") : label)}</span></div>`
  ).join("");

  const byConsole = new Map();
  for (const game of games) {
    const now = byConsole.get(game.console) || { size: 0, count: 0 };
    now.size += game.size;
    now.count += 1;
    byConsole.set(game.console, now);
  }
  const ranked = [...byConsole.entries()].sort((a, b) => b[1].size - a[1].size);
  const widest = ranked[0]?.[1].size || 1;
  els.storageConsoles.innerHTML = ranked.map(([name, n]) => `
      <div class="storagebar">
        <span class="storagename">${esc(name)}</span>
        <span class="storagetrack"><span class="storagefill"
          style="width:${Math.max(2, (n.size / widest) * 100).toFixed(1)}%"></span></span>
        <span class="storageval">${esc(humanSize(n.size))}
          <span class="storagecount">${esc(t("{n} games", { n: n.count }))}</span></span>
      </div>`).join("");

  const biggest = [...games].sort((a, b) => b.size - a.size).slice(0, 12);
  els.storageBiggest.innerHTML = biggest.map((g) => `
      <div class="storagerow">
        <span class="storagegame">${esc(g.name)}
          <span class="storagesub">${esc(g.console)}${
            g.playSeconds ? "" : ` &middot; ${esc(t("never started"))}`}</span></span>
        <span class="storageval">${esc(humanSize(g.size))}</span>
      </div>`).join("");

  els.storageNote.textContent = games.length
    ? t("Sizes are what is on your disk. A game kept as a folder counts everything in it.")
    : t("Nothing on the shelf yet.");
}

/* The box art beside a suggestion.
 *
 * The same lookup the shelf itself uses - a cover the user picked by hand
 * first, then the names worked out from the filename - so a game recommended
 * here wears the picture it already wears in the library rather than a second
 * opinion about the same game. A game whose art nothing can find keeps its
 * console name in the slot: an empty gap in a column of pictures reads as a
 * row that failed to draw. */
function nextCoverHtml(g) {
  const tile = nextShelf.get(nextKey(g));
  const urls = libCovers({
    name: g.name, console: g.console,
    cover: tile?.cover || gameAt(g.path)?.cover || "",
    art: tile?.art || "",
    alts: tile?.alts || [],
  });
  const label = esc(g.console || "?");
  if (!urls.length) {
    return `<span class="nextart"><span class="noart">${label}</span></span>`;
  }
  return `<span class="nextart"><img src="${esc(urls[0])}"
    data-rest='${esc(JSON.stringify(urls.slice(1)))}'
    data-title="${label}" alt="" loading="lazy"
    decoding="async" onerror="coverFail(this)"></span>`;
}

/* What to start next.
 *
 * Asked of the shelf you are looking at, not of the library. A playlist is a
 * list of games somebody decided they wanted to play, which is a far better
 * thing to draw a suggestion from than everything on the disk - and on a
 * playlist the games you have not downloaded yet count too. Not owning it is
 * not a reason to leave it out of the answer: the times come from the name and
 * the console, which an entry has whether or not there is a file behind it, so
 * the only difference is what happens when you pick it.
 *
 * The shelf goes to the server rather than the server reading it again, and
 * the server prices a couple of dozen of them against RetroAchievements -
 * which is why this takes a moment and says so. */
const nextKey = (g) => `${g.console || ""}	${g.name || ""}`;

/* What was suggested, and the shelf tile each row came from - which is how a
   row knows whether there is a file to play or a download to start. Both are
   kept so re-ordering the list costs nothing: the same games are shown in a
   different order, not asked for again. */
let nextFound = [];
let nextShown = [];
let nextShelf = new Map();

// Eight is a shortlist. The server prices two dozen so that either order has
// something real to choose from; showing all of them would be a shelf, and a
// shelf is the thing this window is meant to save you from reading.
const NEXT_SHOW = 8;

const suggestGame = (tile) => {
  const it = timeIdent(tile);
  return {
    name: it.name, console: it.console,
    path: tile.game?.path || "",
    // What has never been started is the whole question. A playlist entry
    // with nothing on disk behind it has never been started by definition.
    playSeconds: tile.game?.playSeconds || 0,
  };
};

/** What this window is answering, in the words of whichever shelf and
 *  whichever question is in front of you. */
function nextHintText(pl, all) {
  if (all) {
    return pl
      ? t("Every game on “{name}” RetroAchievements has a time for, played or "
          + "not, downloaded or not. Times are how long their players actually "
          + "took, in hardcore.", { name: pl.name })
      : t("Every game here RetroAchievements has a time for, whether or not "
          + "you have played it. Times are how long their players actually "
          + "took, in hardcore.");
  }
  return pl
    ? t("Games on “{name}” you have never started, the ones you have not "
        + "downloaded included. Times are how long RetroAchievements' players "
        + "actually took, in hardcore.", { name: pl.name })
    // No longer "shortest first": which end of the shortlist you are looking
    // at is a control now, and a line that answers it before you have chosen
    // is a line that is wrong half the time.
    : t("Games you have never started. Times are how long RetroAchievements' "
        + "players actually took, in hardcore.");
}

async function askWhatNext() {
  const pl = currentPlaylist();
  const all = els.nextAll.checked;
  els.nextList.innerHTML = "";
  els.nextSortRow.hidden = true;
  els.nextHint.textContent = nextHintText(pl, all);
  els.nextNote.textContent = t("Looking these up…");
  if (!els.nextDlg.open) els.nextDlg.showModal();

  nextShelf = new Map();
  const asking = new Map();
  for (const tile of shelfTiles()) {
    const game = suggestGame(tile);
    if (!game.name || !game.console) continue;
    const key = nextKey(game);
    // First one wins, so a game that is on the shelf twice is asked about
    // once and keeps the tile that has a file behind it if either does.
    if (!asking.has(key) || (!nextShelf.get(key)?.game && tile.game)) {
      asking.set(key, game);
      nextShelf.set(key, tile);
    }
  }

  let found = null;
  try {
    found = await fetch("/api/suggest", {
      method: "POST", headers: { "Content-Type": "application/json" },
      // `all` turns off the one filter this window is normally built on.
      body: JSON.stringify({ games: [...asking.values()], all }),
    }).then((r) => r.json());
  } catch { /* handled below */ }

  nextFound = found?.games || [];
  if (!nextFound.length) {
    /* With the filter off there is nothing left to blame it on: everything
       here was asked about, so an empty answer means RetroAchievements has no
       times for any of it. Saying "you have started them all" there would be
       plainly untrue and would send somebody looking for a setting to change.
       */
    els.nextNote.textContent = all
      ? t("RetroAchievements has no times for anything on this shelf.")
      : (pl
          ? t("Nothing to suggest — either everything on this playlist has been "
              + "started, or RetroAchievements has no times for the ones that "
              + "haven't.")
          : t("Nothing to suggest — either everything on "
              + "the shelf has been started, or RetroAchievements has no times for "
              + "the ones that haven't."));
    return;
  }
  els.nextSortRow.hidden = false;
  paintNext();
}

els.libNext.addEventListener("click", askWhatNext);

// Changing the question asks it again: this one is the server's filter, not
// an ordering of what is already here, so it cannot be answered from memory.
els.nextAll.addEventListener("change", askWhatNext);

/* One of the two figures. A time nobody has is a dash rather than a blank, so
   the pair still reads as a pair and the column below it stays a column. */
const nextTimeHtml = (seconds, label) => `
  <span class="nexttime"><span class="nextval${seconds ? "" : " dim"}">${
    seconds ? esc(spanText(seconds)) : "&ndash;"}</span>
    <span class="nextkey">${esc(label)}</span></span>`;

/* The chosen order, over the games already priced. A game with no master time
   sorts last rather than as zero - it is not a fast game to master, it is one
   nobody has said - which is how the shelf's own time sorts treat it too. */
function nextOrder(which) {
  return [...nextFound].sort((a, b) => {
    const mine = a[which];
    const theirs = b[which];
    if (mine && theirs) return mine - theirs;
    if (mine) return -1;
    if (theirs) return 1;
    return String(a.name).localeCompare(String(b.name), undefined, { numeric: true });
  });
}

function paintNext() {
  const which = els.nextSort.value === "master" ? "master" : "beat";
  nextShown = nextOrder(which).slice(0, NEXT_SHOW);
  /* The RetroAchievements attributes go on every row, so the right-click menu
     the rest of the app already has - the game's page, its patches, how long
     it takes - works here too without a menu of this window's own. */
  els.nextList.innerHTML = nextShown.map((g, at) => {
    const tile = nextShelf.get(nextKey(g));
    const here = !!(g.path || tile?.game);
    /* A game that isn't downloaded says so where the console goes, and the
       row's own note says what pressing it will do - the two rows behave
       differently, and finding that out by pressing one is not the way to
       learn it. */
    const missing = here ? "" : ` &middot; <span class="nextmiss">${
      esc(tile?.entry?.url ? t("Not downloaded — click to fetch")
                           : t("Not downloaded"))}</span>`;
    /* The row points back at the list it was drawn from by position rather
       than by name: the key these are filed under has a tab in it, and a tab
       is not a thing to trust an HTML attribute to hand back unchanged. */
    return `
      <div class="storagerow nextrow${here ? "" : " missing"}" data-at="${at}"
           ${g.path ? `data-path="${esc(g.path)}"` : ""}
           ${raAttrs(g.console, g.name)}>
        ${nextCoverHtml(g)}
        <span class="storagegame">${esc(g.name)}
          <span class="storagesub">${esc(g.console)}${
            g.achievements ? ` &middot; ${esc(t("{n} achievements",
              { n: g.achievements }))}` : ""}${missing}</span></span>
        <span class="nexttimes">
          ${nextTimeHtml(g.beat, t("to beat"))}
          ${nextTimeHtml(g.master, t("to master"))}
        </span>
      </div>`;
  }).join("");

  const gettable = nextShown.some((g) =>
    !g.path && !nextShelf.get(nextKey(g))?.game);
  els.nextNote.textContent = gettable
    ? t("Click one to play it, or to fetch one you haven't got yet.")
    : t("Click one to play it.");
}

// Re-ordering shows the same priced games from the other end. Nothing is asked
// for again, so this is instant however long the first look-up took.
els.nextSort.addEventListener("change", paintNext);

/* A row is the game. What pressing it does depends on whether the game is
   here: playing it if it is, fetching it if it isn't and there is somewhere to
   fetch it from. A game that is neither - an entry saved before this app kept
   the download address, or one whose file has since gone - opens its preview
   instead, which is the one useful thing left to do with it. */
els.nextList.addEventListener("click", (ev) => {
  const row = ev.target.closest(".nextrow");
  if (!row) return;
  const game = nextShown[Number(row.dataset.at)];
  if (!game) return;
  const tile = nextShelf.get(nextKey(game));
  const path = row.dataset.path || tile?.game?.path || "";
  els.nextDlg.close();
  if (path) {
    playGame(path);
    return;
  }
  if (tile?.entry?.url) {
    // Reported on the button that opened this window: it is the control the
    // click came from, and it is still there once the window has gone.
    startDownloads([downloadItemFromEntry(tile.entry)], els.libNext);
    return;
  }
  openPreview({
    console: game.console, name: game.name,
    title: tile?.title || "", path: "",
    cover: coverSrc(row.querySelector("img")),
  });
});

/* ---------- who is signed in to RetroAchievements ----------

   The strip in the corner of the header: the picture, the points, and what
   you last played. Absent entirely without a username in Settings - not an
   empty frame, not a placeholder avatar - because for somebody who filled in
   a key for the box art alone there is nothing to show and no reason to
   suggest there ought to be.

   Refreshed on a timer rather than only at startup: it says what you are
   playing, and an app left open all evening should not still be claiming you
   are playing the thing you finished at six. */
let raMe = null;

const RA_ME_EVERY = 4 * 60 * 1000;

async function loadRaMe(refresh = false) {
  let found = null;
  try {
    found = await fetch(`/api/ra/me${refresh ? "?refresh=1" : ""}`)
      .then((r) => r.json());
  } catch { /* offline; whatever is on screen stays */ }
  if (!found?.ok) {
    // Only hide it if there was never anything there. A failed refresh should
    // not take the strip away from somebody who is simply offline for a
    // minute.
    if (!raMe) els.raMe.hidden = true;
    return;
  }
  raMe = found;
  paintRaMe();
}

function paintRaMe() {
  if (!raMe) return;
  els.raMe.hidden = false;
  els.raMePic.src = raMe.pic || "";
  els.raMePic.alt = raMe.user || "";
  els.raMeName.textContent = raMe.user || "";
  els.raMeName.title = raMe.rank
    ? t("Rank {n} of {total}", { n: raMe.rank.toLocaleString(),
                                 total: (raMe.ranked || 0).toLocaleString() })
    : t("Your RetroAchievements profile");
  /* Points and RetroPoints. The second is the site's weighting of the first -
     what a set is worth once its difficulty is counted - and the pair is how
     RetroAchievements itself writes somebody's standing. */
  els.raMePoints.innerHTML = `<b>${esc((raMe.points || 0).toLocaleString())}</b>`
    + ` · ${esc((raMe.retropoints || 0).toLocaleString())} ${esc(t("RP"))}`;
  els.raMePoints.title = t("{points} points · {retro} RetroPoints",
    { points: (raMe.points || 0).toLocaleString(),
      retro: (raMe.retropoints || 0).toLocaleString() });

  /* What you are playing, or the last thing you did play - the site's own
     line where there is one, since "Playing X" from the emulator itself is
     better than anything this app could work out. */
  const last = raMe.last;
  const line = raMe.playing || (last ? t("Last played {game}", { game: last.title }) : "");
  els.raMeGame.hidden = !line;
  if (line) {
    els.raMeGameText.textContent = last?.total
      ? `${line} — ${last.earned}/${last.total}`
      : line;
    /* The set's own icon, which is what RetroAchievements puts beside a game
       everywhere on its own site - and at this size a piece of box art would
       be a smudge where the icon is a thing you recognise. */
    els.raMeGameIcon.hidden = !last?.icon;
    if (last?.icon) els.raMeGameIcon.src = last.icon;
    els.raMeGame.title = last
      ? `${last.title}${last.console ? ` · ${last.console}` : ""}`
      : line;
  }
}

/* The picture opens the window; so does the name, since a name that looks
   like a link and does nothing is worse than no link. */
for (const button of [els.raMeFace, els.raMeName, els.raMeGame]) {
  button.addEventListener("click", () => openRaProfile());
}

/** The profile: everything the site's own page shows, in the app.
 *
 *  A panel here rather than a window of its own, because looking at your own
 *  profile is something you do while using the app - and a second window for
 *  it is a second thing to find and shut. The panel is a frame around the same
 *  page the pop-out button opens beside the app, so there is one of these
 *  rather than two that would have to be kept the same. */
const RA_PROFILE_URL = "/raprofile.html";

function openRaProfile() {
  // Loaded when it is opened rather than kept in the background: it is
  // several requests to RetroAchievements, and nobody who never opens this
  // should be paying for them.
  if (!els.proFrame.src.includes(RA_PROFILE_URL)) {
    els.proFrame.src = RA_PROFILE_URL;
  }
  els.profDlg.showModal();
}

/* ...and out into a window of its own, for somebody who wants it beside the
   app rather than over it. The same page, so it opens where it left off. */
els.profPop.addEventListener("click", async () => {
  const url = `${location.origin}${RA_PROFILE_URL}`;
  els.profDlg.close();
  try {
    const res = await fetch("/api/browse/window", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, title: raMe?.user || t("Profile") }),
    }).then((r) => r.json());
    // No native window to be had - `serve` in an ordinary browser - so the
    // browser gets it instead of nothing happening.
    if (!res.opened) window.open(url, "_blank", "noopener");
  } catch { /* nothing else to try */ }
});

/* Right-clicking the name offers the real thing: their page on the site,
   opened wherever Settings says RetroAchievements pages go. The window above
   is this app's rendering of it; this is the site itself, with the wall, the
   tickets and everything else no API returns. */
els.raMe.addEventListener("contextmenu", (ev) => {
  if (!raMe?.url) return;
  ev.preventDefault();
  ev.stopPropagation();
  menuCover = "";
  menuRa = 0;
  els.coverMenuSave.hidden = true;
  els.coverMenuRa.hidden = true;
  els.coverMenuHash.hidden = true;
  els.coverMenuTime.hidden = true;
  els.coverMenuPatch.hidden = true;
  els.coverMenuProfile.hidden = false;
  syncMenuGroups(els.coverMenu);
  openMenu(els.coverMenu, ev);
});

/* ---------- games like the ones you have ----------

   The shelf read back as a statement of taste. Everything about which games
   these are is decided by the server - see recommend.py - because it is the
   side that can ask IGDB what a game is like and the index what can actually
   be downloaded. What is left here is saying it: what the suggestion is, why
   it is being made, and the one press that does something about it.

   The press is a search rather than a download. A recommendation is a
   suggestion, and the honest end of a suggestion is the list of copies with
   their regions and sources, not a gigabyte arriving because somebody was
   curious. */
els.libRecs.addEventListener("click", () => {
  els.recsList.innerHTML = "";
  els.recsSortRow.hidden = true;
  els.recsMoreRow.hidden = true;
  els.recsSortNote.textContent = "";
  els.recsSort.value = "";
  els.recsHint.textContent = t("Read from the games you have, and the ones you "
    + "have played most. Games with an achievement set come first.");
  els.recsDlg.showModal();
  askRecs(true);
});

/** Fetch a page of suggestions - the first one, or the next.
 *
 *  Ten at a time. The whole ranked list is worked out on the server the first
 *  time and kept for a few minutes, so "Find more" walks further down what was
 *  already computed rather than asking IGDB the same questions again. */
async function askRecs(fresh) {
  if (fresh) { recsFound = []; recsAt = 0; }
  els.recsNote.textContent = fresh
    ? t("Looking these up…") : t("Looking for more…");
  els.recsMore.disabled = true;

  let found = null;
  try {
    found = await fetch("/api/recommend", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        games: (libraryData?.games || []).map((g) => ({
          name: g.name, console: g.console, playSeconds: g.playSeconds || 0,
        })),
        offset: recsAt,
        onlyRa: els.recsOnlyRa.checked,
        console: els.recsConsole.value,
      }),
    }).then((r) => r.json());
  } catch { /* handled below */ }
  els.recsMore.disabled = false;

  const games = found?.games || [];
  if (!games.length && !recsFound.length) {
    els.recsMoreRow.hidden = true;
    els.recsNote.textContent = {
      empty: t("There is nothing on the shelf to go on yet."),
      igdb: t("Nothing to suggest yet. Fill in IGDB in Settings → Cover art "
              + "and this can ask what your games are like; without it, it can "
              + "only offer more of the series you already own."),
    }[found?.reason] || t("Nothing to suggest from this shelf.");
    return;
  }

  recsFound = recsFound.concat(games);
  recsAt += games.length;
  els.recsSortRow.hidden = false;
  paintRecsConsoles(found?.consoles || []);
  paintRecs();
  /* Their RetroAchievements ids, so the right-click menu works on these rows
     the way it does everywhere else. The server already knew which of them
     have a set - that is what put them at the top - but the menu reads the
     page's own table, and these titles have never been looked up in it. One
     batch, and the menu is ready before anybody gets as far as right-clicking.
     */
  resolveRa(games.map((g) => ({ console: recsConsole(g), name: g.title })));

  // What is left, said plainly: a button that might be the end of the list is
  // a button nobody presses twice.
  els.recsMoreRow.hidden = !found?.more;
  els.recsNote.textContent = found.igdb
    ? t("Click one to search for it, or its cover to look at it first. "
        + "Suggestions come from IGDB's own “similar games”, narrowed to what "
        + "this app can download.")
    : t("More of the series you already own. Fill in IGDB in Settings → Cover "
        + "art for suggestions that go beyond them.");
}

els.recsMore.addEventListener("click", () => askRecs(false));

/* Both narrow the list rather than reorder it, so both start it again: what
   comes back is the first ten of the narrower list, not the same ten with
   some hidden. */
for (const control of [els.recsConsole, els.recsOnlyRa]) {
  control.addEventListener("change", () => askRecs(true));
}

/** The consoles anything on offer is available for. Filled from the answer so
 *  it never lists a machine with nothing behind it, and the chosen one
 *  survives the list being rebuilt. */
function paintRecsConsoles(consoles) {
  if (!consoles.length) return;
  const keep = els.recsConsole.value;
  els.recsConsole.innerHTML = `<option value="">${esc(t("All consoles"))}</option>`
    + consoles.map((c) => `<option value="${esc(c)}">${esc(c)}</option>`).join("");
  els.recsConsole.value = consoles.includes(keep) ? keep : "";
}

let recsFound = [];
let recsShown = [];
let recsAt = 0;          // how far down the ranked list has been asked for

/* The console a recommendation is filed under: the one its achievement set is
   on where there is one, since that is the copy this app would point at, and
   otherwise the first the index has. */
const recsConsole = (g) => g.raConsole || (g.consoles || [])[0] || "";

/* Box art, from the same lookup the shelf uses. A recommendation is a game
   somebody has never seen; a row of titles is a spreadsheet, and the cover is
   most of what makes one of them worth a second look.
 *
 * The title is all there is to go on - there is no file, because the whole
 * point is that this one is not downloaded - so every console the index has it
 * on is offered as a name to try. */
function recsCoverHtml(g) {
  const files = (g.consoles || []).map((console_) => ({
    console: console_, filename: g.title, ext: "",
  }));
  const urls = files.length ? coverCandidates(files) : [];
  const label = esc(recsConsole(g) || "?");
  if (!urls.length) {
    return `<span class="nextart"><span class="noart">${label}</span></span>`;
  }
  return `<span class="nextart"><img src="${esc(urls[0])}"
    data-rest='${esc(JSON.stringify(urls.slice(1)))}'
    data-title="${label}" alt="" loading="lazy"
    decoding="async" onerror="coverFail(this)"></span>`;
}

function paintRecs() {
  const which = els.recsSort.value;
  recsShown = [...recsFound];
  if (which === "beat" || which === "master") {
    /* Ranked over what has actually been priced, like every other time sort in
       this app: a game with no median sorts last rather than as zero. */
    recsShown.sort((a, b) => {
      const mine = recsTimes.get(recsKey(a))?.[which];
      const theirs = recsTimes.get(recsKey(b))?.[which];
      if (mine && theirs) return mine - theirs;
      if (mine) return -1;
      if (theirs) return 1;
      return a.title.localeCompare(b.title, undefined, { numeric: true });
    });
  }

  els.recsList.innerHTML = recsShown.map((g, at) => {
    const where = (g.consoles || []).join(", ");
    /* Why this one. A recommendation with no reason is an advert; "because you
       have X" is the whole argument, and it is also how somebody spots that
       the reason is a bad one. */
    const because = (g.because || []).slice(0, 2).join(", ");
    const set = g.raId
      ? `<span class="recsra">${esc(t("achievement set"))}</span>` : "";
    const sub = [where, because
      ? t("because you have {name}", { name: because }) : ""]
      .filter(Boolean).join(" · ");
    const row = recsTimes.get(recsKey(g));
    const times = (row?.beat || row?.master)
      ? `<span class="nexttimes">${nextTimeHtml(row.beat, t("to beat"))}${
          nextTimeHtml(row.master, t("to master"))}</span>`
      : "";
    /* The RetroAchievements attributes, so the right-click menu the rest of
       the app has - the game's page, its patches, how long it takes - works on
       these rows too. They are the reason the console is worked out above:
       that menu asks about a console and a name, and a recommendation on three
       systems has to name one. */
    return `
      <div class="storagerow recsrow" data-at="${at}"
           ${raAttrs(recsConsole(g), g.title)}>
        <span class="recsart" title="${esc(t("Look at this one"))}">${
          recsCoverHtml(g)}</span>
        <span class="storagegame">${esc(g.title)}${set}
          <span class="storagesub">${esc(sub)}</span></span>
        ${times}
        <button class="recsfind ghost small">${esc(t("Find it"))}</button>
      </div>`;
  }).join("");
}

/* Their medians, for the two orders. Asked for once, when one of those orders
   is first chosen: two dozen games is two dozen questions to RetroAchievements
   and nobody who wanted "best match" should pay for them. */
const recsTimes = new Map();
const recsKey = (g) => `${recsConsole(g)}\t${g.title}`;
let recsPricing = false;

async function priceRecs() {
  if (recsPricing || !recsFound.length) return;
  const wanted = recsFound.filter((g) => !recsTimes.has(recsKey(g)));
  if (!wanted.length) { paintRecs(); return; }

  recsPricing = true;
  els.recsSortNote.textContent = t("timing…");
  try {
    const found = await fetch("/api/times", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        games: wanted.map((g) => ({ console: recsConsole(g), name: g.title })),
      }),
    }).then((r) => r.json());
    for (const [key, row] of Object.entries(found.times || {})) {
      recsTimes.set(key, row);
    }
    // Asked and answered, even when the answer was "no set": without this the
    // next press would ask the same questions again.
    for (const g of wanted) {
      if (!recsTimes.has(recsKey(g))) recsTimes.set(recsKey(g), {});
    }
    paintRecs();
    const ranked = recsShown.filter((g) => {
      const row = recsTimes.get(recsKey(g));
      return row?.beat || row?.master;
    }).length;
    els.recsSortNote.textContent = t("ranking {n} of {total}",
      { n: ranked, total: recsShown.length });
  } catch {
    els.recsSortNote.textContent = "";
  }
  recsPricing = false;
}

els.recsSort.addEventListener("change", () => {
  if (els.recsSort.value) priceRecs();
  else { els.recsSortNote.textContent = ""; paintRecs(); }
});

/* A recommendation ends in the search box, with the copies of it this app can
   actually get. */
els.recsList.addEventListener("click", (ev) => {
  const row = ev.target.closest(".recsrow");
  if (!row) return;
  const game = recsShown[Number(row.dataset.at)];
  if (!game) return;

  /* The artwork is "tell me about this one", the rest of the row is "get me
     this one". A recommendation is a game somebody has never seen, so looking
     at it before going looking for it is the more likely of the two - and the
     preview is where the screenshots, the blurb and the medians are. */
  if (ev.target.closest(".recsart")) {
    openPreview({
      console: recsConsole(game), name: game.title, title: game.title,
      path: "",                       // nothing to play; it isn't here yet
      cover: coverSrc(row.querySelector("img")),
    });
    return;
  }

  els.recsDlg.close();
  goToSearch();
  els.q.value = game.title;
  els.qClear.hidden = false;
  search(false);
});

/* What still points at a game that has gone. The shelf itself needs no
   repairing - it is read off the disk every time - but the things that refer
   to a game by its path do not clean themselves up, and after a year of moving
   games between drives there can be a lot of them. */
async function showStale() {
  els.storageTidyRow.hidden = true;
  try {
    const found = await fetch("/api/library/stale").then((r) => r.json());
    if (!found.total) return;
    els.storageStale.textContent = t("{n} things still point at games that are "
      + "no longer here — hand-picked covers, per-game emulators and "
      + "recently played.", { n: found.total });
    els.storageTidyRow.hidden = false;
  } catch { /* nothing to offer is the same as nothing to tidy */ }
}

els.storageTidy.addEventListener("click", async () => {
  els.storageTidy.disabled = true;
  try {
    const gone = await fetch("/api/library/tidy", { method: "POST" })
      .then((r) => r.json());
    els.storageStale.textContent = t("Removed {n}.", { n: gone.removed || 0 });
    els.storageTidyRow.hidden = false;
  } catch {
    els.storageStale.textContent = t("Could not tidy those away.");
  }
  els.storageTidy.disabled = false;
  els.storageTidy.hidden = true;
});

els.libStorage.addEventListener("click", () => {
  paintStorage();
  els.storageTidy.hidden = false;
  showStale();
  els.storageDlg.showModal();
});

/* ---------- the preview panel ----------

   One game, from everything this app has learned to ask: the cover, the
   screenshots libretro keeps beside it, RetroAchievements' medians and points,
   and a paragraph from IGDB. The server gathers all of it in one request - see
   preview.py - so the panel arrives whole rather than filling in piece by
   piece under the reader.

   Opened deliberately, never in bulk: a button on a library tile, a button on
   a list row, and a click on a cover in search, which used to open the picture
   on its own and now opens the picture with everything known about it. */
let previewToken = 0;
let previewCover = "";
let previewConsole = "";
let previewShots = [];

// Three thumbnails, then a tile that opens the rest.
const PREVIEW_THUMBS = 3;

/* Any of them opens the whole set at the one that was clicked, the "+n more"
   tile included - it stands for the fourth picture, so that is where it
   starts. */
els.prevShots.addEventListener("click", (ev) => {
  const at = ev.target.closest("[data-shot]")?.dataset.shot;
  if (at !== undefined) openGallery(previewShots, Number(at));
});

/* The heading is a name, not a path: the lookup wants the filename exactly as
   the set spells it, but nobody wants ".zip" in a title. Only the extension
   goes - the region and the tags stay, because "(Pirate)" is the difference
   between two games with one name. */
const withoutExt = (name) => String(name || "").replace(/\.[A-Za-z0-9]{1,4}$/, "");

async function openPreview(about) {
  const mine = ++previewToken;
  previewCover = about.cover || "";
  previewConsole = about.console || "";

  els.prevName.textContent = about.title || withoutExt(about.name);
  els.prevConsole.textContent = about.console || "";
  els.prevCover.removeAttribute("src");
  if (about.cover) els.prevCover.src = about.cover;
  els.prevCover.hidden = !about.cover;
  els.prevStats.hidden = true;
  els.prevStats.innerHTML = "";
  els.prevTimes.innerHTML = "";
  els.prevShots.innerHTML = "";
  els.prevSummary.textContent = "";
  els.prevNote.textContent = t("Looking this game up…");
  // Only for a game that is actually on this machine.
  els.prevPlay.hidden = !about.path;
  if (about.path) {
    els.prevPlay.onclick = () => { els.prevDlg.close(); playGame(about.path); };
  }
  els.prevRa.hidden = true;
  els.prevSave.hidden = !about.cover;
  resetAchievements(els.prevAch);
  els.prevDlg.showModal();

  let found = null;
  try {
    found = await fetch(`/api/preview?console=${
      encodeURIComponent(about.console || "")}&name=${
      encodeURIComponent(about.name || "")}`).then((r) => r.json());
  } catch { /* handled below */ }
  // Shut again, or a second game opened while this one was being fetched.
  if (mine !== previewToken || !els.prevDlg.open) return;
  if (!found) {
    els.prevNote.textContent = t("Could not reach the app.");
    return;
  }

  if (found.cover) {
    previewCover = found.cover;
    els.prevCover.src = found.cover;
    els.prevCover.hidden = false;
  }
  els.prevSave.hidden = !previewCover;

  els.prevRa.hidden = !found.raId;
  if (found.raId) {
    els.prevRa.onclick = () => { els.prevDlg.close(); openRa(found.raId); };
  }

  const ra = found.ra || {};
  /* Your own progress, above the medians: how far through this set you are
     matters more than how long it takes other people. */
  const earned = raProgress.get(found.raId);
  const yours = (earned?.total && earned.hardcore) ? `
      <div class="timerow">
        <span class="timelabel">${esc(t("You have earned"))}
          <span class="timehint">${esc(t("In hardcore, the total the site counts."))}</span></span>
        <span class="timeval">${earned.hardcore}/${earned.total}
          <span class="timefrom">${esc(t("{n}% of the set",
            { n: Math.round((earned.hardcore / earned.total) * 100) }))}</span></span>
      </div>` : "";
  els.prevTimes.innerHTML = yours + timeRowsHtml(ra);
  const stats = timeStatsHtml(ra);
  els.prevStats.innerHTML = stats;
  els.prevStats.hidden = !stats;

  /* Screenshots drop themselves if they 404 rather than leaving a broken
     picture behind. The strip is empty for plenty of games, which is why it
     has no heading of its own to be left stranded. */
  /* Three, and a fourth tile that opens the rest. Ten thumbnails in a strip is
     a strip nobody looks at; three and a count is a strip you can read, with
     everything still one click away. */
  previewShots = found.shots || [];
  const showing = previewShots.slice(0, PREVIEW_THUMBS);
  const rest = previewShots.length - showing.length;
  els.prevShots.innerHTML = showing
    .map((url, at) => `<img src="${esc(url)}" alt="" onerror="this.remove()"
       data-shot="${at}">`).join("")
    + (rest > 0
        ? `<button class="prevmore" data-shot="${PREVIEW_THUMBS}"
             >+${rest}<span>${esc(t("more"))}</span></button>` : "");

  /* The same offer the How Long window makes, in the panel people actually
     open to decide whether to play something. Still a button: this panel is
     already three requests deep by the time it is drawn, and the set is worth
     one more only when somebody wants it. */
  if (found.raId && ra.achievements) {
    achGame = found.raId;
    els.achHead.hidden = false;
  }

  els.prevSummary.textContent = found.summary || "";
  els.prevNote.textContent = (stats || els.prevTimes.innerHTML)
    ? t("Times and points from RetroAchievements; medians of their players' "
        + "own times rather than estimates.")
    : t("RetroAchievements has no achievement set for this game, so there are "
        + "no times or points to show.");
}

/* The console and filename behind whatever is under the pointer, using the
   same attributes the RetroAchievements lookup already stamps on every row.
   Same walk as raIdNear, and for the same reason: a search result's cover sits
   in the card's header rather than inside one of its rows. */
function previewNear(target) {
  const of = (el) => (el?.dataset?.raConsole && el.dataset.raName)
    ? { console: el.dataset.raConsole, name: el.dataset.raName } : null;
  const row = target.closest?.(".file, .cartitem, .dljob, .nextrow");
  if (row) return of(row);
  const scope = target.closest?.(".consec") || target.closest?.(".game");
  if (!scope) return null;
  for (const within of scope.querySelectorAll(".file")) {
    const found = of(within);
    if (found) return found;
  }
  return null;
}

els.prevSave.addEventListener("click", () => {
  if (previewCover) {
    saveCover(previewCover, coverFileName(previewCover), previewConsole);
  }
});
// Stops any picture still downloading when it is shut.
els.prevDlg.addEventListener("close", () => {
  previewToken += 1;
  els.prevCover.removeAttribute("src");
  els.prevShots.innerHTML = "";
});

/* ---------- how long a game takes ----------

   RetroAchievements times its own players and publishes the median. One
   request per game, so this is asked for rather than fetched: the entry is in
   the menu, and nothing happens until somebody presses it. Fetching it for
   every tile on screen the way the ids are fetched would be forty requests to
   answer a question nobody asked.

   Their numbers arrive in seconds. */
function spanText(seconds) {
  if (!seconds) return "";
  const mins = Math.round(seconds / 60);
  if (mins < 60) return t("{n} min", { n: mins });
  const hours = Math.floor(mins / 60);
  const rest = mins % 60;
  return rest ? t("{h} h {m} min", { h: hours, m: rest })
              : t("{h} h", { h: hours });
}

/* Why a number is worth trusting, or isn't. A median of four people is a
   different sort of fact from a median of two thousand, and the difference is
   invisible unless it is written down. */
const fromText = (n) => (n ? t("from {n} players", { n: n.toLocaleString() }) : "");

/* Both hardcore, and only these two. The softcore medians measure how long a
   game takes when you can undo your mistakes, which says more about the
   emulator than about the game. See retro.how_long. */
const TIME_ROWS = [
  ["beat", "Beat the game", "beatFrom",
   "Reaching the ending, in hardcore — no save states, no rewind."],
  ["master", "Master it", "masterFrom",
   "Every achievement, also in hardcore."],
];

const TIME_REASONS = {
  nokey: "Add your RetroAchievements Web API key in Settings → Cover art, and "
       + "this can ask them how long the game takes.",
  noset: "RetroAchievements has no achievement set for this game, so nobody "
       + "has been timed playing it.",
  notimes: "This game has a set, but nobody has finished it in hardcore often "
         + "enough for a median to mean anything yet.",
  badkey: "RetroAchievements would not accept your API key.",
  unreachable: "Could not reach RetroAchievements.",
};

/* Shared with the preview panel, which shows the same two things in a wider
   window. Both are given whatever the server found and draw only the parts
   that are there, so a game with points and no medians - or the other way
   round - is a shorter panel rather than a broken one. */
function timeRowsHtml(found) {
  return TIME_ROWS
    .filter(([key]) => found[key])
    .map(([key, label, countKey, hint]) => `
      <div class="timerow">
        <span class="timelabel">${esc(t(label))}
          <span class="timehint">${esc(t(hint))}</span></span>
        <span class="timeval">${esc(spanText(found[key]))}
          <span class="timefrom">${esc(fromText(found[countKey]))}</span></span>
      </div>`).join("");
}

/* What the set itself is. Four small figures side by side rather than four
   more rows: they are facts about the game, not answers to "how long", and
   stacking them would bury the numbers that are. */
function timeStatsHtml(found) {
  return [
    ["achievements", "Achievements", (n) => n.toLocaleString()],
    ["points", "Points", (n) => n.toLocaleString()],
    ["retropoints", "RetroPoints", (n) => n.toLocaleString()],
    ["ratio", "RetroRatio", (n) => `×${n.toFixed(2)}`],
  ].filter(([key]) => found[key])
   .map(([key, label, show]) => `
      <div class="timestat"><span class="timestatval">${esc(show(found[key]))}</span>
        <span class="timestatkey">${esc(t(label))}</span></div>`).join("");
}

async function showHowLong(id, fallbackTitle = "") {
  els.timeGame.textContent = fallbackTitle || "";
  els.timeBody.innerHTML = `<p class="timewait">${esc(t("Asking…"))}</p>`;
  els.timeNote.textContent = "";
  els.timeOpen.hidden = true;
  els.timePopRow.hidden = true;
  resetAchievements(els.timeAch);
  els.timeDlg.showModal();

  let found;
  try {
    found = await fetch(`/api/howlong?id=${encodeURIComponent(id)}`)
      .then((r) => r.json());
  } catch {
    found = { ok: false, reason: "unreachable" };
  }

  if (found.title) els.timeGame.textContent = found.title;
  if (found.id) {
    els.timeOpen.hidden = false;
    els.timeOpen.onclick = () => { els.timeDlg.close(); openRa(found.id); };
  }

  if (!found.ok) {
    els.timeBody.innerHTML =
      `<p class="timenone">${esc(t(TIME_REASONS[found.reason]
        || TIME_REASONS.unreachable))}</p>`;
    return;
  }

  const rows = timeRowsHtml(found);
  const stats = timeStatsHtml(found);
  els.timeBody.innerHTML = rows
    + (stats ? `<div class="timestats">${stats}</div>` : "")
    + (found.notimes
        ? `<p class="timenone">${esc(t(TIME_REASONS.notimes))}</p>` : "");
  els.timeNote.textContent = rows ? t(
    "Medians of RetroAchievements players' own times, not estimates — so one "
    + "person leaving the emulator running does not move them.") : "";

  // The set is worth offering whenever there is one to list, times or not.
  if (found.id && found.achievements) {
    achGame = found.id;
    els.achHead.hidden = false;
    els.timePopRow.hidden = false;
    achPopTitle = found.title || fallbackTitle || "";
  }
}

/* The same list, in a window beside the app. The panel is where it opens -
   you asked about a game, and a window is a lot of ceremony for a list you
   glance at - but a window is what you want if you are working through a set
   with the game running, so both are offered rather than one chosen. */
let achPopTitle = "";

els.timePop.addEventListener("click", () => {
  if (!achGame) return;
  const url = `${location.origin}/achievements.html?id=${
    encodeURIComponent(achGame)}&title=${encodeURIComponent(achPopTitle)}`;
  els.timeDlg.close();
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title: achPopTitle || t("Achievements") }),
  }).then((r) => r.json()).then((res) => {
    if (!res.opened) window.open(url, "_blank", "noopener");
  }).catch(() => { /* nothing else to try */ });
});

/* The profile panel is this app's own page in a frame, and a right-click in
   there can ask for things only the app proper can do - chiefly "show me this
   game's achievements in the panel I already have". Only messages from a
   frame of our own are listened to, and only the two verbs below. */
addEventListener("message", (ev) => {
  if (ev.origin !== location.origin) return;
  const asked = ev.data;
  if (!asked || asked.romsrx !== 1) return;
  const id = Number(asked.id) || 0;
  /* The profile stays where it is. A list opened from it is a detour - you
     were looking at a career, you wanted to see one game's set, and you will
     want the career back afterwards. Both are dialogs, so the new one stacks
     over the old and closing it puts you back where you were, which is what
     shutting the profile first would have thrown away. */
  if (asked.want === "howlong" && id) {
    showHowLong(id, String(asked.title || ""));
  } else if (asked.want === "web" && asked.url) {
    openWeb(String(asked.url), String(asked.title || ""));
  }
});

/* ---------- the achievements themselves ----------

   The numbers above say a set is forty things worth 500 points. This says
   which forty, and which of them you have - which is the part somebody acts
   on, especially the missable ones, since knowing about those afterwards is
   knowing too late.

   Behind a button on purpose. The list is a second request and a badge per
   achievement on top of it, which is a page's worth of loading to put in front
   of somebody who opened this window to read a median. */
let achGame = 0;
let achFound = null;

/** Put the block in the window that is asking, and start it empty.
 *
 *  Both the How Long window and the preview panel offer the same list, and
 *  they are never open at once - so there is one block, moved between them,
 *  rather than two that would have to be kept in step through every change to
 *  the controls, the state or the handlers. */
function resetAchievements(slot) {
  achGame = 0;
  achFound = null;
  if (slot && els.achBlock.parentElement !== slot) slot.append(els.achBlock);
  els.achBlock.hidden = !slot;
  els.achHead.hidden = true;
  els.achLoad.hidden = false;
  els.achLoad.disabled = false;
  els.achLoad.textContent = t("Load achievements");
  els.achRefresh.hidden = true;
  els.achControls.hidden = true;
  els.achCount.textContent = "";
  els.achList.innerHTML = "";
  els.achNote.textContent = "";
}

/** The window the list is currently sitting in, whichever that is. */
const achDialog = () => els.achBlock.closest("dialog");

// Both this panel and the window that opens beside a game draw the same list,
// so the drawing lives in achshared.js and neither of them owns it.
const ACH_REASONS = Ach.REASONS;

async function loadAchievements(refresh = false) {
  if (!achGame) return;
  els.achLoad.disabled = true;
  els.achRefresh.disabled = true;
  els.achNote.textContent = t("Asking…");
  if (!refresh) els.achLoad.textContent = t("Loading…");

  let found;
  try {
    found = await fetch(`/api/achievements?id=${encodeURIComponent(achGame)}${
      refresh ? "&refresh=1" : ""}`).then((r) => r.json());
  } catch {
    found = { ok: false, reason: "unreachable" };
  }
  // Shut, or another game opened, while this was out.
  if (!achDialog()?.open) return;

  els.achLoad.disabled = false;
  els.achRefresh.disabled = false;
  if (!found.ok) {
    els.achLoad.textContent = t("Load achievements");
    els.achNote.textContent = t(ACH_REASONS[found.reason]
                                || ACH_REASONS.unreachable);
    return;
  }

  achFound = found;
  els.achLoad.hidden = true;
  els.achRefresh.hidden = false;
  els.achControls.hidden = false;
  paintAchievements();
}

function paintAchievements() {
  if (!achFound) return;
  els.achCount.textContent = Ach.countText(achFound);
  els.achList.innerHTML = Ach.listHtml(
    achFound, els.achFilter.value, els.achSort.value);

  els.achNote.textContent = achFound.user
    ? t("Click one to open it on RetroAchievements. Unlocks are counted in "
        + "hardcore, and can take a few minutes to appear.")
    : t("Add your RetroAchievements username in Settings → Cover art to see "
        + "which of these you have earned.");
}

els.achLoad.addEventListener("click", () => loadAchievements(false));
els.achRefresh.addEventListener("click", () => loadAchievements(true));
els.achFilter.addEventListener("change", paintAchievements);
els.achSort.addEventListener("change", paintAchievements);

/* A row is its page. Opened wherever Settings says pages go, like every other
   RetroAchievements link in this app. */
function openAchievement(row) {
  const found = achFound?.achievements?.find(
    (a) => a.id === Number(row?.dataset.ach));
  if (!found) return;
  achDialog()?.close();
  openWeb(found.url, found.title);
}

els.achList.addEventListener("click", (ev) => {
  // The arrow opens the thread; everything else on the row opens the page.
  const talk = ev.target.closest(".achtalkbtn");
  if (talk) {
    ev.preventDefault();
    ev.stopPropagation();
    Ach.toggleComments(talk);
    return;
  }
  // A thread is there to be read - and selected from - not a second target.
  if (ev.target.closest(".achtalk")) return;
  openAchievement(ev.target.closest("[data-ach]"));
});
els.achList.addEventListener("keydown", (ev) => {
  if (ev.key !== "Enter" && ev.key !== " ") return;
  const row = ev.target.closest("[data-ach]");
  if (!row || ev.target.closest(".achtalk")) return;
  ev.preventDefault();
  if (ev.target.closest(".achtalkbtn")) Ach.toggleComments(ev.target);
  else openAchievement(row);
});

/* The game's list of accepted files, which is where RetroAchievements keeps
   the patches. A hack or a translation with a set is never a finished ROM
   anyone distributes - it is the original plus a patch - so for those this is
   the only way in. Opened the same way as the page itself, so it lands in
   whichever place Settings says. */
const openRaHashes = (id) => openWeb(`${RA_PAGE}${id}/hashes`);

/** Fetch the patch itself.
 *
 *  Always the user's own browser, whatever Settings says about pages: this
 *  is a file to save rather than a page to read, and a browser already knows
 *  where downloads go and how to say one has finished. A window of ours would
 *  be a window that appears to do nothing. */
/** Put a patch on a game that is already here.
 *
 *  The server does the work; this is about saying what happened. An archive
 *  holding more than one patch comes back as a list rather than a guess, and
 *  the answer to that is a question - a hack and its variants are different
 *  games to whoever is choosing. */
async function applyPatch(path, url, choose = "") {
  if (!path || !url) return;
  // Said before anything happens rather than after. Patching is a word people
  // reasonably expect to mean "changes my game", and the one thing worth
  // knowing is that it does not: it makes a second copy and leaves the
  // download alone.
  if (!choose) {
    // What this says has to depend on the setting. Promising the original is
    // safe while the setting says to delete it is the worst thing this box
    // could do - it is read precisely by people checking before they commit.
    let replacing = false;
    try {
      replacing = !!(await fetch("/api/downloads/settings")
        .then((r) => r.json())).patch_replace;
    } catch {
      // Unknown, so say the more serious of the two. Warning about a deletion
      // that then does not happen is a surprise nobody minds.
      replacing = true;
    }
    const go = await ask(
      replacing
        ? t("A patch is a list of changes to make to a game you already have — "
            + "a translation, a fan hack, or a fix a set needs.\n\n"
            + "You have chosen to replace the game: the patched version will "
            + "take its name and YOUR ORIGINAL FILE WILL BE DELETED. If you "
            + "want to keep it, turn that off in Settings → Downloads first.\n\n"
            + "Large discs take a minute or so.")
        : t("A patch is a list of changes to make to a game you already have — "
            + "a translation, a fan hack, or a fix a set needs.\n\n"
            + "RomSrx will download it and write a patched copy next to your game. "
            + "Your download is not changed, so you can delete the copy if you "
            + "don't want it.\n\n"
            + "Large discs take a minute or so."),
      { confirm: true, danger: replacing,
        ok: replacing ? t("Replace the game") : t("Patch it"),
        option: { label: t("Replace the game with the patched version"),
                  checked: replacing } });
    if (!go) return;

    // They may have changed their mind in the box itself, which is the whole
    // point of it being there. Stored before patching starts, so the server
    // reads the same answer and Settings agrees afterwards.
    const wanted = askOption();
    if (wanted !== replacing) {
      try {
        await fetch("/api/downloads/settings", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ patch_replace: wanted }),
        });
      } catch {
        await say(t("That setting could not be saved, so nothing was patched."));
        return;      // rather than patch the opposite way to what was asked
      }
    }
  }
  // Downloading the patch and rewriting the ROM takes a moment, and a menu
  // that closes with nothing else happening reads as a click that missed.
  if (!choose) toast(t("Applying the patch…"));
  watchPatch(path.split(/[\\/]/).pop());
  let res;
  try {
    res = await fetch("/api/patch/apply", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path, url, choose }),
    }).then((r) => r.json());
  } catch {
    stopWatchingPatch();
    await say(t("Could not reach the local server."));
    return;
  }
  stopWatchingPatch();

  // The patcher's refusals are English sentences; `t` hands back anything it
  // has no translation for, so the ones worth translating are translated and
  // the rare internal ones still say something.
  if (res.error) { await say(t(res.error)); return; }
  if (res.choices?.length) {
    const picked = await pickOne(t("Which patch?"), res.choices);
    if (picked) applyPatch(path, url, picked);
    return;
  }
  // Names the file to play rather than printing a path and leaving them to
  // work out which of the two copies is now the patched one.
  const made = String(res.written).split(/[\\/]/).pop();
  // Three endings, because three things can have happened. Telling someone
  // their original is safe when it has just been deleted is the one mistake
  // this message must never make.
  await say(res.replaced
    ? t("Done. \"{name}\" is now the patched version, and your original has "
        + "been deleted, as that setting asks.", { name: made })
    : res.cue
      ? t("Done. Play \"{name}\" — its own .cue was made beside it.\n\nYour "
          + "original is still there, unchanged.", { name: made })
      : t("Done. Play \"{name}\".\n\nIt is next to your original, which is "
          + "unchanged.", { name: made }));
  loadLibrary();          // the new file belongs on the shelf
}

/* ---- how far along a patch is ----
   The request that does the patching does not answer until it is finished, so
   the bar is fed by asking a second question on a second connection. The
   server is threaded, which is what makes that work. */
let patchWatch = null;

function watchPatch(label) {
  stopWatchingPatch();
  els.patchBarWhat.textContent = label || t("Patching…");
  els.patchBarPct.textContent = "";
  els.patchBarFill.style.width = "0%";
  els.patchBar.classList.add("unknown");   // no total reported yet
  els.patchBar.hidden = false;

  patchWatch = setInterval(async () => {
    let at;
    try {
      at = await fetch("/api/patch/progress").then((r) => r.json());
    } catch {
      return;              // one missed answer is not worth reacting to
    }
    if (!at.total) return; // still working out how big the job is
    const pct = Math.max(0, Math.min(100, (at.done / at.total) * 100));
    els.patchBar.classList.remove("unknown");
    els.patchBarFill.style.width = `${pct}%`;
    els.patchBarPct.textContent = `${Math.round(pct)}%`;
  }, 400);
}

function stopWatchingPatch() {
  clearInterval(patchWatch);
  patchWatch = null;
  els.patchBar.hidden = true;
  els.patchBar.classList.remove("unknown");
}

/** Which patch to use, when a game has more than one.
 *
 *  Zelda has nineteen - translations into half a dozen languages, a modern
 *  cosmetic set, a flash removal. Picking the first and saying nothing chose
 *  for the user; asking costs a click only when there is genuinely a choice.
 *  Resolves null if they backed out. */
async function chooseRaPatch(id) {
  const list = raPatches.get(id) || [];
  if (!list.length) return null;
  if (list.length === 1) return list[0].url;
  const picked = await pickOne(t("Which patch?"), list.map((p) => p.name));
  if (!picked) return null;
  return (list.find((p) => p.name === picked) || list[0]).url;
}


/* ---- one game's own emulator ----
   Everything here writes against a path, and an empty box means "whatever the
   console says" rather than "nothing" - which is why saving clears the
   override entirely when all three are blank. */
let gameEmuPath = "";

async function openGameEmulator(path, name) {
  if (!path) return;
  gameEmuPath = path;
  els.gameEmuWhat.textContent = name || path.split(/[\\/]/).pop();
  els.gameEmuPath.value = "";
  els.gameEmuCore.value = "";
  els.gameEmuArgs.value = "";
  try {
    const { override } = await fetch("/api/library/emulator", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    }).then((r) => r.json());
    els.gameEmuPath.value = override?.emulator || "";
    els.gameEmuCore.value = override?.core || "";
    els.gameEmuArgs.value = override?.args || "";
  } catch { /* nothing set, which is the usual answer anyway */ }
  els.gameEmuDlg.showModal();
}

async function pickForGame(kind) {
  const field = kind === "core" ? els.gameEmuCore : els.gameEmuPath;
  const button = kind === "core" ? els.gameEmuCorePick : els.gameEmuPick;
  const label = button.textContent;
  button.disabled = true;
  button.textContent = t("Choosing…");
  try {
    const res = await fetch("/api/downloads/browse-exe", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind: kind === "core" ? "core" : undefined }),
    }).then((r) => r.json());
    if (res.file) field.value = res.file;
  } catch { /* leave it as typed */ }
  button.textContent = label;
  button.disabled = false;
}

async function saveGameEmulator(clear = false) {
  const set = clear ? {} : {
    emulator: els.gameEmuPath.value.trim(),
    core: els.gameEmuCore.value.trim(),
    args: els.gameEmuArgs.value.trim(),
  };
  try {
    await fetch("/api/library/emulator", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: gameEmuPath, set }),
    });
  } catch {
    await say(t("Could not reach the local server."));
    return;
  }
  els.gameEmuDlg.close();
  toast(clear || !Object.values(set).some(Boolean)
    ? t("This game uses its console's settings again.")
    : t("Saved for this game only."));
}

els.gameEmuPick.addEventListener("click", () => pickForGame("emulator"));
els.gameEmuCorePick.addEventListener("click", () => pickForGame("core"));
els.gameEmuSave.addEventListener("click", () => saveGameEmulator(false));
els.gameEmuClear.addEventListener("click", () => saveGameEmulator(true));
els.gameEmuCancel.addEventListener("click", () => els.gameEmuDlg.close());

/* ---- the patch tool ----
   The same engine the right-click entry uses, with the two things it needs
   asked for by hand instead: for a patch found somewhere other than
   RetroAchievements, or a game the index has never heard of. */

async function openPatchTool(game = "") {
  els.patchResult.hidden = true;
  // Read fresh rather than remembered: Settings can have changed it since.
  try {
    els.patchDlgReplace.checked = !!(await fetch("/api/downloads/settings")
      .then((r) => r.json())).patch_replace;
  } catch { /* leave whatever it last showed */ }
  if (game) {
    // Opened from a game, so that half is answered and the patch is what is
    // still missing - which is where the pointer should already be.
    els.patchGame.value = game;
    els.patchFile.value = "";
  }
  els.patchDlg.showModal();
  if (game) els.patchFilePick.focus();
}

async function pickForPatch(kind) {
  const field = kind === "patch" ? els.patchFile : els.patchGame;
  const button = kind === "patch" ? els.patchFilePick : els.patchGamePick;
  const label = button.textContent;
  button.disabled = true;
  button.textContent = t("Choosing…");
  try {
    const res = await fetch("/api/patch/browse", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind, start: field.value.trim() }),
    }).then((r) => r.json());
    if (res.file) field.value = res.file;      // empty when they backed out
  } catch { /* leave whatever was typed */ }
  button.textContent = label;
  button.disabled = false;
}

async function runPatchTool(choose = "") {
  const game = els.patchGame.value.trim();
  const patch = els.patchFile.value.trim();
  els.patchResult.hidden = false;
  if (!game || !patch) {
    els.patchResult.textContent = t("Choose a game and a patch first.");
    return;
  }
  els.patchRun.disabled = true;
  els.patchResult.textContent = t("Working… large discs take a minute or so.");

  let res;
  try {
    res = await fetch("/api/patch/apply", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: game, patchPath: patch, choose }),
    }).then((r) => r.json());
  } catch {
    res = { error: "Could not reach the local server." };
  }
  els.patchRun.disabled = false;

  if (res.error) {
    els.patchResult.textContent = t(res.error);
    return;
  }
  if (res.choices?.length) {
    const picked = await pickOne(t("Which patch?"), res.choices);
    if (picked) runPatchTool(picked);
    else els.patchResult.hidden = true;
    return;
  }
  const made = String(res.written).split(/[\\/]/).pop();
  els.patchResult.textContent = res.cue
    ? t("Done — \"{name}\", with its own .cue beside it.", { name: made })
    : t("Done — \"{name}\", next to your original.", { name: made });
  loadLibrary();
}

els.patchGamePick.addEventListener("click", () => pickForPatch("game"));
els.patchFilePick.addEventListener("click", () => pickForPatch("patch"));
els.patchRun.addEventListener("click", () => runPatchTool());
els.patchClose.addEventListener("click", () => els.patchDlg.close());
// Ticking it here is the same as ticking it in Settings, because it is.
els.patchDlgReplace.addEventListener("change", () => {
  fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patch_replace: els.patchDlgReplace.checked }),
  }).catch(() => { /* the patch itself will use whatever is stored */ });
});
els.patchOnline.addEventListener("click",
  () => openWeb(WEB_PATCHER, t("Patch a game online")));


/** Save a patch into the folder set aside for them.
 *
 *  Kept by the app rather than handed to a browser: this way it lands
 *  somewhere known, beside the games it belongs to, instead of in whatever
 *  folder the browser happens to use. Settings -> Paths says where. */
async function downloadPatch(url, quiet = false) {
  if (!url) return null;
  if (!quiet) toast(t("Downloading the patch…"));
  let res;
  try {
    res = await fetch("/api/patch/download", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }).then((r) => r.json());
  } catch {
    if (!quiet) await say(t("Could not reach the local server."));
    return null;
  }
  if (res.error) {
    if (!quiet) await say(t(res.error));
    return null;
  }
  if (!quiet) toast(t("Patch saved to {path}", { path: res.saved }));
  return res.saved;
}

async function resolveRa(pairs) {
  const seen = new Set();
  const wanted = [];
  for (const pair of pairs || []) {
    if (!pair?.console || !pair?.name) continue;
    const key = raKey(pair.console, pair.name);
    if (raIds.has(key) || seen.has(key)) continue;
    seen.add(key);
    wanted.push({ console: pair.console, name: pair.name });
  }
  if (!wanted.length) return;

  // In chunks, so a library of several thousand games is several ordinary
  // requests rather than one enormous one.
  for (let at = 0; at < wanted.length; at += 500) {
    const batch = wanted.slice(at, at + 500);
    // Written down as "asked" before the request goes, so a second render
    // arriving while this one is out doesn't ask the same questions again.
    for (const item of batch) raIds.set(raKey(item.console, item.name), 0);
    try {
      const { ids, patches, patchExts, progress } = await fetch("/api/ra/lookup", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: batch }),
      }).then((r) => r.json());
      batch.forEach((item, i) =>
        raIds.set(raKey(item.console, item.name), (ids || [])[i] || 0));
      // Which of those have a patch, so the menu already knows.
      for (const [id, list] of Object.entries(patches || {})) {
        raPatches.set(Number(id), list);
      }
      // What the patcher can rewrite, decided once by the server so the two
      // sides can't drift apart.
      for (const ext of patchExts || []) patchExts_.add(ext);
      for (const [id, done] of Object.entries(progress || {})) {
        raProgress.set(Number(id), done);
      }
    } catch {
      // Offline, or the app is shutting down. Forget they were asked, so the
      // next redraw tries again rather than deciding these have no page.
      for (const item of batch) raIds.delete(raKey(item.console, item.name));
      return;
    }
  }
}

/* ---------- results ---------- */

function fileRow(f, support = null) {
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
  /* Only ever a mark on the ones that are in the list. The rest are left
     plain rather than badged "no": most files on most cards are not in it,
     and a column of red would say "this game is a problem" when what it means
     is "this particular dump is not the one the set was made from". */
  const raMark = raFileMark(support, f.filename);
  return `
    <div class="file${raMark ? " rahit" : ""}" ${raAttrs(f.console, f.filename)}>
      <div class="fname">
        <div>${esc(f.filename)}${raMark}</div>
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
        <div class="cartitem${selected.has(i.url) ? " picked" : ""}"
             ${raAttrs(i.console, i.filename)}>
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

  resolveRa(items.map((i) => ({ console: i.console, name: i.filename })));

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

/* The older GoodTools sets abbreviate the region to a letter - `Game (U) [!]`
   where No-Intro writes `Game (USA)`. The thumbnail server is named after the
   No-Intro sets throughout, so the short forms never match anything until
   they are spelled out. */
const GOODTOOLS = {
  U: "USA", E: "Europe", J: "Japan", W: "World",
  UE: "USA, Europe", JU: "Japan, USA",
};
/* A name carrying no region at all is the other common shape - a file called
   plainly `Tom Clancy's Splinter Cell.iso`, where the server has
   `Tom Clancy's Splinter Cell (USA).png`. Most likely first. */
const REGION_GUESSES = ["USA", "World", "Europe", "Japan"];
const HAS_REGION = /\((USA|Europe|Japan|World|Asia|Korea|Brazil|Australia|France|Germany|Spain|Italy)/i;
const TRIM_TRIES = 4;

/** The filename, then progressively simpler forms of it.
 *
 *  Plenty of misses are not missing art at all - the file just carries tags
 *  the thumbnail server's copy doesn't. `Crimewave (Europe) (Demo)` has no
 *  cover; `Crimewave (Europe)` does. Trailing bracketed groups come off one
 *  at a time, nearest the end first, since those are the least significant.
 *
 *  Measured over every one of the 129,849 files in the index, against the
 *  server's actual listings: the plain trailing-group trim found art for 70%
 *  of them, and adding the three shapes below - spelled-out regions, dump
 *  flags removed, a region guessed when the name has none - takes it to 77%,
 *  inside the same ten-candidate budget. The rest is genuinely not there:
 *  half of what still misses is homebrew, demos, prototypes and hacks, which
 *  the thumbnail project does not collect. */
function nameVariants(stem) {
  const out = [];
  const seen = new Set();
  const add = (value) => {
    const clean = value.replace(/\s{2,}/g, " ").trim();
    if (clean && !seen.has(clean)) { seen.add(clean); out.push(clean); }
  };

  add(stem);
  const expanded = stem.replace(/\(([A-Z]{1,2})\)/g,
    (whole, code) => (GOODTOOLS[code] ? `(${GOODTOOLS[code]})` : whole));
  add(expanded);

  // `[!]`, `[a1]`, `[b]` and friends are dump flags. They are never part of
  // a cover's name, and unlike the round brackets they can sit anywhere.
  const noFlags = expanded.replace(/\s*\[[^\]]*\]/g, "");
  add(noFlags);

  let current = noFlags;
  for (let i = 0; i < TRIM_TRIES; i++) {
    const trimmed = current.replace(/\s*\([^()]*\)\s*$/, "").trim();
    if (!trimmed || trimmed === current) break;
    current = trimmed;
    add(current);
  }

  // Tried last: guessing a region is the weakest of these, so it must never
  // push a name we actually have out of the ten that get attempted.
  for (const base of [noFlags, current]) {
    if (!base || HAS_REGION.test(base)) continue;
    for (const region of REGION_GUESSES) add(`${base} (${region})`);
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
/* Ask the app itself, which knows what the thumbnail server actually has.
 *
 * It reads the server's directory listings and matches against real
 * filenames, so it finds art the guesses below never could - and title
 * screens or in-game snaps for the homebrew, hacks and prototypes that never
 * came in a box to photograph. A 404 from here costs one request to
 * localhost and falls straight through to the guessing, which is exactly what
 * this did before, so nothing is lost when the listings can't be fetched. */
/* Bumped when the user asks for every cover to be looked up again, and carried
   on the URL so the browser cannot answer out of the redirect it cached
   yesterday. The server ignores it. It lives in sessionStorage because the
   reload that follows is what actually puts the new answers on screen. */
let coverGen = sessionStorage.getItem("coverGen") || "";

/* Where covers come from, and in which order - see artwork.MODES. Mirrored
   into sessionStorage so it is known synchronously: the first tiles can be
   drawn before any fetch has landed, and a tile drawn on the wrong assumption
   asks the wrong server. "gaps" is both the default and what this app did
   before any of this existed, so a cold start behaves as it always has. */
let coverMode = sessionStorage.getItem("coverMode") || "gaps";

async function loadCoverMode() {
  try {
    const { mode } = await fetch("/api/artwork/mode").then((r) => r.json());
    if (mode) {
      coverMode = mode;
      sessionStorage.setItem("coverMode", mode);
    }
  } catch { /* the default is what this app has always done */ }
}

const resolvedCover = (console_, stem) =>
  `/api/cover?console=${encodeURIComponent(console_)}&name=${
    encodeURIComponent(stem)}${coverGen ? `&v=${coverGen}` : ""}`;

/* The guesses go first and the resolver picks up what they miss.
 *
 * That order is deliberate. A guess is an exact filename: when it hits, it is
 * a picture of precisely the release on disk, and nothing can improve on it.
 * The resolver matches on the title with the region and revision stripped, so
 * where a game exists in several editions it has to choose - and choosing is
 * where it can be wrong in a way a person notices, a USA game wearing the
 * European box. It is now careful about that, preferring the exact name and
 * then the matching region, but the guesses are still the better answer when
 * they have one, so they are asked first. */
function coverCandidates(files) {
  const urls = [];
  const seen = new Set();

  const asked = [];
  for (const file of files.slice(0, FILES_PER_KIND)) {
    const stem = file.ext
      ? file.filename.slice(0, -(file.ext.length + 1))
      : file.filename;
    if (!stem || !file.console) continue;
    const url = resolvedCover(file.console, stem);
    if (!seen.has(url)) { seen.add(url); asked.push(url); }
  }
  /* Every guess below is an address on the thumbnail server. Somebody who has
     asked for these services *instead* of libretro would get libretro art back
     through the side door if they were tried anyway, so in that mode there is
     nothing to try but the resolver. */
  if (coverMode === "only") return asked;

  // Which side gets first refusal. In "prefer" the resolver has already asked
  // the services and fallen back to libretro itself, so the guesses sit behind
  // it as a last resort rather than in front of it as the first answer.
  const order = (guesses) =>
    (coverMode === "prefer" ? [...asked, ...guesses] : [...guesses, ...asked]);

  // Room kept back so the guesses can never crowd the resolver out entirely -
  // it is the only one of the two that can answer for a homebrew game.
  const guessLimit = Math.max(1, MAX_COVER_TRIES - asked.length);

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
          if (urls.length >= guessLimit) return order(urls);
        }
      }
    }
  }
  return order(urls);
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

/* How long this game takes, on the result itself.
 *
 * Both figures, whenever they are known - not only while the shelf is ordered
 * by one of them. Once a game has been priced the answer is free to show, and
 * "how long is this" is worth reading whether or not it is why the list is in
 * the order it is in. A game with no set shows nothing at all rather than a
 * pair of dashes, which would be four characters of noise on most results. */
function searchTimeBadges(g) {
  const row = searchTimes.get(groupKey(g));
  if (!row || (!row.beat && !row.master)) return "";
  const one = (seconds, label) => (seconds
    ? `<span class="gtime"><span class="gtimeval">${esc(spanText(seconds))}</span>
         <span class="gtimekey">${esc(label)}</span></span>` : "");
  return `<span class="gtimes">${one(row.beat, t("to beat"))}${
    one(row.master, t("to master"))}</span>`;
}

function gameCard(g, open = false) {
  // Console leads the row so you can see what a result is at a glance.
  const consoles = consoleBadges(g.consoles);
  const regions = g.regions.slice(0, 4)
    .map((r) => `<span class="badge">${esc(r)}</span>`).join("");
  const n = g.files.length;
  const s = g.sources.length;
  const key = groupKey(g);
  const support = raSupported.get(key) || null;

  return `
    <details class="game"${open || support ? " open" : ""} data-group="${esc(key)}">
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
          <span class="gconsoles">${consoles}${searchTimeBadges(g)}${
            raCheckButton(support)}</span>
        </span>
      </summary>
      ${raSupportLine(support)}
      <div class="sections">${consoleSections(g.files).map(
        ([name, files]) => `
        <div class="consec">
          ${consoleArtHtml(name, files)}
          <div class="conbody">
            <div class="conhead">
              <button class="finst" hidden></button>
            </div>
            <div class="files">${files.map((f) => fileRow(f, support)).join("")}</div>
          </div>
        </div>`).join("")}</div>
    </details>`;
}

/* ---------- which copies work with RetroAchievements ----------

   The filter in the bar is about where a file came from: it shows the archive
   items that are RetroAchievements' own sets. That is a useful blunt answer
   and it misses the case people actually hit - a game whose copy on some
   ordinary preservation set is the very dump the set was built from, sitting
   on a card with a dozen others that are not.

   So this is the same question asked per game: press the button on a card and
   the app fetches the list of dumps that game's set accepts and marks the rows
   that are in it. Per card rather than a wider filter because it is a request
   per game - the list is a few hundred names for a Redump title - and because
   the answer is only interesting once you have decided which game you want.

   Matched by name, which is what can be known before downloading: both sides
   name the same dumps from the same preservation sets. The line under the
   heading says so rather than promising a certainty only the file's own hash
   could give. */
const raSupported = new Map();      // groupKey -> the server's answer
const raChecking = new Set();       // ...and which are out being asked

const RA_SUPPORT_REASONS = {
  nokey: "Add your RetroAchievements Web API key in Settings → Cover art, and "
       + "this can check which copies their set accepts.",
  noset: "RetroAchievements has no achievement set for this game.",
  nohashes: "RetroAchievements lists no files for this game's set.",
  unreachable: "Could not reach RetroAchievements.",
};

/** The mark on a file that is one of the dumps the set was built from. */
function raFileMark(support, filename) {
  const row = support?.byName?.get(filename);
  if (!row?.ok) return "";
  const why = row.patch
    ? t("RetroAchievements' set is built from this file, with a patch applied.")
    : t("RetroAchievements' set is built from this exact file.");
  return ` <span class="rayes" title="${esc(why)}">${esc(t("RA"))}${
    row.patch ? `<span class="rapatchmark">${esc(t("patch"))}</span>` : ""}</span>`;
}

function raCheckButton(support) {
  const count = support?.ok
    ? `<span class="racount">${support.matched}/${support.files.length}</span>`
    : "";
  // Pressed once it checks; pressed again it puts the card back as it was.
  // A mark that cannot be taken off is a mark you have to reload the search to
  // be rid of.
  const label = support
    ? t("Clear the RetroAchievements marks on this game")
    : t("Check which copies here work with RetroAchievements");
  return `<button class="racheck${support?.ok ? " on" : ""}" type="button"
    title="${esc(label)}" aria-label="${esc(label)}">
    <img src="/ra.png" alt="" onerror="raLogoFail(this)">
    <span class="ralabel">${esc(t("RA"))}</span>${count}</button>`;
}

/** What the answer means, once there is one.
 *
 *  With a way to dismiss it: it is a paragraph explaining a set of marks, and
 *  once it has been read the marks say the same thing in less space. Closing
 *  it leaves them alone - that is the point of having two controls rather than
 *  one - and it stays closed until the card is checked again. */
const raCloseLine = () => `<button class="raclose" type="button"
  title="${esc(t("Hide this note"))}" aria-label="${esc(t("Hide this note"))}"
  >&times;</button>`;

function raSupportLine(support) {
  if (!support || support.noteOff) return "";
  if (!support.ok) {
    return `<p class="raline bad">${esc(t(RA_SUPPORT_REASONS[support.reason]
      || RA_SUPPORT_REASONS.unreachable))}${raCloseLine()}</p>`;
  }
  const where = (support.sets || []).map((one) => one.console).join(", ");
  const line = support.matched
    ? t("{n} of these {total} copies are dumps the achievement set was built "
        + "from, marked below. Checked by name against the {listed} files "
        + "RetroAchievements lists for {where} — the certain answer is the "
        + "file's own hash, which only the download itself can give.",
        { n: support.matched, total: support.files.length,
          listed: support.total, where })
    : t("None of these {total} copies is among the {listed} files "
        + "RetroAchievements lists for {where}. Another source may still "
        + "have one.",
        { total: support.files.length, listed: support.total, where });
  /* A card can hold systems that have no set at all, and those files were
     never compared against anything. Saying nothing about them would let an
     unmarked row read as "checked and rejected". */
  const unchecked = (support.consoles || 0) - (support.sets || []).length;
  const rest = unchecked > 0
    ? ` ${t("{n} other systems on this card have no set, so their copies were "
            + "not checked.", { n: unchecked })}`
    : "";
  return `<p class="raline${support.matched ? "" : " bad"}">${
    esc(line)}${esc(rest)}${raCloseLine()}</p>`;
}

/* Dismissing the note. Remembered on the answer rather than done to the
   element alone, so a redraw of the card - a download finishing, the shelf
   repainting - does not bring back a paragraph that was closed. */
els.results.addEventListener("click", (ev) => {
  const close = ev.target.closest(".raclose");
  if (!close) return;
  ev.preventDefault();
  ev.stopPropagation();
  const key = close.closest("details.game")?.dataset.group || "";
  const support = raSupported.get(key);
  if (support) support.noteOff = true;
  close.closest(".raline")?.remove();
});

/* The button sits inside the summary, which is a control of its own: without
   this, checking a card would also fold it. */
els.results.addEventListener("click", async (ev) => {
  const button = ev.target.closest(".racheck");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();

  const card = button.closest("details.game");
  const key = card?.dataset.group || "";
  const group = loadedGroups.find((g) => groupKey(g) === key);
  if (!group || raChecking.has(key)) return;

  /* Already answered, so this press is the other half of the switch: it takes
     the marks and the note back off. Asking again is what the button would
     have to be pressed twice for, which is the right way round - the answer
     barely changes, and having no way to undo the marks is the thing worth
     fixing. Nothing is fetched here, so it is instant. */
  if (raSupported.has(key)) {
    raSupported.delete(key);
    const back = document.createElement("div");
    back.innerHTML = gameCard(group, card.open);
    const plain = back.firstElementChild;
    if (plain) {
      card.replaceWith(plain);
      paintInstalled();
      paintAddButtons();
    }
    return;
  }

  raChecking.add(key);
  button.classList.add("asking");
  /* Said out loud while it happens. The first console asked about in a session
     costs a whole game list from RetroAchievements before any hashes are
     fetched, and a card spanning three systems can take the best part of a
     minute - during which a dimmed button is not enough to tell a slow answer
     from a dead one. */
  card.open = true;
  const waiting = document.createElement("p");
  waiting.className = "raline waiting";
  waiting.textContent = t("Asking RetroAchievements which copies its set "
                          + "accepts…");
  card.querySelector(".raline")?.remove();
  card.querySelector("summary")?.after(waiting);
  try {
    const found = await fetch("/api/ra/supported", {
      method: "POST", headers: { "Content-Type": "application/json" },
      // Each file with the machine it is for: one card is one game and can
      // still span half a dozen systems, and each of those is a set of its
      // own to be checked against.
      body: JSON.stringify({
        files: group.files.map((f) => ({
          filename: f.filename, console: f.console,
        })),
      }),
    }).then((r) => r.json());
    // Keyed by the very spelling that was sent, so drawing the marks is a
    // lookup rather than the page matching names a second time and possibly
    // differently.
    found.byName = new Map((found.files || []).map((row) => [row.filename, row]));
    raSupported.set(key, found);
  } catch {
    raSupported.set(key, { ok: false, reason: "unreachable" });
  }
  raChecking.delete(key);
  waiting.remove();

  /* Only this card is redrawn. Rebuilding the whole list would answer one
     question and shut every other card somebody had opened, which is a worse
     trade than it sounds when the reason cards get opened is to compare
     sources. Opened as it is replaced, since the marks are inside it. */
  const fresh = document.createElement("div");
  fresh.innerHTML = gameCard(group, true);
  const drawn = fresh.firstElementChild;
  if (drawn) {
    card.replaceWith(drawn);
    paintInstalled();
    paintAddButtons();
  }
});

/* ---------- ordering search results by how long a game takes ----------

   RetroAchievements has no way to ask which games are fastest: the only bulk
   endpoint returns titles, points and achievement counts and no times at all,
   so a time is one request per game. Ranking the whole index would be twenty
   thousand of them.

   What this does instead is rank what has been loaded. Every page that arrives
   is priced and the whole accumulated set is re-sorted - not just the new page,
   which would append 1h, 3h, 8h and then 0.5h, 2h, 9h and read as broken. The
   note under the control says how many games are actually being ranked, so it
   never pretends to be more than it is. */
let loadedGroups = [];
const searchTimes = new Map();

/* A group is a game; its files are the copies. The first file is what the
   RetroAchievements lookup elsewhere is keyed on, so it is what is priced. */
const groupKey = (group) => {
  const file = group?.files?.[0];
  return file ? `${file.console}	${file.filename}` : "";
};

function sortLoaded() {
  const which = els.searchSort.value;
  if (which !== "beat" && which !== "master") return false;
  loadedGroups.sort((a, b) => {
    const mine = searchTimes.get(groupKey(a))?.[which];
    const theirs = searchTimes.get(groupKey(b))?.[which];
    if (mine && theirs) return mine - theirs;
    if (mine) return -1;
    if (theirs) return 1;
    return (a.title || "").localeCompare(b.title || "", undefined, { numeric: true });
  });
  return true;
}

function drawLoaded() {
  els.results.innerHTML = loadedGroups.map((g) => gameCard(g)).join("");
  paintInstalled();
  paintAddButtons();
}

let searchPricing = false;

/** Price whatever is loaded, then re-order and redraw. */
async function priceSearch() {
  const which = els.searchSort.value;
  if ((which !== "beat" && which !== "master") || searchPricing) return;
  searchPricing = true;
  els.searchSortNote.textContent = t("timing…");
  try {
    const wanted = loadedGroups
      .map((g) => g.files?.[0])
      .filter(Boolean)
      .map((f) => ({ console: f.console, name: f.filename }));
    const found = await fetch("/api/times", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ games: wanted }),
    }).then((r) => r.json());
    for (const [key, row] of Object.entries(found.times || {})) {
      searchTimes.set(key, row);
    }
    if (sortLoaded()) drawLoaded();
    const ranked = loadedGroups.filter((g) => searchTimes.get(groupKey(g))?.[which]).length;
    els.searchSortNote.textContent = found.waiting
      ? t("ranking {n} of the {total} loaded — {left} still to time",
          { n: ranked, total: loadedGroups.length, left: found.waiting })
      : t("ranking the {total} games loaded so far", { total: loadedGroups.length });
  } catch {
    els.searchSortNote.textContent = t("could not time these");
  }
  searchPricing = false;
}

els.searchSort.addEventListener("change", () => {
  if (!els.searchSort.value) {
    els.searchSortNote.textContent = "";
    // Back to the order the server sent, which is what it always was.
    search(false);
    return;
  }
  priceSearch();
});

async function search(append = false) {
  const mine = ++seq;
  if (!append) offset = 0;

  els.hint.textContent = t("searching…");
  const res = await fetch(`/api/search?${params({ offset })}`);
  const data = await res.json();
  if (mine !== seq) return; // a newer keystroke already won

  total = data.total;
  if (!append) renderFilters(data.facets);

  // Kept, so a time sort can re-order everything loaded rather than only the
  // page that just arrived.
  loadedGroups = append ? [...loadedGroups, ...data.groups] : [...data.groups];

  // Cards always start collapsed - expanding is the user's call.
  const html = data.groups.map((g) => gameCard(g)).join("");

  // Every file on the page, not only the cards that happen to be open: a
  // card is expanded with a click and the menu has to be right immediately.
  resolveRa(data.groups.flatMap((g) => g.files.map(
    (f) => ({ console: f.console, name: f.filename }))));

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
  // A time sort prices the new arrivals and re-orders the whole set.
  if (els.searchSort.value) priceSearch();
  // Never over the library - a search can be re-run while the shelf is on
  // screen, switching language does exactly that - nor over the front page,
  // which is showing consoles rather than games. paintMore() knows both.
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

/* Built with t() rather than marked up with data-i18n, like every other
   piece of HTML this file writes: the markup is injected long after the pass
   that translates the page has run over it. */
function firstRunHtml() {
  return `
    <div class="firstrun">
      <h2>${esc(t("Nothing indexed yet"))}</h2>
      <p>${esc(t("RomSrx searches its own local copy of what archive.org holds. "
                 + "Building that copy takes a couple of minutes and only has to "
                 + "happen once — everything after it is offline and instant."))}</p>
      <button id="firstindex" class="bigbtn">${esc(t("Build the index"))}</button>
      <p class="firstnote">${esc(t("You can rebuild it any time with the"))}
         <span class="inlineicon">&#8635;</span>
         ${esc(t("button in the corner."))}</p>
    </div>`;
}

/* Until an index exists there is nothing to search, nothing to filter and
   nothing to download, so everything is turned off except the two buttons
   that build it: the one in the middle of the page and the ↻ in the corner.
   Settings included - every one of its pages is about games, downloads or
   folders that do not exist yet.

   Two layers, because disabling buttons only stops the ones that were
   thought of. `disabled` is what makes the header look switched off, and the
   guard below is what makes the rule true: a link in the footer, a keyboard
   shortcut, something a gamepad drives, or anything added later. */
const INDEX_ALLOWED = "#reindex, #firstindex, #indexdlg";

function lockUntilIndexed() {
  const usable = !indexEmpty;
  for (const el of [els.libBtn, els.searchBtn, els.homeBtn, els.titleBtn,
                    els.cartBtn, els.dlBtn, els.acctBtn, els.q,
                    els.settingsBtn, els.raBtn, els.webPatchBtn]) {
    if (el) el.disabled = !usable;
  }
  document.body.classList.toggle("noindex", indexEmpty);
  if (indexEmpty) {
    // Anything already open was opened before the answer came back.
    for (const dialog of document.querySelectorAll("dialog[open]")) {
      if (dialog.id !== "indexdlg") dialog.close();
    }
  }
  // Stats are what decide whether there is an index, so this is the moment
  // the page can put up the panel that offers to build one - rather than
  // waiting for a search that, with everything switched off, never comes.
  paintHome();
}

/* Swallowed on the way down, before whatever was aimed at hears about it.
   Only pointer and keyboard activation - not focus, not scrolling - so the
   page can still be read and the one live button still reached by tab. */
for (const kind of ["pointerdown", "click", "keydown", "contextmenu"]) {
  document.addEventListener(kind, (ev) => {
    if (!indexEmpty || ev.target?.closest?.(INDEX_ALLOWED)) return;
    // Enter and space are how a button is pressed from the keyboard; the
    // rest are how someone reads the page, and are none of this rule's
    // business.
    if (kind === "keydown" && !["Enter", " ", "Spacebar"].includes(ev.key)) return;
    ev.preventDefault();
    ev.stopPropagation();
  }, true);
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
    // `notes` for the wide box: this is several paragraphs of prose, and the
    // question-sized one turns it into a column of five-word lines.
    await say(res.error
      || plainNotes(res.notes)
      || `RomSrx ${version} — no notes were published for this version.`,
    { notes: true });
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
    <div class="dljob ${esc(job.status)}" data-id="${job.id}"
         ${raAttrs(job.console, job.filename)}>
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

/** The library entry a finished download turned into, if it can be played.
 *
 *  A download knows what it fetched, not what ended up on disk - the archive
 *  is unpacked and the game inside it is what the library indexed. So this
 *  goes through the same name-join the "In Library" markers use, and answers
 *  with nothing unless the console also has an emulator set: a button that
 *  can only apologise is worse than no button.
 */
function jobPlayPath(job) {
  if (!job?.filename) return "";
  // The extension has to come off first. installKey only folds case and
  // spacing - taking the type off is installStem's job - and the library is
  // indexed under names that never had one, so keying on "game.zip" looks up
  // something that cannot be there.
  const ext = (String(job.filename).match(/\.([A-Za-z0-9]{1,4})$/) || ["", ""])[1];
  const stem = installStem(job.filename, ext);
  const matches = installedIndex.get(installKey(stem)) || [];
  // The console decides between two games of the same name, the way the
  // "In Library" marker does.
  const game = matches.find((g) => g.console === job.console)
    || matches.find((g) => !g.console) || matches[0];
  if (!game) return "";
  return consoleSetup.get(game.console || "")?.emulator ? game.path : "";
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

let lastDownloadState = null;

function renderDownloads(state) {
  lastDownloadState = state;
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
    // A download that just finished has a button now that it did not before.
    paintDownloadPlay();
    return;
  }
  renderedJobs = signature;

  resolveRa(jobs.map((j) => ({ console: j.console, name: j.filename })));

  els.dlJobs.innerHTML = jobs.length
    ? jobSections(jobs)
    : `<p class="empty">${esc(t("Nothing downloading. Add files from your list."))}</p>`;
  paintDownloadPlay();
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

els.patchBrowse.addEventListener("click", async () => {
  const label = els.patchBrowse.textContent;
  els.patchBrowse.disabled = true;
  els.patchBrowse.textContent = t("Choosing…");
  try {
    const res = await fetch("/api/downloads/browse", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start: els.patchFolder.value.trim() }),
    }).then((r) => r.json());
    if (res.folder) {
      els.patchFolder.value = res.folder;   // null when cancelled
      await saveDownloadSettings();
    }
  } catch { /* leave the typed path alone */ }
  els.patchBrowse.textContent = label;
  els.patchBrowse.disabled = false;
});

// Typed by hand, saved once the typing stops - the same as the folder above.
// Wrapped rather than passed directly: the debounced version is declared
// further down this file, so naming it here would read it before it exists
// and take the rest of the script down with it.
els.patchFolder.addEventListener("input", () => saveSettingsSoon());
els.patchReplace.addEventListener("change", () => saveDownloadSettings());

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
    // Left blank on purpose when unset: the placeholder says what happens
    // then, which is truer than filling in a path nobody chose.
    els.patchFolder.value = s.patch_folder || "";
    els.patchReplace.checked = !!s.patch_replace;
    // 0 is the stored value for "Unlimited", so don't fall back on it.
    els.dlWorkers.value = String(s.workers ?? 3);
    els.dlExtract.checked = !!s.extract;
    els.dlExtractMode.value = s.extract_mode === "here" ? "here" : "folder";
    els.dlExtractMode.disabled = !s.extract;
    els.dlDelete.checked = !!s.delete_archive;
    els.dlDelete.disabled = !s.extract;
    els.perConsole.checked = !!s.per_console;
    // The first entry is the preference; the rest are the fallback order.
    els.regionPref.value = (s.region_priority || [])[0] || "USA";
    els.cartClrDone.checked = !!s.clear_when_done;
    els.notifyDone.checked = !!prefs.notifyDone;
    els.webTarget.value = prefs.webTarget === "browser" ? "browser" : "app";
    syncWorkerInfo();
    } catch { /* leave whatever is on screen */ }
}

/* Taking finished downloads off the list is the server's job - it has to
   happen for things that finish while this dialog, or the whole window, is
   shut. All the page does is set the switch and pick the change up again. */
els.notifyDone.addEventListener("change", () => {
  savePrefs({ notifyDone: els.notifyDone.checked });
});

els.webTarget.addEventListener("change", () => {
  savePrefs({ webTarget: els.webTarget.value === "browser" ? "browser" : "app" });
});

els.cartClrDone.addEventListener("change", async () => {
  await fetch("/api/downloads/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ clear_when_done: els.cartClrDone.checked }),
  });
});

/* The optional cover services. See romsrx/artwork.py for what they are and
   why the app ships with none of them switched on.
 *
 * Saved as you type, like every other panel in Settings, but on a delay: a
 * client secret is thirty characters, and every save throws away the misses
 * this app has remembered so it will go and look again. Thirty of those while
 * somebody pastes a key would be thirty pointless round trips. */
const ART_PROVIDERS = [
  { name: "retroachievements", on: "artRaOn", state: "artRaState",
    test: "artRaTest", out: "artRaResult",
    fields: { api_key: "artRaKey", username: "artRaUser" } },
  { name: "igdb", on: "artIgdbOn", state: "artIgdbState",
    test: "artIgdbTest", out: "artIgdbResult",
    fields: { client_id: "artIgdbId", client_secret: "artIgdbSecret" } },
  { name: "steamgriddb", on: "artSgdbOn", state: "artSgdbState",
    test: "artSgdbTest", out: "artSgdbResult",
    fields: { api_key: "artSgdbKey" } },
];

const artOrder = () =>
  [...els.artProvs.querySelectorAll(".artprov")].map((p) => p.dataset.prov);

function artPayload() {
  const out = { mode: els.artMode.value, order: artOrder() };
  for (const p of ART_PROVIDERS) {
    out[p.name] = { on: els[p.on].checked };
    for (const [key, id] of Object.entries(p.fields)) {
      out[p.name][key] = els[id].value.trim();
    }
  }
  return out;
}

/* Only the labels, never the boxes: this runs after a save, and a save happens
   while somebody is still typing into one of them. */
function paintArtState(status) {
  const by = Object.fromEntries(
    (status?.providers || []).map((p) => [p.name, p]));
  for (const p of ART_PROVIDERS) {
    const info = by[p.name] || {};
    const el = els[p.state];
    el.textContent = !info.ready ? t("not set up")
      : info.on ? t("in use") : t("switched off");
    el.classList.toggle("on", !!(info.ready && info.on));
  }
  els.artCount.textContent = status?.cached
    ? t("{n} looked up so far", { n: status.cached }) : "";
  // Chosen and effective differ only when a mode has been picked that needs a
  // working service and there isn't one. Saying so beats silently ignoring it.
  els.artModeNote.hidden = !status
    || status.mode === "gaps" || status.mode === status.effective;
}

async function loadArtwork() {
  try {
    const status = await fetch("/api/artwork").then((r) => r.json());
    els.artMode.value = status.mode || "gaps";
    for (const name of status.order || []) {
      const panel = els.artProvs.querySelector(`.artprov[data-prov="${name}"]`);
      if (panel) els.artProvs.append(panel);      // append in order = reorder
    }
    paintArtArrows();
    const by = Object.fromEntries(
      (status.providers || []).map((p) => [p.name, p]));
    for (const p of ART_PROVIDERS) {
      const info = by[p.name] || {};
      els[p.on].checked = !!info.on;
      for (const [key, id] of Object.entries(p.fields)) {
        els[id].value = (info.fields || {})[key] || "";
      }
    }
    paintArtState(status);
  } catch { /* leave whatever is on screen */ }
}

async function saveArtworkNow() {
  try {
    const status = await fetch("/api/artwork/settings", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(artPayload()),
    }).then((r) => r.json());
    paintArtState(status);
    els.artSaved.hidden = false;
    clearTimeout(saveArtworkNow.timer);
    saveArtworkNow.timer = setTimeout(() => { els.artSaved.hidden = true; }, 1400);
  } catch { /* nothing worth interrupting the user for */ }
}

const saveArtworkSoon = debounce(saveArtworkNow, 700);

for (const p of ART_PROVIDERS) {
  els[p.on].addEventListener("change", saveArtworkNow);
  for (const id of Object.values(p.fields)) {
    els[id].addEventListener("input", saveArtworkSoon);
    // Leaving the box is a stronger signal than a pause in typing.
    els[id].addEventListener("change", saveArtworkNow);
  }
  els[p.test].addEventListener("click", async () => {
    // Whatever is in the boxes right now is what gets tested, so it has to be
    // saved first - otherwise Test checks the key you had before.
    await saveArtworkNow();
    const out = els[p.out];
    els[p.test].disabled = true;
    out.className = "arttest";
    out.textContent = t("Checking…");
    try {
      const result = await fetch("/api/artwork/test", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: p.name }),
      }).then((r) => r.json());
      out.className = `arttest ${result.ok ? "good" : "bad"}`;
      out.textContent = result.ok
        ? (result.detail || t("That worked."))
        : (result.error || t("That did not work."));
    } catch {
      out.className = "arttest bad";
      out.textContent = t("Could not reach the app.");
    }
    els[p.test].disabled = false;
  });
}

/* The arrows that decide which service is asked first.
 *
 * The panels themselves are the list: moving one moves its whole block, so
 * what you see down the page is the order the app will use, and there is no
 * second representation of it anywhere to disagree. The first panel's "up"
 * and the last one's "down" are disabled rather than hidden, so the two
 * buttons don't shuffle sideways as a panel moves. */
function paintArtArrows() {
  const panels = [...els.artProvs.querySelectorAll(".artprov")];
  panels.forEach((panel, at) => {
    const up = panel.querySelector('[data-move="up"]');
    const down = panel.querySelector('[data-move="down"]');
    if (up) up.disabled = at === 0;
    if (down) down.disabled = at === panels.length - 1;
  });
}

els.artProvs.addEventListener("click", (ev) => {
  const button = ev.target.closest("[data-move]");
  if (!button || button.disabled) return;
  const panel = button.closest(".artprov");
  const other = button.dataset.move === "up"
    ? panel.previousElementSibling : panel.nextElementSibling;
  if (!other) return;
  // A cover already on screen was resolved under the old order, so the new one
  // only shows on the next lookup. Saving throws away the remembered misses,
  // which is most of what would change.
  if (button.dataset.move === "up") panel.after(other);
  else panel.before(other);
  paintArtArrows();
  saveArtworkNow();
});

/* Changing where covers come from changes what every tile should be showing,
   and the page decides half of that itself before it ever asks the server. So
   this is one of the few settings that genuinely has to reload. */
els.artMode.addEventListener("change", async () => {
  await saveArtworkNow();
  const { effective } = await fetch("/api/artwork").then((r) => r.json());
  sessionStorage.setItem("coverMode", effective || "gaps");
  sessionStorage.setItem("coverGen", String(Date.now()));
  location.reload();
});

/* Forget every answer and start over. The reload is the point: the covers
   already on screen are <img> elements that fetched their redirect hours ago,
   and nothing short of asking for them again under a new address replaces
   them. See coverGen. */
els.artForget.addEventListener("click", async () => {
  els.artForget.disabled = true;
  await saveArtworkNow();
  try {
    await fetch("/api/artwork/forget", { method: "POST" });
    sessionStorage.setItem("coverGen", String(Date.now()));
    location.reload();
  } catch {
    els.artForget.disabled = false;
  }
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
      patch_folder: els.patchFolder.value.trim(),
      patch_replace: els.patchReplace.checked,
      region_priority: regionOrderFrom(els.regionPref.value),
    }),
  });
  els.dlSaved.hidden = false;
  clearTimeout(saveDownloadSettings.timer);
  saveDownloadSettings.timer = setTimeout(() => { els.dlSaved.hidden = true; }, 1400);
}

/* The chosen region first, then the rest in their usual order. Picking Japan
   should not mean a game with no Japanese release stops being sorted sensibly -
   it means Japan wins where there is a choice. */
const REGION_FALLBACK = ["USA", "Europe", "Japan", "World"];
const regionOrderFrom = (first) =>
  [first, ...REGION_FALLBACK.filter((r) => r !== first)];

// Typing waits for a pause; the rest apply on the spot.
const saveSettingsSoon = debounce(saveDownloadSettings, 700);
els.dlFolder.addEventListener("input", saveSettingsSoon);
for (const control of [els.dlWorkers, els.dlExtract, els.dlExtractMode,
                       els.regionPref,
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
/* The cover that actually turned up, per game.
 *
 * A tile is drawn with a list of candidates and works down it, and for a game
 * whose art is not where the first guesses say it is that means several 404s
 * before the picture appears. That cost is fine once. It is not fine on every
 * redraw of the shelf - folding a console, deleting one game, a download
 * finishing - which is what "the covers all reload" is: the same walk down the
 * same list of misses, again, for every tile on screen.
 *
 * So the URL that answered is remembered and put at the front of that game's
 * list next time. The browser has it in cache, so the tile paints from memory
 * with no request at all, and nothing else about the ordering changes: it is
 * the same list with the known-good address moved to the top. */
const coverWorked = new Map();

function rememberCover(img) {
  const key = img.closest("[data-key]")?.dataset.key;
  if (key && img.naturalWidth && isCoverUrl(img.currentSrc || img.src)) {
    coverWorked.set(key, img.currentSrc || img.src);
  }
}

function libCovers(tile) {
  const urls = [coverWorked.get(tile.key), tile.cover, tile.art]
    .filter(isCoverUrl);
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

/* Opens the preview. Drawn rather than lettered so it reads at tile size, and
   the same mark in both views so the two are obviously the same button. */
const INFO_ICON = `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11.2v4.6"/><path d="M12 8.1v.9"/></svg>`;

const infoButton = () => `<button class="libinfo" title="${esc(t("Preview"))}"
  aria-label="${esc(t("Preview"))}">${INFO_ICON}</button>`;

/* How much of this game's achievement set you have earned.
 *
 * Hardcore is the number shown, because that is the one RetroAchievements
 * treats as the real total and the one the rest of this app reports times for.
 * A set you have not started is left blank rather than badged "0/37": a shelf
 * of zeroes is noise, and the games worth seeing are the ones you are part way
 * through or have finished. */
/* The figure the shelf is currently ordered by, on the game it belongs to.
 *
 * Only while one of the two time sorts is chosen: a number on every tile all
 * the time is clutter, but when the whole shelf is arranged by how long things
 * take, not saying how long each one takes is withholding the one fact the
 * order is made of. A game with no time shows nothing rather than a dash - it
 * is already at the end, which says the same thing more quietly. */
/* ...and the same figures asked for outright, whatever the shelf is ordered
   by. Ordering by a time answers "which is shortest"; this answers "how long
   is this one", which is a question people have while looking at a shelf
   sorted by name. Both can be on at once: two lines, beat above master,
   labelled, since a bare pair of numbers says nothing about which is which. */
const TIME_SHOWN = { off: [], beat: ["beat"], master: ["master"],
                     both: ["beat", "master"] };

function timeBadge(console_, name) {
  const sort = prefs.libSort;
  const asked = TIME_SHOWN[prefs.libTimes] || [];
  // The sort's own figure is still shown while that sort is chosen, even with
  // the toggle off: not saying how long each one takes while the whole shelf
  // is arranged by it is withholding the fact the order is made of.
  const wanted = asked.length
    ? asked
    : ((sort === "beat" || sort === "master") ? [sort] : []);
  if (!wanted.length) return "";

  const row = libTimes.get(`${console_}	${name}`);
  const lines = wanted
    .map((which) => [which, row?.[which]])
    .filter(([, seconds]) => seconds);
  if (!lines.length) return "";

  const label = (which) => (which === "beat" ? t("to beat") : t("to master"));
  const title = lines
    .map(([which, seconds]) => `${spanText(seconds)} ${label(which)}`)
    .join(" · ");
  /* Just the figures on the artwork. The words that say which is which were
     half the width of the badge and are the part you only need once: the
     tooltip spells both out, and the order is fixed - to beat above, to
     master below - so the pair is readable at a glance once you know that.
     Each line carries the whole sentence as its own tooltip, so pointing at
     one number answers for that number rather than for the pair. */
  const inner = lines
    .map(([which, seconds]) => `<span class="libspanline"
       title="${esc(`${spanText(seconds)} ${label(which)}`)}">${
       esc(spanText(seconds))}</span>`).join("");
  return `<span class="libspan${lines.length > 1 ? " two" : ""}"
    title="${esc(title)}">${inner}</span>`;
}

function achievementBadge(console_, name) {
  const done = raProgress.get(raId(console_, name));
  if (!done?.total || !done.hardcore) return "";
  const full = done.hardcore >= done.total;
  const label = t("{done} of {total} achievements",
                  { done: done.hardcore, total: done.total });
  return `<span class="libach${full ? " done" : ""}" title="${esc(label)}"
    >${done.hardcore}/${done.total}</span>`;
}

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
  return `<span class="libadds">${playButton(tile)}${get}<button class="libadd"
    aria-haspopup="menu" aria-label="${esc(t("Add to…"))}">+</button></span>`;
}

/* Starting the game, where a click on the artwork no longer does.
 *
 * Only in that mode: with the cover itself playing, a play button beside it is
 * a second way to do the thing that already happens, and one more control on a
 * tile that has four. It sits with the other actions rather than somewhere of
 * its own, so "the buttons" stay one group in both views. */
const PLAY_ICON = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>`;

function playButton(tile) {
  if (prefs.libClick !== "preview" || !tile.game) return "";
  return `<button class="libplay" title="${esc(t("Play"))}"
    aria-label="${esc(t("Play"))}">${PLAY_ICON}</button>`;
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
  /* On the artwork rather than under the name: the name is already the thing
     being read, and a second line under every tile would push the shelf out
     for the sake of a figure most games have nothing to put in. */
  const spent = tile.game ? humanPlaytime(tile.game.playSeconds) : "";
  const clock = spent
    ? `<span class="libtime" title="${esc(t("{time} played", { time: spent }))}"
         >${esc(spent)}</span>`
    : "";
  return `
    <div class="libcard${tile.game ? "" : " missing"}" ${tileAttrs(tile)}
         title="${esc(tile.game ? tile.name : `${tile.name} — ${t("Not downloaded")}`)}">
      ${libCoverHtml(tile, true, badge + clock
                      + timeBadge(tile.game?.console || tile.entry?.console || '',
                                  tile.game?.name || tile.entry?.name || '')
                      + achievementBadge(tile.game?.console || tile.entry?.console || '',
                                         tile.game?.name || tile.entry?.name || '')
                      + infoButton() + tileActions(tile))}
      <span class="libtick"></span>
      <span class="libname${hit}">${esc(tile.title)}</span>
    </div>`;
}

function libListRow(tile) {
  const game = tile.game;
  // Its own column beside the size rather than the end of the detail line:
  // the two are the same kind of fact - a number about this game - and a
  // column of them reads down the shelf, which a figure buried at the end of
  // a run of tags does not.
  const spent = game ? humanPlaytime(game.playSeconds) : "";
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
      <span class="librowname${hit}">${esc(tile.name)}${infoButton()}
        <span class="librowsub">${bits.map(esc).join(" &middot; ")}</span>
      </span>
      ${timeBadge(game?.console || tile.entry?.console || "",
                  game?.name || tile.entry?.name || "")}
      ${achievementBadge(game?.console || tile.entry?.console || "",
                         game?.name || tile.entry?.name || "")}
      ${spent ? `<span class="librowtime"
        title="${esc(t("{time} played", { time: spent }))}">${esc(spent)}</span>` : ""}
      <span class="librowsize">${tile.size ? humanSize(tile.size) : ""}</span>
      ${tileActions(tile)}
    </div>`;
}

/* What a shelf files a game under.
 *
 * There used to be an "Unsorted" heading here for anything with no console,
 * and it was the wrong answer twice over: it read like a machine, it sorted
 * in among the real ones, and on a library the scan had failed to place it
 * was the first thing you saw. The scan no longer hands over games with no
 * console at all - see library.scan - so the only thing that can still land
 * here is a playlist entry saved by an older version, which gets a heading
 * that is plainly not a console. */
const UNKNOWN_CONSOLE = "Unknown";
const consoleOf = (tile) => tile.console || UNKNOWN_CONSOLE;

/** The console menu, counted from whatever shelf is on screen - so a playlist
 *  offers its own consoles rather than every console you own. */
function renderLibraryConsoles(tiles) {
  const counts = new Map();
  for (const tile of tiles) {
    const key = consoleOf(tile);
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

/* The preview button on a tile or a row. Its own listener rather than a branch
   in the one below: a click on a library card means play, and this has to take
   the click before that decides anything. */
els.libBody.addEventListener("click", (ev) => {
  const button = ev.target.closest(".libinfo");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();
  openPreviewFor(button.closest("[data-path], [data-key]"));
}, true);

/** The preview for whatever tile or row this is, from the button on it or
 *  from a click on the artwork - the two want exactly the same panel. */
function openPreviewFor(card) {
  if (!card) return;
  const game = gameAt(card.dataset.path);
  const entry = entryForCard(card);
  openPreview({
    console: game?.console || entry?.console || "",
    name: game?.name || entry?.name || "",
    title: game?.name || entry?.name || "",
    // Only a game on this machine gets a Play button.
    path: card.dataset.path || "",
    cover: coverSrc(card.querySelector("img")),
  });
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

  const all = shelfTiles();
  renderLibraryConsoles(all);

  const total = all.length;
  const wanted = els.libConsole.value;
  const needle = els.libQ.value.trim().toLowerCase();
  let tiles = wanted ? all.filter((tile) => consoleOf(tile) === wanted) : all;
  if (needle) tiles = tiles.filter((tile) => tileMatches(tile, needle));
  /* Finished sets out of the way, and only while the shelf is ordered by what
     you have earned - which is the order in which they are in the way. It
     counts as narrowing the shelf, so the line below says how many are being
     shown rather than letting the total quietly disagree with the tiles. */
  const hidingMastered = prefs.libSort === "earned" && prefs.libHideMastered;
  if (hidingMastered) tiles = tiles.filter((tile) => !isMastered(tile));
  const shownBytes = tiles.reduce((n, tile) => n + (tile.size || 0), 0);
  const narrowed = wanted || needle || hidingMastered;

  resolveRa(tiles.map((tile) => ({ console: tile.console, name: tile.name })));

  // No folder path here - with per-console paths there isn't a single one.
  const missing = pl ? tiles.filter((tile) => !tile.game).length : 0;
  els.libStats.textContent = !total
    ? (pl ? t("This playlist is empty") : t("No games found"))
    : (narrowed
        ? `${t("{shown} of {total} games", {
              shown: tiles.length.toLocaleString(),
              total: total.toLocaleString() })} · ${humanSize(shownBytes)}`
        : `${total.toLocaleString()} ${t(total === 1 ? "game" : "games")} · ${humanSize(shownBytes)}`)
      + (missing ? ` · ${missing} ${t("not downloaded")}` : "");

  /* Files in the download folder that belong to no console are left off the
     shelf rather than gathered under a made-up one. Left at that they would
     simply be missing, with nothing to say so - hence this line, and the
     button beside it, which is the existing "look for console folders and
     write down where they are" and the actual fix in almost every case. */
  /* Waved away for good, unless more turn up than were waved away - a number
     that has grown is news again, the same number is not. */
  const stray = pl ? 0 : (libraryData?.unplaced || 0);
  els.libStray.hidden = !stray || stray <= (prefs.strayHidden || 0);
  if (stray) {
    els.libStrayText.textContent = t(
      "{n} files aren't in any console's folder, so they aren't shown.",
      { n: stray });
  }

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
          : (wanted
              ? t("No games for that console.")
              // Nothing narrowing the shelf but the toggle, so it is the
              // toggle that emptied it - and that is worth being told.
              : t("Every game here is one you have already mastered."))}</p>`
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
    // A game with no time sorts last rather than as zero, which would put
    // everything RetroAchievements has never heard of at the top.
    "beat": (a, b) => byTime(a, b, "beat"),
    "master": (a, b) => byTime(a, b, "master"),
    "earned": byEarned,
  }[prefs.libSort] || ((a, b) => a.title.localeCompare(b.title));

  const groups = new Map();
  for (const tile of tiles) {
    const key = consoleOf(tile);
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
    // Starred first, then wherever you dragged it to, then alphabetically for
    // everything nobody has touched.
    order2.sort(([a], [b]) =>
      pinRank(a) - pinRank(b) || dragRank(a) - dragRank(b) || a.localeCompare(b));
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
        <!-- Always covers, whichever view the shelf below is in. This row is
             a different thing from the library - a handful of games to pick up
             again, not a catalogue to search - and it should not change shape
             underneath you when you switch how the catalogue is listed. -->
        <div class="recentrail libgrid">
          ${recent.map(libGridCard).join("")}
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
    <section class="libgroup${shut ? " shut" : ""}"
             data-console="${esc(console_)}"${showingAll ? ' data-reorder="1"' : ""}>
      <h3 class="libhead">
        ${showingAll ? `<span class="libdrag" title="${esc(t("Drag to reorder"))}"
          aria-hidden="true">&#8942;&#8942;</span>` : ""}
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
  paintFoldAll();
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
  if (!(img instanceof HTMLImageElement)) return;
  rememberCover(img);
  if (!img.closest(".libart")) return;
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

/** Every console heading currently on the shelf. */
const shownConsoles = () =>
  [...els.libBody.querySelectorAll(".libgroup:not(.librecent) .libfold")]
    .map((b) => b.dataset.console);

/** Fold or unfold the lot, whichever there is more sense in doing.
 *
 *  One button, because the answer to "which would this do" is on screen: if
 *  anything is open it closes everything, and once everything is closed the
 *  only thing left to do is open it. Consoles that aren't on the shelf right
 *  now - filtered out, or on another playlist - keep whatever state they had,
 *  since this is a button about what you are looking at. */
function foldAllConsoles() {
  const here = shownConsoles();
  if (!here.length) return;
  const shut = new Set(prefs.libShut || []);
  const anyOpen = here.some((name) => !shut.has(name));
  for (const name of here) {
    if (anyOpen) shut.add(name);
    else shut.delete(name);
  }
  savePrefs({ libShut: [...shut] });
  renderLibrary();
}

/** The button says which way it will go next. */
function paintFoldAll() {
  const here = shownConsoles();
  const shut = new Set(prefs.libShut || []);
  const anyOpen = here.some((name) => !shut.has(name));
  els.libFoldAll.hidden = !here.length;
  els.libFoldAll.innerHTML = anyOpen ? "&#9650;" : "&#9660;";
  const label = anyOpen ? t("Collapse every console") : t("Expand every console");
  els.libFoldAll.title = label;
  els.libFoldAll.setAttribute("aria-label", label);
}

/** Sort key: pinned consoles by their place in the list, everything else
 *  after them. Equal ranks fall through to an alphabetical tiebreak, so this
 *  must be a real number rather than Infinity - subtracting two Infinities
 *  gives NaN, and a NaN comparator scrambles the order. */
function pinRank(console_) {
  const at = (prefs.libPinned || []).indexOf(console_);
  return at < 0 ? Number.MAX_SAFE_INTEGER : at;
}

/** Where a console sits in the order the user dragged it into.
 *
 *  Anything never dragged sorts after everything that has been, and falls
 *  back to alphabetical among its own kind - so a shelf nobody has rearranged
 *  looks exactly as it always did, and rearranging one console doesn't
 *  scramble the rest.
 */
function dragRank(console_) {
  const at = (prefs.libOrder || []).indexOf(console_);
  return at < 0 ? Number.MAX_SAFE_INTEGER : at;
}

/** Record the shelf's order after a drag.
 *
 *  Stored as the whole visible order rather than as the one thing that moved,
 *  because that is what has to survive a reload: a list of "this console goes
 *  third" is meaningless once another console appears or disappears.
 *
 *  Pinned consoles are a band at the top, so dropping across that line has to
 *  mean something. It sets the star to match where the console landed -
 *  otherwise the row would spring back above or below the line the moment it
 *  was let go, which reads as the drag not having worked.
 */
function applyConsoleOrder(names, moved) {
  const wasPinned = new Set(prefs.libPinned || []);
  const kept = new Set(names);
  const pinned = new Set(wasPinned);

  /* Only the console that was actually dragged changes its star, and it
     changes it to match where it landed: starred if it came to rest against
     another starred one, unstarred if it left them behind. Judging the band
     by its old size instead - taking the top N - silently unpinned whatever
     the newcomer pushed down, so dragging one console demoted another. */
  const at = names.indexOf(moved);
  if (at >= 0) {
    const above = at > 0 ? names[at - 1] : null;
    const neighbour = above ?? names[at + 1] ?? null;
    if (neighbour && wasPinned.has(neighbour)) pinned.add(moved);
    else pinned.delete(moved);
  }

  // Consoles not on screen keep the places, and the stars, they already had.
  const order = [...names, ...(prefs.libOrder || []).filter((n) => !kept.has(n))];
  const stillPinned = [...names.filter((n) => pinned.has(n)),
                       ...(prefs.libPinned || []).filter((n) => !kept.has(n))];
  savePrefs({ libOrder: order, libPinned: stillPinned });
  renderLibrary();
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
    // The play button only appears where it would work: a console with no
    // emulator set would answer with a dialog explaining that, which is a
    // worse thing to click than nothing at all.
    const canPlay = !!consoleSetup.get(game.console || "")?.emulator;
    slot.innerHTML = `<span class="finst-tick">&#10003;</span>${esc(t("In Library"))}`
      + (canPlay
        ? `<button type="button" class="finst-play" data-play="${esc(game.path)}"
             title="${esc(t("Play"))}" aria-label="${esc(t("Play"))}">
             <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5l11 7-11 7z"/></svg>
           </button>`
        : "");
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
// Consoles this app can fetch a libretro core for, from the server so
// the two lists cannot drift apart.
const coreConsoles = new Set();

async function loadConsoleSetup() {
  try {
    const answer = await fetch("/api/downloads/folders").then((r) => r.json());
    const { consoles } = answer;
    for (const name of answer.coreConsoles || []) coreConsoles.add(name);
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
  repaintDownloads();
}



/** Put a play button on every finished download that has somewhere to go.
 *
 *  Painted on rather than built in, for the same reason the "In Library"
 *  marker is: a download row is drawn as soon as the panel has something to
 *  say, and whether that download can be played depends on the library, which
 *  is read separately and often later. Baking the answer in freezes whichever
 *  was true first. This runs whenever either side changes and simply agrees
 *  with whatever is known now.
 */
function paintDownloadPlay() {
  const jobs = new Map((lastDownloadState?.jobs || []).map((j) => [String(j.id), j]));
  for (const row of document.querySelectorAll(".dljob")) {
    const job = jobs.get(String(row.dataset.id));
    const path = job && job.status === "done" ? jobPlayPath(job) : "";
    const already = row.querySelector(".dj-play");

    if (!path) {
      already?.remove();
      continue;
    }
    if (already) {
      already.dataset.play = path;      // the game may have moved or been renamed
      continue;
    }
    const button = document.createElement("button");
    button.className = "dj-play";
    button.type = "button";
    button.dataset.play = path;
    button.title = t("Play");
    button.innerHTML = "&#9654;";
    // Before the folder button, so the two live together at the same end of
    // the row rather than one drifting off on its own.
    const top = row.querySelector(".dj-top");
    const folder = row.querySelector(".dj-open");
    if (folder) folder.before(button);
    else top?.append(button);
  }
}

/** Draw the downloads again once the library is known.
 *
 *  A finished download only knows it can be played after the library has been
 *  read, and the two land in either order. Cheap, and only when the panel is
 *  actually on screen. */
function repaintDownloads() {
  // Only the buttons, not the rows: the rows are fine, it is the answer about
  // the library that has changed.
  paintDownloadPlay();
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
  repaintDownloads();
  if (libraryOpen) renderLibrary();

  /* Then the folders are read again, in case something else changed while we
     were not looking - but the shelf is only redrawn if that read actually
     found a different set of games. Deleting one game almost never does: the
     page has already taken it off, so the scan comes back agreeing, and
     redrawing on the strength of "the scan finished" was rebuilding every
     tile on screen to change nothing. */
  const before = shelfSignature();
  fetchLibrary()
    .then(() => {
      if (libraryOpen && shelfSignature() !== before) renderLibrary();
    })
    .catch(() => { /* the folders get read again on Refresh */ });
}

/** What the shelf is made of right now, cheaply comparable.
 *
 *  Paths and play time: the first says which games there are, the second is
 *  the only other thing a rescan can change that the shelf actually draws. */
function shelfSignature() {
  return (libraryData?.games || [])
    .map((g) => `${g.path}:${g.playSeconds || 0}`).join(" ");
}

async function loadLibrary() {
  els.libBody.innerHTML = `<p class="empty">Reading your folders…</p>`;
  try {
    await fetchLibrary();
    renderLibrary();
    priceShelfIfNeeded();
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
  const group = consoleOf(game);
  if (isCollapsed(group)) toggleInPref("libShut", group);
  renderLibrary();

  // Paths carry backslashes and brackets, so the lookup inside markFound is a
  // scan rather than an attribute selector - no escaping to get wrong.
  const card = markFound(path);
  if (!card) return;
  card.scrollIntoView({ block: "center", behavior: "smooth" });
}

/* Both play buttons, wherever they are: on a search result that is already in
   the library, and on a download that has finished. Caught here rather than
   on each, so it is one rule and cannot come apart. Stopped before it
   bubbles, since the things underneath it - "show me this in the library",
   the download row itself - are not what was pressed. */
document.addEventListener("click", (ev) => {
  const button = ev.target.closest("[data-play]");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();
  playGame(button.dataset.play);
}, true);

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
  paintMore();
  els.libBtn.classList.toggle("on", on);
  els.searchBtn.classList.toggle("on", !on);
  if (!on) return;
  // The scan may already have run for the search's "In Library" markers, in
  // which case the data is here but was never drawn - so an empty body means
  // render, not rescan.
  if (!libraryData) { loadLibrary(); return; }
  if (!els.libBody.firstElementChild) renderLibrary();
  // The sort is remembered between sessions; the times it needs are not.
  priceShelfIfNeeded();

  /* Then read the folders again behind what is already on screen. Games get
     added and deleted outside the app, and having to remember to press Refresh
     to see your own disk is a poor deal - but so is a blank "Reading your
     folders…" every time you glance at the tab, which is why the cached view
     is shown first and quietly replaced.

     Replaced only if it turns out to be different, though. Coming back to the
     library with nothing changed on disk should leave the shelf exactly as it
     was, not rebuild it. */
  const before = shelfSignature();
  fetchLibrary()
    .then(() => { if (shelfSignature() !== before) renderLibrary(); })
    .catch(() => { /* Refresh still works */ });
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
els.libFoldAll.addEventListener("click", foldAllConsoles);

/* ---------- dragging consoles into the order you want ----------

   The shelf is one long column of sections, so the only question a drag has
   to answer is which section the pointer is currently above and whether it is
   in the top or bottom half of it. The dragged section is moved in the DOM as
   you go, which is both the preview and - once you let go - the answer: the
   new order is simply read back off the page.

   Driven by pointer events rather than by HTML5 drag-and-drop. The native
   kind runs its own nested loop and keeps the wheel to itself: for as long as
   a drag is in progress the page receives no wheel events at all, so the one
   thing you actually want while dragging a shelf to the far end of a long
   library - scrolling to where it is going - cannot be done. Running it
   ourselves costs the handful of lines below and hands the wheel back.

   Only when every console is on screen. With a filter on, the shelf is a
   subset and dragging within it could not describe a whole order. */
const REORDER = ".libgroup[data-reorder]";
const DRAG_SLOP = 5;       // pixels of movement before it counts as a drag

let dragging = null;       // the section being moved, once one is
let dragFrom = null;       // where the pointer went down, until then
let dragPointer = null;
let swallowClick = false;  // the click that ends a drag isn't a click

/* Scrolling to somewhere that isn't on screen yet, two ways: the wheel, and
   holding the pointer near the top or bottom of the window. The second is
   what a file manager does, and it is the only one available while a button
   is held down and the other hand isn't on the wheel. Faster the closer to
   the edge, so a nudge past the boundary creeps and the last few pixels move
   properly. */
const EDGE_BAND = 96;      // how far from an edge the scrolling starts
const EDGE_SPEED = 22;     // pixels per tick once hard against it
const EDGE_TICK = 16;      // roughly a frame

let edgeSpeed = 0;
let edgeTimer = null;
let dragAt = { x: 0, y: 0 };   // the last place the pointer was seen

/** How fast, and which way, for a pointer this far down the window. */
function edgeRate(y) {
  const above = y - EDGE_BAND;                        // past the top edge
  const below = y - (innerHeight - EDGE_BAND);        // ...and the bottom
  if (above < 0) return Math.round(EDGE_SPEED * Math.max(above, -EDGE_BAND) / EDGE_BAND);
  if (below > 0) return Math.round(EDGE_SPEED * Math.min(below, EDGE_BAND) / EDGE_BAND);
  return 0;
}

/* An interval rather than requestAnimationFrame: the two behave the same
   here, and this one keeps running when the window isn't painting, which is
   what makes it something that can be tested rather than assumed. */
function edgeScroll(y) {
  edgeSpeed = edgeRate(y);
  if (edgeSpeed && edgeTimer === null) {
    edgeTimer = setInterval(() => {
      if (!dragging || !edgeSpeed) { edgeStop(); return; }
      scrollBy(0, edgeSpeed);
      placeDragged();     // the page moved under a still pointer
    }, EDGE_TICK);
  }
}

function edgeStop() {
  edgeSpeed = 0;
  if (edgeTimer !== null) clearInterval(edgeTimer);
  edgeTimer = null;
}

/** Put the dragged section wherever the pointer is now pointing.
 *
 *  Read off the page rather than from the event, so that scrolling moves the
 *  section too: the wheel and the edge scroll both change what is under a
 *  pointer that never moved. `.dragging` is taken out of the hit test in the
 *  stylesheet, so this finds the section underneath rather than itself. */
function placeDragged() {
  if (!dragging) return;
  const under = document.elementFromPoint(dragAt.x, dragAt.y);
  const over = under?.closest?.(REORDER);
  if (!over || over === dragging) return;
  const box = over.getBoundingClientRect();
  const before = dragAt.y < box.top + box.height / 2;
  over.parentNode.insertBefore(dragging, before ? over : over.nextSibling);
}

function startDrag(group) {
  dragging = group;
  group.classList.add("dragging");
  document.body.classList.add("libdragging");
}

function endDrag() {
  edgeStop();
  dragFrom = dragPointer = null;
  if (!dragging) return;
  const moved = dragging.dataset.console;
  dragging.classList.remove("dragging");
  document.body.classList.remove("libdragging");
  dragging = null;
  // Letting go after a drag is not a click on whatever is under the pointer.
  // The console name is both a handle and a button, so without this, moving a
  // console would fold it on the way down.
  swallowClick = true;
  applyConsoleOrder([...els.libBody.querySelectorAll(REORDER)]
    .map((g) => g.dataset.console), moved);
}

/* Caught going down, before the button it lands on hears about it, and only
   ever the one click that ends a drag. */
els.libBody.addEventListener("click", (ev) => {
  if (!swallowClick) return;
  swallowClick = false;
  ev.preventDefault();
  ev.stopPropagation();
}, true);

els.libBody.addEventListener("pointerdown", (ev) => {
  /* A new press, so any click still owed from the last drag is out of date.
     Without this the flag waits indefinitely for a click that may never come
     and then eats an unrelated one much later - which is exactly what it did
     the first time round. */
  swallowClick = false;
  if (ev.button !== 0) return;
  const group = ev.target.closest?.(REORDER);
  if (!group) return;
  // Only from the heading. Everything below it is games, where a press is a
  // click on a game and dragging one has never meant anything.
  if (!ev.target.closest(".libhead")) return;
  /* ...and not from the controls sitting in that heading - except the console
     name, which is the obvious thing to take hold of. It is a button, and it
     stays one: a press that never travels still folds the console, because a
     drag only begins once the pointer has moved. What it must not do is both,
     which is what the click swallowed below is for. */
  if (ev.target.closest("button:not(.libname-btn), input, select, a")) return;

  dragFrom = { x: ev.clientX, y: ev.clientY, group };
  dragPointer = ev.pointerId;
  dragAt = { x: ev.clientX, y: ev.clientY };
});

els.libBody.addEventListener("pointermove", (ev) => {
  if (ev.pointerId !== dragPointer) return;
  dragAt = { x: ev.clientX, y: ev.clientY };

  if (!dragging) {
    // Held still, or barely moved: still a click, not a drag.
    if (Math.abs(ev.clientX - dragFrom.x) + Math.abs(ev.clientY - dragFrom.y)
        < DRAG_SLOP) return;
    startDrag(dragFrom.group);
    // From here the gesture belongs to this element however far it strays.
    try { els.libBody.setPointerCapture(dragPointer); } catch { /* gone */ }
  }
  // Stops the press turning into a text selection down the page.
  ev.preventDefault();
  placeDragged();
  edgeScroll(ev.clientY);
});

for (const done of ["pointerup", "pointercancel"]) {
  els.libBody.addEventListener(done, (ev) => {
    if (ev.pointerId !== dragPointer) return;
    try { els.libBody.releasePointerCapture(ev.pointerId); } catch { /* gone */ }
    endDrag();
  });
}

/* The wheel, which is the whole reason this is not an HTML5 drag. Scrolled
   here rather than left to the browser so the section can be re-placed
   afterwards: the pointer hasn't moved, but what is under it has. */
addEventListener("wheel", (ev) => {
  if (!dragging) return;
  ev.preventDefault();
  scrollBy(0, ev.deltaY);
  placeDragged();
}, { passive: false });

// A drag that outlives its window is worse than one that ends early.
addEventListener("blur", endDrag);

for (const [button, mode] of [[els.libGrid, "grid"], [els.libList, "list"]]) {
  button.addEventListener("click", () => {
    savePrefs({ libView: mode });
    renderLibrary();
  });
}

els.wideLayout.addEventListener("change", () => {
  savePrefs({ wideLayout: els.wideLayout.checked });
  document.body.classList.toggle("wide", els.wideLayout.checked);
});

els.indexAutoClose.addEventListener("change", () => {
  savePrefs({ indexAutoClose: els.indexAutoClose.checked });
});

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
  if (els.libSort.value === "beat" || els.libSort.value === "master") {
    priceLibrary();
  }
  paintMasteredToggle();
  renderLibrary();
});

/* "Hide mastered" belongs to the one sort it means anything to, so it appears
   with it and goes away again. Left on screen the rest of the time it would be
   a filter people forget they set, quietly shortening a shelf sorted by name
   for reasons nothing on screen explains. */
function paintMasteredToggle() {
  els.libMasteredWrap.hidden = prefs.libSort !== "earned";
}

els.libMastered.addEventListener("change", () => {
  savePrefs({ libHideMastered: els.libMastered.checked });
  renderLibrary();
});

/* Asking for a time on every tile is asking for a time for every game, which
   is a request per game the first time. Same pricing the sorts use, so a shelf
   already priced for "fastest to beat" shows them instantly. */
els.libTimesPick.addEventListener("change", () => {
  savePrefs({ libTimes: els.libTimesPick.value });
  renderLibrary();
  if (prefs.libTimes !== "off") priceShelfIfNeeded(true);
});

/* What a click on the artwork does. Changing it changes what is drawn - the
   play button only exists where the click no longer plays - so the shelf is
   redrawn rather than left disagreeing with the setting. */
els.libClick.addEventListener("change", () => {
  savePrefs({ libClick: els.libClick.value });
  if (libraryOpen) renderLibrary();
});

els.achOnPlay.addEventListener("change", () => {
  savePrefs({ achOnPlay: els.achOnPlay.value });
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
  // A shelf can hold games the last run never asked about: anything on a
  // playlist that isn't downloaded is not in the library at all.
  priceShelfIfNeeded();
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
    /* Only this heading changes, so only this heading is touched. Redrawing
       the shelf would rebuild every tile on it - including the covers of the
       consoles nobody folded, which then walk their candidate lists again and
       flicker back into place one by one. Nothing about the other groups has
       changed; leaving them alone is both faster and what the eye expects. */
    foldGroupInPlace(fold.closest(".libgroup"), fold.dataset.console);
  }
});

/** Show or hide one console's games, without redrawing anything else. */
function foldGroupInPlace(group, console_) {
  if (!group) return;
  const shut = isCollapsed(console_);
  group.classList.toggle("shut", shut);
  const label = shut ? t("Show these games") : t("Hide these games");
  for (const button of group.querySelectorAll(".libfold, .libname-btn")) {
    button.title = label;
  }
  group.querySelector(".libfold")?.setAttribute("aria-expanded", String(!shut));
  paintFoldAll();
}

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

/* The play button, wherever it is. Before the handler below, and stopping
   there, because that one is about the artwork and this is a control on top of
   it. */
els.libBody.addEventListener("click", (ev) => {
  const button = ev.target.closest(".libplay");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();
  const path = button.closest("[data-path]")?.dataset.path;
  if (path) playGame(path);
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
  /* One click, and what it does is a setting. Playing is the default and what
     this always did; the preview is for people who want to look before they
     start - and in that mode the play button on the tile is what starts it, so
     the game is still one click away rather than two. The folder lives in the
     right-click menu either way, so nothing has to wait to find out whether a
     second click is coming. */
  if (prefs.libClick === "preview") openPreviewFor(card);
  else playGame(path);
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
  openAchievementsBeside(console_, game?.name || "");
}

/* The set, in a window of its own, next to the game that just started.
 *
 * Off unless asked for: it is a second window on every single launch, which is
 * exactly what somebody working through a set wants and an interruption for
 * everybody else. Only for a game RetroAchievements actually has a set for -
 * the id is already known from the shelf being drawn, so a game without one
 * opens nothing rather than a window that says "nothing here".
 *
 * The page is this app's own, served from this app, so it is a window rather
 * than a browser tab regardless of where Settings sends RetroAchievements
 * itself: that setting is about their site, and this is not their site. */
function openAchievementsBeside(console_, name) {
  // Stored as a word now; `true` is what the switch this replaced wrote, and
  // it meant the built-in list.
  const which = prefs.achOnPlay === true ? "app" : (prefs.achOnPlay || "off");
  if (which === "off") return;
  const id = raId(console_, name);
  if (!id) return;

  /* Either goes in a window of the app's own, beside the game. The built-in
     list loads instantly and needs no sign-in; their page is the real thing,
     with the leaderboards and the comments, and the window remembers a
     sign-in between sessions - which is why it is worth offering both rather
     than deciding for everybody. */
  const url = which === "site"
    ? `${RA_PAGE}${id}`
    : `${location.origin}/achievements.html?id=${
        encodeURIComponent(id)}&title=${encodeURIComponent(name)}`;
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title: name || t("Achievements") }),
  }).then((r) => r.json()).then((res) => {
    // No window to be had - `serve` in an ordinary browser - so their page
    // goes to the browser instead. The built-in list is not worth a tab: the
    // app it belongs to is already open in one.
    if (!res.opened && which === "site") {
      fetch("/api/browse/open", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      }).catch(() => { /* nothing else to try */ });
    }
  }).catch(() => { /* no window to be had; the game still started */ });
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
  // Their rows under "Finished" went with them, so the panel is out of date.
  if (res.forgotDownloads) pollDownloads();
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
let menuRa = 0;            // the RetroAchievements page for what was clicked

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
/* Folded groups.
 *
 * A group is a heading and a stack of entries that starts closed. Two rules
 * keep it honest: a group whose entries are all hidden hides itself, so
 * "Patches" never opens onto nothing; and every group is closed again each
 * time a menu opens, so the menu is the same size every time rather than
 * remembering what somebody expanded ten minutes ago. */
function syncMenuGroups(menu) {
  for (const group of menu.querySelectorAll(".menugroup")) {
    const inside = [...group.querySelectorAll(".menusub button")];
    group.hidden = inside.length > 0 && inside.every((b) => b.hidden);
    group.querySelector(".menusub").hidden = true;
    group.querySelector("[data-fold]").setAttribute("aria-expanded", "false");
  }
}

for (const menu of [$("libmenu"), $("covermenu")]) {
  menu.addEventListener("click", (ev) => {
    const fold = ev.target.closest("[data-fold]");
    if (!fold) return;
    // Nothing was chosen, so the menu must not close underneath the pointer.
    ev.stopPropagation();
    const sub = fold.parentElement.querySelector(".menusub");
    const open = sub.hidden;
    sub.hidden = !open;
    fold.setAttribute("aria-expanded", String(open));
    // A menu opened near the bottom of the window grows downwards off it.
    const box = menu.getBoundingClientRect();
    const over = box.bottom - (window.innerHeight - 8);
    if (over > 0) menu.style.top = `${Math.max(8, box.top - over)}px`;
  });
}

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

  // Offered only for games that have a page. Playlist entries are covered
  // too: an entry knows its console and its filename whether or not the
  // game behind it has been downloaded yet.
  menuRa = raId(game?.console || entry?.console || "",
                game?.name || entry?.name || "");
  els.libMenuRa.hidden = !menuRa;
  els.libMenuHash.hidden = !menuRa;   // same answer, same game
  els.libMenuTime.hidden = !menuRa;   // and so is this one
  els.libMenuPatch.hidden = !(raPatches.get(menuRa) || []).length;
  // Applying one needs the game on this machine, and a game the patcher can
  // actually rewrite - a disc image is not one.
  const hasPatch = !!(raPatches.get(menuRa) || []).length;
  // Judged by the file rather than the console: a raw disc image patches
  // like anything else, a .chd cannot. An entry stored as a folder has no
  // extension to go on, so it is offered and the server decides.
  const ext = (game?.ext || "").toLowerCase();
  const canDoItHere = !ext || patchExts_.size === 0 || patchExts_.has(ext);
  els.libMenuApply.hidden = !here || !hasPatch || !canDoItHere;
  // Where this app cannot do it, say where it can be done instead, rather
  // than leaving a game with a patch and no way to use it.
  els.libMenuWeb.hidden = !here || !hasPatch || canDoItHere;
  els.libMenuTool.hidden = !here;
  els.libMenuEmu.hidden = !here;
  // Only a game the library read a disc number out of.
  els.libMenuM3u.hidden = !here || !game?.disc;

  syncMenuGroups(els.libMenu);
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
  !!url && (url.startsWith(THUMB_BASE) || url.startsWith("/covers/")
            || url.startsWith("/api/cover?"));

/** The src of an image only if it is box art. */
function coverSrc(img) {
  const raw = img?.tagName === "IMG" ? img.getAttribute("src") || "" : "";
  return isCoverUrl(raw) ? raw : "";
}

/** The thumbnail server names its files the way emulators expect them, so
 *  its own name is the right suggestion. Covers the user supplied are stored
 *  under a hash, so those fall back to the game's name. */
function coverFileName(url, fallback = "cover") {
  // The resolved-cover URL is a query, not a path: its last segment is the
  // word "cover", which would save every game's art under the same name.
  if (url.startsWith("/api/cover?")) return `${fallback}.png`;
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

/* ---------- a cover at full size ----------

   Every cover on these pages is drawn small: a grid of them is the point, and
   the picture behind each one is several times the size of the square it sits
   in. Clicking opens that picture instead of the copy the browser squeezed
   down for the grid, with the save entry repeated underneath - the right-click
   menu is still there for anyone who never opens it, but a menu is a poor way
   to offer something to a person who is looking at a picture.

   Which covers: the ones on the search page, the download list and the
   downloads panel. Not the library, where a click already means play. */
const BIG_COVERS = ".coverbox img, .conart img, .ci-art img, .dj-art img";

let bigCoverUrl = "";
let bigCoverConsole = "";
/* One picture or several. A cover opens alone, as it always did; the preview
   panel's screenshots open as a set you can walk through. Saving is offered
   for the first case only - "Save cover image" is the wrong offer to make
   about the fourth screenshot of a game. */
let gallery = [];
let galleryAt = 0;
let gallerySavable = true;

function showGalleryAt(index) {
  galleryAt = Math.max(0, Math.min(index, gallery.length - 1));
  bigCoverUrl = gallery[galleryAt] || "";
  // Cleared before it is set, rather than on the way out. A picture that is
  // still downloading draws the last one until it arrives, so moving to the
  // next would show the previous one for as long as the wait.
  els.coverBig.removeAttribute("src");
  els.coverBig.src = bigCoverUrl;

  const many = gallery.length > 1;
  els.coverPrev.hidden = !many;
  els.coverNext.hidden = !many;
  els.coverPrev.disabled = galleryAt === 0;
  els.coverNext.disabled = galleryAt === gallery.length - 1;
  els.coverCount.textContent = many
    ? t("{n} of {total}", { n: galleryAt + 1, total: gallery.length }) : "";
  els.coverBigSave.hidden = !gallerySavable;
}

function openCoverView(url, console_) {
  gallery = [url];
  gallerySavable = true;
  bigCoverConsole = console_ || "";
  showGalleryAt(0);
  els.coverDlg.showModal();
}

/** A set of pictures, opened at the one that was clicked. */
function openGallery(urls, index) {
  gallery = urls.filter(Boolean);
  if (!gallery.length) return;
  gallerySavable = false;
  showGalleryAt(index);
  els.coverDlg.showModal();
}

const stepGallery = (by) => showGalleryAt(galleryAt + by);
els.coverPrev.addEventListener("click", () => stepGallery(-1));
els.coverNext.addEventListener("click", () => stepGallery(1));
/* Arrow keys, because a set of pictures with buttons either side is a thing
   people try to page with the keyboard. Only while this dialog is the one on
   top - Escape already closes it, and every other key belongs to whatever is
   underneath. */
document.addEventListener("keydown", (ev) => {
  if (!els.coverDlg.open || gallery.length < 2) return;
  if (ev.key === "ArrowLeft") { ev.preventDefault(); stepGallery(-1); }
  if (ev.key === "ArrowRight") { ev.preventDefault(); stepGallery(1); }
});

document.addEventListener("click", (ev) => {
  const img = ev.target.closest?.(BIG_COVERS);
  if (!img) return;
  const url = coverSrc(img);
  if (!url) return;
  // A cover in a search result sits inside the card's <summary>, where a
  // click would fold the card open or shut underneath the picture.
  ev.preventDefault();
  closeMenus();
  /* The picture on its own was all there was to show when this was written.
     Now there is a panel for the game, and the picture is one part of it - so
     a cover that can be traced back to a game opens that, and one that cannot
     still opens the way it always did. */
  const about = previewNear(img);
  if (about) openPreview({ ...about, cover: url });
  else openCoverView(url, coverConsole(img));
});

els.coverBigSave.addEventListener("click", () => {
  if (bigCoverUrl) saveCover(bigCoverUrl, coverFileName(bigCoverUrl), bigCoverConsole);
});
els.coverBigClose.addEventListener("click", () => els.coverDlg.close());
els.coverDlg.addEventListener("click", (ev) => {
  if (ev.target === els.coverDlg) els.coverDlg.close();
});
// Stops the picture downloading if it is shut before it finished.
els.coverDlg.addEventListener("close", () => els.coverBig.removeAttribute("src"));

/* Everywhere except the library, which offers both of these on its own menu.
   Two things can be on offer and either can be absent, so what opens is
   whatever applies: the cover entry wherever there is artwork under the
   pointer, the RetroAchievements one anywhere on a row for a game that has a
   page. With neither, no menu opens and the right-click does nothing, which
   is what it did before any of this existed. */
document.addEventListener("contextmenu", (ev) => {
  if (ev.target.closest("#libbody")) return;
  const url = coverSrc(ev.target);
  const ra = raIdNear(ev.target);
  if (!url && !ra) return;
  ev.preventDefault();
  menuCover = url;
  menuConsole = url ? coverConsole(ev.target) : "";
  menuRa = ra;
  els.coverMenuSave.hidden = !url;
  els.coverMenuRa.hidden = !ra;
  els.coverMenuHash.hidden = !ra;
  els.coverMenuTime.hidden = !ra;
  els.coverMenuPatch.hidden = !(raPatches.get(ra) || []).length;
  // Only ever offered on the profile strip, which has its own handler.
  els.coverMenuProfile.hidden = true;
  syncMenuGroups(els.coverMenu);
  openMenu(els.coverMenu, ev);
});

els.coverMenu.addEventListener("click", (ev) => {
  const action = ev.target.closest("button")?.dataset.act;
  if (!action) return;
  const url = menuCover;
  const console_ = menuConsole;
  const ra = menuRa;
  closeMenus();
  if (action === "ra") {
    if (ra) openRa(ra);
  } else if (action === "howlong") {
    if (ra) showHowLong(ra);
  } else if (action === "rahash") {
    if (ra) openRaHashes(ra);
  } else if (action === "rapatch") {
    chooseRaPatch(ra).then((chosen) => downloadPatch(chosen));
  } else if (action === "profile") {
    // Their site, not this app's rendering of it - so it goes wherever
    // Settings sends RetroAchievements pages.
    if (raMe?.url) openWeb(raMe.url, raMe.user || t("Profile"));
  } else if (url) {
    saveCover(url, coverFileName(url), console_);
  }
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
  const ra = menuRa;
  const game = gameAt(path);
  const pl = currentPlaylist();
  // Read before the menu closes, since closing is what forgets which card
  // this was about.
  const entry = pl?.items.find((i) => i.key === key)
    || (game ? entryFromGame(game) : null);
  closeLibMenu();

  if (action === "ra") {
    if (ra) openRa(ra);
    return;
  }
  if (action === "howlong") {
    if (ra) showHowLong(ra, game?.name || "");
    return;
  }
  if (action === "rahash") {
    if (ra) openRaHashes(ra);
    return;
  }
  if (action === "rapatch") {
    chooseRaPatch(ra).then((url) => downloadPatch(url));
    return;
  }
  if (action === "applypatch") {
    chooseRaPatch(ra).then((url) => url && applyPatch(path, url));
    return;
  }
  if (action === "gameemu") {
    openGameEmulator(path, game?.name || "");
    return;
  }
  if (action === "m3u") {
    const made = await fetch("/api/library/m3u", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    }).then((r) => r.json()).catch(() => null);
    await say(made?.ok
      ? t("Made \"{name}\", listing {n} discs.\n\nPoint your emulator at that "
          + "file instead of a single disc and it can swap them itself.",
          { name: made.name, n: made.discs.length })
      : (made?.error || t("Could not make the playlist.")));
    if (made?.ok) loadLibrary();
    return;
  }
  if (action === "patchtool") {
    openPatchTool(path);      // the game is known; only the patch is not
    return;
  }
  if (action === "patchweb") {
    // The patch is fetched too, so both halves are to hand: the page needs
    // the ROM and the patch, and hunting for the patch again would be the
    // tedious part.
    // Saved first, so the file is already waiting by the time the page it
    // has to be fed to is on screen.
    await downloadPatch(await chooseRaPatch(ra));
    openWeb(WEB_PATCHER, t("Patch a game online"));
    return;
  }
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
      if (consoleOf(g) === consoleOf({ console: key })) libSelected.add(g.path);
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
    if (res.forgotDownloads) pollDownloads();
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

function folderRow(entry, pickable = false) {
  // The effective path is the placeholder, so you can always see where a
  // console will land even without an override set.
  const hint = shortPath(entry.effective, folderState.base);
  // Both cover toggles are meaningless without somewhere to keep the images,
  // so they follow the cover folder rather than standing on their own.
  const noCover = entry.cover ? "" : " disabled";
  /* The name is part of the tick, not a heading sitting next to one. A row of
     thirty-six consoles is picked from by reading names, and having to land
     on a 15-pixel box beside the name you just read is the sort of aim nobody
     should be asked for. */
  const heading = pickable
    ? `<label class="fr-picker" title="${esc(t("Select this console"))}">
         <input type="checkbox" class="fr-pick">
         <span class="fr-title">${esc(entry.console)}</span></label>`
    : `<span class="fr-title">${esc(entry.console)}</span>`;
  return `
    <div class="folderrow" data-console="${esc(entry.console)}">
      <h4 class="fr-name">${heading}</h4>

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
        ${coreConsoles.has(entry.console) ? `<button class="fr-coreget ghost small"
               title="${esc(t("Download the best core for this console and use it"))}"
               >${esc(t("Get"))}</button>` : ""}
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

/* Which consoles are ticked in the every-console window. Deliberately not
   remembered once that window closes: a selection you cannot see is one you
   will act on by accident. */
const consPicked = new Set();

/* The machines whose own emulator is the better answer, even though RetroArch
   will happily run them.
 *
 * The server already refuses to recommend a core for the GameCube, the Wii and
 * the PlayStation 2 - see cores.NO_CORE - so those never reach this list. The
 * two that do are Sony's handheld and its first console, where the cores are
 * genuinely good and plenty of people still keep PPSSPP and DuckStation
 * separately. They are left out of the one-press selection and can still be
 * ticked by hand, which is the right way round for a shortcut: it should do
 * the obvious thing, not every thing. */
const OWN_EMULATOR_BETTER = new Set([
  "PlayStation", "PlayStation 2", "PSP", "GameCube", "Nintendo Wii",
]);

/** Everything RetroArch is the right answer for, out of what is on screen. */
const retroarchConsoles = () => (folderState.consoles || [])
  .map((c) => c.console)
  .filter((name) => coreConsoles.has(name) && !OWN_EMULATOR_BETTER.has(name));

/* Console rows exist in two places now - the one under the dropdown, and all
   of them in the window - and every handler below has to work in either. */
const folderRows = () => [
  ...els.folderList.querySelectorAll(".folderrow"),
  ...els.consAllGrid.querySelectorAll(".folderrow"),
];

function paintConsBulk() {
  const n = consPicked.size;
  els.consBulk.hidden = !n;
  if (n) {
    els.consBulkCount.textContent = t("{n} consoles selected", { n });
  }
  for (const row of folderRows()) {
    const box = row.querySelector(".fr-pick");
    if (box) box.checked = consPicked.has(row.dataset.console);
    row.classList.toggle("picked", consPicked.has(row.dataset.console));
  }
}

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
  els.consClear.hidden = !folderConsole;
  els.consBtn.insertAdjacentHTML("beforeend", '<span class="fcaret">&#9662;</span>');

  els.consItems.innerHTML = shown.length
    ? shown.map((c) => `<button class="fitem consitem${
        c.console === folderConsole ? " on" : ""}" data-console="${esc(c.console)}">
        <span class="mlabel">${esc(c.console)}</span>${
        configured(c) ? '<span class="consdone">&#10003;</span>' : ""}</button>`).join("")
    : `<div class="fempty">${esc(t("No matches"))}</div>`;

  const entry = folderEntry(folderConsole);
  els.folderList.innerHTML = entry ? folderRow(entry) : "";

  // The window, if it is open. Configured consoles first: they are the ones
  // you come back to, and thirty-six untouched ones above them is a long
  // scroll to reach the two you actually use.
  if (els.consAllDlg.open) {
    els.consAllBase.textContent = folderState.base;
    const rows = [...folderState.consoles].sort(
      (a, b) => (configured(b) ? 1 : 0) - (configured(a) ? 1 : 0)
        || a.console.localeCompare(b.console));
    els.consAllGrid.innerHTML = rows.map((c) => folderRow(c, true)).join("");
  }

  applyLanguage(prefs.lang);
  paintConsBulk();
}


async function loadFolders() {
  try {
    folderState = await fetch("/api/downloads/folders").then((r) => r.json());
    for (const name of folderState.coreConsoles || []) coreConsoles.add(name);
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
  // The library's own gear: how the shelf behaves, and then the paths it
  // plays from. Its own settings first - they are what the gear on that panel
  // is being pressed for - with the per-console paths under them because that
  // is where the emulators are set.
  consoles: ["setlibrary", "setconsoles"],
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
  // The shelf's own behaviour, and the paths it plays from. The same pair the
  // library's gear opens, so the two ways in agree about what "library
  // settings" means.
  library: ["setlibrary", "setconsoles"],
  paths: ["setcart", "setdownloads", "setconsoles"],
  art: ["setart"],
  web: ["setweb"],
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
  // Which tab is showing, so the box can be as tall as that tab needs and no
  // taller. Blank while a panel's own gear is driving it - there are no tabs
  // then, and the scope decides the size instead.
  els.settingsDlg.dataset.tab = scope ? "" : settingsTab;
}

let settingsScope = "";

async function openSettings(scope = "") {
  settingsScope = scope;
  paintSettings(scope);
  // Which scope opened it, so the box can be sized for what is actually in
  // it: the tall shape is for the tabbed view, and a panel's own gear that
  // shows one switch has no use for it.
  els.settingsDlg.dataset.scope = scope;
  els.settingsDlg.showModal();
  els.settingsDlg.scrollTop = 0;
  await Promise.all([loadDownloadSettings(), loadFolders(), loadArtwork()]);
}

els.setTabs.addEventListener("click", (ev) => {
  const tab = ev.target.closest("button")?.dataset.tab;
  if (!tab || !(tab in SETTINGS_TABS)) return;
  settingsTab = tab;
  paintSettings(settingsScope);
  // A tab is a fresh page, not a place in the one you were reading.
  els.settingsDlg.scrollTop = 0;
});

// The site itself, rather than a particular game's page on it. Same two
// destinations as every other RetroAchievements link in the app, so it lands
// in the window the user is already signed in to.
els.raBtn.addEventListener("click", () => openWeb(RA_HOME));
els.webPatchBtn.addEventListener("click", () => openPatchTool());

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

/* Bound to both places a console row can live: the one under the dropdown,
   and every one of them in the window. */
function wireFolderRows(host) {
  host.addEventListener("click", async (ev) => {
  const row = ev.target.closest(".folderrow");
  if (!row) return;

  // Fetch the core for this console and fill the box in. Handled before the
  // columns below because it is the only button here that goes and gets
  // something rather than opening a picker.
  const get = ev.target.closest(".fr-coreget");
  if (get) {
    const console_ = row.dataset.console || "";
    const label = get.textContent;
    get.disabled = true;
    get.textContent = t("Getting…");
    let res;
    try {
      res = await fetch("/api/cores/install", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ console: console_ }),
      }).then((r) => r.json());
    } catch {
      res = { error: "Could not reach the local server." };
    }
    get.textContent = label;
    get.disabled = false;

    if (res.error) { await say(t(res.error)); return; }
    row.querySelector(".fr-emucore").value = res.path;
    await saveFolders(false);
    await loadFolders();
    toast(res.installed
      ? t("Installed {core} and set it for {console}.",
          { core: res.core, console: console_ })
      : t("{core} was already installed. Set it for {console}.",
          { core: res.core, console: console_ }));
    return;
  }

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
  host.addEventListener("input", debounce(async (ev) => {
    if (!ev.target.closest(
      ".fr-path, .fr-cover, .fr-emu, .fr-emucore, .fr-emuargs")) return;
    await saveFolders(false);
  }, 800));

  /* A tick is a decision, not a phrase being typed, so it saves at once
     rather than 800ms later - long enough for the window to be closed in
     between. */
  host.addEventListener("change", async (ev) => {
    if (!ev.target.closest(".fr-coverauto, .fr-coverdelete")) return;
    await saveFolders(false);
  });

  // ...and the tick that puts a console into a bulk change.
  host.addEventListener("change", (ev) => {
    const box = ev.target.closest(".fr-pick");
    if (!box) return;
    const name = box.closest(".folderrow").dataset.console;
    if (box.checked) consPicked.add(name); else consPicked.delete(name);
    paintConsBulk();
  });
}

wireFolderRows(els.folderList);
wireFolderRows(els.consAllGrid);

/* ---------- the console picker ---------- */
/* Where this menu will actually fit.

   The stylesheet hangs it under the button and gives the list inside a fixed
   340px, which is right until the button is near the bottom of the window -
   and in Paths it usually is, because the dialog is tall and the button sits
   below a paragraph of explanation. Then most of the menu is off-screen: the
   list scrolls, but only a sliver of it is on the glass to scroll.

   So it is measured. If there is not enough room under the button it opens
   upwards instead, and either way the list is capped to what is left, which
   is what its own scrollbar is for. */
const CONS_GAP = 6;        // the offset the stylesheet uses
const CONS_EDGE = 12;      // never flush against the window edge
const CONS_MIN = 160;      // less room than this below and it is worth flipping
const CONS_FLOOR = 90;     // ...but never so short it shows one entry

function placeConsoleMenu() {
  const menu = els.consMenu;
  const list = els.consItems;
  // Back to what the stylesheet says first, so the last opening has no say in
  // this one - the button moves as the dialog scrolls.
  menu.style.top = "";
  menu.style.bottom = "";
  list.style.maxHeight = "";

  const anchor = els.consBtn.getBoundingClientRect();
  // The search box and the padding around the list: whatever the menu is
  // taller than its own list by.
  const chrome = menu.offsetHeight - list.offsetHeight;
  const below = innerHeight - anchor.bottom - CONS_GAP - CONS_EDGE;
  const above = anchor.top - CONS_GAP - CONS_EDGE;

  const flip = below < CONS_MIN && above > below;
  if (flip) {
    menu.style.top = "auto";
    menu.style.bottom = `calc(100% + ${CONS_GAP}px)`;
  }
  list.style.maxHeight = `${Math.max((flip ? above : below) - chrome, CONS_FLOOR)}px`;
}

function openConsoleMenu(on) {
  els.consMenu.hidden = !on;
  els.consBtn.setAttribute("aria-expanded", String(on));
  if (!on) return;
  placeConsoleMenu();
  // Straight into the box: opening this menu is nearly always the first half
  // of typing a name.
  els.consSearch.focus();
  els.consSearch.select();
}

els.consBtn.addEventListener("click", (ev) => {
  ev.stopPropagation();
  openConsoleMenu(els.consMenu.hidden);
});

/* The dialog scrolls underneath, and the menu is pinned to the button, so it
   travels with it - far enough and it ends up above the top of the window
   instead of below the bottom. So it is placed again as that happens, and
   shut once the button has left the screen altogether: a menu hanging off a
   control nobody can see any more is not one anyone meant to leave open. */
els.settingsDlg.addEventListener("scroll", () => {
  if (els.consMenu.hidden) return;
  const anchor = els.consBtn.getBoundingClientRect();
  if (anchor.bottom < 0 || anchor.top > innerHeight) {
    openConsoleMenu(false);
    return;
  }
  placeConsoleMenu();
});

els.consClear.addEventListener("click", (ev) => {
  ev.stopPropagation();
  folderConsole = "";
  els.consSearch.value = "";
  openConsoleMenu(false);
  renderFolders();
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

/* ---------- one console, or all of them ---------- */

els.consModeAll.addEventListener("click", () => {
  openConsoleMenu(false);
  consPicked.clear();
  els.consAllDlg.showModal();
  renderFolders();               // fills the grid now that the window is open
  els.consAllGrid.scrollTop = 0;
});

/* Nothing is lost on the way out - every box in there saves itself as it is
   changed - so closing just empties the grid and drops the ticks. The panel
   behind is redrawn because a path set in the window changes the ✓ marks in
   the dropdown. */
els.consAllDlg.addEventListener("close", () => {
  consPicked.clear();
  els.consAllGrid.innerHTML = "";
  els.consRetroNote.textContent = "";
  paintConsBulk();
  renderFolders();
});

els.consBulkNone.addEventListener("click", () => {
  consPicked.clear();
  paintConsBulk();
});

/* One press for the selection this window is mostly opened to make. Ticks
   rather than acts: what happens to them - one emulator path, then Get cores -
   is still the two buttons in the bar, and the two consoles left out are still
   there to be ticked by hand. Pressed again with the same set already ticked,
   it clears them, so it is a switch rather than a one-way door. */
els.consRetroarch.addEventListener("click", () => {
  const wanted = retroarchConsoles();
  if (!wanted.length) {
    els.consRetroNote.textContent =
      t("No consoles here have a core to recommend.");
    return;
  }
  const already = wanted.every((name) => consPicked.has(name));
  for (const name of wanted) {
    if (already) consPicked.delete(name); else consPicked.add(name);
  }
  els.consRetroNote.textContent = already ? "" : t(
    "{n} ticked. Sony's machines, the GameCube and the Wii are left out — "
    + "their own emulators are better. Tick those by hand if you want them.",
    { n: wanted.length });
  paintConsBulk();
});

/* Pick the program once and write it to every ticked console. This is the
   reason the all-consoles view exists: one RetroArch runs a dozen systems,
   and setting it a dozen times through a dropdown is the sort of task people
   give up halfway through and end up with half a library that won't launch. */
async function bulkSetPath(kind) {
  const names = [...consPicked];
  if (!names.length) return;

  const button = kind === "core" ? els.consBulkCore : els.consBulkEmu;
  const label = button.textContent;
  button.disabled = true;
  button.textContent = t("Choosing…");
  let chosen = "";
  try {
    const res = await fetch("/api/downloads/browse-exe", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind: kind === "core" ? "core" : undefined }),
    }).then((r) => r.json());
    chosen = res.file || "";
  } catch { /* leave everything as it was */ }
  button.textContent = label;
  button.disabled = false;
  if (!chosen) return;

  /* Written into the boxes on screen, not into our copy of the settings.
     saveFolders() reads the rows back before it sends anything - so setting
     the values in memory here would be overwritten by the empty inputs a
     moment later, which is exactly what happened the first time. */
  const field = kind === "core" ? ".fr-emucore" : ".fr-emu";
  for (const name of names) {
    const row = folderRows().find((r) => r.dataset.console === name);
    const input = row?.querySelector(field);
    if (input) input.value = chosen;
  }
  await saveFolders(false);
  await loadFolders();
  toast(kind === "core"
    ? t("Core set for {n} consoles.", { n: names.length })
    : t("Emulator set for {n} consoles.", { n: names.length }));
}


/** Fetch the right core for every ticked console.
 *
 *  One at a time rather than all at once: these come from someone else's
 *  build server, and a dozen simultaneous downloads is a rude way to ask.
 *  A console with no RetroArch set, or none worth recommending, is counted
 *  and reported at the end rather than interrupting the run.
 */
async function bulkGetCores() {
  const names = [...consPicked];
  if (!names.length) return;

  const button = els.consBulkGetCores;
  const label = button.textContent;
  button.disabled = true;

  let got = 0, already = 0;
  const refused = [];
  for (const [n, name] of names.entries()) {
    button.textContent = t("Getting {n} of {total}…", { n: n + 1, total: names.length });
    let res;
    try {
      res = await fetch("/api/cores/install", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ console: name }),
      }).then((r) => r.json());
    } catch {
      res = { error: "Could not reach the local server." };
    }
    if (res.error) { refused.push(name); continue; }
    if (res.installed) got++; else already++;
    // Into the box on screen, not our copy of the settings - saveFolders
    // reads the rows back, so anything written elsewhere would be lost.
    const row = folderRows().find((r) => r.dataset.console === name);
    const input = row?.querySelector(".fr-emucore");
    if (input) input.value = res.path;
  }

  button.textContent = label;
  button.disabled = false;
  await saveFolders(false);
  await loadFolders();

  toast(t("{got} downloaded, {already} already there, {skipped} skipped.",
          { got, already, skipped: refused.length }));
  if (refused.length) {
    await say(t("These were left alone, because RomSrx has no core to "
                + "recommend for them or RetroArch is not set as their "
                + "emulator:\n\n{list}", { list: refused.join(", ") }));
  }
}

els.consBulkGetCores.addEventListener("click", bulkGetCores);

els.consBulkEmu.addEventListener("click", () => bulkSetPath("emulator"));
els.consBulkCore.addEventListener("click", () => bulkSetPath("core"));

/** Fold what is on screen back into our copy of every console's settings.
 *
 *  Load-bearing now that only one console is shown at a time. The server
 *  replaces each of these maps wholesale, so building them from the visible
 *  rows - which is what this did when every console had a row - would send a
 *  map containing one console and wipe the settings of all the others. The
 *  page's own copy is the full picture; the row on screen only updates its
 *  own entry in it. */
/* Every row on screen, not just the first: the every-console window has all
   thirty-six of them up at once, and reading only the top one would quietly
   throw away anything typed into any of the others. */
function readFolderRow() {
  for (const row of folderRows()) {
    const entry = folderEntry(row.dataset.console);
    if (!entry) continue;

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

/* The same job, offered where the problem is visible. Someone looking at
   "8 files aren't in any console's folder" should not have to be told that
   the cure lives behind a gear, three groups down a settings dialog. */
els.libStrayFix.addEventListener("click", () => els.foldersDetect.click());

/* Remembers how many were being complained about, not just that it was shut:
   the note has done its job for these files, but a folder full of new ones
   later is worth mentioning again. */
els.libStrayHide.addEventListener("click", () => {
  savePrefs({ strayHidden: libraryData?.unplaced || 0 });
  els.libStray.hidden = true;
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
  // Straight to the server: reading the rows back first would put the values
  // still sitting in the boxes on screen back over what was just cleared.
  els.folderList.innerHTML = "";
  els.consAllGrid.innerHTML = "";
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
      ? t("Session stored at {path}", { path: state.config })
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

  // Left open long enough to see it say Done, rather than vanishing the
  // instant the last source lands - which reads as the window closing on
  // its own for no reason anyone saw.
  if (els.indexAutoClose.checked && els.dlg.open) {
    setTimeout(() => {
      if (!indexing && els.dlg.open) els.dlg.close();
    }, 1200);
  }
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
  // The width option lives here because it is part of how the app looks, and
  // because this already runs both on load and whenever it changes.
  document.body.classList.toggle("wide", !!prefs.wideLayout);
  els.wideLayout.checked = !!prefs.wideLayout;
  els.indexAutoClose.checked = !!prefs.indexAutoClose;
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
// `data-i18n` rather than t() at build time: this runs once, and the language
// can be changed afterwards without the page reloading. Marked up, the name
// on a swatch is re-read along with every other string in the app.
els.accentRow.innerHTML = ACCENTS.map(([value, label]) => `
  <button class="swatch" data-accent="${value}" title="${label}" data-i18n
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
  await Promise.all([loadPrefs(), loadCoverMode()]);
  // Language first: everything drawn after this should already be in it.
  applyLanguage(prefs.lang);
  paintLanguagePicker();
  applyTheme();
  applyWide();
  paintMute();
  els.libTitles.checked = prefs.libTitles;
  els.libSize.value = String(prefs.libSize);
  els.libSort.value = prefs.libSort;
  els.libMastered.checked = !!prefs.libHideMastered;
  els.libTimesPick.value = prefs.libTimes || "off";
  els.libClick.value = prefs.libClick || "play";
  els.achOnPlay.value = prefs.achOnPlay === true ? "app" : (prefs.achOnPlay || "off");
  paintMasteredToggle();
  els.cartSort.value = prefs.cartSort;
  applyCompact(prefs.cartCompact);
  await Promise.all([loadCart(), loadPlaylists(), loadRecent()]);
  paintAddButtons();     // the first search may have drawn before these landed
  /* Who is signed in to RetroAchievements, last: it is the one thing in the
     header that needs their servers, and nothing else waits on it. Then on a
     quiet timer, because it says what you are playing. */
  loadRaMe();
  setInterval(() => loadRaMe(true), RA_ME_EVERY);
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
  .replace(/\*\*(.+?)\*\*/g, "$1")
  /* The notes use <sub> to push the explanations into the background on
     GitHub, where they are rendered. Here they are read as plain text, so the
     tags would otherwise be shown as words. */
  .replace(/<\/?[a-z][^>]*>/gi, "")
  // A headline and its explanation are two lines there and one sentence here.
  .replace(/\n{3,}/g, "\n\n");

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
/** Close this copy of the app and start another.
 *
 *  The page goes quiet either way: if it worked, the server it is talking to
 *  is about to stop. So the last thing shown is a note that this is expected,
 *  rather than the connection error that follows on its own. */
async function restartApp() {
  let res = {};
  try {
    res = await fetch("/api/restart", { method: "POST" }).then((r) => r.json());
  } catch {
    // The server can stop before the answer arrives, which means it worked.
    res = { restarting: true };
  }
  if (res.error) {
    await say(t(res.error));
    return;
  }
  toast(t("Restarting…"));
}

async function runBackup(button, route, busyText, body = null) {
  const label = button.textContent;
  button.disabled = true;
  button.textContent = busyText;
  try {
    const res = await fetch(route, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    }).then((r) => r.json());
    if (res.cancelled) { /* they closed the picker; say nothing */ }
    else if (res.error) await say(res.error);
    else if (route === "/api/backup") {
      await say(t("Backup saved to {path}\n\n{n} items.",
                  { path: res.path, n: res.files }));
    } else {
      // Offered as a button rather than left as an instruction. Not offered
      // at all when this is being read in a browser, where restarting would
      // pull the server out from under the page saying so.
      const message = t("Restored {n} items.\n\nRomSrx needs to be restarted "
                        + "for all of it to take effect.", { n: res.files });
      if (!res.canRestart) {
        await say(message);
      } else if (await ask(message, { confirm: true, ok: t("Restart now"),
                                      cancel: t("Later") })) {
        await restartApp();
      }
    }
  } catch {
    await say(t("Could not reach the app."));
  }
  button.textContent = label;
  button.disabled = false;
}

/* Asked before the file picker rather than after: choosing what goes in is
   part of deciding to make a backup, and being asked afterwards - with the
   filename already typed - reads as the app changing its mind. */
/* How much there is to back up, beside the tick box. Asked for when the window
   opens rather than kept up to date: it means walking three emulators' folders,
   and the answer only matters at the moment somebody is deciding. */
async function showSaveSize() {
  els.backupSaves.textContent = "";
  try {
    const found = await fetch("/api/saves").then((r) => r.json());
    if (!found.files) {
      els.backupSaves.textContent = t("none found");
      return;
    }
    els.backupSaves.textContent = t("{n} files, {size}",
      { n: found.files.toLocaleString(), size: humanSize(found.bytes) });
  } catch { /* the tick box works without a number beside it */ }
}

/* What was ticked last time.
 *
 * Kept as the parts left *out*, which is what makes an empty stored value mean
 * "everything", the same thing the window has always opened with. Written the
 * moment a box is touched rather than when the backup runs: somebody who
 * unticks the download queue, thinks better of it and closes the window has
 * still said what they want the next time they open it, and being asked the
 * same question again every session is the complaint this fixes. */
function paintBackupParts() {
  // Never touched: the markup already says what a first backup should be, and
  // that is not "everything" - the search index starts unticked because it is
  // by far the largest thing here and the one part that rebuilds itself.
  if (!prefs.backupSkip) return;
  const skip = new Set(prefs.backupSkip);
  for (const box of els.backupList.querySelectorAll("input[data-part]")) {
    box.checked = !skip.has(box.dataset.part);
  }
}

function saveBackupParts() {
  savePrefs({
    backupSkip: [...els.backupList.querySelectorAll("input[data-part]")]
      .filter((box) => !box.checked).map((box) => box.dataset.part),
  });
}

els.backupList.addEventListener("change", saveBackupParts);

els.backupSave.addEventListener("click", () => {
  paintBackupParts();
  els.backupDlg.showModal();
  showSaveSize();
});

els.backupAll.addEventListener("click", () => {
  for (const box of els.backupList.querySelectorAll("input")) box.checked = true;
  saveBackupParts();
});

els.backupCancel.addEventListener("click", () => els.backupDlg.close());

els.backupGo.addEventListener("click", async () => {
  const parts = [...els.backupList.querySelectorAll("input:checked")]
    .map((box) => box.dataset.part);
  if (!parts.length) {
    await say(t("Tick at least one thing to back up."));
    return;
  }
  els.backupDlg.close();
  await runBackup(els.backupSave, "/api/backup", t("Choosing…"), { parts });
});

els.backupLoad.addEventListener("click", async () => {
  // Restoring replaces what is here now, which is worth one question.
  const go = await ask(
    t("Restore from a backup?\n\nYour current settings, download list and "
      + "playlists on this machine are replaced by the ones in the file."),
    { confirm: true, ok: t("Restore") });
  if (go) await runBackup(els.backupLoad, "/api/restore", t("Choosing…"));
});

