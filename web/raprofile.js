/* The profile window. One request to this app, which makes several to
   RetroAchievements on its behalf - see profile.py - so this page waits once
   and then draws everything it has.

   Every row here is a link to the real page for that thing: a game to its
   game page, a person to their profile, an award to the game it was won in.
   They are opened by asking the app, which sends them wherever Settings says
   RetroAchievements pages should go - a window of its own, or the browser the
   user already has. */

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[c]);

// Awards are the one list that can run to hundreds. A screenful, then a
// button - the same deal the recommendations get, and for the same reason.
const AWARDS_AT_ONCE = 24;

let found = null;
let awardsShown = AWARDS_AT_ONCE;
let awardTab = "mastered";      // the first tab, and the one people open this for
let prefs = {};

/* Which blocks are shown in which order, and whether the awards are pictures
   alone. Kept with the app's other preferences, so the arrangement survives
   the window being shut - the whole point of arranging it. */
const SECTIONS = ["recent", "awards", "following", "ranking"];

const savePref = (changes) => {
  Object.assign(prefs, changes);
  fetch("/api/prefs", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  }).catch(() => { /* a lost preference is not worth an error */ });
};

const day = (text) => {
  const at = Date.parse(text || "");
  return Number.isNaN(at) ? "" : new Date(at).toLocaleDateString();
};

/** How long ago something was, in the roughest terms that are still useful:
 *  "now" and "3 days ago" are both better answers than a timestamp. */
function ago(text) {
  const at = Date.parse((text || "").replace(" ", "T") + "Z");
  if (Number.isNaN(at)) return "";
  const mins = Math.round((Date.now() - at) / 60000);
  if (mins < 5) return t("now");
  if (mins < 60) return t("{n} min ago", { n: mins });
  const hours = Math.round(mins / 60);
  if (hours < 24) return t("{n} h ago", { n: hours });
  const days = Math.round(hours / 24);
  return days < 30 ? t("{n} d ago", { n: days })
                   : new Date(at).toLocaleDateString();
}

/** How long somebody has played something, in the app's own shorthand. */
function spanText(seconds) {
  const mins = Math.round((Number(seconds) || 0) / 60);
  if (!mins) return "";
  if (mins < 60) return t("{n} min", { n: mins });
  const hours = Math.floor(mins / 60);
  const rest = mins % 60;
  return rest ? t("{h} h {m} min", { h: hours, m: rest }) : t("{h} h", { h: hours });
}

/** A row that goes somewhere. `data-url` is what the click reads. */
const linkRow = (url, inner, extra = "") =>
  `<div class="rawinrow${url ? " goes" : ""}"${
    url ? ` data-url="${esc(url)}" role="link" tabindex="0"` : ""}${extra}>${
    inner}</div>`;

function paintStats() {
  const rows = [
    [(found.points || 0).toLocaleString(), t("Points")],
    [(found.retropoints || 0).toLocaleString(), t("RetroPoints")],
    [found.rank ? `#${found.rank.toLocaleString()}` : "—", t("Rank")],
    [(found.counts?.mastery || 0).toLocaleString(), t("Mastered")],
  ];
  $("stats").innerHTML = rows.map(([value, label]) => `
    <div class="timestat"><span class="timestatval">${esc(value)}</span>
      <span class="timestatkey">${esc(label)}</span></div>`).join("");

  /* The figures underneath: everything their own page works out rather than
     stores. Each is a value and the thing it measures, with the sums that are
     not obvious spelled out in the tooltip - "97% of the games you started"
     is a different claim from "97% of the games you own". */
  const s = found.stats || {};
  const figures = [
    [(s.unlocked || 0).toLocaleString(), t("Achievements unlocked"), ""],
    [(s.beaten || 0).toLocaleString(), t("Games beaten"),
     t("Counted once each, however many awards a game earned")],
    [`${s.beatenShare || 0}%`, t("Of games started"),
     t("{beaten} beaten out of {started} started",
       { beaten: s.beaten || 0, started: s.started || 0 })],
    [`${s.completion || 0}%`, t("Average completion"),
     t("Across the {n} games you have started", { n: s.started || 0 })],
    [s.ratio ? `×${s.ratio}` : "—", t("RetroRatio"),
     t("RetroPoints divided by points - how hard your sets are")],
    [(s.week || 0).toLocaleString(), t("Points, 7 days"),
     t("{n} achievements", { n: s.weekCount || 0 })],
    [(s.month || 0).toLocaleString(), t("Points, 30 days"),
     t("{n} achievements", { n: s.monthCount || 0 })],
    [(s.perWeek || 0).toLocaleString(), t("Points a week"),
     t("Since {when}", { when: (found.since || "").slice(0, 10) })],
  ];
  $("figures").innerHTML = figures.map(([value, label, tip]) => `
    <div class="rawinfig"${tip ? ` title="${esc(tip)}"` : ""}>
      <span class="rawinfigval">${esc(String(value ?? "—"))}</span>
      <span class="rawinfigkey">${esc(label)}</span>
    </div>`).join("");
}

/* How far through a set you are, as the site draws it: the figures, and a bar
   that says the same thing without being read. */
function progress(game) {
  if (!game.total) return "";
  const done = game.earned || 0;
  const share = Math.round((done / game.total) * 100);
  return `
    <span class="rawinprog">
      <span class="rawinbar"><span style="width:${share}%"></span></span>
      <span class="rawinnum">${done}/${game.total}${
        share >= 100 ? ` · ${esc(t("mastered"))}` : ` · ${share}%`}</span>
    </span>`;
}

/* What the award says, and nothing about how long it took.
 *
 * These used to read "Mastered in 2 h 46 min", with the time filled in from
 * userTotalPlaytime - which is the total this person has ever spent in the
 * game, not the time they took to earn the award. For anyone who kept playing
 * afterwards, or who had played it before the set existed, the sentence was
 * simply false: a friend who beat Burnout 2 in about six hours was reported
 * as "Beaten in 10 h 40 min", his lifetime total.
 *
 * RetroAchievements does not publish a per-person time-to-award anywhere -
 * API_GetGameInfoAndUserProgress gives UserTotalPlaytime and the awards
 * endpoint gives a date, and that is the whole of it. So the award is stated
 * plainly, the date goes beside it as it always did, and the hours are shown
 * as what they are: the total, next to the title. */
const AWARD_VERB = {
  "Mastery/Completion": "Mastered",
  "Game Beaten": "Beaten",
};

/* What a game cost and what came of it. "Mastered in 2 h 46 min" is the line
   somebody actually wants off a profile - the hours on their own say how long
   it was played, and the award on its own says nothing about the effort. */
function playLine(g) {
  const verb = AWARD_VERB[g.award];
  if (verb) return t(verb);
  /* No award yet, so how far in they are - which is the honest answer for a
     game somebody is in the middle of, and the one the card is being read
     for. */
  if (g.total) {
    const share = Math.round(((g.earned || 0) / g.total) * 100);
    return share >= 100
      ? t("Mastered")
      : t("{done} of {total} · {share}%",
          { done: g.earned || 0, total: g.total, share });
  }
  return "";
}

/** The hours in this game, labelled as the total they are. */
const totalPlayed = (g) => (g.seconds ? spanText(g.seconds) : "");

/** The set's own worth, which is the same for everybody who plays it. */
function setWorth(g) {
  if (!g.setPoints) return "";
  return `${g.setPoints.toLocaleString()} ${t("pts")} · ${
    (g.setRetro || 0).toLocaleString()} ${t("RP")}${
    g.ratio ? ` · ×${g.ratio}` : ""}`;
}

/* Everything known about a game, for the card that appears when the pointer
   rests on its icon - the same handful of facts their own site shows there. */
function hoverCard(g) {
  /* Two lines rather than one long one: what the game and its set are, then
     what you did with it. Strung together they made a card wider than the row
     it hangs off, and the second half is the part somebody is reading for. */
  const bits = [
    g.console,
    g.total ? t("{n} achievements", { n: g.total }) : "",
    setWorth(g),
  ].filter(Boolean);
  const did = [
    playLine(g),
    g.awardWhen ? t("on {when}", { when: day(g.awardWhen) }) : "",
    totalPlayed(g) ? t("{time} played in total", { time: totalPlayed(g) }) : "",
  ].filter(Boolean);
  /* The name on its own line and the facts flowing under it, rather than one
     fact per line: five stacked lines made a tall narrow card beside a 56px
     icon, which is the shape least like the thing it is describing. */
  return `<span class="rawinpeek" aria-hidden="true">
    ${g.icon ? `<img src="${esc(g.icon)}" alt="">` : ""}
    <span class="rawinpeektext">
      <b>${esc(g.title)}</b>
      <span class="rawinpeekbits">${
        bits.map((one) => `<span>${esc(one)}</span>`).join("")}</span>
      ${did.length ? `<span class="rawinpeekbits rawinpeekdid">${
        did.map((one) => `<span>${esc(one)}</span>`).join("")}</span>` : ""}
    </span></span>`;
}

/* The card over somebody's picture, arranged the way their own site arranges
   it: both point totals, where they stand and what share of the ranked table
   that is, when they were last at it, and how long they have been here. */
function personCard(who) {
  const share = (who.rank && who.ranked)
    ? ` (${t("Top {n}%", { n: Math.max(0.01, (who.rank / who.ranked) * 100).toFixed(2) })})`
    : "";
  const lines = [
    [t("Points"), `${(who.points || 0).toLocaleString()} (${
      (who.retropoints || 0).toLocaleString()})`],
    who.rank ? [t("Site Rank"), `#${who.rank.toLocaleString()}${share}`] : null,
    who.seen ? [t("Last Activity"), ago(who.seen)] : null,
    who.since ? [t("Member Since"), day(who.since)] : null,
  ].filter(Boolean);
  return `<span class="rawinpeek rawinwhopeek" aria-hidden="true">
    ${who.pic ? `<img src="${esc(who.pic)}" alt="">` : ""}
    <span class="rawinpeektext">
      <b>${esc(who.user)}</b>
      ${lines.map(([label, value]) => `<span class="rawinpeekline"><i>${
        esc(label)}:</i> ${esc(value)}</span>`).join("")}
    </span></span>`;
}

/** One game's row, wherever it appears: the owner's list, or a friend's. */
function gameRow(g, owner, arrowAttr) {
  const worth = setWorth(g);
  const line = playLine(g);
  return `
    <div class="rawingame" data-game="${g.id}" data-title="${esc(g.title)}"
         data-owner="${esc(owner)}">
      <div class="rawinrow goes" role="button" tabindex="0"
           title="${esc(t("Show the achievements"))}">
        <span class="rawiniconwrap${g.url ? " rawingoes" : ""}"${
          g.url ? ` data-url="${esc(g.url)}" data-title="${esc(g.title)}"
                   role="link" tabindex="0"
                   title="${esc(t("Open this game on RetroAchievements"))}"` : ""}>
          ${g.icon ? `<img class="rawinicon" src="${esc(g.icon)}" alt=""
                        loading="lazy" onerror="this.remove()">`
                   : `<span class="rawinicon"></span>`}
          ${hoverCard(g)}
        </span>
        <span class="rawinmain">
          <span class="rawintitle">${/* The name is the link to the game's
            page, and looks like one. The row around it still opens the set. */
            g.url ? `<span class="rawinlink" data-url="${esc(g.url)}"
                       data-title="${esc(g.title)}" role="link" tabindex="0"
                       title="${esc(t("Open this game on RetroAchievements"))}"
                     >${esc(g.title)}</span>` : esc(g.title)}${
            /* The hours in it, beside the name and labelled as the total -
               which is the one thing the site actually publishes about a
               person and a game. It used to be spent claiming to be how long
               the award took. */
            totalPlayed(g) ? `<span class="rawintotal" title="${
              esc(t("Total time played, all sessions"))}">${
              esc(totalPlayed(g))}</span>` : ""}</span>
          <span class="rawinsub">${esc(g.console)}${
            g.when ? ` · ${esc(day(g.when))}` : ""}${
            worth ? ` · ${esc(worth)}` : ""}</span>
          ${line ? `<span class="rawinsub rawindid">${esc(line)}</span>` : ""}
        </span>
        ${progress(g)}
        <button class="rawinopen" ${arrowAttr}="${g.id}" aria-expanded="false"
                title="${esc(t("Show the achievements"))}"
                aria-label="${esc(t("Show the achievements"))}">&#9662;</button>
      </div>
      <div class="rawinset" hidden></div>
    </div>`;
}

function paintRecent() {
  const rows = found.recent || [];
  if (!rows.length) {
    $("recent").innerHTML = `<p class="achnothing">${
      esc(t("Nothing played yet."))}</p>`;
    return;
  }
  /* Each game can be opened out into its set: every achievement as a badge,
     the ones you have in colour and the rest greyed, which is how the site
     shows a game you are part way through. Behind an arrow because it is a
     request per game - six of them opened at once would be six. */
  $("recent").innerHTML = rows
    .map((g) => gameRow(g, found.user || "", "data-open")).join("");
}

/* The set behind one of those rows. The same answer the app's own achievement
   list uses, so a badge here is the badge there - unlocked in colour, still
   locked in the site's own greyed artwork. */
async function toggleSet(button) {
  const block = button.closest("[data-game]");
  const panel = block?.querySelector(".rawinset");
  if (!panel) return;

  if (!panel.hidden) {
    panel.hidden = true;
    button.setAttribute("aria-expanded", "false");
    return;
  }
  panel.hidden = false;
  button.setAttribute("aria-expanded", "true");
  if (panel.dataset.loaded) return;

  panel.innerHTML = `<p class="achnothing">${esc(t("Asking…"))}</p>`;
  let answer;
  try {
    answer = await fetch(`/api/achievements?id=${
      encodeURIComponent(block.dataset.game)}`).then((r) => r.json());
  } catch {
    answer = { ok: false };
  }
  if (!answer.ok) {
    panel.innerHTML = `<p class="achnothing">${
      esc(t("Could not reach RetroAchievements."))}</p>`;
    return;
  }
  panel.dataset.loaded = "1";
  const rows = answer.achievements || [];
  const got = rows.filter((a) => a.unlocked).length;
  /* The list itself at the end of the wall of badges: the badges say how far
     through you are, and the list is where the descriptions, the filters and
     the comments are. Where a badge sends you to that achievement's page,
     this stays in the app. */
  panel.innerHTML = `
    <p class="rawinsetnote">${esc(t("{done} of {total} earned",
      { done: got, total: rows.length }))}</p>
    <div class="rawinbadges">${Ach.badgesHtml(rows, answer.players || 0)}
      <button class="rawinsetopen" data-list="${esc(block.dataset.game)}"
              title="${esc(t("Open the achievement list"))}">${
        esc(t("Open the list"))}</button>
    </div>`;
}

/* "Open the list" - the app's own achievement list for that game, and only
   that. Wired for both lists: a friend's games carry it too, and there it
   opens *your* progress through that set rather than theirs, because the
   list in the app is always about the account the app is signed in as. */
for (const where of ["recent", "following"]) {
  $(where).addEventListener("click", (ev) => {
    const button = ev.target.closest("[data-list]");
    if (!button) return;
    ev.preventDefault();
    ev.stopPropagation();
    const block = button.closest("[data-game]");
    openList(Number(button.dataset.list),
             block?.dataset.title
             || block?.querySelector(".rawintitle")?.textContent.trim() || "");
  });
}

/* The icon goes to the game's page; the rest of the row opens its set. The
   arrow is still there and still works - it is what says the row opens - but
   nobody should have to aim at it. */
$("recent").addEventListener("click", (ev) => {
  if (ev.target.closest("[data-url]") || ev.target.closest(".rawinset")) return;
  const row = ev.target.closest(".rawingame");
  const button = row?.querySelector("[data-open]");
  if (!button) return;
  ev.preventDefault();
  toggleSet(button);
});

const AWARD_WORDS = {
  "Mastery/Completion": "Mastered",
  "Game Beaten": "Beaten",
  Event: "Event",
  "Site Award": "Site award",
};

/* Mastered first, then beaten, then whatever else there is. Tabs rather than
   one long wall: finishing a game and taking every last thing out of it are
   different achievements in the ordinary sense of the word, and a list that
   mixes them answers neither question. Mastery leads because it is the harder
   of the two and the one people keep a profile for. */
const AWARD_TABS = [
  ["mastered", "Mastered", (a) => a.kind === "Mastery/Completion"],
  ["beaten", "Beaten", (a) => a.kind === "Game Beaten"],
  ["other", "Events & site", (a) => a.kind !== "Game Beaten"
                                    && a.kind !== "Mastery/Completion"],
];

/** The games that were taken all the way, by id. Every one of them also has a
 *  "beaten" award, which is what the toggle on that tab is about. */
const masteredGames = () => new Set((found.awards || [])
  .filter((a) => a.kind === "Mastery/Completion" && a.game)
  .map((a) => a.game));

function awardsIn(tab) {
  const rows = (found.awards || [])
    .filter(AWARD_TABS.find(([id]) => id === tab)?.[2] || (() => true));
  /* Mastering a game earns a beaten award too, so this tab is mostly a
     shorter copy of the next one. Ticked, it answers the question people
     actually have of it: which games did I finish and then leave. */
  if (tab === "beaten" && prefs.raBeatenOnly) {
    const done = masteredGames();
    return rows.filter((a) => !done.has(a.game));
  }
  return rows;
}

function paintAwards() {
  const counts = found.counts || {};
  $("awardtabs").innerHTML = AWARD_TABS.map(([id, label]) => {
    const n = awardsIn(id).length;
    return `<button class="rawintab${id === awardTab ? " on" : ""}"
      data-tab="${id}"${n ? "" : " disabled"}>${esc(t(label))}
      <span class="rawintabn">${n}</span></button>`;
  }).join("") + `<span class="rawintabnote">${esc(t(
    "{total} awards in all", { total: counts.total || 0 }))}</span>`;

  // Only on the tab it means anything to.
  $("beatenonlywrap").hidden = awardTab !== "beaten";

  const rows = awardOrder(awardTab, awardsIn(awardTab));
  const bare = !!prefs.raAwardIcons;      // pictures with no words beside them
  const done = masteredGames();
  $("awards").classList.toggle("bare", bare);
  if (!rows.length) {
    /* Which is a real answer on the beaten tab with the toggle on: it means
       every game you finished you went on to master, and an empty box with no
       explanation would read as something having gone wrong. */
    $("awards").innerHTML = `<p class="achnothing">${esc(
      awardTab === "beaten" && prefs.raBeatenOnly
        ? t("Every game you have beaten you also mastered.")
        : t("Nothing here yet."))}</p>`;
    $("awardmorerow").hidden = true;
    return;
  }
  $("awards").innerHTML = rows.slice(0, awardsShown).map((a) => {
    /* No word beside the name saying which kind it is: the tab above already
       says that, and printing it on every one of forty rows is the same
       sentence forty times. The full description stays in the tooltip, where
       it also carries the console and the date. */
    const tip = `${a.title}${a.console ? ` · ${a.console}` : ""} · ${
      t(AWARD_WORDS[a.kind] || a.kind)}${a.when ? ` · ${day(a.when)}` : ""}`;
    // Mastered games are marked wherever they appear, including on the beaten
    // tab, where the mark is what tells the two halves of that list apart.
    const mastered = a.kind === "Mastery/Completion" || done.has(a.game);
    /* The same card the games get, over the badge - an award is a game you
       finished, and the questions somebody has about it are the same ones. */
    const card = {
      id: a.game, title: a.title, console: a.console, icon: a.icon,
      award: a.kind, awardWhen: a.when,
    };
    return `
      <div class="rawinaward${a.url ? " goes" : ""}${mastered ? " mastered" : ""}"${
        a.url ? ` data-url="${esc(a.url)}" data-title="${esc(a.title)}"
                  role="link" tabindex="0"` : ""}
        data-award="${esc(awardKey(a))}"${
          a.game ? ` data-award-game="${a.game}"` : ""}
        draggable="true" title="${esc(tip)}">
        ${a.icon ? `<img src="${esc(a.icon)}" alt="" loading="lazy"
                      draggable="false" onerror="this.remove()">` : ""}
        ${bare ? "" : `<span class="rawinawardname">${esc(a.title)}</span>`}
        ${hoverCard(card)}
      </div>`;
  }).join("");
  $("awardmorerow").hidden = rows.length <= awardsShown;
  $("awardreset").hidden = !(prefs.raAwardOrder || {})[awardTab];
}

/* ---------- arranging the awards ----------

   Their own site lets somebody choose which awards lead their profile, and
   the reason is the same here: the newest thing you won is not always the one
   you want first. So each tab keeps an order of its own - a list of keys,
   applied to whatever the site sends back - and anything not in that list
   follows on in the order it arrived, so a new award appears rather than
   disappearing into a gap.

   Dragged rather than nudged with arrows: this is a wall of pictures, and
   moving one across a wall is a drag everywhere else it is ever done. */
const awardKey = (a) => `${a.kind}:${a.game || a.title}`;

function awardOrder(tab, rows) {
  const wanted = (prefs.raAwardOrder || {})[tab];
  if (!wanted?.length) return rows;
  const at = new Map(wanted.map((key, i) => [key, i]));
  // Anything the stored order has never seen keeps its own place at the end
  // rather than jumping to the front.
  return [...rows].sort((a, b) =>
    (at.get(awardKey(a)) ?? Number.MAX_SAFE_INTEGER)
    - (at.get(awardKey(b)) ?? Number.MAX_SAFE_INTEGER));
}

function saveAwardOrder() {
  const keys = [...$("awards").querySelectorAll("[data-award]")]
    .map((el) => el.dataset.award);
  savePref({ raAwardOrder: { ...(prefs.raAwardOrder || {}), [awardTab]: keys } });
  $("awardreset").hidden = false;
}

let dragging = null;

$("awards").addEventListener("dragstart", (ev) => {
  dragging = ev.target.closest("[data-award]");
  if (!dragging) return;
  dragging.classList.add("dragging");
  ev.dataTransfer.effectAllowed = "move";
  // Firefox refuses to start a drag without something on the transfer.
  ev.dataTransfer.setData("text/plain", dragging.dataset.award);
});

$("awards").addEventListener("dragover", (ev) => {
  if (!dragging) return;
  ev.preventDefault();
  const over = ev.target.closest("[data-award]");
  if (!over || over === dragging) return;
  /* Dropped before or after, decided by which half of the card the pointer is
     in - so a card can be moved to either side of its neighbour rather than
     always landing in front of it. */
  const box = over.getBoundingClientRect();
  const after = ev.clientX > box.left + box.width / 2;
  over.parentNode.insertBefore(dragging, after ? over.nextSibling : over);
});

$("awards").addEventListener("drop", (ev) => ev.preventDefault());

$("awards").addEventListener("dragend", () => {
  if (!dragging) return;
  dragging.classList.remove("dragging");
  dragging = null;
  saveAwardOrder();
});

$("awardreset").addEventListener("click", () => {
  const orders = { ...(prefs.raAwardOrder || {}) };
  delete orders[awardTab];
  savePref({ raAwardOrder: orders });
  paintAwards();
});

$("beatenonly").addEventListener("change", () => {
  savePref({ raBeatenOnly: $("beatenonly").checked });
  awardsShown = AWARDS_AT_ONCE;
  paintAwards();
});

$("awardtabs").addEventListener("click", (ev) => {
  const tab = ev.target.closest("[data-tab]")?.dataset.tab;
  if (!tab || tab === awardTab) return;
  awardTab = tab;
  awardsShown = AWARDS_AT_ONCE;      // a new tab starts at the top
  paintAwards();
});

$("iconsonly").addEventListener("change", () => {
  savePref({ raAwardIcons: $("iconsonly").checked });
  paintAwards();
});

function paintFollowing() {
  let rows = found.following || [];
  if (!rows.length) {
    $("following").innerHTML = `<p class="achnothing">${
      esc(t("You do not follow anybody yet."))}</p>`;
    return;
  }
  /* Whoever was last at it, first. Points used to be the other choice here
     and no longer needs to be: the ranking underneath answers that question
     properly, over three windows, so this list is free to answer the other
     one - who is about right now. */
  rows = [...rows].sort((a, b) =>
    (Date.parse((b.seen || "").replace(" ", "T")) || 0)
    - (Date.parse((a.seen || "").replace(" ", "T")) || 0));
  $("following").innerHTML = rows.map((who, at) => `
    <div class="rawinfriend" data-user="${esc(who.user)}">
      ${linkRow("", `
    <span class="rawinplace">${at + 1}</span>
    <span class="rawiniconwrap rawingoes" data-url="${esc(who.url)}"
          data-title="${esc(who.user)}" role="link" tabindex="0">
      ${who.pic ? `<img class="rawinface" src="${esc(who.pic)}" alt=""
                     loading="lazy" onerror="this.remove()">`
                : `<span class="rawinface"></span>`}
      ${personCard(who)}</span>
    <span class="rawinmain">
      <span class="rawintitle">${esc(who.user)}${
        who.mutual ? `<span class="rawinmutual">${esc(t("follows you"))}</span>` : ""}
        ${who.rank ? `<span class="rawinsub">#${
          esc(who.rank.toLocaleString())}</span>` : ""}
        ${/* Last seen, which is as close as the API gets: the moment their
              game last said anything about them. */
          who.seen ? `<span class="rawinseen" title="${esc(who.seen)}">${
            esc(ago(who.seen))}</span>` : ""}</span>
      ${/* What they are playing: the set's icon, then the game's name, then
            whatever the game itself is saying about them underneath. Their
            rich presence line is "4 lives, 0 points" - it means nothing
            without the game's name in front of it, which is exactly how their
            own site arranges the two. */
        who.game ? `
        <span class="rawinsub rawinnow">
          ${who.game.icon ? `<span class="rawiniconwrap rawinnowwrap">
            <img class="rawinnowicon" src="${esc(who.game.icon)}"
              alt="" loading="lazy" onerror="this.remove()">
            ${/* The same card the games in a list get, over the little icon
                  of whatever they are in the middle of. */
              hoverCard({ ...who.game, seconds: who.game.seconds })}
          </span>` : ""}
          <span class="rawinnowname">${esc(who.game.title)}</span>
          ${/* How long they have put into that game. Without it "playing X"
                says nothing about whether they just started it or have been
                at it for a week. */
            who.game.seconds ? `<span class="rawinhours">${
              esc(spanText(who.game.seconds))}</span>` : ""}
        </span>
        ${who.playing ? `<span class="rawinsub rawinnowsub">${
          esc(who.playing)}</span>` : ""}`
        : `<span class="rawinsub">${esc(who.playing || t("Nothing right now"))}</span>`}
    </span>
    <span class="rawinpoints">${esc((who.points || 0).toLocaleString())}
      <span class="rawinretro">${
        esc((who.retropoints || 0).toLocaleString())} ${esc(t("RP"))}</span></span>
    <button class="rawinopen" data-who="${esc(who.user)}" aria-expanded="false"
            title="${esc(t("More about this player"))}"
            aria-label="${esc(t("More about this player"))}">&#9662;</button>`,
    // What a window opened from this row gets called. Without it the title
    // came from the row's text, which begins with its place in the list - so
    // opening a friend produced a window called "1".
    ` data-title="${esc(who.user)}"`)}
      <div class="rawinmore" hidden></div>
    </div>`).join("");
}

/* One person, opened out: their standing, when they joined, and the last few
   games they played with how far through each they are. Fetched when the row
   is opened rather than with the list, so following a dozen people costs a
   dozen requests only if you open a dozen rows. */
async function toggleFriend(button) {
  const block = button.closest("[data-user]");
  const panel = block?.querySelector(".rawinmore");
  if (!panel) return;

  if (!panel.hidden) {
    panel.hidden = true;
    button.setAttribute("aria-expanded", "false");
    return;
  }
  panel.hidden = false;
  button.setAttribute("aria-expanded", "true");
  if (panel.dataset.loaded) return;

  panel.innerHTML = `<p class="achnothing">${esc(t("Asking…"))}</p>`;
  let who;
  try {
    who = await fetch(`/api/ra/user?u=${encodeURIComponent(block.dataset.user)}`)
      .then((r) => r.json());
  } catch {
    who = { ok: false };
  }
  if (!who.ok) {
    panel.innerHTML = `<p class="achnothing">${
      esc(t("Could not reach RetroAchievements."))}</p>`;
    return;
  }
  panel.dataset.loaded = "1";

  /* The same figures the owner's own page carries, as far as they can be had
     for somebody else: their standing, what they have finished, and what the
     last month looked like. */
  const s = who.stats || {};
  const figures = [
    [(who.points || 0).toLocaleString(), t("Points")],
    [(who.retropoints || 0).toLocaleString(), t("RetroPoints")],
    [who.rank ? `#${who.rank.toLocaleString()}` : "—", t("Rank")],
    [who.ratio ? `×${who.ratio}` : "—", t("RetroRatio")],
    [(s.unlocked || 0).toLocaleString(), t("Achievements unlocked")],
    [(who.counts?.mastery || 0).toLocaleString(), t("Mastered")],
    [(s.beaten || 0).toLocaleString(), t("Games beaten")],
    [(s.week || 0).toLocaleString(), t("Points, 7 days")],
    [(s.month || 0).toLocaleString(), t("Points, 30 days")],
  ];
  panel.innerHTML = `
    <div class="rawinfigures">${figures.map(([value, label]) => `
      <div class="rawinfig"><span class="rawinfigval">${esc(value)}</span>
        <span class="rawinfigkey">${esc(label)}</span></div>`).join("")}</div>
    ${who.since ? `<p class="rawinsetnote">${esc(t("Member since {when}",
      { when: who.since.slice(0, 10) }))}${
      who.motto ? ` — ${esc(who.motto)}` : ""}</p>` : ""}
    <div class="rawinlist">${(who.recent || [])
      .map((g) => gameRow(g, who.user, "data-theirs")).join("")
      || `<p class="achnothing">${esc(t("Nothing played yet."))}</p>`}</div>`;
}

/* One of their games, opened out: the same wall of badges the owner's own
   games get, but read against *their* progress - so it says what that person
   has and has not unlocked. */
async function toggleTheirSet(button) {
  const block = button.closest("[data-game]");
  const panel = block?.querySelector(".rawinset");
  if (!panel) return;

  if (!panel.hidden) {
    panel.hidden = true;
    button.setAttribute("aria-expanded", "false");
    return;
  }
  panel.hidden = false;
  button.setAttribute("aria-expanded", "true");
  if (panel.dataset.loaded) return;

  panel.innerHTML = `<p class="achnothing">${esc(t("Asking…"))}</p>`;
  let answer;
  try {
    answer = await fetch(`/api/ra/user/game?u=${
      encodeURIComponent(block.dataset.owner)}&g=${
      encodeURIComponent(block.dataset.game)}`).then((r) => r.json());
  } catch {
    answer = { ok: false };
  }
  if (!answer.ok) {
    panel.innerHTML = `<p class="achnothing">${
      esc(t("Could not reach RetroAchievements."))}</p>`;
    return;
  }
  panel.dataset.loaded = "1";
  const rows = answer.achievements || [];
  panel.innerHTML = `
    <p class="rawinsetnote">${esc(t("{done} of {total} earned",
      { done: answer.hardcore || answer.earned || 0, total: rows.length }))}${
      answer.playtime ? ` · ${esc(spanText(answer.playtime))}` : ""}</p>
    <div class="rawinbadges">${Ach.badgesHtml(rows, answer.players || 0)}
      ${/* Their badges, but the list this opens is yours: it is the app's own
            list, and the app is signed in as you. Worth having here - "how am
            I doing in the thing they are playing" is the question a friend's
            row provokes. */""}
      <button class="rawinsetopen" data-list="${esc(block.dataset.game)}"
              title="${esc(t("Open your own list for this game"))}">${
        esc(t("Open my list"))}</button>
    </div>`;
}

/* ---------- who is ahead ----------

   All time is free - it is the points everyone already carries. The two
   windows are counted from what each person earned in them, one request each,
   so they are asked for when the tab is pressed and kept for a few minutes
   afterwards. */
let rankWindow = "all";

async function loadRanking(window_) {
  rankWindow = window_;
  for (const tab of $("ranktabs").querySelectorAll("[data-window]")) {
    tab.classList.toggle("on", tab.dataset.window === window_);
  }
  $("ranking").innerHTML = `<p class="achnothing">${esc(t("Asking…"))}</p>`;

  let answer;
  try {
    answer = await fetch(`/api/ra/ranking?window=${encodeURIComponent(window_)}`)
      .then((r) => r.json());
  } catch {
    answer = { ok: false };
  }
  if (!answer.ok) {
    $("ranking").innerHTML = `<p class="achnothing">${
      esc(t("Could not reach RetroAchievements."))}</p>`;
    return;
  }
  const unit = window_ === "all" ? t("points") : t("points won");
  $("ranking").innerHTML = (answer.players || []).map((one, at) => `
    <div class="rawinrow goes${one.me ? " isme" : ""}" data-url="${esc(one.url)}"
         data-title="${esc(one.user)}" role="link" tabindex="0">
      <span class="rawinplace">${at + 1}</span>
      <span class="rawiniconwrap">
        ${one.pic ? `<img class="rawinface" src="${esc(one.pic)}" alt=""
                       loading="lazy" onerror="this.remove()">`
                  : `<span class="rawinface"></span>`}
        ${personCard(one)}
      </span>
      <span class="rawinmain">
        <span class="rawintitle">${esc(one.user)}${
          one.me ? `<span class="rawinmutual">${esc(t("you"))}</span>` : ""}</span>
        <span class="rawinsub">${esc(unit)}${
          one.got ? ` · ${esc(t("{n} achievements", { n: one.got }))}` : ""}${
          one.rank ? ` · #${esc(one.rank.toLocaleString())}` : ""}</span>
      </span>
      <span class="rawinpoints">${esc((one.won || 0).toLocaleString())}
        <span class="rawinretro">${
          /* The RetroPoints won in this window, not their lifetime total -
             a day's points beside an all-time figure is two different
             questions printed as one row. */
          esc((one.wonRetro || 0).toLocaleString())} ${esc(t("RP"))}</span></span>
    </div>`).join("")
    || `<p class="achnothing">${esc(window_ === "all"
      ? t("Nobody has won anything yet.")
      : t("Nobody you follow has earned anything in this window."))}</p>`;

  /* The people who were left out, counted rather than listed. Somebody who
     earned nothing today is not last - they were not playing - and a column
     of zeroes pushes the two or three who did something off the bottom. */
  const quiet = answer.quiet || 0;
  $("rankquiet").hidden = !quiet;
  $("rankquiet").textContent = quiet
    ? t("{n} others you follow earned nothing in this window.", { n: quiet })
    : "";
}

$("ranktabs").addEventListener("click", (ev) => {
  const which = ev.target.closest("[data-window]")?.dataset.window;
  if (which && which !== rankWindow) loadRanking(which);
});

$("following").addEventListener("click", (ev) => {
  // A picture is a link to the person or the game it shows; everything else
  // opens the row it is in.
  if (ev.target.closest("[data-url]") || ev.target.closest(".rawinset")) return;

  const game = ev.target.closest(".rawingame");
  if (game) {
    const theirs = game.querySelector("[data-theirs]");
    if (!theirs) return;
    ev.preventDefault();
    toggleTheirSet(theirs);
    return;
  }
  const person = ev.target.closest(".rawinfriend");
  const button = person?.querySelector("[data-who]");
  if (!button) return;
  ev.preventDefault();
  toggleFriend(button);
});

/* The blocks, in the order the reader put them. An unknown name in the stored
   order is ignored and a missing one is appended, so adding a block later
   cannot leave somebody with a page that has lost a piece of itself. */
function paintOrder() {
  const wanted = (prefs.raProfileOrder || []).filter((id) => SECTIONS.includes(id));
  for (const id of SECTIONS) if (!wanted.includes(id)) wanted.push(id);
  const host = $("sections");
  for (const id of wanted) {
    const block = host.querySelector(`[data-sec="${id}"]`);
    if (block) host.append(block);      // append in turn = that order
  }
  // The first block cannot go up and the last cannot go down.
  const blocks = [...host.querySelectorAll(".rawinsec")];
  blocks.forEach((block, at) => {
    block.querySelector('[data-move="-1"]').disabled = at === 0;
    block.querySelector('[data-move="1"]').disabled = at === blocks.length - 1;
  });
}

$("sections").addEventListener("click", (ev) => {
  const button = ev.target.closest("[data-move]");
  if (!button) return;
  const block = button.closest(".rawinsec");
  const order = [...$("sections").querySelectorAll(".rawinsec")]
    .map((s) => s.dataset.sec);
  const at = order.indexOf(block.dataset.sec);
  const to = at + Number(button.dataset.move);
  if (to < 0 || to >= order.length) return;
  order.splice(to, 0, ...order.splice(at, 1));
  savePref({ raProfileOrder: order });
  paintOrder();
});

/** The head: who this is. Everything else arrives under it. */
function paintHead() {
  $("pic").src = found.pic || "";
  $("namebtn").textContent = found.user || "";
  // The picture and the name both go to the real page - which is what a
  // profile picture does everywhere else on the web.
  for (const id of ["picbtn", "namebtn"]) {
    $(id).dataset.url = found.url || "";
    $(id).title = t("Open your profile on RetroAchievements");
  }
  document.title = found.user || "Profile";
  $("rank").textContent = found.rank
    ? t("Rank {n} of {total}", { n: found.rank.toLocaleString(),
                                 total: (found.ranked || 0).toLocaleString() })
    : "";
  $("playing").textContent = found.playing || "";
  paintStats();
  paintRecent();
  paintAwards();
  paintFollowing();
  $("note").textContent = t("Everything here is a link to RetroAchievements. "
    + "Click a game, an award or a person to open its page.");
}

/* ---------- loading, a panel at a time ----------

   Everything used to arrive together, which meant waiting for thirty-odd
   requests before anything appeared. Each block is asked for on its own now,
   in the order the blocks are actually arranged - so the first thing somebody
   sees is the first thing fetched, and if they have put the people they
   follow at the top, that is what loads first.

   The head - picture, name, points - comes first whatever the order, because
   it is the one part that is not a block and the one that answers "is this
   even me". */
const PANELS = {
  recent: { url: "recent", paint: () => paintRecent(), busy: "recent" },
  awards: { url: "awards", paint: () => paintAwards(), busy: "awards" },
  following: { url: "following", paint: () => paintFollowing(), busy: "following" },
};

function waiting(where) {
  const box = $(where);
  if (box && !box.innerHTML) {
    box.innerHTML = `<p class="achnothing">${esc(t("Asking…"))}</p>`;
  }
}

async function panel(name, refresh) {
  const one = PANELS[name];
  if (!one) return;
  waiting(one.busy);
  try {
    const answer = await fetch(`/api/ra/panel/${one.url}${
      refresh ? "?refresh=1" : ""}`).then((r) => r.json());
    if (!answer.ok) return;
    Object.assign(found, answer);
    one.paint();
  } catch { /* the block simply stays as it was */ }
}

async function load(refresh = false) {
  $("refresh").disabled = true;
  if (!found) $("note").textContent = t("Asking RetroAchievements…");

  let mine;
  try {
    mine = await fetch(`/api/ra/me${refresh ? "?refresh=1" : ""}`)
      .then((r) => r.json());
  } catch {
    mine = { ok: false, reason: "unreachable" };
  }
  if (!mine.ok) {
    $("refresh").disabled = false;
    $("note").textContent = mine.reason === "nouser"
      ? t("Add your RetroAchievements username in Settings → Cover art.")
      : t("Could not reach RetroAchievements.");
    return;
  }
  found = { ...(found || {}), ...mine };
  paintHead();

  // The figures under the head, then every block in the order they are in.
  fetch(`/api/ra/panel/figures${refresh ? "?refresh=1" : ""}`)
    .then((r) => r.json()).then((answer) => {
      if (!answer.ok) return;
      Object.assign(found, answer);
      paintStats();
    }).catch(() => { /* the four headline figures are already up */ });

  for (const name of shownOrder()) await panel(name, refresh);
  $("refresh").disabled = false;
  $("note").textContent = t("Everything here is a link to RetroAchievements. "
    + "Click a game, an award or a person to open its page.");
}

/** The blocks as they are arranged on screen, top first. */
const shownOrder = () => [...$("sections").querySelectorAll(".rawinsec")]
  .map((one) => one.dataset.sec);

$("refresh").addEventListener("click", () => load(true));
$("awardmore").addEventListener("click", () => {
  awardsShown += AWARDS_AT_ONCE;
  paintAwards();
});

/* ---------- keeping a hover card on screen ----------

   The cards are positioned against the thing they describe, which is right
   until that thing is in the last column or the bottom row: an award at the
   right-hand edge had half its card outside the window, and a window cannot
   scroll to show something that is only there while the pointer is still on
   the icon.

   So the moment one is shown, it is measured and nudged back inside - left or
   right, and above the icon instead of below it when there is no room under.
   Done here rather than in the stylesheet because only the browser knows how
   much room there is. */
function placeCard(card) {
  if (!card) return;
  card.style.left = "";
  card.style.right = "";
  card.style.top = "";
  card.style.bottom = "";
  card.style.transform = "";
  card.classList.remove("flipped");

  const box = card.getBoundingClientRect();
  const edge = 8;
  const over = box.right - (innerWidth - edge);
  const under = edge - box.left;
  if (over > 0 || under > 0) {
    /* Slid along by however much it overhangs, rather than flipped to the
       other side: the card stays under the icon it belongs to, which is what
       says which icon it is about. */
    const shift = over > 0 ? -over : under;
    const already = card.style.transform || getComputedStyle(card).transform;
    card.style.transform = already && already !== "none"
      ? `${card.classList.contains("centred") ? "translateX(-50%) " : ""}translateX(${shift}px)`
      : `translateX(${shift}px)`;
    // Re-read: centred cards carry a transform of their own, and the two have
    // to be combined rather than one replacing the other.
    const moved = card.getBoundingClientRect();
    if (moved.right > innerWidth - edge || moved.left < edge) {
      card.style.transform = "none";
      card.style.left = "auto";
      card.style.right = "0";
    }
  }
  const room = innerHeight - card.getBoundingClientRect().bottom;
  if (room < edge) card.classList.add("flipped");
}

/* What an award's set is worth. The awards panel is seventy icons; asking
   what each one is worth as it is built would be seventy requests before
   anything appeared, so it is asked when one is actually pointed at - once
   per game, and the answer is kept by the server for a fortnight. */
const worthAsked = new Map();

async function fillWorth(card, game) {
  if (!game || card.dataset.worth) return;
  card.dataset.worth = "1";
  if (!worthAsked.has(game)) {
    worthAsked.set(game, fetch(`/api/ra/game?id=${encodeURIComponent(game)}`)
      .then((r) => r.json()).catch(() => ({ ok: false })));
  }
  const found = await worthAsked.get(game);
  if (!found?.ok) return;
  const bits = [
    found.achievements ? t("{n} achievements", { n: found.achievements }) : "",
    found.points
      ? `${found.points.toLocaleString()} ${t("pts")} · ${
          (found.retropoints || 0).toLocaleString()} ${t("RP")}${
          found.ratio ? ` · ×${found.ratio}` : ""}`
      : "",
  ].filter(Boolean);
  if (!bits.length) return;
  const line = card.querySelector(".rawinpeekbits");
  if (line) {
    line.innerHTML = [...line.querySelectorAll("span")]
      .map((one) => one.outerHTML).join("")
      + bits.map((one) => `<span>${esc(one)}</span>`).join("");
  }
  placeCard(card);
}

/* Every card, wherever it is. One listener rather than a handler per card:
   they are drawn by four different functions and all of them want this. */
document.addEventListener("pointerover", (ev) => {
  const holder = ev.target.closest?.(
    ".rawiniconwrap, .rawinbadgewrap, .rawinaward, .achbadgewrap");
  if (!holder) return;
  const card = holder.querySelector(".rawinpeek, .achpeek");
  if (!card) return;
  requestAnimationFrame(() => placeCard(card));
  // Awards know their game but not what its set is worth; the games in a
  // list already carry theirs.
  if (holder.classList.contains("rawinaward")) {
    fillWorth(card, Number(holder.dataset.awardGame || 0));
  }
});

/* Anything with a URL on it goes there, wherever Settings says such pages go.
   One listener for the whole window rather than one per list. */
function follow(el) {
  const url = el?.dataset.url;
  if (!url) return;
  /* What the window ends up called. The row's own text starts with its place
     in the list, so taking the text gave windows called "1" and "2"; anything
     that goes somewhere now says what it is, and the text is only a fallback
     for the odd link with nothing better. */
  const title = el.dataset.title
    || el.querySelector(".rawintitle, .rawinawardname")?.textContent.trim()
    || el.textContent.trim().slice(0, 60);
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title }),
  }).then((r) => r.json()).then((res) => {
    if (!res.opened) {
      fetch("/api/browse/open", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      }).catch(() => { /* nothing else to try */ });
    }
  }).catch(() => { /* nothing else to try */ });
}

/* ---------- the right-click menu ----------

   Everything here that stands for a game - a row in Last played, an award, a
   badge - answers the same three questions. Two of them are pages on their
   site; the third is this app's own achievement list, which lives in the app
   rather than in this window, so asking for it means asking the app.

   When this page is the panel inside the app it can simply say so; opened as
   a window of its own there is no app to talk to, so it opens the standalone
   list instead. Both end up at the same list. */
const framed = window.parent !== window;

function askApp(want, data) {
  if (framed) {
    parent.postMessage({ romsrx: 1, want, ...data }, location.origin);
    return true;
  }
  return false;
}

/** The app's own achievement list for a game - just the list. */
function openList(id, title) {
  if (askApp("achievements", { id, title })) return;
  const url = `${location.origin}/achievements.html?id=${
    encodeURIComponent(id)}&title=${encodeURIComponent(title || "")}`;
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title: title || "Achievements" }),
  }).then((r) => r.json()).then((res) => {
    if (!res.opened) location.href = url;
  }).catch(() => { location.href = url; });
}

function openHowLong(id, title) {
  if (askApp("howlong", { id, title })) return;
  // No app to ask - this window is on its own - so the list opens as a window
  // beside it, which is the same list.
  const url = `${location.origin}/achievements.html?id=${
    encodeURIComponent(id)}&title=${encodeURIComponent(title || "")}`;
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title: title || "Achievements" }),
  }).then((r) => r.json()).then((res) => {
    if (!res.opened) location.href = url;
  }).catch(() => { location.href = url; });
}

let menuGame = { id: 0, title: "", url: "" };

function openGameMenu(ev, game) {
  menuGame = game;
  const menu = $("gamemenu");
  menu.hidden = false;
  menu.style.left = `${Math.min(ev.clientX,
    innerWidth - menu.offsetWidth - 8)}px`;
  menu.style.top = `${Math.min(ev.clientY,
    innerHeight - menu.offsetHeight - 8)}px`;
}

const closeGameMenu = () => { $("gamemenu").hidden = true; };

document.addEventListener("contextmenu", (ev) => {
  /* The game behind whatever was aimed at. A badge belongs to the game whose
     set it is in, which is the block it sits in - so the nearest thing with a
     game on it wins, and a right-click on the empty space between rows opens
     nothing, exactly as it did before. */
  const holder = ev.target.closest("[data-game], [data-award-game]");
  const id = Number(holder?.dataset.game || holder?.dataset.awardGame || 0);
  if (!id) return;
  ev.preventDefault();
  openGameMenu(ev, {
    id,
    title: holder.dataset.title
      || holder.querySelector(".rawintitle, .rawinawardname")?.textContent.trim()
      || "",
    url: `https://retroachievements.org/game/${id}`,
  });
});

$("gamemenu").addEventListener("click", (ev) => {
  const act = ev.target.closest("button")?.dataset.act;
  closeGameMenu();
  if (!act || !menuGame.id) return;
  if (act === "howlong") {
    openHowLong(menuGame.id, menuGame.title);
  } else if (act === "ra") {
    if (!askApp("web", { url: menuGame.url, title: menuGame.title })) {
      follow({ dataset: { url: menuGame.url }, textContent: menuGame.title });
    }
  } else if (act === "hashes") {
    const url = `${menuGame.url}/hashes`;
    if (!askApp("web", { url, title: menuGame.title })) {
      follow({ dataset: { url }, textContent: menuGame.title });
    }
  }
});

document.addEventListener("click", closeGameMenu);
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") closeGameMenu();
});

document.addEventListener("click", (ev) => follow(ev.target.closest("[data-url]")));
document.addEventListener("keydown", (ev) => {
  if (ev.key !== "Enter" && ev.key !== " ") return;
  const row = ev.target.closest("[data-url]");
  if (!row) return;
  ev.preventDefault();
  follow(row);
});

/* The app's own look, so this window belongs to the app that opened it. */
(async () => {
  try {
    prefs = await fetch("/api/prefs").then((r) => r.json());
    applyLanguage(prefs.lang || "en");
    document.documentElement.dataset.tone = prefs.tone || "default";
    document.documentElement.dataset.accent = prefs.accent || "blue";
    $("iconsonly").checked = !!prefs.raAwardIcons;
    $("beatenonly").checked = !!prefs.raBeatenOnly;
  } catch { /* the defaults are perfectly readable */ }
  paintOrder();
  await load(false);
  // Today, which is what somebody opens a ranking to see.
  loadRanking("day");
})();
