// Aggregat network map: projects, the people behind them, device families and the relations between projects.
// Plain SVG and a small force layout; no libraries. Data: export/aggregat.json (projects, relations, devices).
// Loaded by index.html; exposes window.AggNetwork.draw(container, D, {words, dev, onOpen}).
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const list = s => String(s || "").split(",").filter(Boolean);

  // ---------------------------------------------------------------- colour encodings (max three hues + neutral)
  // groups follow the list a project is in, as on the community page
  const groupOf = p => { const l = String(p.list || "").split(","); return l.includes("mods") ? "mods" : l.includes("musician") ? "tools" : l.includes("dev") ? "research" : "other"; };
  const KIND_LABEL = {mods: "Mods and loaders", research: "Developer tools", tools: "Tools for musicians", other: "Other"};
  function licFamily(p) {
    const l = (p.license || p.gh_license || "").toLowerCase();
    if (/proprietary|all rights reserved|elastic|-nc\b|non-?commercial|see rule/.test(l)) return "restricted";
    if (!l || /not stated|unspecified|none|unknown|noassertion/.test(l)) return "none";
    if (/gpl|mpl|eupl|copyleft/.test(l)) return "copyleft";
    if (/cc0|unlicense|public domain/.test(l)) return "pd";
    if (/mit|bsd|apache|isc|zlib/.test(l)) return "permissive";
    return "none";
  }
  const LIC_LABEL = {permissive: "Permissive (MIT, BSD, Apache)", copyleft: "Copyleft (GPL, AGPL)", pd: "Public domain (CC0, Unlicense)",
                     restricted: "Restricted terms (closed, non-commercial)", none: "None stated or not recorded"};
  const SLOT = {mods: "var(--s1)", tools: "var(--s2)", research: "var(--s3)", other: "var(--s0)",
                permissive: "var(--s1)", copyleft: "var(--s2)", pd: "var(--s3)", restricted: "var(--s5)", none: "var(--s0)"};
  // Link kinds, in legend order: label, dash pattern, strong (dark ink) or quiet (muted ink)
  const REL = {
    vendors: ["vendors or ports code from", "", 1], fork_of: ["fork of", "2 3", 1], copy_of: ["copy of", "2 3", 0],
    port_of: ["port of", "", 0], variant_of: ["variant of", "", 0], same_project: ["same project as", "", 0],
    builds_on: ["builds on", "8 3", 1], bundles: ["bundles", "8 3", 0], mod_for: ["mod for (loader or platform)", "5 4", 0],
    uses_tool: ["uses as a tool (not shipped)", "5 3 1 3", 0], describes: ["describes", "1 3", 0], cites: ["credits or cites", "1 3", 0],
    unclear: ["relation unclear (same name)", "3 5", 0]};
  const REL_LABEL = Object.fromEntries(Object.entries(REL).map(([k, v]) => [k, v[0]]));

  // ---------------------------------------------------------------- state kept between draws
  const S = {opts: {rel: true, people: true, solo: false, devices: false, lonely: false, color: "device", size: "stars"},
             off: new Set(["cites", "uses_tool"]), sel: null, hover: null, needFit: true, view: {x: 0, y: 0, k: 1}, pos: {}, built: null};

  function build(D, devOk) {
    const famOf = {}; D.devices.forEach(d => famOf[d.slug] = d.family);
    const projects = D.projects.filter(p => devOk(list(p.devices)));
    const byId = {}; projects.forEach(p => byId[p.id] = p);
    const nodes = [], edges = [], N = {};
    const add = (id, o) => { if (!N[id]) { N[id] = Object.assign({id, deg: 0}, o); nodes.push(N[id]); } return N[id]; };
    const link = (a, b, type, extra) => { edges.push(Object.assign({a, b, type}, extra || {})); N[a].deg++; N[b].deg++; };
    projects.forEach(p => add("p:" + p.id, {t: "p", p, label: p.name}));
    if (S.opts.rel) D.relations.forEach(r => {
      if (byId[r.project] && byId[r.target] && !S.off.has(r.type)) link("p:" + r.project, "p:" + r.target, "rel", {rel: r.type, ev: r.evidence});
    });
    if (S.opts.people) {
      const owned = {};
      projects.forEach(p => { if (p.owner) (owned[p.owner] = owned[p.owner] || []).push(p); });
      Object.entries(owned).forEach(([o, ps]) => {
        if (ps.length < 2 && !S.opts.solo) return;
        add("o:" + o, {t: "o", owner: o, ps, label: o});
        ps.forEach(p => link("o:" + o, "p:" + p.id, "own"));
      });
    }
    if (S.opts.devices) projects.forEach(p => {
      [...new Set(list(p.devices).map(d => famOf[d] || d))].forEach(f => {
        add("d:" + f, {t: "d", fam: f, label: f});
        link("p:" + p.id, "d:" + f, "dev");
      });
    });
    const keep = nodes.filter(n => n.t !== "p" || n.deg > 0 || S.opts.lonely);
    const kept = new Set(keep.map(n => n.id));
    return {nodes: keep, edges: edges.filter(e => kept.has(e.a) && kept.has(e.b)), N, total: projects.length};
  }

  let CTX = {devs: []};   // the last draw context (selected devices)
  function colour(n) {
    if (n.t === "o") return "var(--person)";
    if (n.t === "d") return S.opts.color === "device" ? `var(--c-${n.id.slice(2)}, var(--chip))` : "var(--chip)";
    if (S.opts.color === "device") { const ds = list(n.p.devices); const d = ds.find(x => CTX.devs.includes(x)) || ds[0];
      return d ? `var(--c-${d}, var(--s0))` : "var(--s0)"; }
    if (S.opts.color === "licence") return SLOT[licFamily(n.p)];
    if (S.opts.color === "age") return n.p.created ? ageColour(n.p.created) : "var(--s0)";
    return SLOT[groupOf(n.p)];
  }
  const AGE_STEPS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];
  function ageColour(d) {
    // months before today, newest darkest: <1, <2, <3, <6, <12, <36, older
    const m = (Date.now() - Date.parse(d)) / 2.63e9;
    const i = m < 1 ? 6 : m < 2 ? 5 : m < 3 ? 4 : m < 6 ? 3 : m < 12 ? 2 : m < 36 ? 1 : 0;
    return AGE_STEPS[i];
  }
  function radius(n) {
    if (n.t === "d") return 16;
    if (n.t === "o") return 4 + Math.min(8, Math.sqrt(n.ps.length) * 2.2);
    if (S.opts.size === "stars") return 5 + Math.min(12, Math.sqrt(n.p.stars || 0) * 0.9);
    return 6;
  }

  // ---------------------------------------------------------------- force layout
  function layout(G, W, H, onTick, done) {
    const nodes = G.nodes, idx = {}; nodes.forEach((n, i) => { idx[n.id] = i; n.q = Math.min(2, Math.sqrt(1 + n.deg * 0.15)); });
    const E = G.edges.map(e => ({s: idx[e.a], t: idx[e.b], L: e.type === "own" ? 34 : e.type === "dev" ? 110 : 64,
                                 k: e.type === "dev" ? 0.015 : 0.06}));
    let alpha = Object.keys(S.pos).length ? 0.4 : 1, stopped = false;
    function step() {
      const n = nodes.length;
      for (let i = 0; i < n; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < n; j++) {
          const b = nodes[j];
          let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy;
          if (d2 > 90000) continue;
          if (d2 < 1) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; d2 = 1; }
          const f = 260 * alpha * a.q * b.q / d2;
          a.vx += dx * f; a.vy += dy * f; b.vx -= dx * f; b.vy -= dy * f;
        }
      }
      E.forEach(e => {
        const a = nodes[e.s], b = nodes[e.t];
        const dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 1;
        const f = (d - e.L) / d * e.k * alpha * 4;
        a.vx += dx * f; a.vy += dy * f; b.vx -= dx * f; b.vy -= dy * f;
      });
      nodes.forEach(a => {
        a.vx += (W / 2 - a.x) * 0.018 * alpha; a.vy += (H / 2 - a.y) * 0.018 * alpha;
        if (a.fixed) { a.vx = a.vy = 0; return; }
        a.vx *= 0.55; a.vy *= 0.55;
        a.x += Math.max(-20, Math.min(20, a.vx)); a.y += Math.max(-20, Math.min(20, a.vy));
      });
      alpha *= 0.985;
    }
    function frame() {
      if (stopped) return;
      for (let i = 0; i < 3; i++) step();
      onTick();
      if (alpha > 0.02) requestAnimationFrame(frame); else { nodes.forEach(n => S.pos[n.id] = {x: n.x, y: n.y}); done && done(); }
    }
    requestAnimationFrame(frame);
    return {stop() { stopped = true; nodes.forEach(n => S.pos[n.id] = {x: n.x, y: n.y}); }, heat() { if (alpha < 0.15) { alpha = 0.15; if (!stopped) requestAnimationFrame(frame); } }};
  }

  // ---------------------------------------------------------------- drawing
  let sim = null;
  function draw(root, D, ctx) {
    if (sim) sim.stop();
    const words = ctx.words || [];
    CTX = ctx;
    const G = build(D, ctx.devOk);
    root.innerHTML = `
      <div class="net-ctl">
        <span class="net-group"><b>Show</b>
          <label><input type="checkbox" data-o="rel"> relations</label>
          <label><input type="checkbox" data-o="people"> people</label>
          <label title="also people with a single project"><input type="checkbox" data-o="solo"> incl. one-project people</label>
          <label><input type="checkbox" data-o="devices"> device families</label>
          <label title="projects with no link to anything shown"><input type="checkbox" data-o="lonely"> unlinked projects</label></span>
        <span class="net-group"><b>Colour</b> <select data-o="color"><option value="device">by device</option><option value="kind">by kind</option><option value="licence">by licence</option><option value="age">by repo age</option></select></span>
        <span class="net-group"><b>Size</b> <select data-o="size"><option value="stars">by GitHub stars</option><option value="equal">equal</option></select></span>
        <button class="net-btn" data-a="fit">Fit</button> <button class="net-btn" data-a="relayout">Re-layout</button>
      </div>
      <div class="net-legend"></div><div class="net-kinds"></div>
      <div class="net-wrap"><svg class="net-svg" role="img" aria-label="Network of projects, people and relations"></svg>
        <div class="net-tip" hidden></div><button class="net-pt" type="button"></button><aside class="net-panel"></aside></div>`;
    root.querySelectorAll("[data-o]").forEach(el => {
      const k = el.dataset.o;
      if (el.type === "checkbox") el.checked = S.opts[k]; else el.value = S.opts[k];
      el.onchange = () => { S.opts[k] = el.type === "checkbox" ? el.checked : el.value; draw(root, D, ctx); };
    });
    const svg = root.querySelector("svg"), tip = root.querySelector(".net-tip"), panel = root.querySelector(".net-panel");
    const W = svg.clientWidth || 900, H = svg.clientHeight || 600;
    svg.innerHTML = `<defs>${["rel", "hi"].map(k => `<marker id="arr-${k}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="var(${k === "hi" ? "--fg" : "--mute"})"/></marker>`).join("")}</defs><g class="net-vp"><g class="net-e"></g><g class="net-n"></g><g class="net-l"></g></g>`;
    const vp = svg.querySelector(".net-vp"), gE = svg.querySelector(".net-e"), gN = svg.querySelector(".net-n"), gL = svg.querySelector(".net-l");

    // matches for the search box
    const hay = n => n.t === "p" ? [n.p.id, n.p.name, n.p.author, n.p.owner, n.p.kind, n.p.license, n.p.gh_license, n.p.notes].join(" ").toLowerCase()
                  : (n.label || "").toLowerCase();
    const match = new Set(words.length ? G.nodes.filter(n => words.every(w => hay(n).includes(w))).map(n => n.id) : []);

    const eEls = G.edges.map(e => {
      const l = document.createElementNS(NS, "line");
      l.setAttribute("class", "e e-" + e.type + (e.type === "rel" && REL[e.rel] && REL[e.rel][2] ? " e-strong" : ""));
      if (e.type === "rel") { l.setAttribute("marker-end", "url(#arr-rel)"); if (REL[e.rel] && REL[e.rel][1]) l.setAttribute("stroke-dasharray", REL[e.rel][1]); }
      gE.appendChild(l); return l;
    });
    const nEls = G.nodes.map(n => {
      let el;
      if (n.t === "d") {
        el = document.createElementNS(NS, "rect"); el.setAttribute("width", 34); el.setAttribute("height", 22); el.setAttribute("rx", 6);
      } else { el = document.createElementNS(NS, "circle"); el.setAttribute("r", radius(n)); }
      el.setAttribute("class", "n n-" + n.t + (n.t === "p" && S.opts.color === "licence" && !n.p.license ? " n-unchecked" : ""));
      el.style.fill = colour(n);
      el.dataset.id = n.id; gN.appendChild(el); return el;
    });
    const many = G.nodes.length > 150;   // crowded: label only the hubs, the rest on hover, search or zoom
    const big = new Set(G.nodes.filter(n => n.t === "d" || (n.t === "o" && (!many || n.ps.length >= 4))
      || (n.t === "p" && (n.deg >= (many ? 7 : 3) || (n.p.stars || 0) >= (many ? 80 : 40)))).map(n => n.id));
    const lEls = G.nodes.map(n => {
      const t = document.createElementNS(NS, "text");
      t.setAttribute("class", "lbl lbl-" + n.t + (big.has(n.id) ? " lbl-big" : ""));
      t.textContent = n.label.length > 28 ? n.label.slice(0, 27) + "…" : n.label; gL.appendChild(t); return t;
    });

    // neighbours for highlighting
    const nb = {}; G.nodes.forEach(n => nb[n.id] = new Set([n.id]));
    G.edges.forEach(e => { nb[e.a].add(e.b); nb[e.b].add(e.a); });
    function paint() {
      const cur = S.hover || S.sel, focus = cur && nb[cur] ? nb[cur] : null;
      G.nodes.forEach((n, i) => {
        const on = focus ? focus.has(n.id) : (!match.size || match.has(n.id));
        nEls[i].classList.toggle("dim", !on);
        nEls[i].classList.toggle("sel", n.id === S.sel);
        nEls[i].classList.toggle("hit", match.has(n.id));
        lEls[i].classList.toggle("dim", !on);
        lEls[i].classList.toggle("show", on && (focus || match.size) ? true : false);
      });
      G.edges.forEach((e, i) => {
        const on = focus ? (e.a === cur || e.b === cur) : (!match.size || match.has(e.a) || match.has(e.b));
        eEls[i].classList.toggle("dim", !on);
        eEls[i].classList.toggle("hi", !!focus && on);
        if (e.type === "rel") eEls[i].setAttribute("marker-end", `url(#arr-${focus && on ? "hi" : "rel"})`);
      });
      svg.classList.toggle("zoomed", S.view.k > 1.6);
    }
    function tick() {
      G.edges.forEach((e, i) => {
        const a = G.N[e.a], b = G.N[e.b];
        let x2 = b.x, y2 = b.y;
        if (e.type === "rel") { // stop the arrow at the target's edge
          const dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 1, r = radius(b) + 2;
          x2 = b.x - dx / d * r; y2 = b.y - dy / d * r;
        }
        eEls[i].setAttribute("x1", a.x.toFixed(1)); eEls[i].setAttribute("y1", a.y.toFixed(1));
        eEls[i].setAttribute("x2", x2.toFixed(1)); eEls[i].setAttribute("y2", y2.toFixed(1));
      });
      G.nodes.forEach((n, i) => {
        if (n.t === "d") { const k = 1 / S.view.k, w = Math.max(40, n.label.length * 7.2) * k, h = 22 * k;
          nEls[i].setAttribute("width", w.toFixed(1)); nEls[i].setAttribute("height", h.toFixed(1)); nEls[i].setAttribute("rx", (6 * k).toFixed(1));
          nEls[i].setAttribute("x", (n.x - w / 2).toFixed(1)); nEls[i].setAttribute("y", (n.y - h / 2).toFixed(1)); }
        else { nEls[i].setAttribute("cx", n.x.toFixed(1)); nEls[i].setAttribute("cy", n.y.toFixed(1)); }
        lEls[i].setAttribute("x", n.x.toFixed(1));
        lEls[i].setAttribute("y", (n.t === "d" ? n.y + 4 / S.view.k : n.y - radius(n) - 3).toFixed(1));
      });
    }
    function applyView() {
      vp.setAttribute("transform", `translate(${S.view.x},${S.view.y}) scale(${S.view.k})`);
      svg.classList.toggle("zoomed", S.view.k > 1.6);
      gL.style.fontSize = (11 / S.view.k).toFixed(2) + "px"; gL.style.strokeWidth = (3 / S.view.k).toFixed(2) + "px";  // labels keep their screen size
      if (S.opts.devices) tick();
    }
    function fit() {
      if (!G.nodes.length) return;
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      G.nodes.forEach(n => { x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y); });
      const k = Math.min(2.5, 0.92 * Math.min(W / Math.max(60, x1 - x0), H / Math.max(60, y1 - y0)));
      S.view = {k, x: W / 2 - k * (x0 + x1) / 2, y: H / 2 - k * (y0 + y1) / 2}; applyView();
    }

    // ---------------------------------------------------------------- panel
    function rows(ps) {
      return ps.slice().sort((a, b) => (b.stars || 0) - (a.stars || 0)).map(p =>
        `<li><a href="#" data-go="p:${esc(p.id)}">${esc(p.name)}</a> <span class="meta">${esc(p.kind)}${p.stars ? " · ★" + p.stars : ""}</span></li>`).join("");
    }
    // the side panel can be closed; the choice is remembered, clicking a dot opens it again
    const wrap = root.querySelector(".net-wrap"), pBtn = root.querySelector(".net-pt");
    function setPanel(open) {
      S.panel = open; try { localStorage.setItem("agg-net-panel", open ? "1" : "0"); } catch (e) { /* storage may be off */ }
      wrap.classList.toggle("net-closed", !open);
      pBtn.textContent = open ? "×" : "‹ Info"; pBtn.title = open ? "Hide this panel" : "Show the panel";
    }
    if (S.panel === undefined) { let v = null; try { v = localStorage.getItem("agg-net-panel"); } catch (e) { /* ignore */ } S.panel = v !== "0"; }
    setPanel(S.panel);
    pBtn.onclick = () => setPanel(!S.panel);
    function showPanel() {
      const n = S.sel && G.N[S.sel];
      if (n && !S.panel) setPanel(true);
      if (!n) {
        const people = G.nodes.filter(x => x.t === "o").length, projs = G.nodes.filter(x => x.t === "p").length;
        panel.innerHTML = `<h3>How to read this</h3>
          <p>${projs} of ${G.total} projects shown${people ? `, ${people} people` : ""}, ${G.edges.filter(e => e.type === "rel").length} relations.${words.length ? ` <b>${match.size}</b> match the search.` : ""}</p>
          <p>Read an arrow as "project, link kind, project" (fork of, builds on, mod for ...); each link names its evidence in <code>data/projects.yml</code>. Click a link kind above to hide or show it ("uses as a tool" and "credits or cites" start hidden, so the map stays readable). Hover a dot to see only its links.
          Uncoloured dots in the text colour are people (GitHub owners), joined to their projects.${S.opts.devices ? " Grey boxes are device families." : ""}</p>
          <p>Click a dot for details and its neighbours. Drag to move, scroll to zoom. The search box above highlights matches.
          The <a href="?t=projects">Projects</a> tab has the same data as a list.</p>`;
        return;
      }
      if (n.t === "p") {
        const p = n.p;
        const rel = G.edges.filter(e => e.type === "rel" && (e.a === n.id || e.b === n.id)).map(e => {
          const out = e.a === n.id, o = G.N[out ? e.b : e.a];
          return `<li>${out ? "" : `<a href="#" data-go="${esc(o.id)}">${esc(o.label)}</a> `}${esc(REL_LABEL[e.rel] || e.rel)}${out ? ` <a href="#" data-go="${esc(o.id)}">${esc(o.label)}</a>` : " this"}
            ${e.ev ? `<div class="meta">${esc(e.ev)}</div>` : ""}</li>`;
        }).join("");
        const lic = p.license || (p.gh_license ? p.gh_license + " (detected by GitHub)" : "not recorded");
        panel.innerHTML = `<h3>${p.repo ? `<a href="${esc(p.repo)}">${esc(p.name)}</a>` : esc(p.name)}</h3>
          <p class="meta">${esc(p.author || "")}${p.owner ? ` · <a href="#" data-go="o:${esc(p.owner)}">${esc(p.owner)}</a>` : ""}</p>
          <dl><dt>Kind</dt><dd>${esc(p.kind)}</dd><dt>Devices</dt><dd>${list(p.devices).map(d => esc(ctx.devName[d] || d)).join(", ")}</dd>
          <dt>Licence</dt><dd>${esc(lic)}</dd>
          ${p.created ? `<dt>Repo created</dt><dd>${esc(p.created)}</dd>` : ""}
          ${p.pushed ? `<dt>Last push</dt><dd>${esc(p.pushed)}</dd>` : ""}
          ${p.stars != null ? `<dt>Stars</dt><dd>${p.stars}${p.forks ? ` · ${p.forks} forks` : ""}</dd>` : ""}
          ${p.status ? `<dt>Status</dt><dd>${esc(p.status)}</dd>` : ""}</dl>
          ${rel ? `<h4>Relations</h4><ul>${rel}</ul>` : ""}
          <p><a href="?t=projects&q=${encodeURIComponent(p.id)}">Full entry in Projects</a></p>`;
      } else if (n.t === "o") {
        const ps = n.ps, stars = ps.reduce((s, p) => s + (p.stars || 0), 0);
        const first = ps.map(p => p.created).filter(Boolean).sort()[0];
        const devs = [...new Set(ps.flatMap(p => list(p.devices)))].map(d => ctx.devName[d] || d);
        panel.innerHTML = `<h3><a href="https://github.com/${esc(n.owner)}">${esc(n.owner)}</a></h3>
          <p class="meta">${ps.length} project${ps.length > 1 ? "s" : ""}${stars ? ` · ★${stars} in total` : ""}${first ? ` · first repo here ${esc(first)}` : ""}</p>
          <p class="meta">${esc(devs.join(", "))}</p><ul>${rows(ps)}</ul>`;
      } else {
        const ps = G.edges.filter(e => e.b === n.id).map(e => G.N[e.a].p);
        panel.innerHTML = `<h3>${esc(n.fam)}</h3><p class="meta">${ps.length} projects shown</p><ul>${rows(ps)}</ul>`;
      }
    }
    panel.onclick = e => {
      const a = e.target.closest("[data-go]"); if (!a) return;
      e.preventDefault(); select(a.dataset.go, true);
    };
    function select(id, centre) {
      S.sel = id && G.N[id] ? id : null; paint(); showPanel();
      if (centre && S.sel) { const n = G.N[S.sel]; S.view.x = W / 2 - S.view.k * n.x; S.view.y = H / 2 - S.view.k * n.y; applyView(); }
    }

    // ---------------------------------------------------------------- pointer: hover, drag, pan, zoom
    const pt = ev => { const r = svg.getBoundingClientRect(); return {x: (ev.clientX - r.left - S.view.x) / S.view.k, y: (ev.clientY - r.top - S.view.y) / S.view.k}; };
    let drag = null, pan = null, moved = false;
    svg.onpointerdown = ev => {
      const id = ev.target.dataset && ev.target.dataset.id; moved = false;
      svg.setPointerCapture(ev.pointerId);
      if (id) { drag = G.N[id]; drag.fixed = true; } else pan = {x: ev.clientX - S.view.x, y: ev.clientY - S.view.y};
    };
    svg.onpointermove = ev => {
      if (drag) { const p = pt(ev); drag.x = p.x; drag.y = p.y; moved = true; tick(); sim && sim.heat(); return; }
      if (pan) { S.view.x = ev.clientX - pan.x; S.view.y = ev.clientY - pan.y; moved = true; applyView(); return; }
      const id = ev.target.dataset && ev.target.dataset.id;
      if ((id || null) !== S.hover) { S.hover = id || null; paint(); }
      if (!id) { tip.hidden = true; return; }
      const n = G.N[id], r = svg.getBoundingClientRect();
      tip.innerHTML = n.t === "p" ? `<b>${esc(n.p.name)}</b><br>${esc(n.p.kind)} · ${esc(n.p.owner || n.p.author || "")}${n.p.stars ? " · ★" + n.p.stars : ""}`
        : n.t === "o" ? `<b>${esc(n.owner)}</b><br>${n.ps.length} projects` : `<b>${esc(n.fam)}</b>`;
      tip.style.left = (ev.clientX - r.left + 14) + "px"; tip.style.top = (ev.clientY - r.top + 10) + "px"; tip.hidden = false;
    };
    svg.onpointerup = ev => {
      if (drag) { if (!moved && drag.t !== "d") { drag.fixed = false; select(drag.id === S.sel ? null : drag.id); } else if (!moved) select(drag.id === S.sel ? null : drag.id); S.pos[drag.id] = {x: drag.x, y: drag.y}; drag = null; return; }
      if (pan && !moved) select(null);
      pan = null;
    };
    svg.ondblclick = ev => { const id = ev.target.dataset && ev.target.dataset.id; if (id) { G.N[id].fixed = false; sim && sim.heat(); } };
    svg.onpointerleave = () => { tip.hidden = true; if (S.hover) { S.hover = null; paint(); } };
    svg.addEventListener("wheel", ev => {
      ev.preventDefault();
      const r = svg.getBoundingClientRect(), mx = ev.clientX - r.left, my = ev.clientY - r.top;
      const k = Math.max(0.2, Math.min(6, S.view.k * Math.exp(-ev.deltaY * 0.0015)));
      S.view.x = mx - (mx - S.view.x) * k / S.view.k; S.view.y = my - (my - S.view.y) * k / S.view.k; S.view.k = k; applyView();
    }, {passive: false});
    root.querySelector('[data-a="fit"]').onclick = fit;
    root.querySelector('[data-a="relayout"]').onclick = () => { S.pos = {}; S.view = {x: 0, y: 0, k: 1}; S.needFit = true; draw(root, D, ctx); };

    // ---------------------------------------------------------------- legend
    const leg = root.querySelector(".net-legend");
    let items;
    if (S.opts.color === "licence") items = Object.keys(LIC_LABEL).map(k => [SLOT[k], LIC_LABEL[k]]);
    else if (S.opts.color === "age") items = [[AGE_STEPS[6], "repo under 1 month old"], [AGE_STEPS[4], "under 3 months"], [AGE_STEPS[2], "under a year"], [AGE_STEPS[0], "older"], ["var(--s0)", "no GitHub repo"]];
    else if (S.opts.color === "device") items = D.devices.filter(d => !ctx.devs.length || ctx.devs.includes(d.slug))
      .map(d => [`var(--c-${d.slug})`, d.name.replace(/ \(.*?\)/g, "")]).concat(ctx.devs.length ? [] : [])
      .concat([["var(--s0)", "no device"]]).slice(0, 20);
    else items = ["mods", "tools", "research", "other"].map(k => [SLOT[k], KIND_LABEL[k]]);
    leg.innerHTML = items.map(([c, l]) => `<span><i style="background:${c}"></i>${esc(l)}</span>`).join("")
      + (S.opts.people ? `<span><i style="background:var(--person)"></i>person (GitHub owner)</span>` : "")
      + (S.opts.color === "licence" ? `<span><i class="i-dash"></i>dashed outline: licence not checked by us (GitHub's detection or none)</span>` : "")
      + `<span class="meta">${S.opts.size === "stars" ? "Size: GitHub stars. " : ""}Numbers from GitHub, refreshed daily.</span>`;
    const counts = {}; D.relations.forEach(r => { if (!ctx.devs.length || (G.N["p:" + r.project] || S.off.has(r.type))) counts[r.type] = (counts[r.type] || 0) + 1; });
    const kinds = root.querySelector(".net-kinds");
    kinds.innerHTML = `<b>Link kinds</b> <span class="meta">click to hide or show</span>` + Object.keys(REL).filter(k => counts[k]).map(k =>
      `<button class="net-kind${S.off.has(k) ? " off" : ""}" data-k="${k}" aria-pressed="${!S.off.has(k)}"><svg width="30" height="10"><line x1="1" y1="5" x2="23" y2="5" stroke="var(${REL[k][2] ? "--fg" : "--mute"})" stroke-width="1.6" stroke-dasharray="${REL[k][1]}"/><path d="M22,1 L29,5 L22,9 z" fill="var(${REL[k][2] ? "--fg" : "--mute"})"/></svg>${esc(REL[k][0])} <span class="meta">${counts[k]}</span></button>`).join("");
    kinds.onclick = e => { const b = e.target.closest("[data-k]"); if (!b) return; const k = b.dataset.k;
      S.off.has(k) ? S.off.delete(k) : S.off.add(k); draw(root, D, ctx); };

    if (S.sel && !G.N[S.sel]) S.sel = null;
    // start or resume the layout
    const isNew = G.nodes.some(n => !S.pos[n.id]);
    G.nodes.forEach((n, i) => {
      const old = n.t === "d" ? null : S.pos[n.id];
      if (old) { n.x = old.x; n.y = old.y; } else if (n.t === "d") {   // device families start on a ring
        const ds = G.nodes.filter(x => x.t === "d"), j = ds.indexOf(n), a = j / ds.length * 2 * Math.PI;
        n.x = W / 2 + W * 0.8 * Math.cos(a); n.y = H / 2 + H * 0.9 * Math.sin(a); n.fixed = true;   // pinned: the projects arrange between them
      } else {
        const a = i * 2.39996, r = 12 * Math.sqrt(i + 1);
        n.x = W / 2 + r * Math.cos(a); n.y = H / 2 + r * Math.sin(a);
      }
      n.vx = 0; n.vy = 0;
    });
    tick(); paint(); showPanel();
    if (isNew) S.needFit = true;
    sim = layout(G, W, H, tick, () => { if (S.needFit) { fit(); S.needFit = false; } });
    applyView(); if (S.needFit) setTimeout(() => { if (S.needFit) fit(); }, 700);
    if (words.length && match.size === 1) select([...match][0], false);
  }

  window.AggNetwork = {draw, stop() { if (sim) sim.stop(); }};
})();
