/* ---------- controller support ----------

   A gamepad drives the page the mouse already built: the stick moves the
   browser's own focus between real elements and A presses whatever it lands
   on. Nothing here reimplements a screen or a menu, so anything added to the
   app later is reachable from the pad without being told about it.

   Typing is the one thing a pad genuinely cannot do, which is what the
   on-screen keyboard at the bottom of this file is for.

   Loaded after app.js: top-level `const`/`let` in a classic script go into the
   shared global scope, so `els`, `showTop`, `navBack` and friends are all in
   hand here. */

const PAD_DEADZONE = 0.55;     // stick past this counts as a direction
const PAD_FIRST_REPEAT = 400;  // ms a direction is held before it repeats
const PAD_REPEAT = 110;
const PAD_SCROLL_STICK = 26;   // px per frame at full deflection

/* Standard-mapping indices. Every pad the browser recognises reports this same
   layout whatever is printed on the plastic, so the names here are positions,
   not labels: `face0` is the bottom face button, which is Cross on a
   PlayStation pad and A on an Xbox one. What each one is *called* is decided
   later, by PAD_LABELS, once we know whose controller it is. */
const PAD_BUTTONS = {
  face0: 0, face1: 1, face2: 2, face3: 3,
  l1: 4, r1: 5, l2: 6, r2: 7,
  select: 8, start: 9,
  up: 12, down: 13, left: 14, right: 15,
};

// Held down, these keep firing; the rest act once per press. The shoulders are
// deliberately not in here - one press, one step, so walking the header can't
// run away from you.
const PAD_REPEATS = new Set(["up", "down", "left", "right"]);

/* Whose controller is this? The id string is all we get, and every browser
   writes it differently:

     Chromium   Wireless Controller (STANDARD GAMEPAD Vendor: 054c Product: 09cc)
     Firefox    054c-09cc-Wireless Controller

   Firefox is the one that matters on Linux, where the app runs in the default
   browser rather than in a window of its own - so both spellings of the vendor
   id are read, and only after that do we fall back to words. Words alone are
   no good: "Wireless Controller" is what a DualShock 4 calls itself and says
   nothing. Anything unrecognised gets the Xbox legend, which is what an
   unbranded pad almost always turns out to be. */
const PAD_VENDORS = { "054c": "ps", "057e": "nintendo", "045e": "xbox" };

function padBrand(id) {
  const text = (id || "").toLowerCase();
  for (const [vendor, brand] of Object.entries(PAD_VENDORS)) {
    // "vendor: 054c" (Chromium) or a leading "054c-09cc-" (Firefox).
    if (new RegExp(`vendor:\\s*${vendor}|(^|[^0-9a-f])${vendor}-[0-9a-f]{4}`)
      .test(text)) return brand;
  }
  if (/dualsense|dualshock|playstation|\bps[345]\b|\bsony\b/.test(text)) return "ps";
  if (/nintendo|switch|joy-con|pro controller/.test(text)) return "nintendo";
  return "xbox";
}

/* What each position is called, per brand. Nintendo's face buttons sit in the
   mirror image of everyone else's, so position 0 - the bottom one - really is
   B there, and labelling it A would send people to the wrong button. */
const PAD_LABELS = {
  xbox: { face0: "A", face1: "B", face2: "X", face3: "Y",
          l1: "LB", r1: "RB", l2: "LT", r2: "RT",
          select: "View", start: "Menu" },
  ps: { l1: "L1", r1: "R1", l2: "L2", r2: "R2",
        select: "Share", start: "Options" },
  nintendo: { face0: "B", face1: "A", face2: "Y", face3: "X",
              l1: "L", r1: "R", l2: "ZL", r2: "ZR",
              select: "−", start: "+" },
};

/* PlayStation's four are shapes, not letters, and as characters they refused
   to sit still: ✕ ○ □ △ are drawn on wildly different baselines and at
   different weights, so centring the text box left every one of them visibly
   off-centre in its badge and none of them the same size. Drawn as paths they
   are all built on the same 24x24 box around a common centre, which is the
   only way to get four different shapes to look like a matched set.

   The triangle is nudged up a hair: a shape with all its mass along the bottom
   edge reads as low when its bounding box is centred. */
const PAD_PS_SHAPES = {
  face0: `<svg viewBox="0 0 24 24"><path d="M7 7l10 10M17 7L7 17"/></svg>`,
  face1: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="6.2"/></svg>`,
  face2: `<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="1.6"/></svg>`,
  face3: `<svg viewBox="0 0 24 24"><path d="M12 5.4l6.4 12.1H5.6z"/></svg>`,
};

// ...and their colours, straight off the controller. Everything else stays
// monochrome, because the real buttons are.
const PAD_FACE_TINT = {
  face0: "ps-cross", face1: "ps-circle",
  face2: "ps-square", face3: "ps-triangle",
};

/* The sticks. One outline for the gate and a filled dot for the top, with the
   side lettered beside it - which is how they are marked on every pad, and
   reads at a glance where "Stick" alone did not say which one. */
const PAD_STICK = `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/>`
  + `<circle cx="12" cy="12" r="3.2" fill="currentColor" stroke="none"/></svg>`;

/* The legend, in the order it reads along the header. Several names on one
   entry means a set that does one job between them. */
const PAD_LEGEND = [
  [["face0"], "Select"],
  [["face1"], "Back"],
  [["face2"], "Keyboard"],
  [["face3"], "Options"],
  [["l1", "r1"], "Header"],
  [["l2"], "Search"],
  [["r2"], "Library"],
  [["select"], "Download list"],
  [["start"], "Downloads"],
  [["stickL"], "Move"],
  [["stickR"], "Scroll"],
];

/* What the focus ring may land on. `[data-path]` is in here for the library's
   tiles and rows, which are plain divs - they are made focusable on demand
   rather than carrying a tabindex, so the tab order a keyboard user gets is
   left exactly as it was. */
const PAD_FOCUSABLE = [
  "a[href]", "button:not(:disabled)", "input:not(:disabled)",
  "select:not(:disabled)", "textarea:not(:disabled)", "summary",
  '[tabindex]:not([tabindex="-1"])', "[data-path]",
].join(",");

// Fields the on-screen keyboard can type into.
const PAD_TYPABLE =
  'input[type="text"], input[type="search"], input[type="email"], '
  + 'input[type="password"], input[type="url"], input:not([type]), textarea';

/* ---------- reading the pad ---------- */

const padDue = new Map();      // control name -> when it may fire again
let padFrame = null;
let padMenuOrigin = null;      // what a context menu was opened from

function padSnapshot() {
  const pads = navigator.getGamepads ? [...navigator.getGamepads()] : [];
  const live = pads.filter((p) => p && p.connected);
  if (!live.length) return null;

  const on = {};
  for (const name of Object.keys(PAD_BUTTONS)) on[name] = false;
  let scroll = 0;

  for (const pad of live) {
    const pressed = (i) => !!pad.buttons[i]?.pressed;
    for (const [name, index] of Object.entries(padLayout(pad))) {
      if (pressed(index)) on[name] = true;
    }

    // The left stick doubles as the d-pad; the right one scrolls.
    const [ax = 0, ay = 0] = pad.axes;
    if (ay < -PAD_DEADZONE) on.up = true;
    if (ay > PAD_DEADZONE) on.down = true;
    if (ax < -PAD_DEADZONE) on.left = true;
    if (ax > PAD_DEADZONE) on.right = true;

    const ry = pad.axes[padRightStickAxis(pad)] || 0;
    if (Math.abs(ry) > 0.2) scroll += ry;

    padReadHat(pad, on);
  }
  return { on, scroll };
}

/* ---------- pads the browser didn't normalise ----------

   Standard mapping is a promise about which index is which, and on Linux it is
   often not kept: Firefox reports `mapping: ""` for most pads, and the kernel's
   own layout comes through instead. Two things move when that happens, and
   both are worth handling because the alternative is a controller that scrolls
   when you pull a trigger and has no d-pad at all. */

/* A DualShock/DualSense as the Linux kernel presents it, when the browser has
   not normalised the pad. The raw order starts at Square, so read with the
   standard indices Cross would open the keyboard and Square would select -
   which is what "the gamepad does the wrong things on Linux" looks like.

   The d-pad is deliberately absent: these pads report it as the hat axis
   handled below, not as buttons. */
const PAD_SONY_RAW = {
  face0: 1, face1: 2, face2: 0, face3: 3,
  l1: 4, r1: 5, l2: 6, r2: 7,
  select: 8, start: 9,
};

/** Which index is which, for this particular pad. */
function padLayout(pad) {
  if (pad.mapping === "standard") return PAD_BUTTONS;
  return padBrand(pad.id) === "ps" ? PAD_SONY_RAW : PAD_BUTTONS;
}

/** Vertical axis of the right stick.
 *
 *  Standard mapping puts it at 3. The evdev layout Linux hands over unmapped
 *  is LX LY LT RX RY RT, which puts it at 4 - and reading 3 there would be the
 *  right stick's *horizontal* axis, so pushing sideways would scroll. */
function padRightStickAxis(pad) {
  return pad.mapping !== "standard" && pad.axes.length >= 6 ? 4 : 3;
}

/** D-pad reported as a hat axis rather than as buttons 12-15.
 *
 *  Unmapped pads on Linux commonly expose the d-pad as a single extra axis
 *  encoding eight directions, with a value outside the circle meaning centred.
 *  Without this the d-pad simply does nothing, which on a controller-driven
 *  page means the stick is the only way to move. */
function padReadHat(pad, on) {
  if (pad.buttons.length > 15) return;      // real d-pad buttons; nothing to do
  const hat = pad.axes[9];
  if (typeof hat !== "number" || hat > 1.1 || hat < -1.1) return;

  // -1 is up, and it sweeps clockwise through eight positions from there.
  const step = Math.round((hat + 1) * 3.5);
  if (step === 7 || step === 0 || step === 1) on.up = true;
  if (step >= 1 && step <= 3) on.right = true;
  if (step >= 3 && step <= 5) on.down = true;
  if (step >= 5 && step <= 7) on.left = true;
}

/** True on the frame a control should act: once when first pressed, then
 *  again on a repeat interval for the ones that are held. */
function padFired(name, pressed, now) {
  if (!pressed) { padDue.delete(name); return false; }
  if (!padDue.has(name)) {
    padDue.set(name, PAD_REPEATS.has(name) ? now + PAD_FIRST_REPEAT : Infinity);
    return true;
  }
  const due = padDue.get(name);
  if (now < due) return false;
  padDue.set(name, now + PAD_REPEAT);
  return true;
}

function padLoop() {
  const state = padSnapshot();
  if (!state) { padFrame = null; padDue.clear(); return; }

  /* A controller is read by whatever page asks, focused or not - it is not
     routed to the foreground window the way a keyboard is. So a PlayStation
     pad being used in a game, or just resting with a stick off-centre, was
     quietly driving this page behind everything else.

     The presses are still *read* while we are in the background, so that a
     button held across an alt-tab is already accounted for and doesn't fire
     the moment you come back. They simply aren't acted on. */
  const listening = document.hasFocus();

  const now = performance.now();
  for (const [name, pressed] of Object.entries(state.on)) {
    if (padFired(name, pressed, now) && listening) padPress(name);
  }
  if (state.scroll && listening) {
    padWoke();     // the right stick counts as picking the pad up too
    padScroll(state.scroll * PAD_SCROLL_STICK);
  }

  padFrame = requestAnimationFrame(padLoop);
}

function padStart() {
  if (padFrame === null) padFrame = requestAnimationFrame(padLoop);
}

/* ---------- what the buttons do ---------- */

/** Share and Options are the only two that work as a switch: the button that
 *  opened a panel shuts it again. They are shortcuts to a place rather than
 *  actions, and reaching for Circle to undo a press of the same button reads
 *  as a longer way round. */
function padTogglePanel(dialog, button) {
  if (dialog.open) { dialog.close(); return; }
  if (!button.disabled) button.click();
}

function padPress(name) {
  padWoke();      // a button press means the pad is the thing in their hands
  switch (name) {
    case "up": case "down": case "left": case "right":
      padMove(name);
      return;
    case "face0":
      padActivate();
      return;
    case "face1":
      padBack();
      return;
    case "face2": {
      if (isShown(osk)) { closeKeyboard(); return; }
      const field = padTypeTarget();
      if (field) { openKeyboard(field); return; }
      // Nothing here to type into - so go where there is something, which is
      // what asking for a keyboard from the library means in practice.
      if (!els.searchBtn.disabled && !document.querySelector("dialog[open]")) {
        goToSearch();
        openKeyboard(els.q);
      }
      return;
    }
    case "face3":
      padContextMenu();
      return;
    case "l1":
      padHeaderStep(-1);
      return;
    case "r1":
      padHeaderStep(1);
      return;
    case "l2":
      if (!els.searchBtn.disabled) goToSearch();
      return;
    case "r2":
      if (!els.libBtn.disabled) els.libBtn.click();
      return;
    case "select":
      padTogglePanel(els.cartDlg, els.cartBtn);
      return;
    case "start":
      padTogglePanel(els.dlDlg, els.dlBtn);
      return;
    default:
  }
}

/* ---------- the legend ---------- */

// Shapes carry no text, so each says out loud what it is.
const PAD_PS_NAMES = { face0: "Cross", face1: "Circle",
                       face2: "Square", face3: "Triangle" };

function padKeyHtml(brand, name) {
  if (name === "stickL" || name === "stickR") {
    const side = name === "stickL" ? "L" : "R";
    return `<span class="padkey padstick" role="img"
      aria-label="${side === "L" ? "Left" : "Right"} stick"
      >${PAD_STICK}${side}</span>`;
  }
  if (brand === "ps" && PAD_PS_SHAPES[name]) {
    return `<span class="padkey round ${PAD_FACE_TINT[name]}" role="img"
      aria-label="${PAD_PS_NAMES[name]}">${PAD_PS_SHAPES[name]}</span>`;
  }
  const labels = PAD_LABELS[brand] || PAD_LABELS.xbox;
  const round = name.startsWith("face") ? " round" : "";
  return `<span class="padkey${round}">${esc(labels[name] || name)}</span>`;
}

/** Draw the legend for whichever pad is in hand. Redrawn on connect rather
 *  than built once, so swapping an Xbox pad for a PlayStation one relabels
 *  everything instead of lying about it. */
function padLegend(brand) {
  els.padHints.innerHTML = PAD_LEGEND.map(([names, what]) =>
    `<span class="padhint">${names.map((n) => padKeyHtml(brand, n)).join("")
      }${esc(what)}</span>`).join("");
  els.padHints.hidden = false;
}

/* Which input the page is dressed for. Plenty of people play with a pad in
   their lap and a mouse on the desk, and whichever they touched last is the
   one they are using - so the legend and the focus ring follow the hands
   rather than the cable. Switching back and forth costs nothing: the pad is
   still polled the whole time, it just stops shouting about itself. */
let padMode = false;
let padCurrentBrand = "xbox";

/* The on-screen keyboard belongs to the pad, so it goes away with it and comes
   back with it. Leaving it up once the mouse is in hand covers the page with
   something nobody is going to press; making them reopen it every time they
   pick the controller up again is just as annoying the other way. */
let padKeyboardWasOpen = false;
let padKeyboardField = null;

function padSetMode(on) {
  if (padMode === on) return;
  padMode = on;
  document.body.classList.toggle("padnav", on);

  if (on) {
    padLegend(padCurrentBrand);
    if (padKeyboardWasOpen && padKeyboardField?.isConnected) {
      openKeyboard(padKeyboardField);
    }
    padKeyboardWasOpen = false;
  } else {
    els.padHints.hidden = true;
    // Remembered before closing, since closing forgets which field it was on.
    padKeyboardWasOpen = isShown(osk);
    padKeyboardField = oskTarget;
    if (padKeyboardWasOpen) closeKeyboard();
  }
  measureHeader();       // the legend changes how tall the header is
}

/** A controller has turned up, or one has just been used again. The focus ring
 *  comes on - it is the cursor from here - the legend goes up, and the two
 *  chromeless ways back to the search stop pretending to be buttons, since the
 *  pad is not allowed to reach them. */
function padWoke(brand) {
  if (brand) padCurrentBrand = brand;
  padSetMode(true);
}

/* Real input only. Everything the pad does to the page it does through
   `.click()` and synthesised events, which arrive untrusted - taking those as
   "the mouse is back" would hide the legend the moment you pressed a button
   with it. */
let padLastPointer = null;

function padHandsOff(ev) {
  if (!ev.isTrusted || !padMode) return;
  if (ev.type === "mousemove") {
    // Scrolling and layout shifts replay a mousemove at the same spot; only a
    // pointer that has actually travelled counts as someone reaching for it.
    const at = `${ev.clientX},${ev.clientY}`;
    if (at === padLastPointer) return;
    padLastPointer = at;
  }
  padSetMode(false);
}

for (const type of ["mousemove", "mousedown", "wheel", "keydown", "touchstart"]) {
  addEventListener(type, padHandsOff, { passive: true, capture: true });
}

/* ---------- moving the focus ---------- */

/** Whatever is on top owns the pad: a question, then a context menu, then the
 *  keyboard, then the newest open dialog, then the page itself. The menus come
 *  high up because they are opened *over* a dialog and are the thing you just
 *  asked for. */
function padScope() {
  if (els.askDlg.open) return els.askDlg;
  if (isShown(els.libMenu)) return els.libMenu;
  if (isShown(els.coverMenu)) return els.coverMenu;
  if (isShown(els.addMenu)) return els.addMenu;
  if (isShown(osk)) return osk;
  const open = [...document.querySelectorAll("dialog[open]")];
  if (open.length) return open[open.length - 1];
  return document.body;
}

function padVisible(el) {
  if (el.disabled || el.closest("[inert]")) return false;
  // The logo and the app name are mouse affordances only. There are already
  // two ways to the search on the pad - L2 and the magnifier - and a ring
  // landing on the branding reads as a bug.
  if (el.closest("[data-nopad]")) return false;

  /* A collapsed result card is the trap here. The browser hides the contents
     of a closed <details> without touching display, visibility or the box: the
     Download button in an unopened card still reports a real 82x31 rect at a
     real position, several hundred of them stacked over the ones you can see.
     Moving down then landed on a button nobody could see, and every press
     after that found another invisible neighbour - which is what made the
     ring stop dead on the second result.

     checkVisibility() is the only thing that knows. Where it is missing -
     older WebKitGTK, which is what a Linux fallback can be - the same case is
     tested by hand. */
  if (typeof el.checkVisibility === "function") {
    if (!el.checkVisibility()) return false;
  } else {
    const details = el.closest("details");
    if (details && !details.open && !el.closest("summary")) return false;
  }

  const box = el.getBoundingClientRect();
  if (box.width < 2 || box.height < 2) return false;
  return getComputedStyle(el).visibility !== "hidden";
}

/* The page has two zones, and the stick treats them as separate places.
   Sweeping left or right along a row of results used to drift up into the
   header as soon as the row ran out, which put the ring somewhere you never
   asked to be. Sideways movement now stays in its own zone, and the header is
   reachable only by going up past everything else - or instantly, with the
   shoulder buttons. */
const padInHeader = (el) => !!el?.closest?.(".topbar");

function padTargets(scope) {
  return [...scope.querySelectorAll(PAD_FOCUSABLE)].filter(padVisible);
}

function padFocus(el) {
  if (!el) return;
  // Library tiles are divs; without a tabindex focus() is a no-op on them.
  if (el.tabIndex < 0 && !el.hasAttribute("tabindex")) {
    el.setAttribute("tabindex", "-1");
  }
  el.focus({ preventScroll: true });
  el.scrollIntoView({ block: "nearest", inline: "nearest" });
}

/** Nearest thing in that direction.
 *
 *  Two tiers. Anything that overlaps the line of travel - the same row when
 *  moving sideways, the same column when moving up or down - is considered
 *  first, nearest wins. Only when there is nothing at all in line does it look
 *  at candidates off to one side.
 *
 *  The tiers matter more than they sound. With a single blended score, one
 *  wide element could beat a correctly-aligned one just by being nearer:
 *  pressing right from the last filter chip jumped up into the search box,
 *  because the box is wide enough that its centre still counted as "to the
 *  right". Sorting by alignment first makes the ring go where you pointed. */
const PAD_OFF_LINE = 1e6;      // stand-in for "only if there is nothing else"

function padNearest(from, dir, list) {
  const a = from.getBoundingClientRect();
  const ax = (a.left + a.right) / 2, ay = (a.top + a.bottom) / 2;
  const sideways = dir === "left" || dir === "right";
  const sign = (dir === "right" || dir === "down") ? 1 : -1;

  let best = null;
  let bestScore = Infinity;
  for (const el of list) {
    if (el === from || from.contains(el) || el.contains(from)) continue;
    const b = el.getBoundingClientRect();
    const bx = (b.left + b.right) / 2, by = (b.top + b.bottom) / 2;

    const along = (sideways ? bx - ax : by - ay) * sign;
    if (along <= 1) continue;                       // not that way
    const off = sideways
      ? Math.max(0, a.top - b.bottom, b.top - a.bottom)
      : Math.max(0, a.left - b.right, b.left - a.right);

    const score = along + off * 3 + (off > 0 ? PAD_OFF_LINE : 0);
    if (score < bestScore) { bestScore = score; best = el; }
  }
  return best;
}

/** The header buttons, left to right. Document order is that order, and the
 *  branding is already filtered out by padVisible. */
const padHeaderTargets = () => padTargets(els.header);

/** L1 and R1: step along the header and nowhere else, wrapping at the ends.
 *  From anywhere else on the page the first press simply lands in the header -
 *  at the near end, so the direction you pressed is the direction you go. */
function padHeaderStep(delta) {
  const list = padHeaderTargets();
  if (!list.length) return;
  const at = list.indexOf(document.activeElement);
  if (at < 0) { padFocus(delta > 0 ? list[0] : list[list.length - 1]); return; }
  padFocus(list[(at + delta + list.length) % list.length]);
}

function padMove(dir) {
  const scope = padScope();
  const list = padTargets(scope);
  if (!list.length) return;

  const current = document.activeElement;
  const inside = current && current !== document.body && scope.contains(current)
    && padVisible(current);
  if (!inside) { padFocus(list[0]); return; }

  // A slider is a control in its own right: left and right set it rather than
  // stepping off it.
  if (current.type === "range" && (dir === "left" || dir === "right")) {
    const step = Number(current.step) || 1;
    current.value = String(Number(current.value)
      + (dir === "right" ? step : -step));
    current.dispatchEvent(new Event("input", { bubbles: true }));
    current.dispatchEvent(new Event("change", { bubbles: true }));
    return;
  }

  // On the page proper, the header and the body below it are separate zones.
  // Inside a dialog or a menu there is only ever one.
  if (scope === document.body) {
    const fromHeader = padInHeader(current);
    const sameZone = list.filter((el) => padInHeader(el) === fromHeader);
    const next = padNearest(current, dir, sameZone);
    if (next) { padFocus(next); return; }

    // Only once the zone is exhausted does the ring cross over, and only
    // vertically: up out of the top of the page, or down out of the header.
    if (dir === "up" && !fromHeader) {
      const into = padNearest(current, "up", list.filter(padInHeader));
      if (into) { padFocus(into); return; }
    } else if (dir === "down" && fromHeader) {
      const into = padNearest(current, "down",
        list.filter((el) => !padInHeader(el)));
      if (into) { padFocus(into); return; }
    }
    if (dir === "up" || dir === "down") {
      padScroll(dir === "down" ? window.innerHeight * 0.5
                               : -window.innerHeight * 0.5);
    }
    return;
  }

  const next = padNearest(current, dir, list);
  if (next) { padFocus(next); return; }
  // Nothing that way, so move the panel instead - the next row may simply not
  // have been scrolled into view yet.
  if (dir === "up" || dir === "down") {
    padScroll(dir === "down" ? window.innerHeight * 0.5
                             : -window.innerHeight * 0.5);
  }
}

/** The innermost thing that can actually scroll, so a list inside a dialog
 *  moves rather than the whole window. */
function padScrollHost() {
  const start = document.activeElement;
  for (let node = start; node && node !== document.body; node = node.parentElement) {
    const style = getComputedStyle(node);
    if (/(auto|scroll)/.test(style.overflowY)
        && node.scrollHeight > node.clientHeight + 2) return node;
  }
  const scope = padScope();
  if (scope !== document.body && scope.scrollHeight > scope.clientHeight + 2) {
    return scope;
  }
  return null;
}

function padScroll(amount) {
  const host = padScrollHost();
  if (host) host.scrollBy(0, amount); else window.scrollBy(0, amount);
}

/* ---------- pressing things ---------- */

function padActivate() {
  const el = document.activeElement;
  if (!el || el === document.body) { padMove("down"); return; }

  // Picking something off a context menu closes it, which would leave the ring
  // on a button that no longer exists. Put it back where the menu came from.
  if (el.closest("#libmenu, #covermenu")) {
    const origin = padMenuOrigin;
    el.click();
    if (origin?.isConnected && padVisible(origin)) padFocus(origin);
    return;
  }

  if (el.matches(PAD_TYPABLE)) { openKeyboard(el); return; }
  // A native dropdown can't be opened from script, so A steps through it.
  if (el.tagName === "SELECT") {
    el.selectedIndex = (el.selectedIndex + 1) % el.options.length;
    el.dispatchEvent(new Event("change", { bubbles: true }));
    return;
  }
  // The library only treats the artwork and the title as the game; the rest
  // of the tile is deliberately dead, so aim at the live part.
  if (el.matches("[data-path]")) {
    (el.querySelector(".libhit") || el).click();
    return;
  }
  el.click();
}

function padBack() {
  if (isShown(osk)) { closeKeyboard(); return; }
  if (isShown(els.libMenu) || isShown(els.coverMenu) || isShown(els.addMenu)) {
    closeMenus();
    if (padMenuOrigin?.isConnected && padVisible(padMenuOrigin)) {
      padFocus(padMenuOrigin);
    }
    return;
  }
  // A question is answered, not stepped back from: B is the safe answer,
  // which is Cancel when there is one and OK when the box only says something.
  if (els.askDlg.open) {
    (els.askCancel.hidden ? els.askOk : els.askCancel).click();
    return;
  }
  navBack();
}

/** The right mouse button, as a controller button.
 *
 *  Rather than reimplementing the menus, this fires the same `contextmenu`
 *  event a right-click would, aimed at the middle of whatever the ring is on -
 *  so the library's game menu, and the "save cover image" menu on any artwork,
 *  both open exactly as they do with a mouse, with no second code path to keep
 *  in step. The ring then moves into the menu, since padScope puts an open
 *  menu above everything else. */
function padContextMenu() {
  const el = document.activeElement;
  if (!el || el === document.body) return;
  padMenuOrigin = el;
  const box = el.getBoundingClientRect();
  el.dispatchEvent(new MouseEvent("contextmenu", {
    bubbles: true, cancelable: true, button: 2,
    clientX: Math.round(box.left + box.width / 2),
    clientY: Math.round(box.top + box.height / 2),
  }));
  // Whichever menu that opened, put the ring on its first entry.
  for (const menu of [els.libMenu, els.coverMenu, els.addMenu]) {
    if (!isShown(menu)) continue;
    const first = padTargets(menu)[0];
    if (first) padFocus(first);
    return;
  }
}

/** Which field the keyboard should type into: whatever has the focus if it
 *  takes text, otherwise the search box. */
function padTypeTarget() {
  const el = document.activeElement;
  if (el && el.matches?.(PAD_TYPABLE) && padVisible(el)) return el;
  if (!libraryOpen && !document.querySelector("dialog[open]")) return els.q;
  return null;
}

/* ---------- on-screen keyboard ----------

   Ten columns throughout, so every key lines up with the one above it and the
   stick walks the grid predictably. Letters carry their lower-case form in
   `data-base`; shift only rewrites the label and the character sent, which
   keeps the focus where it is instead of rebuilding the panel under it. */

const OSK_ROWS = [
  [..."1234567890"],
  [..."qwertyuiop"],
  [..."asdfghjkl@"],
  ["shift", ..."zxcvbnm,."],
  [..."-':/!?()&_"],
];

const osk = asPopover(document.createElement("div"));
osk.id = "osk";

let oskTarget = null;
let oskShift = false;

osk.innerHTML = `
  <div class="oskhead">
    <span class="osklabel" id="osklabel">Search</span>
    <span class="oskvalue" id="oskvalue"></span>
  </div>
  ${OSK_ROWS.map((row) => `<div class="oskrow">${row.map((key) => key === "shift"
      ? `<button class="oskkey oskmod" data-act="shift"
           title="Capitals" aria-label="Shift">&#8679;</button>`
      : `<button class="oskkey" data-base="${esc(key)}"
           data-key="${esc(key)}">${esc(key)}</button>`).join("")}</div>`).join("")}
  <div class="oskrow oskactions">
    <button class="oskkey oskspace" data-key=" ">space</button>
    <button class="oskkey" data-act="back" title="Backspace">&#9003;</button>
    <button class="oskkey" data-act="clear">clear</button>
    <button class="oskkey oskdone" data-act="done">done</button>
  </div>`;
document.body.append(osk);

const oskLabel = osk.querySelector("#osklabel");
const oskValue = osk.querySelector("#oskvalue");

function paintOsk() {
  for (const key of osk.querySelectorAll(".oskkey[data-base]")) {
    const base = key.dataset.base;
    if (!/[a-z]/.test(base)) continue;
    const char = oskShift ? base.toUpperCase() : base;
    key.dataset.key = char;
    key.textContent = char;
  }
  osk.querySelector('[data-act="shift"]').classList.toggle("on", oskShift);
  // What you have typed so far, spelled out down here - the field itself is
  // often behind the panel or off the top of the screen.
  oskValue.textContent = oskTarget
    ? (oskTarget.type === "password"
        ? "•".repeat(oskTarget.value.length)
        : oskTarget.value)
    : "";
}

/** The name of the field being typed into, for the panel's own heading. */
function oskFieldName(input) {
  const label = input.closest("label");
  const text = label?.childNodes[0]?.textContent?.trim();
  if (text) return text;
  return input.getAttribute("placeholder") || input.getAttribute("aria-label")
    || "Text";
}

function openKeyboard(input) {
  const field = input || els.q;
  if (!field || field.disabled) return;
  oskTarget = field;
  oskLabel.textContent = field === els.q ? "Search" : oskFieldName(field);
  oskShift = false;
  paintOsk();

  /* Moved into whatever dialog the field belongs to. A modal dialog makes
     everything outside its own subtree inert, so a keyboard parked in the body
     would be drawn over the dialog and quietly refuse every mouse click - the
     same trap the right-click menus have to step around. Being a popover is
     what keeps it positioned against the viewport once it is in there, rather
     than against the dialog's own transformed box. */
  const host = field.closest("dialog") || document.body;
  if (osk.parentElement !== host) {
    hideTop(osk);                 // moving a shown popover would close it anyway
    host.append(osk);
  }
  showTop(osk);
  document.body.classList.add("oskopen");
  padFocus(osk.querySelector(".oskkey"));
}

function closeKeyboard() {
  if (!isShown(osk)) return;
  hideTop(osk);
  document.body.classList.remove("oskopen");
  const field = oskTarget;
  oskTarget = null;
  if (field && field.isConnected) padFocus(field);
}

function oskEdges() {
  const field = oskTarget;
  const end = field.value.length;
  const start = field.selectionStart ?? end;
  const finish = field.selectionEnd ?? start;
  return [Math.min(start, finish), Math.max(start, finish)];
}

function oskSet(value, caret) {
  const field = oskTarget;
  field.value = value;
  // Rejected by types that have no selection to speak of, which is harmless -
  // the caret just stays at the end.
  try { field.setSelectionRange(caret, caret); } catch { /* no selection API */ }
  field.dispatchEvent(new Event("input", { bubbles: true }));
  paintOsk();
}

function oskType(text) {
  if (!oskTarget) return;
  const [start, end] = oskEdges();
  oskSet(oskTarget.value.slice(0, start) + text + oskTarget.value.slice(end),
         start + text.length);
}

function oskBackspace() {
  if (!oskTarget) return;
  const [start, end] = oskEdges();
  if (end > start) { oskSet(oskTarget.value.slice(0, start)
                            + oskTarget.value.slice(end), start); return; }
  if (!start) return;
  oskSet(oskTarget.value.slice(0, start - 1) + oskTarget.value.slice(start),
         start - 1);
}

// Mouse and touch work too, and pressing a key must not pull the caret out of
// the field - so the press is swallowed and the click handled on its own.
osk.addEventListener("mousedown", (ev) => ev.preventDefault());

osk.addEventListener("click", (ev) => {
  const key = ev.target.closest(".oskkey");
  if (!key || !oskTarget) return;

  if (key.dataset.key !== undefined) { oskType(key.dataset.key); return; }
  switch (key.dataset.act) {
    case "shift": oskShift = !oskShift; paintOsk(); return;
    case "back": oskBackspace(); return;
    case "clear": oskSet("", 0); return;
    case "done": closeKeyboard(); return;
    default:
  }
});

// Esc closes it like any other overlay, and a dialog closing takes the
// keyboard it was opened from with it.
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") closeKeyboard();
});
for (const dialog of document.querySelectorAll("dialog")) {
  dialog.addEventListener("close", () => {
    if (oskTarget && !oskTarget.isConnected) { hideTop(osk); oskTarget = null; }
    else if (oskTarget && oskTarget.closest("dialog") === dialog) closeKeyboard();
  });
}

/* ---------- wiring ---------- */

const livePads = () =>
  (navigator.getGamepads ? [...navigator.getGamepads()] : [])
    .filter((p) => p && p.connected);

/** Connecting is what turns the whole thing on. The legend is relabelled for
 *  whichever pad arrived, so plugging in a different one is enough to correct
 *  it - no reload, no setting to find. */
function padArrived(ev) {
  padStart();
  padWoke(padBrand(ev?.gamepad?.id ?? livePads()[0]?.id));
}

addEventListener("gamepadconnected", padArrived);

addEventListener("gamepaddisconnected", () => {
  const rest = livePads();
  if (rest.length) { padLegend(padBrand(rest[0].id)); return; }
  // The last one has gone. The loop stops, but the legend and the focus ring
  // stay: the pad is usually back in a moment, and having the page change
  // shape underneath you every time a battery dies would be worse.
  if (padFrame !== null) {
    cancelAnimationFrame(padFrame);
    padFrame = null;
    padDue.clear();
  }
});

/* A pad already in hand when the page loads announces itself only once it is
   touched - Chromium reports nothing at all before that - so this catches the
   reload case, where the browser already knows about it. */
if (livePads().length) padArrived();

/* And a periodic look, because `gamepadconnected` cannot be relied on. Firefox
   does not always deliver it to a page that was already open, which on Linux
   is every page - the app opens in the system browser there rather than in a
   window of its own, and a pad that never announces itself is a pad that does
   nothing at all. One array read a second, and it stops mattering the moment
   the real loop is running. */
setInterval(() => {
  if (padFrame === null && livePads().length) padArrived();
}, 1000);
