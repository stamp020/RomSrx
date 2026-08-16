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
const SECTIONS = ["recent", "awards", "following"];

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
  $("recent").innerHTML = rows.map((g) => `
    <div class="rawingame" data-game="${g.id}">
      <div class="rawinrow${g.url ? " goes" : ""}"${
        g.url ? ` data-url="${esc(g.url)}" role="link" tabindex="0"` : ""}>
        ${g.icon ? `<img class="rawinicon" src="${esc(g.icon)}" alt=""
                      loading="lazy" onerror="this.remove()">`
                 : `<span class="rawinicon"></span>`}
        <span class="rawinmain">
          <span class="rawintitle">${esc(g.title)}</span>
          <span class="rawinsub">${esc(g.console)}${
            g.when ? ` · ${esc(day(g.when))}` : ""}</span>
        </span>
        ${progress(g)}
        <button class="rawinopen" data-open="${g.id}" aria-expanded="false"
                title="${esc(t("Show the achievements"))}"
                aria-label="${esc(t("Show the achievements"))}">&#9662;</button>
      </div>
      <div class="rawinset" hidden></div>
    </div>`).join("");
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
    <div class="rawinbadges">${rows.map((a) => `
      <a class="rawinbadge${a.unlocked ? " got" : ""}" data-url="${esc(a.url)}"
         role="link" tabindex="0"
         title="${esc(`${a.title} · ${a.points} ${t("pts")}${
           a.description ? ` — ${a.description}` : ""}`)}">
        <img src="${esc((a.unlocked ? a.badge : a.badgeLocked) || a.badge)}"
             alt="" loading="lazy" onerror="this.remove()">
      </a>`).join("")}
      <button class="rawinsetopen" data-list="${esc(block.dataset.game)}"
              title="${esc(t("Open the achievement list"))}">${
        esc(t("Open the list"))}</button>
    </div>`;
}

$("recent").addEventListener("click", (ev) => {
  const button = ev.target.closest("[data-list]");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();
  const block = button.closest("[data-game]");
  openHowLong(Number(button.dataset.list),
              block?.querySelector(".rawintitle")?.textContent.trim() || "");
});

$("recent").addEventListener("click", (ev) => {
  const button = ev.target.closest("[data-open]");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();      // the row itself opens the game's page
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
    return `
      <div class="rawinaward${a.url ? " goes" : ""}${mastered ? " mastered" : ""}"${
        a.url ? ` data-url="${esc(a.url)}" role="link" tabindex="0"` : ""}
        data-award="${esc(awardKey(a))}"${
          a.game ? ` data-award-game="${a.game}"` : ""}
        draggable="true" title="${esc(tip)}">
        ${a.icon ? `<img src="${esc(a.icon)}" alt="" loading="lazy"
                      draggable="false" onerror="this.remove()">` : ""}
        ${bare ? "" : `<span class="rawinawardname">${esc(a.title)}</span>`}
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
  const rows = found.following || [];
  if (!rows.length) {
    $("following").innerHTML = `<p class="achnothing">${
      esc(t("You do not follow anybody yet."))}</p>`;
    return;
  }
  /* Ordered by points, which is the only ranking the API gives for a list of
     people - and the one their own leaderboards are built on. The place in
     that order is printed, since "third of the people you follow" is the
     thing somebody is actually looking for. */
  $("following").innerHTML = rows.map((who, at) => `
    <div class="rawinfriend" data-user="${esc(who.user)}">
      ${linkRow(who.url, `
    <span class="rawinplace">${at + 1}</span>
    ${who.pic ? `<img class="rawinface" src="${esc(who.pic)}" alt=""
                   loading="lazy" onerror="this.remove()">`
              : `<span class="rawinface"></span>`}
    <span class="rawinmain">
      <span class="rawintitle">${esc(who.user)}${
        who.mutual ? `<span class="rawinmutual">${esc(t("follows you"))}</span>` : ""}
        ${who.rank ? `<span class="rawinsub">#${
          esc(who.rank.toLocaleString())}</span>` : ""}</span>
      ${/* What they are playing: the set's icon, then the game's name, then
            whatever the game itself is saying about them underneath. Their
            rich presence line is "4 lives, 0 points" - it means nothing
            without the game's name in front of it, which is exactly how their
            own site arranges the two. */
        who.game ? `
        <span class="rawinsub rawinnow">
          ${who.game.icon ? `<img class="rawinnowicon" src="${esc(who.game.icon)}"
            alt="" loading="lazy" onerror="this.remove()">` : ""}
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
            aria-label="${esc(t("More about this player"))}">&#9662;</button>`)}
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

  const figures = [
    [(who.points || 0).toLocaleString(), t("Points")],
    [(who.retropoints || 0).toLocaleString(), t("RetroPoints")],
    [who.rank ? `#${who.rank.toLocaleString()}` : "—", t("Rank")],
    [who.ratio ? `×${who.ratio}` : "—", t("RetroRatio")],
  ];
  panel.innerHTML = `
    <div class="rawinfigures">${figures.map(([value, label]) => `
      <div class="rawinfig"><span class="rawinfigval">${esc(value)}</span>
        <span class="rawinfigkey">${esc(label)}</span></div>`).join("")}</div>
    ${who.since ? `<p class="rawinsetnote">${esc(t("Member since {when}",
      { when: who.since.slice(0, 10) }))}${
      who.motto ? ` — ${esc(who.motto)}` : ""}</p>` : ""}
    <div class="rawinlist">${(who.recent || []).map((g) => `
      <div class="rawingame" data-game="${g.id}" data-title="${esc(g.title)}"
           data-owner="${esc(who.user)}">
        <div class="rawinrow${g.url ? " goes" : ""}"${
          g.url ? ` data-url="${esc(g.url)}" role="link" tabindex="0"` : ""}>
          ${g.icon ? `<img class="rawinicon" src="${esc(g.icon)}" alt=""
                        loading="lazy" onerror="this.remove()">`
                   : `<span class="rawinicon"></span>`}
          <span class="rawinmain">
            <span class="rawintitle">${esc(g.title)}</span>
            <span class="rawinsub">${esc(g.console)}${
              g.when ? ` · ${esc(day(g.when))}` : ""}</span>
          </span>
          ${progress(g)}
          <button class="rawinopen" data-theirs="${g.id}" aria-expanded="false"
                  title="${esc(t("Show what they have unlocked"))}"
                  aria-label="${esc(t("Show what they have unlocked"))}">&#9662;</button>
        </div>
        <div class="rawinset" hidden></div>
      </div>`).join("")
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
    <div class="rawinbadges">${rows.map((a) => `
      <a class="rawinbadge${a.unlocked ? " got" : ""}" data-url="${esc(a.url)}"
         role="link" tabindex="0"
         title="${esc(`${a.title} · ${a.points} ${t("pts")}${
           a.description ? ` — ${a.description}` : ""}`)}">
        <img src="${esc((a.unlocked ? a.badge : a.badgeLocked) || a.badge)}"
             alt="" loading="lazy" onerror="this.remove()">
      </a>`).join("")}</div>`;
}

$("following").addEventListener("click", (ev) => {
  // Their own row opens the person; a row inside it opens one of their games.
  const theirs = ev.target.closest("[data-theirs]");
  if (theirs) {
    ev.preventDefault();
    ev.stopPropagation();
    toggleTheirSet(theirs);
    return;
  }
  const button = ev.target.closest("[data-who]");
  if (!button) return;
  ev.preventDefault();
  ev.stopPropagation();      // the row itself opens their profile
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

function paint() {
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

async function load(refresh = false) {
  $("refresh").disabled = true;
  if (!found) $("note").textContent = t("Asking RetroAchievements…");
  let answer;
  try {
    answer = await fetch(`/api/ra/profile${refresh ? "?refresh=1" : ""}`)
      .then((r) => r.json());
  } catch {
    answer = { ok: false, reason: "unreachable" };
  }
  $("refresh").disabled = false;
  if (!answer.ok) {
    $("note").textContent = answer.reason === "nouser"
      ? t("Add your RetroAchievements username in Settings → Cover art.")
      : t("Could not reach RetroAchievements.");
    return;
  }
  found = answer;
  paint();
}

$("refresh").addEventListener("click", () => load(true));
$("awardmore").addEventListener("click", () => {
  awardsShown += AWARDS_AT_ONCE;
  paintAwards();
});

/* Anything with a URL on it goes there, wherever Settings says such pages go.
   One listener for the whole window rather than one per list. */
function follow(el) {
  const url = el?.dataset.url;
  if (!url) return;
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title: el.textContent.trim().slice(0, 60) }),
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
})();
