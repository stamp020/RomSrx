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
  function rowHtml(a, players = 0) {
    const badge = (a.unlocked ? a.badge : a.badgeLocked) || a.badge;
    const kind = TYPES[a.type];
    const rare = rarity(a, players);
    /* The row is the link to its page, and the arrow is a control inside it -
       hence the two nested pieces. Without the wrapper there is nowhere for
       the thread to open into that is not on top of the row itself. */
    /* The badge is the link; the rest of the row opens the thread. Two
       targets in one row, and which is which follows what each one looks
       like: a picture of the achievement goes to the achievement, and the
       words about it open the words about it. */
    return `
      <div class="achrow${a.unlocked ? " got" : ""}" data-ach="${a.id}">
        <div class="achmain" role="button" tabindex="0"
             title="${esc(t("Show what people said about this one"))}">
          <span class="achbadgewrap">
            ${badge ? `<img class="achbadge achgoes" src="${esc(badge)}" alt=""
                         loading="lazy" decoding="async" onerror="this.remove()">`
                    : `<span class="achbadge"></span>`}
            ${badgeCard(a, players)}
          </span>
          <span class="achtext">
            <span class="achname"><span class="achgoes achlink">${esc(a.title)}</span>${
              kind ? `<span class="achkind ${esc(a.type)}">${esc(t(kind))}</span>` : ""}</span>
            <span class="achdesc">${esc(a.description)}</span>
            ${/* When you got it, under the description and smaller than it -
                  a footnote to the achievement rather than part of what it
                  asks of you. */
              a.unlocked && a.date
                ? `<span class="achwhen">${esc(t("Unlocked {when}",
                    { when: stamp(a.date) }))}</span>` : ""}
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
    if (panel.dataset.loaded) {
      toLatest(panel);
      return;
    }

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
    toLatest(panel);
  }

  /* Opened at the bottom. A thread arrives oldest first, as their site sends
     it, and the part anybody wants is the end of it - the hint somebody left
     last week, not the note about who uploaded the achievement in 2023. So
     the panel starts where the reading starts and scrolls up into the
     history, rather than making every reader scroll down past it. */
  function toLatest(panel) {
    /* Twice, and the first one straight away. Reading scrollHeight forces the
       panel to be laid out, so the assignment lands - where a frame-later
       assignment on its own can arrive while the panel is still the height it
       was when it was hidden, and scroll to nothing. The second is for
       anything that reflows after. */
    const bottom = () => { panel.scrollTop = panel.scrollHeight; };
    bottom();
    requestAnimationFrame(bottom);
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

  /* Two things worth saying above the list, when they are true.
   *
   * A set read from the copy kept on disk is as old as that copy - every
   * unlock in it was true when it was written down and may not be now, so it
   * says when rather than presenting itself as current.
   *
   * A revision is the one that matters: an author adding achievements can
   * take a mastery away, and the numbers changing under somebody with no
   * explanation is how that gets discovered the hard way. */
  function stateNote(found) {
    const bits = [];
    if (found?.offline) {
      const when = found.storedAt
        ? new Date(found.storedAt * 1000).toLocaleDateString() : "";
      bits.push(when
        ? t("RetroAchievements could not be reached — this is the list as it "
            + "stood on {date}.", { date: when })
        : t("RetroAchievements could not be reached — this is the list from "
            + "your last visit."));
    }
    if (found?.revised) {
      const was = found.revised.was || {};
      const now = found.revised.now || {};
      bits.push(was.total === now.total
        ? t("This set has been reworked since you last looked: {before} points "
            + "became {after}.", { before: was.points, after: now.points })
        : t("This set has changed since you last looked: {before} achievements "
            + "became {after}.", { before: was.total, after: now.total }));
    }
    return bits.join(" ");
  }

  const REASONS = {
    nokey: "Add your RetroAchievements Web API key in Settings → Cover art, and "
         + "this can list the set.",
    noset: "RetroAchievements has no achievement set for this game.",
    noachievements: "RetroAchievements has no achievements listed for this game.",
    badkey: "RetroAchievements would not accept your API key.",
    unreachable: "Could not reach RetroAchievements.",
  };

  /* The wall of badges under a game, in the order somebody reads it: what
     they have first and newest first among those, because the last thing you
     unlocked is the thing you are looking for - then everything still locked,
     left in the set's own order, which is the order it is meant to be played
     in. */
  function badgeOrder(rows) {
    const when = (a) => Date.parse(a.date || "") || 0;
    return [...rows].sort((a, b) => {
      if (!!a.unlocked !== !!b.unlocked) return a.unlocked ? -1 : 1;
      if (a.unlocked) return when(b) - when(a);
      return a.order - b.order || a.id - b.id;
    });
  }

  /* The day and the time, the way their own site prints an unlock: knowing it
     was Tuesday evening is part of remembering doing it. */
  const stamp = (text) => {
    const at = Date.parse((text || "").replace(" ", "T"));
    if (Number.isNaN(at)) return "";
    const when = new Date(at);
    return `${when.toLocaleDateString(undefined, {
      month: "short", day: "numeric", year: "numeric" })}, ${
      when.toLocaleTimeString(undefined, {
        hour: "numeric", minute: "2-digit" })}`;
  };

  /* What one badge is, in a card rather than in the browser's own tooltip.
     A native tooltip is a second of waiting, one grey font, no picture and no
     way to lay four facts out - and a wall of forty badges is exactly the
     place somebody is asking "what is this one" over and over. */
  function badgeCard(a, players) {
    const bits = [
      `${a.points} ${t("pts")}`,
      a.retropoints ? `${a.retropoints} ${t("RP")}` : "",
      rarity(a, players),
    ].filter(Boolean);
    const kind = TYPES[a.type];
    return `<span class="rawinpeek achpeek" aria-hidden="true">
      <img src="${esc((a.unlocked ? a.badge : a.badgeLocked) || a.badge)}" alt="">
      <span class="rawinpeektext">
        <b>${esc(a.title)}${kind ? `<span class="achkind ${esc(a.type)}">${
          esc(t(kind))}</span>` : ""}</b>
        ${a.description
          ? `<span class="rawinpeekdesc">${esc(a.description)}</span>` : ""}
        <span class="rawinpeekbits">${
          bits.map((one) => `<span>${esc(one)}</span>`).join("")}</span>
        <span class="rawinpeekbits rawinpeekdid"><span>${esc(a.unlocked
          ? (a.date ? t("Unlocked {when}", { when: stamp(a.date) })
                    : t("Unlocked"))
          : t("Still locked"))}</span></span>
      </span></span>`;
  }

  /** One game's set as a wall of badges. Shared so the owner's own games and
   *  a friend's look the same, because they are the same thing. */
  function badgesHtml(rows, players = 0) {
    return badgeOrder(rows).map((a) => `
      <span class="rawinbadgewrap">
        <a class="rawinbadge${a.unlocked ? " got" : ""}" data-url="${esc(a.url)}"
           data-title="${esc(a.title)}" role="link" tabindex="0">
          <img src="${esc((a.unlocked ? a.badge : a.badgeLocked) || a.badge)}"
               alt="" loading="lazy" onerror="this.remove()">
        </a>
        ${badgeCard(a, players)}
      </span>`).join("");
  }

  window.Ach = { esc, matches, ORDER, rarity, TYPES, rowHtml, listHtml,
                 countText, stateNote, REASONS, toggleComments,
                 badgeOrder, badgesHtml };
})();
