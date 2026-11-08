// Aggregat community overview: who builds what, since when, for which device, under which licence.
// Plain HTML/SVG; data from export/aggregat.json. Exposes window.AggCommunity.draw(container, D, {words, dev, devName}).
(function () {
  "use strict";
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const list = s => String(s || "").split(",").filter(Boolean);
  const GROUP = {mod: "mods", firmware: "mods", loader: "mods", tool: "tools", editor: "tools", library: "tools",
                 "agent-skill": "tools", research: "research", emulator: "research", resource: "research"};
  const GROUPS = [["mods", "Mods, firmware, loaders", "var(--s1)"], ["tools", "Tools, editors, libraries", "var(--s2)"],
                  ["research", "Research, emulators", "var(--s3)"], ["other", "Other", "var(--s0)"]];
  function licFamily(p) {
    const l = (p.license || p.gh_license || "").toLowerCase();
    if (!l || /not stated|unspecified|none|unknown|noassertion/.test(l)) return "None stated";
    if (/proprietary/.test(l)) return "Closed (proprietary)";
    if (/gpl|mpl|eupl/.test(l)) return "Copyleft (GPL, AGPL)";
    if (/cc0|unlicense|public domain/.test(l)) return "Public domain (CC0, Unlicense)";
    if (/mit|bsd|apache|isc|zlib/.test(l)) return "Permissive (MIT, BSD, Apache)";
    return "None stated";
  }
  const DAY = 864e5;
  const monday = t => { const d = new Date(t); const wd = (d.getUTCDay() + 6) % 7; return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - wd); };
  const fmt = t => new Date(t).toISOString().slice(5, 10).replace("-", "/");

  function draw(root, D, ctx) {
    const words = ctx.words || [];
    let P = D.projects.filter(p => !ctx.dev || list(p.devices).includes(ctx.dev));
    if (words.length) P = P.filter(p => words.every(w => [p.id, p.name, p.author, p.owner, p.kind, p.license, p.notes].join(" ").toLowerCase().includes(w)));
    const now = Date.now();
    const gh = P.filter(p => p.created);
    const owners = {}; P.forEach(p => { const o = p.owner || null; if (o) (owners[o] = owners[o] || []).push(p); });
    const new30 = gh.filter(p => now - Date.parse(p.created) < 30 * DAY).length;
    const pushed7 = P.filter(p => p.pushed && now - Date.parse(p.pushed) < 7 * DAY);
    const stars = P.reduce((s, p) => s + (p.stars || 0), 0);
    const oldest = gh.slice().sort((a, b) => a.created.localeCompare(b.created))[0];

    // ---------------------------------------------------------------- weekly bars (last 26 weeks)
    const W0 = monday(now) - 25 * 7 * DAY, weeks = [];
    for (let i = 0; i < 26; i++) weeks.push({t: W0 + i * 7 * DAY, ps: []});
    let older = 0;
    gh.forEach(p => { const t = monday(Date.parse(p.created)); const i = Math.round((t - W0) / (7 * DAY)); if (i >= 0 && i < 26) weeks[i].ps.push(p); else if (i < 0) older++; });
    const maxW = Math.max(1, ...weeks.map(w => w.ps.length));
    const CW = 760, CH = 180, padL = 28, padB = 22, bw = (CW - padL) / 26;
    const ticks = [0, Math.ceil(maxW / 2), maxW];
    const bars = weeks.map((w, i) => {
      const h = w.ps.length / maxW * (CH - padB - 8);
      const x = padL + i * bw + 1, y = CH - padB - h;
      const names = w.ps.slice().sort((a, b) => (b.stars || 0) - (a.stars || 0)).slice(0, 6).map(p => esc(p.name)).join(", ");
      const tipTxt = `Week of ${fmt(w.t)}: ${w.ps.length} new repo${w.ps.length === 1 ? "" : "s"}${names ? " - " + names + (w.ps.length > 6 ? ", ..." : "") : ""}`;
      return `<g class="cm-hit" data-tip="${tipTxt}"><rect x="${x - 1}" y="8" width="${bw}" height="${CH - padB - 8}" fill="transparent"/>
        ${h > 0 ? `<path d="M${x},${CH - padB} V${y + 4} q0,-4 4,-4 H${x + bw - 6} q4,0 4,4 V${CH - padB} Z" fill="var(--s1)"/>` : ""}</g>`
        + (i % 4 === 0 ? `<text class="cm-ax" x="${x}" y="${CH - 6}">${fmt(w.t)}</text>` : "");
    }).join("");
    const grid = ticks.map(v => { const y = CH - padB - v / maxW * (CH - padB - 8);
      return `<line x1="${padL}" x2="${CW}" y1="${y}" y2="${y}" class="cm-grid"/><text class="cm-ax" x="${padL - 6}" y="${y + 4}" text-anchor="end">${v}</text>`; }).join("");

    // ---------------------------------------------------------------- per device, stacked by kind group
    const devRows = D.devices.map(d => {
      const ps = P.filter(p => list(p.devices).includes(d.slug));
      const by = {}; ps.forEach(p => { const g = GROUP[p.kind] || "other"; by[g] = (by[g] || 0) + 1; });
      return {d, n: ps.length, by};
    }).filter(r => r.n).sort((a, b) => b.n - a.n);
    const maxD = Math.max(1, ...devRows.map(r => r.n));
    const devHtml = devRows.map(r => {
      let segs = "";
      GROUPS.forEach(([g, label, col]) => { const v = r.by[g] || 0; if (!v) return;
        segs += `<span class="cm-seg" style="flex:${v};background:${col}" data-tip="${esc(r.d.name)}: ${v} ${esc(label.toLowerCase())}"></span>`; });
      return `<div class="cm-row"><span class="cm-lab">${esc(r.d.name)}</span><span class="cm-track"><span class="cm-stack" style="width:${(r.n / maxD * 100).toFixed(1)}%">${segs}</span></span><span class="cm-val">${r.n}</span></div>`;
    }).join("");

    // ---------------------------------------------------------------- licences
    const lic = {}; P.forEach(p => { const f = licFamily(p); lic[f] = (lic[f] || 0) + 1; });
    const licRows = Object.entries(lic).sort((a, b) => b[1] - a[1]);
    const maxL = Math.max(1, ...licRows.map(r => r[1]));
    const licHtml = licRows.map(([f, n]) => `<div class="cm-row"><span class="cm-lab">${esc(f)}</span><span class="cm-track"><span class="cm-bar" style="width:${(n / maxL * 100).toFixed(1)}%" data-tip="${esc(f)}: ${n} projects"></span></span><span class="cm-val">${n}</span></div>`).join("");

    // ---------------------------------------------------------------- people
    const people = Object.entries(owners).map(([o, ps]) => ({o, ps, stars: ps.reduce((s, p) => s + (p.stars || 0), 0),
      first: ps.map(p => p.created).filter(Boolean).sort()[0] || "", devs: [...new Set(ps.flatMap(p => list(p.devices)))]}))
      .sort((a, b) => b.ps.length - a.ps.length || b.stars - a.stars).slice(0, 15);
    const maxP = Math.max(1, ...people.map(x => x.ps.length));
    const pplHtml = people.map(x => `<tr><td><a href="https://github.com/${esc(x.o)}">${esc(x.o)}</a></td>
      <td class="cm-num"><span class="cm-inl" style="width:${(x.ps.length / maxP * 60).toFixed(0)}px"></span> ${x.ps.length}</td>
      <td class="meta">${esc(x.devs.map(d => ctx.devName[d] || d).join(", "))}</td><td class="cm-num">${x.stars || ""}</td><td class="meta">${esc(x.first)}</td>
      <td><a href="?t=network&q=${encodeURIComponent(x.o)}">map</a></td></tr>`).join("");

    const top = P.filter(p => p.stars).sort((a, b) => b.stars - a.stars).slice(0, 10);
    const topHtml = top.map(p => `<li><a href="${esc(p.repo)}">${esc(p.name)}</a> <span class="meta">★${p.stars} · ${esc(p.owner || "")} · ${esc(p.kind)}</span></li>`).join("");
    const recent = pushed7.slice().sort((a, b) => b.pushed.localeCompare(a.pushed)).slice(0, 25);
    const recHtml = recent.map(p => `<li><a href="${esc(p.repo)}">${esc(p.name)}</a> <span class="meta">${esc(p.pushed)} · ${esc(p.owner || "")}</span></li>`).join("");

    root.innerHTML = `
      ${words.length || ctx.dev ? `<p class="meta">Filtered by the search box and device bar: ${P.length} projects.</p>` : ""}
      <div class="cm-kpis">
        <div><b>${P.length}</b><span>projects catalogued</span></div>
        <div><b>${Object.keys(owners).length}</b><span>people and groups on GitHub</span></div>
        <div><b>${new30}</b><span>repos created in the last 30 days</span></div>
        <div><b>${pushed7.length}</b><span>repos pushed in the last 7 days</span></div>
        <div><b>${stars.toLocaleString("en")}</b><span>GitHub stars in total</span></div>
      </div>
      <section class="cm-card"><h3>New repos per week</h3>
        <p class="meta">By the date GitHub created the repo, last 26 weeks. ${older} older repos${oldest ? `, the oldest from ${esc(oldest.created.slice(0, 4))} (${esc(oldest.name)})` : ""}. ${P.length - gh.length} entries have no GitHub repo.</p>
        <svg class="cm-svg" viewBox="0 0 ${CW} ${CH}" role="img" aria-label="Bar chart of new repos per week">${grid}${bars}</svg></section>
      <div class="cm-two">
        <section class="cm-card"><h3>Projects per device</h3>
          <div class="cm-legend">${GROUPS.map(([g, l, c]) => `<span><i style="background:${c}"></i>${esc(l)}</span>`).join("")}</div>${devHtml}
          <p class="meta">A project for several devices counts for each.</p></section>
        <section class="cm-card"><h3>Licences</h3>${licHtml}
          <p class="meta">The licence our catalogue records, or the one GitHub detects when we recorded none.</p></section>
      </div>
      <section class="cm-card"><h3>People with the most projects</h3>
        <table class="cm-table"><thead><tr><th>GitHub owner</th><th>Projects</th><th>Devices</th><th>Stars</th><th>First repo</th><th></th></tr></thead><tbody>${pplHtml}</tbody></table></section>
      <div class="cm-two">
        <section class="cm-card"><h3>Most starred</h3><ol>${topHtml}</ol></section>
        <section class="cm-card"><h3>Pushed in the last 7 days</h3><ul>${recHtml || "<li class='meta'>none</li>"}</ul>${pushed7.length > 25 ? `<p class="meta">and ${pushed7.length - 25} more</p>` : ""}</section>
      </div>
      <p class="meta">GitHub numbers (creation date, stars, last push, detected licence) come from <code>scripts/repo_meta.py</code>, refreshed by the daily update. A person here is a GitHub owner, which can be a group.</p>
      <div class="net-tip cm-tip" hidden></div>`;

    const tip = root.querySelector(".cm-tip");
    root.onmousemove = ev => {
      const t = ev.target.closest("[data-tip]");
      if (!t) { tip.hidden = true; return; }
      const r = root.getBoundingClientRect();
      tip.textContent = t.dataset.tip; tip.hidden = false;
      tip.style.left = Math.min(ev.clientX - r.left + 12, r.width - 260) + "px"; tip.style.top = (ev.clientY - r.top + 14) + "px";
    };
    root.onmouseleave = () => { tip.hidden = true; };
  }
  window.AggCommunity = {draw};
})();
