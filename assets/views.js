// Aggregat: the newer website views, each drawn into the main area.
//   AggViews.finder   "Mod finder": device -> OS -> mods with a risk light (tested? recovery proven?)
//   AggViews.news     "New": catalogue entries and knowledge-base changes, newest first (export/web/news.json)
//   AggViews.tests    "Test your unit": stock tests anyone can run, with a prefilled report form
//   AggViews.addresses "Addresses": the RAM tenancy register as lanes, and every address the facts name
//   AggViews.project  the page of one catalogue entry (?p=<id>), the permalink every card links to
// Plain HTML; reads the global data object D that index.html loads. No dependencies.
(function () {
  "use strict";
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
  const list = s => String(s || "").split(",").filter(Boolean);
  const REPO = "https://github.com/70b185/Aggregat";
  const BLOB = REPO + "/blob/master/";
  const FORM = REPO + "/issues/new?template=test-result.yml";
  const short = (s, n) => { const t = String(s || "").replace(/\s+/g, " ").trim(); return t.length <= n ? t : t.slice(0, n - 1).replace(/\s+\S*$/, "") + " …"; };
  const devShort = (ctx, d) => (ctx.devName[d] || d).replace(/ \(.*\)$/, "");
  const devTag = (ctx, d) => `<span class="md-tag" style="--dc:var(--c-${esc(d)})">${esc(devShort(ctx, d))}</span>`;
  const own = p => { try { return JSON.parse(p.own_mods || "[]"); } catch (e) { return []; } };
  const isMod = p => list(p.list).includes("mods") && !["loader", "tool"].includes(p.kind) && !own(p).length;
  const TESTED = {unit: "tested on a unit", partly: "partly tested on a unit", emulator: "emulator only", "not-stated": "tests not stated"};
  const RECOVERY = {proven: "recovery proven on units", reported: "recovery reported once", documented: "recovery documented, never reported used", unknown: "recovery unknown"};

  // free-text device columns of the research map -> slugs
  const TXT_DEV = [[/\bDigitakt II\b|\bDT2\b/, "digitakt-2"], [/\bDigitone II\b|\bDN2\b/, "digitone-2"],
    [/\bDigitakt (mk1|MKI)\b|\bDT1\b|\bDT mk1\b|DT\/DN mk1/i, "digitakt"], [/\bDigitone (mk1|MKI)\b|\bDN1\b|\bDN mk1\b|DT\/DN mk1|Digitone Keys/i, "digitone"],
    [/\bSyntakt\b/, "syntakt"], [/Heat/, "analog-heat"], [/Octatrack/, "octatrack"], [/Rytm/, "analog-rytm"],
    [/\bA4\b|Analog Four|Analog Keys/, "analog-four-keys"], [/Model:Cycles/, "model-cycles"], [/Model:Samples/, "model-samples"],
    [/Machinedrum/, "machinedrum"], [/Monomachine/, "monomachine"]];
  const devsIn = t => /\ball four\b/i.test(t || "") ? ["digitakt-2", "digitakt", "digitone-2", "analog-heat"]
    : TXT_DEV.filter(([rx]) => rx.test(t || "")).map(([, s]) => s);

  // ---------------------------------------------------------------- mod finder
  const F = {dev: "", os: "", showAll: false};
  const OS_RX = /\b(\d\.\d{2}[A-Z]?)\b/g;   // Elektron OS numbers have two decimals (1.12, 1.10E); "1.0" is a mod's own version
  // device names as they appear in base_os texts ("Digitakt mk1 1.54; Digitone II 1.12", "1.73 (Rytm), 1.56 (Keys)")
  const OS_DEV = {"digitakt-2": /Digitakt ?(II|2)\b|\bDT2\b/g, "digitone-2": /Digitone ?(II|2)\b|\bDN2\b/g, "digitakt": /Digitakt(?! ?(II|2)\b)/g,
    "digitone": /Digitone(?! ?(II|2)\b)/g, "syntakt": /Syntakt/g, "analog-heat": /Heat/g, "octatrack": /Octatrack/g, "analog-rytm": /Rytm/g,
    "analog-four-keys": /Analog Four|\bA4\b|Keys/g, "model-cycles": /Cycles/g, "model-samples": /Samples/g, "machinedrum": /Machinedrum/g, "monomachine": /Monomachine/g};
  // the OS versions a mod names for one device: each version goes to the nearest device name in the text
  // (the one before it, or one right after it in brackets); a text without device names applies to every device
  function osFor(p, slug) {
    const t = String(p.base_os || ""), vers = [...t.matchAll(OS_RX)].filter(m => !/\bnot $/.test(t.slice(0, m.index))).map(m => ({v: m[1], i: m.index}));
    const names = list(p.devices).flatMap(d => OS_DEV[d] ? [...t.matchAll(OS_DEV[d])].map(m => ({d, i: m.index, e: m.index + m[0].length})) : []);
    if (!names.length) return vers.map(x => x.v);
    return vers.filter(x => {
      const after = names.filter(n => t.slice(x.i + x.v.length, n.i) === " (")[0];
      const before = names.filter(n => n.i < x.i).sort((a, b) => b.i - a.i)[0];
      const near = after || before || names[0];
      // "Digitakt mk1, Digitone mk1 / Keys OS 1.44": names in a row share the version that follows them
      const row = before ? names.filter(n => n.i <= before.i && !vers.some(y => y.i > n.i && y.i < before.i)) : [];
      return near.d === slug || (!after && row.some(n => n.d === slug));
    }).map(x => x.v);
  }
  function risk(p, dev) {
    const t = p.tested || "not-stated", rec = dev.recovery || "unknown";
    const recOk = rec === "proven" || rec === "reported";
    if (t === "unit" && recOk) return 0;
    if (t === "unit" || (t === "partly" && recOk)) return 1;
    return 2;
  }
  const RISK = [["low", "Lower risk", "the author reports it running on a unit, and stock recovery has been used on this device"],
                ["mid", "Some risk", "tested on a unit only in part, or recovery on this device has not been reported used"],
                ["high", "Higher risk", "emulator only or no test stated: you would be among the first on real hardware"]];

  function finder(root, D, ctx) {
    const mods = D.projects.concat(window.AggMods ? AggMods.ownMods(D) : []).filter(isMod)
      .filter(p => F.showAll || !["unreachable", "unverified", "request"].includes(p.status));
    const hosts = {};
    D.relations.forEach(r => { if (r.type === "mod_for") (hosts[r.project] = hosts[r.project] || []).push(r.target); });
    const byId = Object.fromEntries(D.projects.map(p => [p.id, p]));
    const via = p => p.platform ? (byId[p.platform] || {}).name : p.install || (hosts[p.id] || []).map(h => (byId[h] || {name: h}).name.replace(/\s*\(.*\)$/, "")).join(", ")
      || (["firmware"].includes(p.kind) ? "its own patcher" : "see its repo");
    const count = s => mods.filter(p => list(p.devices).includes(s)).length;
    const devCards = D.devices.map(d => `<button class="fd-dev${F.dev === d.slug ? " on" : ""}" data-d="${esc(d.slug)}" style="--dc:var(--c-${esc(d.slug)})">
        <b>${esc(devShort(ctx, d.slug))}</b><span>${count(d.slug)} mods</span><span class="fd-rec fd-rec-${esc(d.recovery)}">${esc(RECOVERY[d.recovery] || "")}</span></button>`).join("");
    let body = "";
    if (F.dev) {
      const dev = D.devices.find(d => d.slug === F.dev);
      const dm = mods.filter(p => list(p.devices).includes(F.dev));
      const versions = [...new Set(dm.flatMap(p => osFor(p, F.dev)))].sort((a, b) => b.localeCompare(a, "en", {numeric: true}));
      const fits = p => !F.os || osFor(p, F.dev).includes(F.os);
      const shown = dm.filter(fits);
      const noOs = F.os ? dm.filter(p => !osFor(p, F.dev).length) : [];
      const groups = [0, 1, 2].map(r => shown.filter(p => risk(p, dev) === r));
      const nBugs = (D.stock_bugs || []).filter(b => list(b.devices).includes(F.dev)).length;
      const nInc = (D.incidents || []).filter(i => list(i.devices).includes(F.dev)).length;
      const card = p => {
        const r = risk(p, dev);
        return `<article class="md-card fd-card fd-r${r}" style="--dc:var(--c-${esc(F.dev)})">
          <div class="md-top"><span class="fd-light fd-l${r}" title="${esc(RISK[r][1])}"></span><span class="md-kind">${esc(p.kind === "firmware" ? "custom OS" : p.kind)}</span>
            ${p.status && p.status !== "active" ? `<span class="md-st">${esc(p.status)}</span>` : ""}<a class="md-date" href="?p=${esc(p.platform || p.id)}">details</a></div>
          <h3>${p.repo ? `<a href="${esc(p.repo)}">${esc(p.name)}</a>` : esc(p.name)}</h3>
          <div class="md-by">${esc(short(p.author, 60))}</div>
          <p>${esc(short(p.notes, 180))}</p>
          <div class="fd-why"><span class="fd-t fd-t-${esc(p.tested || "not-stated")}">${esc(TESTED[p.tested || "not-stated"])}</span>
            ${p.tested_note ? `<span class="md-note">${esc(short(p.tested_note, 120))}</span>` : ""}</div>
          <div class="md-foot"><span class="md-via">via ${esc(via(p))}</span></div>
          ${p.base_os ? `<div class="md-os">needs ${esc(short(p.base_os, 90))}</div>` : `<div class="md-os">OS version not stated</div>`}
        </article>`;
      };
      body = `
        <div class="fd-step"><span class="fd-n">2</span> Which OS is on your ${esc(devShort(ctx, F.dev))}? <span class="meta">(SETTINGS &gt; SYSTEM &gt; OS INFO or similar)</span></div>
        <div class="fd-os">${["", ...versions].map(v => `<button class="${F.os === v ? "on" : ""}" data-os="${esc(v)}">${v ? "OS " + esc(v) : "show all"}</button>`).join("")}</div>
        <div class="fd-step"><span class="fd-n">3</span> Before you flash anything</div>
        <div class="cm-card fd-check">
          <p><b>Recovery on this device:</b> <span class="fd-rec fd-rec-${esc(dev.recovery)}">${esc(RECOVERY[dev.recovery])}</span> ${esc(dev.recovery_note || "")}</p>
          <ol>
            <li>Back up projects, sounds and the +Drive with Elektron Transfer.</li>
            <li>Keep the stock OS file for exactly your version, and a DIN MIDI interface: the startup-menu recovery listens to DIN MIDI only.</li>
            <li>Never cut the power during an update, including the restart right after it. First start of a new audio build: volume down.</li>
            <li>Read the mod's own install notes; they win over anything here.</li>
          </ol>
          <p class="meta"><a href="${BLOB}hardware/common/recovery.md">Recovery notes</a> · <a href="?t=stock_bugs&d=${esc(F.dev)}">${nBugs} known bugs in Elektron's own OS</a> (check before you blame a mod)
            · <a href="?t=incidents&d=${esc(F.dev)}">${nInc} things that went wrong on real units</a> · <a href="${BLOB}export/context/${esc(F.dev)}-brief.md">everything for agents</a></p>
        </div>
        <div class="fd-step"><span class="fd-n">4</span> ${shown.length} ${shown.length === 1 ? "mod" : "mods"}${F.os ? ` for OS ${esc(F.os)}` : ""}, by risk
          <label class="md-chk"><input type="checkbox" id="fd-all"${F.showAll ? " checked" : ""}> unreachable and unverified too</label></div>
        <p class="md-lead">The light is our reading of what the authors say, not a test of ours: green when a mod is reported running on a real unit and stock recovery has been used on this device. Mods are unofficial and can brick a unit.</p>
        ${groups.map((g, r) => g.length ? `<h2 class="md-h"><span class="fd-light fd-l${r}"></span>${RISK[r][1]} <span>${g.length} · ${RISK[r][2]}</span></h2><div class="md-grid">${g.map(card).join("")}</div>` : "").join("")}
        ${noOs.length ? `<h2 class="md-h">OS not stated <span>${noOs.length} mods for this device that name no OS version for it: check their repo</span></h2><div class="md-grid">${noOs.map(card).join("")}</div>` : ""}
        ${!shown.length && !noOs.length ? `<div class="empty">No mod for this OS version. Pick "show all" to see what exists for other versions.</div>` : ""}`;
    }
    root.innerHTML = `<p class="md-lead">Find mods that fit your unit and see how far each has been tested. Three steps; nothing to install.</p>
      <div class="fd-step"><span class="fd-n">1</span> Which device do you have?</div>
      <div class="fd-devs">${devCards}</div>${body}`;
    root.querySelector(".fd-devs").onclick = e => { const b = e.target.closest("button"); if (!b) return; F.dev = F.dev === b.dataset.d ? "" : b.dataset.d; F.os = ""; finder(root, D, ctx); };
    const os = root.querySelector(".fd-os"); if (os) os.onclick = e => { const b = e.target.closest("button"); if (!b) return; F.os = b.dataset.os; finder(root, D, ctx); };
    const all = root.querySelector("#fd-all"); if (all) all.onchange = e => { F.showAll = e.target.checked; finder(root, D, ctx); };
    const c = document.getElementById("count"); if (c) c.textContent = F.dev ? "" : `${mods.length} mods`;
  }

  // ---------------------------------------------------------------- what's new
  const N = {kind: "all"};
  function news(root, D, ctx) {
    const all = D.news || [];
    const words = ctx.words || [];
    let rows = all.filter(e => N.kind === "all" || e.type === N.kind)
      .filter(e => e.type === "update" || !(ctx.devs || []).length || ctx.devOk(e.devices || []))
      .filter(e => !words.length || words.every(w => [e.title, e.text, e.kind].join(" ").toLowerCase().includes(w)));
    const weeks = {};
    rows.forEach(e => { const d = new Date(e.date + "T00:00:00Z"); const wd = (d.getUTCDay() + 6) % 7;
      const k = new Date(d.getTime() - wd * 864e5).toISOString().slice(0, 10); (weeks[k] = weeks[k] || []).push(e); });
    const item = e => e.type === "project"
      ? `<div class="nw-item"><span class="nw-date">${esc(e.date.slice(5))}</span><div><a class="nw-title" href="?p=${esc(e.project)}">${esc(e.title.replace(/^New in the catalogue: /, ""))}</a>
          ${e.tested ? `<span class="fd-t fd-t-${esc(e.tested)}">${esc(TESTED[e.tested] || e.tested)}</span>` : ""}
          <div class="nw-text">${esc(e.text)}</div></div></div>`
      : `<div class="nw-item nw-up"><span class="nw-date">${esc(e.date.slice(5))}</span><div><a href="${esc(e.link)}">${esc(e.title)}</a> <span class="meta">knowledge base</span></div></div>`;
    root.innerHTML = `<p class="md-lead">What appeared in the catalogue and what changed in the knowledge base, newest first.
        Follow it in a feed reader: <a href="feed.xml">feed.xml</a> (Atom).</p>
      <div class="md-ctl">${[["all", "everything"], ["project", "new projects"], ["update", "knowledge-base changes"]]
        .map(([k, l]) => `<label class="md-chk"><input type="radio" name="nw" value="${k}"${N.kind === k ? " checked" : ""}> ${l}</label>`).join("")}</div>
      ${Object.keys(weeks).sort().reverse().map(w => `<h2 class="md-h">Week of ${esc(w)} <span>${weeks[w].length}</span></h2>${weeks[w].map(item).join("")}`).join("")
        || `<div class="empty">Nothing matches.</div>`}`;
    root.querySelectorAll("input[name=nw]").forEach(r => r.onchange = () => { N.kind = r.value; news(root, D, ctx); });
    const c = document.getElementById("count"); if (c) c.textContent = `${rows.length} of ${all.length}`;
  }

  // ---------------------------------------------------------------- test your unit
  function tests(root, D, ctx) {
    const words = ctx.words || [];
    const match = (t, devs) => (!(ctx.devs || []).length || ctx.devOk(devs)) && (!words.length || words.every(w => t.toLowerCase().includes(w)));
    const hyps = (D.hypotheses || []).filter(h => h.kind === "stock" && h.status === "open").map(h => ({...h, devs: devsIn(h.devices)}))
      .filter(h => match([h.id, h.inference, h.test, h.devices].join(" "), h.devs));
    const tasks = (D.tasks || []).filter(t => t.status === "open" && t.effort === "S" && /files|pdf|reading/i.test(t.needs))
      .map(t => ({...t, devs: devsIn(t.devices)})).filter(t => match([t.id, t.task, t.devices].join(" "), t.devs));
    const report = id => `${FORM}&title=${encodeURIComponent(`[Test result] ${id}: <device> <OS>`)}&test_id=${encodeURIComponent(id)}`;
    const issues = id => `${REPO}/issues?q=${encodeURIComponent(`is:issue "${id}" in:title`)}`;
    const md = window.AggMd || (s => esc(s));
    root.innerHTML = `
      <div class="cm-card tu-intro"><h3>Five minutes, no flashing, real help</h3>
        <p>Everything here runs on the <b>stock OS</b>. You need your unit, sometimes a computer or a phone camera. Each answer settles a
        question that mod developers are guessing about right now. A result that <b>contradicts</b> the expectation is just as useful.</p>
        <p class="meta">Report with the button on each card (the form opens on GitHub with the test filled in). Maintainers merge results by hand, with credit.</p></div>
      <h2 class="md-h">Stock tests <span>${hyps.length} open</span></h2>
      <div class="md-grid">${hyps.map(h => `<article class="md-card tu-card" style="--dc:var(--c-${esc(h.devs[0] || "")})">
          <div class="md-top"><span class="md-kind">${esc(h.id)}</span>${h.goals ? `<span class="md-st">goal ${esc(h.goals)}</span>` : ""}<span class="md-date">stock OS</span></div>
          <h3>${md(short(h.inference, 160), "hardware/HYPOTHESES.md")}</h3>
          <p><b>How:</b> ${md(h.test, "hardware/HYPOTHESES.md")}</p>
          <div class="md-foot">${h.devs.map(d => devTag(ctx, d)).join("")}</div>
          <div class="tu-act"><a class="tu-btn" href="${report(h.id)}">Report your result</a> <a class="meta" href="${issues(h.id)}">reports so far</a></div>
        </article>`).join("") || `<div class="empty">No stock test for this device yet.</div>`}</div>
      <h2 class="md-h">Small tasks without a unit <span>${tasks.length} open · files, a PDF or reading</span></h2>
      <div class="md-grid">${tasks.map(t => `<article class="md-card tu-card" style="--dc:var(--c-${esc(t.devs[0] || "")})">
          <div class="md-top"><span class="md-kind">${esc(t.id)}</span><span class="md-st">needs ${esc(t.needs)}</span><span class="md-date">effort ${esc(t.effort)}</span></div>
          <h3>${md(short(t.task, 200), "research/RESEARCH-MAP.md")}</h3>
          <p class="meta">${md(t.value, "research/RESEARCH-MAP.md")}</p>
          <div class="md-foot">${t.devs.map(d => devTag(ctx, d)).join("")}</div>
          <div class="tu-act"><a class="tu-btn" href="${report(t.id)}">Share what you found</a> <a class="meta" href="${BLOB}.github/CONTRIBUTING.md">how to contribute</a></div>
        </article>`).join("") || `<div class="empty">Nothing open.</div>`}</div>`;
    const c = document.getElementById("count"); if (c) c.textContent = `${hyps.length + tasks.length} things to do`;
  }

  // ---------------------------------------------------------------- addresses
  const A = {os: "", open: ""};
  const hex = v => "0x" + v.toString(16).padStart(8, "0");
  function addresses(root, D, ctx) {
    const devs = (ctx.devs || []).length ? ctx.devs : [];
    const ten = (D.ram_tenancy || []).filter(r => !devs.length || devs.includes(r.device));
    const q = (ctx.words || []).join(" ");
    const qhex = /^(0x)?[0-9a-f]{5,8}$/.test(q) ? parseInt(q.replace(/^0x/, ""), 16) : null;
    // lanes: one per memory space, one row per user
    const spaces = {};
    ten.forEach(r => { const k = r.device + "|" + r.space; (spaces[k] = spaces[k] || []).push(r); });
    const oses = [...new Set(ten.map(r => r.os).filter(o => o !== "both"))].sort();
    const lane = (k, rs) => {
      rs = rs.filter(r => !A.os || r.os === A.os || r.os === "both");
      if (!rs.length) return "";
      // scale to where the mods are: stock's large cleared range would squeeze everything else into a sliver
      const mine = rs.filter(r => r.user !== "stock"), M = 0x100000;
      const lo = mine.length ? Math.max(Math.min(...rs.map(r => r.start)), Math.floor(Math.min(...mine.map(r => r.start)) / M) * M - M) : Math.min(...rs.map(r => r.start));
      const hi = Math.max(...rs.map(r => r.end || r.start + 1));
      rs = rs.filter(r => (r.end || r.start + 1) > lo).map(r => r.start < lo ? {...r, start: lo, cut: true} : r);
      const span = Math.max(1, hi - lo), users = [...new Set(rs.map(r => r.user))];
      const x = v => ((v - lo) / span * 100).toFixed(3);
      const bar = r => { const e = r.end || r.start + 1, w = Math.max(0.35, (e - r.start) / span * 100);
        const hit = qhex !== null && qhex >= r.start && qhex < e;
        return `<span class="ad-bar${r.user === "stock" ? " ad-stock" : ""}${r.end ? "" : " ad-pt"}${hit ? " ad-hit" : ""}" style="left:${x(r.start)}%;width:${w.toFixed(3)}%"
          title="${esc(`${r.user}: ${r.cut ? "… " : hex(r.start)}-${r.end ? hex(r.end) : "?"} · ${r.use} · OS ${r.os} · [${r.evidence || "?"}]`)}"></span>`; };
      const [dev, space] = k.split("|");
      return `<div class="cm-card ad-lane"><h3>${esc(space)}</h3><p class="meta">${hex(lo)} … ${hex(hi)} · ${rs.length} ranges · hover a bar for details</p>
        ${qhex !== null && qhex >= lo && qhex < hi ? `<div class="ad-mark" style="left:calc(184px + (100% - 198px) * ${x(qhex) / 100})"></div>` : ""}
        ${users.map(u => `<div class="ad-row"><span class="ad-user">${esc(u)}</span><span class="ad-track">${rs.filter(r => r.user === u).map(bar).join("")}</span></div>`).join("")}
      </div>`;
    };
    // address list from the facts
    const facts = (D.facts || []).filter(f => f.addresses && (!devs.length || ctx.devOk(list(f.devices))));
    const at = {};
    facts.forEach(f => list(f.addresses).forEach(a => { const v = parseInt(a, 16); (at[v] = at[v] || []).push(f); }));
    let keys = Object.keys(at).map(Number).sort((a, b) => a - b);
    if (qhex !== null) keys = keys.filter(v => Math.abs(v - qhex) <= 0x10000);
    else if (q) keys = keys.filter(v => at[v].some(f => [f.text, f.section].join(" ").toLowerCase().includes(q)));
    const shown = keys.slice(0, 400);
    const claim = v => ten.filter(r => v >= r.start && v < (r.end || r.start + 1)).map(r => r.user);
    root.innerHTML = `<p class="md-lead">Which memory is whose. The lanes come from the <a href="${BLOB}hardware/RAM-TENANCY.md">RAM tenancy register</a>
        (mod platforms and stock, per OS); the list below is every address a hardware fact names. Type an address in the search box (e.g. <code>0x46800000</code>)
        to see who claims it and what is known nearby. Pick a device above to narrow it down.</p>
      ${oses.length ? `<div class="md-ctl"><span class="meta">OS:</span> ${["", ...oses].map(o => `<label class="md-chk"><input type="radio" name="ados" value="${esc(o)}"${A.os === o ? " checked" : ""}> ${o || "all"}</label>`).join("")}</div>` : ""}
      ${Object.entries(spaces).map(([k, rs]) => lane(k, rs)).join("") || (ten.length ? "" : `<div class="cm-card"><p class="meta">No tenancy register for this device yet: so far it covers the Digitone II and Digitakt II. <a href="${BLOB}hardware/RAM-TENANCY.md">Add yours.</a></p></div>`)}
      <h2 class="md-h">Addresses named in facts <span>${keys.length}${keys.length > shown.length ? `, first ${shown.length} shown` : ""}${qhex !== null ? " within ±64 KB" : ""}</span></h2>
      <div class="ad-list">${shown.map(v => { const fs = at[v], c = claim(v);
        return `<details class="ad-item"${A.open === String(v) || (qhex === v) ? " open" : ""} data-v="${v}"><summary><code>${hex(v)}</code>
          <span class="meta">${fs.length} fact${fs.length > 1 ? "s" : ""}</span> ${[...new Set(fs.flatMap(f => list(f.devices)))].map(d => devTag(ctx, d)).join("")}
          ${c.length ? `<span class="ad-claim">${esc([...new Set(c)].join(", "))}</span>` : ""}</summary>
          ${fs.map(f => `<div class="ad-fact"><a class="meta" href="${BLOB}${esc(f.file)}#L${f.line}">${esc(f.file.replace("hardware/", ""))}:${f.line}</a>
            ${list(f.evidence).map(e => `<span class="chip ev-${e === "?" ? "q" : esc(e)}">[${esc(e)}]</span>`).join(" ")}
            <div class="text">${(window.AggMd || esc)(short(f.text, 600), f.file)}</div></div>`).join("")}</details>`; }).join("") || `<div class="empty">No address matches.</div>`}</div>`;
    root.querySelectorAll("input[name=ados]").forEach(r => r.onchange = () => { A.os = r.value; addresses(root, D, ctx); });
    const c = document.getElementById("count"); if (c) c.textContent = `${ten.length} ranges · ${Object.keys(at).length} addresses`;
  }

  // ---------------------------------------------------------------- one project
  function project(root, D, ctx, id) {
    const all = D.projects.concat(window.AggMods ? AggMods.ownMods(D) : []);
    const p = all.find(x => x.id === id);
    if (!p) { root.innerHTML = `<div class="empty">No entry "${esc(id)}". It may have been renamed or merged; try the search.</div>`; return; }
    const byId = Object.fromEntries(all.map(x => [x.id, x]));
    const name = i => byId[i] ? byId[i].name : i;
    const rel = D.relations.filter(r => r.project === p.id).map(r => `<li>${esc(r.type.replace(/_/g, " "))} <a href="?p=${esc(r.target)}">${esc(name(r.target))}</a>${r.evidence ? ` <span class="meta">${esc(r.evidence)}</span>` : ""}</li>`)
      .concat(D.relations.filter(r => r.target === p.id).map(r => `<li><a href="?p=${esc(r.project)}">${esc(name(r.project))}</a> ${esc(r.type.replace(/_/g, " "))} this${r.evidence ? ` <span class="meta">${esc(r.evidence)}</span>` : ""}</li>`));
    let links = {}; try { links = JSON.parse(p.links || "{}"); } catch (e) {}
    let srcs = []; try { srcs = JSON.parse(p.sources || "[]"); } catch (e) {}
    const md = window.AggMd || (s => esc(s));
    const devs = list(p.devices).map(s => D.devices.find(d => d.slug === s)).filter(Boolean);
    const kv = [["Kind", p.kind === "firmware" ? "custom OS" : p.kind], ["Status", p.status], ["Tested", p.tested ? `${TESTED[p.tested] || p.tested}${p.tested_note ? ` (${p.tested_note})` : ""}` : ""],
      ["Base OS", p.base_os], ["Version", p.version], ["Licence", p.license || p.gh_license], ["Last activity", [p.last_activity, p.pushed && `pushed ${p.pushed.slice(0, 10)}`].filter(Boolean).join(" · ")],
      ["Created", p.created && p.created.slice(0, 10)], ["Stars", p.stars], ["In Aggregat since", p.first_seen], ["Install", p.install]].filter(([, v]) => v !== null && v !== undefined && v !== "");
    const ms = own(byId[p.platform] || p);
    root.innerHTML = `<article class="pj">
      <p class="meta"><a href="?t=mods">← all mods</a></p>
      <h2 class="pj-h">${esc(p.name)}</h2>
      <p class="md-by">${esc(p.author)}</p>
      <div class="md-foot">${devs.map(d => devTag(ctx, d.slug)).join("")}</div>
      <div class="pj-act">${p.repo ? `<a class="tu-btn" href="${esc(p.repo)}">Repository</a>` : ""}
        ${Object.entries(links).map(([k, v]) => [].concat(v).map(u => `<a class="md-x" href="${esc(u)}">${esc(k.replace(/_/g, " "))}</a>`).join(" ")).join(" ")}
        <button class="md-x" id="pj-copy">copy link</button></div>
      <div class="text pj-notes">${md(p.notes, "data/projects.yml")}</div>
      ${p.contains ? `<h3>What is inside</h3><p class="text">${esc(p.contains)}</p>` : ""}
      ${ms.length ? `<h3>Mods it ships (${ms.length})</h3><ul>${ms.map(m => `<li><b>${esc(m.name)}</b>${m.version ? " " + esc(m.version) : ""}: ${esc(m.what)} <span class="meta">${esc(TESTED[m.tested] || "tests not stated")}</span></li>`).join("")}</ul>` : ""}
      <dl class="pj-kv">${kv.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
      ${rel.length ? `<h3>Related entries</h3><ul>${rel.join("")}</ul>` : ""}
      ${["mod", "firmware", "loader"].includes(p.kind) ? `<div class="cm-card"><h3>Before you flash</h3>
        <ul>${devs.map(d => `<li>${esc(devShort(ctx, d.slug))}: <span class="fd-rec fd-rec-${esc(d.recovery)}">${esc(RECOVERY[d.recovery] || "")}</span>
          · <a href="?t=finder">mod finder</a> · <a href="?t=stock_bugs&d=${esc(d.slug)}">stock bugs</a> · <a href="${BLOB}export/context/${esc(d.slug)}-brief.md">agent pack</a></li>`).join("")}</ul>
        <p class="meta">Mods are unofficial and can brick a unit. Back up first, keep the stock OS file and a DIN MIDI interface at hand. <a href="${BLOB}hardware/common/recovery.md">Recovery notes</a>.</p></div>` : ""}
      ${srcs.length ? `<p class="meta">Sources: ${srcs.map(s => md(String(s), "data/projects.yml")).join(" · ")}</p>` : ""}
      <p class="meta">Something wrong or missing? <a href="${BLOB}data/projects.yml">Edit data/projects.yml</a> (search for <code>id: ${esc(p.platform || p.id)}</code>) or open an issue.</p>
    </article>`;
    const cp = root.querySelector("#pj-copy");
    cp.onclick = () => { const u = location.origin + location.pathname.replace(/p\/[^/]+\/?$/, "") + "p/" + encodeURIComponent(p.platform || p.id) + "/";
      (navigator.clipboard ? navigator.clipboard.writeText(u) : Promise.reject()).then(() => { cp.textContent = "copied"; }, () => { prompt("Link:", u); }); };
    document.title = `${p.name} - Aggregat`;
    const c = document.getElementById("count"); if (c) c.textContent = "";
  }

  window.AggViews = {finder, news, tests, addresses, project, devsIn};
})();
