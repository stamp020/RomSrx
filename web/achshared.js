/* One achievement set, drawn the same way in both places that draw one.

   The app's own How Long / Achievements panel shows this list, and so does the
   window that opens beside a game when it starts. They are different pages -
   one is the whole app, the other is a single-purpose window with no library
   in it - so what they share has to live somewhere neither of them owns.
   Without this there would be two copies of "what a missable looks like", and
   the second copy is always the one that stops matching.

   Loaded as a plain script by both, and it asks for nothing but `t` from
   i18n.js. Everything else it needs is in the answer the server sends. */

(() => {
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);

  /* Which of them to show. "Still locked" is the one this exists for - a set
     you are part way through is a list of things already done and a handful
     still to do, and only the second half is a plan. */
  function matches(a, filter) {
    if (filter === "locked") return !a.unlocked;
    if (filter === "unlocked") return !!a.unlocked;
    if (filter === "missable") return a.type === "missable";
    if (filter === "progression") {
      return a.type === "progression" || a.type === "win_condition";
    }
    return true;
  }

  const ORDER = {
    order: (a, b) => a.order - b.order || a.id - b.id,
    points: (a, b) => b.points - a.points || a.order - b.order,
    // Rarest by how many people have it in hardcore, which is what the site's
    // own rarity is about. Fewest first.
    rare: (a, b) => (a.awardedHardcore || a.awarded) - (b.awardedHardcore || b.awarded)
                    || a.order - b.order,
  };

  /* How rare one is, in the site's own terms: the share of the people who have
     played this game at all who have this. Left out entirely when the numbers
     to work it out are missing, rather than printed as 0%. */
  function rarity(a, players) {
    const got = a.awardedHardcore || a.awarded || 0;
    if (!players || !got) return "";
    return t("{n}% have this",
             { n: Math.max(0.1, (got / players) * 100).toFixed(1) });
  }

  const TYPES = {
    missable: "Missable",
    progression: "Progression",
    win_condition: "Win condition",
  };

  /** One row: badge, what it is called, what it asks of you, what it is worth.
   *
   *  The whole row is the link to its page - `data-ach` is the id, and each
   *  page wires its own click, since where a page opens is the app's business
   *  and the window's is not the same answer. */
  function rowHtml(a, players) {
    const badge = (a.unlocked ? a.badge : a.badgeLocked) || a.badge;
    const kind = TYPES[a.type];
    const rare = rarity(a, players);
    /* The row is the link to its page, and the arrow is a control inside it -
       hence the two nested pieces. Without the wrapper there is nowhere for
       the thread to open into that is not on top of the row itself. */
    return `
      <div class="achrow${a.unlocked ? " got" : ""}" data-ach="${a.id}">
        <div class="achmain" role="link" tabindex="0"
             title="${esc(t("Open this achievement on RetroAchievements"))}">
          ${badge ? `<img class="achbadge" src="${esc(badge)}" alt="" loading="lazy"
                       decoding="async" onerror="this.remove()">`
                  : `<span class="achbadge"></span>`}
          <span class="achtext">
            <span class="achname">${esc(a.title)}${
              kind ? `<span class="achkind ${esc(a.type)}">${esc(t(kind))}</span>` : ""}</span>
            <span class="achdesc">${esc(a.description)}</span>
          </span>
          <span class="achnums">
            <span class="achpoints">${esc(t("{n} pts", { n: a.points }))}${
              a.retropoints ? `<span class="achtrue">${
                esc(t("{n} RP", { n: a.retropoints }))}</span>` : ""}</span>
            ${rare ? `<span class="achrare">${esc(rare)}</span>` : ""}
          </span>
          <button class="achtalkbtn" type="button"
                  title="${esc(t("What people said about this one"))}"
                  aria-label="${esc(t("What people said about this one"))}"
                  aria-expanded="false">&#9662;</button>
        </div>
        <div class="achtalk" hidden></div>
      </div>`;
  }

  /* -- what people said about one of them --------------------------------

     Asked for per achievement, when the arrow on that row is pressed: a set
     of forty would be forty requests to answer a question nobody asked of
     thirty-nine of them.

     Most threads on a quiet achievement are the site's own bookkeeping, and
     the server marks those - see retro.comments. They are kept and made
     quieter rather than dropped: "promoted to the Core set" is the
     achievement's history, and somebody reading a thread for a hint can tell
     the two apart at a glance once they look different. */
  const when = (text) => {
    const at = Date.parse(text || "");
    return Number.isNaN(at) ? "" : new Date(at).toLocaleDateString();
  };

  function talkHtml(rows) {
    if (!rows.length) {
      return `<p class="achnothing">${esc(t("Nobody has commented on this one."))}</p>`;
    }
    return rows.map((c) => `
      <div class="achsaid${c.server ? " bot" : ""}">
        <span class="achsaidwho">${esc(c.user)}<span class="achsaidwhen">${
          esc(when(c.when))}</span></span>
        <span class="achsaidtext">${esc(c.text)}</span>
      </div>`).join("");
  }

  /** Open or shut one row's thread, fetching it the first time. */
  async function toggleComments(button) {
    const row = button.closest("[data-ach]");
    const panel = row?.querySelector(".achtalk");
    if (!panel) return;

    if (!panel.hidden) {
      panel.hidden = true;
      button.setAttribute("aria-expanded", "false");
      row.classList.remove("talking");
      return;
    }
    panel.hidden = false;
    row.classList.add("talking");
    button.setAttribute("aria-expanded", "true");
    if (panel.dataset.loaded) return;

    panel.innerHTML = `<p class="achnothing">${esc(t("Asking…"))}</p>`;
    let found;
    try {
      found = await fetch(`/api/achievements/comments?id=${
        encodeURIComponent(row.dataset.ach)}`).then((r) => r.json());
    } catch {
      found = { ok: false, reason: "unreachable" };
    }
    if (!found.ok) {
      panel.innerHTML = `<p class="achnothing">${
        esc(t(REASONS[found.reason] || REASONS.unreachable))}</p>`;
      return;
    }
    panel.dataset.loaded = "1";
    panel.innerHTML = talkHtml(found.comments || []);
  }

  /** The list, filtered and ordered as the two controls say. */
  function listHtml(found, filter, sort) {
    const shown = (found.achievements || [])
      .filter((a) => matches(a, filter))
      .sort(ORDER[sort] || ORDER.order);
    if (!shown.length) {
      return `<p class="achempty">${esc(t("None of them match that."))}</p>`;
    }
    return shown.map((a) => rowHtml(a, found.players || 0)).join("");
  }

  /* Yours, when the app knows who you are. Without a username the site will
     still list the set but cannot say what you have, and a column of locked
     badges would be a lie told in pictures - so the count says so instead. */
  const countText = (found) => (found.user
    ? t("{done} of {total} earned", { done: found.hardcore, total: found.total })
    : t("{n} achievements", { n: found.total }));

  const REASONS = {
    nokey: "Add your RetroAchievements Web API key in Settings → Cover art, and "
         + "this can list the set.",
    noset: "RetroAchievements has no achievement set for this game.",
    noachievements: "RetroAchievements has no achievements listed for this game.",
    badkey: "RetroAchievements would not accept your API key.",
    unreachable: "Could not reach RetroAchievements.",
  };

  window.Ach = { esc, matches, ORDER, rarity, TYPES, rowHtml, listHtml,
                 countText, REASONS, toggleComments };
})();
