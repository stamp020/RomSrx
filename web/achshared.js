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

  /* A comment is often a hint with a link in it - a video of the trick, a
     forum thread arguing about the trigger - and those arrived as plain text
     nobody could follow without retyping them.

     Escaped first and linked second, never the other way round: the text is
     written by strangers, and building HTML out of it before it is escaped is
     how somebody's comment becomes somebody's script. The pattern therefore
     runs over text that is already safe, and what it wraps is safe too. */
  const LINK_RE = /\bhttps?:\/\/[^\s<>"']+/g;

  function linked(text) {
    return esc(text).replace(LINK_RE, (found) => {
      // A stop or a bracket at the end of a sentence is punctuation, not part
      // of the address.
      const trail = found.match(/[.,;:!?)\]]+$/);
      const url = trail ? found.slice(0, -trail[0].length) : found;
      return `<a class="achlink" href="${url}" data-link="${url}"
        >${url}</a>${trail ? trail[0] : ""}`;
    });
  }

  function talkHtml(rows) {
    if (!rows.length) {
      return `<p class="achnothing">${esc(t("Nobody has commented on this one."))}</p>`;
    }
    /* A face against each comment, and a way through to whoever wrote it.
       Worth having because a hint is only as good as who is giving it, and
       "is this person forty thousand points in or is this their first week"
       is a click away rather than a name to go and type into the site.

       The picture is at a predictable address on their media host, so a
       thread of twenty costs no extra requests of ours - and one that was
       never set 404s, which `onerror` turns back into the plain name rather
       than a broken image. The site's own bookkeeping rows have no author
       and get neither. */
    return rows.map((c) => {
      const face = c.avatar && c.profile
        ? `<a class="achface" href="${esc(c.profile)}"
             data-link="${esc(c.profile)}" title="${esc(c.user)}"
             ><img src="${esc(c.avatar)}" alt=""
                   onerror="this.remove()"></a>`
        : "";
      const who = c.profile
        ? `<a class="achsaidname" href="${esc(c.profile)}" data-link="${
             esc(c.profile)}">${esc(c.user)}</a>`
        : esc(c.user);
      return `
      <div class="achsaid${c.server ? " bot" : ""}">
        ${face}
        <span class="achsaidwho">${who}<span class="achsaidwhen">${
          esc(when(c.when))}</span></span>
        <span class="achsaidtext">${linked(c.text)}</span>
      </div>`;
    }).join("");
  }

  /* Opened in the reader's own browser rather than in here. This window is a
     list of achievements next to a running game; following a link into it
     would replace that with a web page and there is no way back - it has no
     address bar and no back button, on purpose.

     Caught on the way up rather than bound per link, because a thread is
     drawn fresh every time it is opened. */
  document.addEventListener("auxclick", (ev) => {
    // Middle click too. The href is real - so the address can be copied out
    // of the context menu - which means without this it would open somewhere,
    // and in this window "somewhere" is a page with no way back.
    if (ev.button === 1
        && ev.target.closest("a.achlink, a.achface, a.achsaidname")) {
      ev.preventDefault();
    }
  });

  document.addEventListener("click", (ev) => {
    const link = ev.target.closest("a.achlink, a.achface, a.achsaidname");
    if (!link) return;
    ev.preventDefault();
    const url = link.dataset.link || link.getAttribute("href") || "";
    if (!/^https?:\/\//i.test(url)) return;
    fetch("/api/browse/open", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }).catch(() => { /* no browser configured; nothing useful to say */ });
  });

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

  /* -- how big the rows are drawn ------------------------------------------

     One number scaling one CSS variable, which the stylesheet applies to
     `.achlist` - so it reaches every place the list is drawn rather than the
     one it was written for. The comments scale with it: they are the smallest
     text on the row and the likeliest reason somebody reached for the slider.

     Remembered in localStorage rather than the app's settings, and shared by
     every window: it is a property of the screen and the distance somebody is
     sitting at, not of one window, and having the popped-out list disagree
     with the panel it came from would read as a bug. */
  const ZOOM_KEY = "romsrx.achZoom";

  function zoomSaved() {
    try { return Number(localStorage.getItem(ZOOM_KEY)) || 100; } catch {
      return 100;                      // private browsing, or no storage
    }
  }

  function applyZoom(percent) {
    const size = Math.min(180, Math.max(80, Number(percent) || 100));
    document.documentElement.style.setProperty("--achscale", size / 100);
    try { localStorage.setItem(ZOOM_KEY, String(size)); } catch { /* as above */ }
    return size;
  }

  /** Wire a range input to the scale, starting it where it was left. */
  function wireZoom(input) {
    if (!input) return;
    input.value = String(applyZoom(zoomSaved()));
    input.addEventListener("input", (ev) => applyZoom(ev.target.value));
  }

  /* -- the other boards built on one game -----------------------------------

     RetroAchievements calls them subsets and gives each its own id: "Donkey
     Kong Country [Subset - Bonus]" is a separate set from Donkey Kong
     Country. Drawn the way the site draws them - the icons in a row, the
     chosen one marked, what it is worth underneath - because a subset's icon
     is usually a variation on the game's, and picking the one with the star
     off a row is a glance where reading four near-identical names is a task.

     Here rather than in the window's own script so the panel inside the app
     gets the same strip. Both hand in their own elements and their own "now
     show this set instead"; everything else is common. */
  function setsFigures(one) {
    // "114 achievements worth 688 points (1,979 · ×2.88)", the site's own
    // line. The bracket is the RetroPoints and the ratio between them - what
    // a set is worth against what it costs, which is what people compare
    // subsets on. Left out when the set could not be priced up.
    const n = (value) => Number(value || 0).toLocaleString();
    const bits = [t("{n} achievements", { n: n(one.achievements) })];
    if (one.points) bits.push(t("worth {n} points", { n: n(one.points) }));
    if (one.retropoints) {
      const ratio = one.points
        ? ` · ×${(one.retropoints / one.points).toFixed(2)}` : "";
      bits.push(`(${n(one.retropoints)}${ratio})`);
    }
    return bits.join(" ");
  }

  function paintSets(row, says, sets, current) {
    row.innerHTML = sets.map((one) => {
      const name = one.part || t("Base Set");
      const here = one.id === current;
      // The name lives in the tooltip and under the row, not on the icon:
      // four icons fit across a narrow window and four names do not.
      return `<button class="achseticon${here ? " on" : ""}" role="tab"
                aria-selected="${here}" data-set="${one.id}"
                title="${esc(name)}">${
        one.icon ? `<img src="${esc(one.icon)}" alt="" loading="lazy">`
                 : `<span class="achseticontext">${esc(name.slice(0, 2))}</span>`
      }</button>`;
    }).join("");
    const chosen = sets.find((one) => one.id === current);
    says.textContent = chosen
      ? `${chosen.part || t("Base Set")} — ${setsFigures(chosen)}` : "";
  }

  /** Fetch the sets for `game` and draw them, or hide the strip if there is
   *  only one. Answers the list, so the caller can keep it for redraws. */
  async function offerSets(strip, row, says, game) {
    if (!strip) return [];
    let related;
    try {
      related = await fetch(`/api/achievements/related?id=${game}`)
        .then((r) => r.json());
    } catch {
      return [];                                // no list is not a failure
    }
    const sets = related?.sets || [];
    // One set is not a choice, and a strip of one icon is furniture.
    if (sets.length < 2) {
      strip.hidden = true;
      return sets;
    }
    paintSets(row, says, sets, game);
    strip.hidden = false;
    return sets;
  }

  window.Ach = { esc, matches, ORDER, rarity, TYPES, rowHtml, listHtml,
                 countText, stateNote, REASONS, toggleComments,
                 badgeOrder, badgesHtml,
                 ZOOM_KEY, applyZoom, zoomSaved, wireZoom,
                 setsFigures, paintSets, offerSets };
})();
