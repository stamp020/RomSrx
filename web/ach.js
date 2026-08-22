/* The achievements window: one game, one set, nothing else.

   Opened beside a game as it starts, when Settings says to. Everything it
   draws comes from one request; the rows themselves are drawn by achshared.js,
   which the app's own panel uses too, so the two cannot end up disagreeing
   about what a missable looks like.

   The window has no chrome of its own beyond the refresh button - it is meant
   to sit next to a game and be glanced at, and a game you are playing is not
   a moment for a second navigation. */

const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);
let gameId = Number(params.get("id") || 0);

/* How big the rows are drawn. This window is opened beside a running game -
   often on a second screen, or a television, or the other side of a desk -
   and the size that suits a laptop three feet away suits none of those.

   The slider itself lives in achshared.js, along with the setting it writes,
   because the panel inside the app has one too and the two must agree. */
Ach.wireZoom($("zoom"));

let found = null;

/* The name is in the URL because the app already knows it and this window
   would otherwise have to ask a second time to print a heading. The answer
   carries the site's own title, which replaces it as soon as it lands. */
$("game").textContent = params.get("title") || "";
document.title = params.get("title") || "Achievements";

function paint() {
  if (!found) return;
  $("sub").textContent = Ach.countText(found);
  $("controls").hidden = false;
  $("list").innerHTML = Ach.listHtml(found, $("filter").value, $("sort").value);
  const ordinary = found.user
    ? t("Unlocks are counted in hardcore, and can take a few minutes to appear. "
        + "Click one to open it on RetroAchievements.")
    : t("Add your RetroAchievements username in Settings → Cover art to see "
        + "which of these you have earned.");
  // Same two warnings the panel in the app shows: a list read off the disk,
  // and a set that has been revised since it was last looked at.
  const state = Ach.stateNote(found);
  $("note").textContent = state ? `${state} ${ordinary}` : ordinary;
}

async function load(refresh = false) {
  if (!gameId) {
    $("note").textContent = t("No game was named.");
    return;
  }
  $("refresh").disabled = true;
  if (!found) $("note").textContent = t("Asking…");

  let answer;
  try {
    answer = await fetch(`/api/achievements?id=${gameId}${
      refresh ? "&refresh=1" : ""}`).then((r) => r.json());
  } catch {
    answer = { ok: false, reason: "unreachable" };
  }
  $("refresh").disabled = false;

  if (!answer.ok) {
    // Keeps whatever was already on screen: a failed refresh should not empty
    // a list that was perfectly good a moment ago.
    $("note").textContent = t(Ach.REASONS[answer.reason] || Ach.REASONS.unreachable);
    return;
  }
  found = answer;
  if (found.title) {
    $("game").textContent = found.title;
    document.title = found.title;
  }
  paint();
  offerSets();          // after the list, so it never delays what matters
}

/* The other boards built on this game - the base set and its subsets. Drawn
   by achshared.js, which the panel inside the app uses too; this only says
   where to put it and what to do when one is picked. */
let theSets = [];

function paintSets() {
  Ach.paintSets($("setrow"), $("setsays"), theSets, gameId);
}

async function offerSets() {
  theSets = await Ach.offerSets($("whichset"), $("setrow"), $("setsays"),
                                gameId);
}

$("setrow").addEventListener("click", (ev) => {
  const picked = Number(ev.target.closest("[data-set]")?.dataset.set) || 0;
  if (!picked || picked === gameId) return;
  gameId = picked;
  found = null;
  // Marked straight away rather than after the fetch: the press has to look
  // like it landed, and the list underneath is about to be replaced anyway.
  $("game").textContent = theSets.find((one) => one.id === picked)?.title || "";
  paintSets();
  $("list").innerHTML = "";
  load();
});

$("filter").addEventListener("change", paint);
$("sort").addEventListener("change", paint);
$("refresh").addEventListener("click", () => load(true));

/* A row is its page. This window has no opinion about where pages go - it is
   already a window of the app's own - so it asks the app, which reads the
   same setting the rest of the app does. */
function openAchievement(row) {
  const one = found?.achievements?.find((a) => a.id === Number(row?.dataset.ach));
  if (!one) return;
  fetch("/api/browse/window", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: one.url, title: one.title }),
  }).then((r) => r.json()).then((res) => {
    // No window to be had - `serve` in a browser - so the browser gets it.
    if (!res.opened) {
      fetch("/api/browse/open", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: one.url }),
      }).catch(() => { /* nothing else to try */ });
    }
  }).catch(() => { /* nothing else to try */ });
}

$("list").addEventListener("click", (ev) => {
  if (ev.target.closest(".achtalk")) return;
  // The badge opens its page; the rest of the row opens the comments.
  if (ev.target.closest(".achgoes")) {
    openAchievement(ev.target.closest("[data-ach]"));
    return;
  }
  const talk = ev.target.closest("[data-ach]")?.querySelector(".achtalkbtn");
  if (!talk) return;
  ev.preventDefault();
  Ach.toggleComments(talk);
});
$("list").addEventListener("keydown", (ev) => {
  if (ev.key !== "Enter" && ev.key !== " ") return;
  const row = ev.target.closest("[data-ach]");
  if (!row || ev.target.closest(".achtalk")) return;
  ev.preventDefault();
  const talk = row.querySelector(".achtalkbtn");
  if (talk) Ach.toggleComments(talk);
});

/* The app's own language, theme and colour, so this window looks like the one
   that opened it rather than like a web page that wandered in. */
(async () => {
  try {
    const prefs = await fetch("/api/prefs").then((r) => r.json());
    applyLanguage(prefs.lang || "en");
    // Both always set, exactly as applyTheme does it in the app: the
    // stylesheet reads "default" as a value, not as the attribute's absence.
    document.documentElement.dataset.tone = prefs.tone || "default";
    document.documentElement.dataset.accent = prefs.accent || "blue";
    /* A custom colour is a value, not a name: the stylesheet cannot know it,
       so it has to be set on the element. Without this, data-accent="custom"
       fell through to the blue the rule below it defaults to - which is why
       this window stayed blue while the app went red. */
    if (prefs.accent === "custom"
        && /^#[0-9a-f]{6}$/i.test(String(prefs.accentCustom || ""))) {
      document.documentElement.style.setProperty("--hue", prefs.accentCustom);
    }
  } catch { /* the defaults are perfectly readable */ }
  await load(false);
})();
