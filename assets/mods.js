// Aggregat mod browser: every mod, custom OS and loader we know, as cards with filters.
// Plain HTML; data from export/aggregat.json. Exposes window.AggMods.draw(container, D, {words, dev, devName}).
(function () {
  "use strict";
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const list = s => String(s || "").split(",").filter(Boolean);
  const TESTED = [["unit", "On a unit"], ["partly", "Partly"], ["emulator", "Emulator only"], ["not-stated", "Not stated"]];
  const T_LABEL = Object.fromEntries(TESTED);
  const DAY = 864e5;
  // what the user picked, kept while the page is open
  const S = {tested: "", via: "", sort: "updated", all: false, open: {}};

  const updated = p => [p.last_activity || "", p.pushed || ""].sort().pop();
  const found = p => p.first_seen || "";
  function short(s, n) {
    let t = String(s || "").replace(/\s+/g, " ").trim();
    const m = t.match(/^(.{40,}?[a-z0-9)\]])\. /);
    if (m && m[1].length < n) t = m[1] + ".";
    return t.length <= n ? t : t.slice(0, n - 1).replace(/\s+\S*$/, "") + " …";
  }
  const isMod = p => list(p.list).includes("mods");
  const isLoader = p => p.kind === "loader" || (isMod(p) && p.kind === "tool");

  function draw(root, D, ctx) {
    const byId = Object.fromEntries(D.projects.map(p => [p.id, p]));
    const hosts = {};  // mod id -> [loader ids]
    D.relations.forEach(r => { if (r.type === "mod_for") (hosts[r.project] = hosts[r.project] || []).push(r.target); });
    const via = p => p.install || (hosts[p.id] || []).map(h => byId[h] ? byId[h].name.replace(/\s*\(.*\)$/, "") : h).join(", ")
      || (["firmware", "loader"].includes(p.kind) || p.links && p.links !== "{}" ? "own patcher" : "see repo");
    const checked = D.meta.checked, cutNew = [new Date(Date.parse(checked) - 7 * DAY).toISOString().slice(0, 10), "2026-11-03"].sort().pop();  // BULK_UNTIL in build.py

    const all = D.projects.filter(isMod);
    const loaders = all.filter(isLoader);
    let mods = all.filter(p => !isLoader(p));
    const words = ctx.words || [];
    // device and search filter first: the counts on the chips follow them
    let base = mods.filter(p => !ctx.dev || list(p.devices).includes(ctx.dev));
    if (!S.all) base = base.filter(p => !["unreachable", "unverified"].includes(p.status));
    if (words.length) base = base.filter(p => words.every(w => [p.id, p.name, p.author, p.notes, p.contains, p.base_os, p.version, via(p)]
      .join(" ").toLowerCase().includes(w)));
    if (S.via) base = base.filter(p => (hosts[p.id] || []).includes(S.via));
    const tcount = Object.fromEntries(TESTED.map(([k]) => [k, base.filter(p => (p.tested || "not-stated") === k).length]));
    let rows = S.tested ? base.filter(p => (p.tested || "not-stated") === S.tested) : base;
    const SORT = {
      updated: (a, b) => updated(b).localeCompare(updated(a)),
      tested: (a, b) => TESTED.findIndex(t => t[0] === (a.tested || "not-stated")) - TESTED.findIndex(t => t[0] === (b.tested || "not-stated"))
        || updated(b).localeCompare(updated(a)),
      found: (a, b) => found(b).localeCompare(found(a)),
      name: (a, b) => a.name.localeCompare(b.name, "en", {sensitivity: "base"})
    };
    rows = rows.slice().sort(SORT[S.sort]);
    const nNew = mods.filter(p => p.status !== "unverified" && found(p) > cutNew).length;
    const nUnit = mods.filter(p => p.tested === "unit").length;

    const loaderCount = id => mods.filter(p => (hosts[p.id] || []).includes(id)).length;
    const ls = loaders.filter(l => !ctx.dev || list(l.devices).includes(ctx.dev))
      .sort((a, b) => loaderCount(b.id) - loaderCount(a.id) || a.name.localeCompare(b.name));

    const devs = p => list(p.devices).map(d => `<span class="md-tag">${esc((ctx.devName[d] || d).replace(/ \(.*\)$/, ""))}</span>`).join("");
    const card = p => {
      const isNew = p.status !== "unverified" && found(p) > cutNew;
      const st = ["active", "unverified"].includes(p.status) ? "" : `<span class="md-st">${esc(p.status)}</span>`;
      const os = p.base_os ? short(p.base_os, 70) : "";
      return `<article class="md-card${["unreachable", "unverified"].includes(p.status) ? " md-dim" : ""}">
        <div class="md-top">${isNew ? `<span class="md-new">new</span>` : ""}${p.status === "unverified" ? `<span class="md-st">unverified lead</span>` : st}
          <span class="md-date">${esc(updated(p) || "")}</span></div>
        <h3>${p.repo ? `<a href="${esc(p.repo)}">${esc(p.name)}</a>` : esc(p.name)}</h3>
        <div class="md-by">${esc(short(p.author, 60))}</div>
        <p>${esc(short(p.notes, 190))}</p>
        ${p.contains ? `<details><summary>What is inside</summary><div>${esc(p.contains)}</div></details>` : ""}
        <div class="md-foot">${devs(p)}<span class="md-via">via ${esc(via(p))}</span></div>
        ${os ? `<div class="md-os">${esc(os)}</div>` : ""}
      </article>`;
    };

    root.innerHTML = `
      <p class="md-lead">${mods.length} mods and custom OS builds, ${nUnit} of them reported running on a real unit, ${nNew} new in the last 7 days.
        Mods are unofficial: <a href="https://github.com/70b185/aggregat/blob/master/hardware/common/recovery.md">read the recovery notes</a> before you flash anything.
        &ldquo;Tested&rdquo; is what the authors say, not our own test.</p>
      <div class="md-ctl">
        <div class="md-seg" role="group" aria-label="Tested">
          <button data-t="" class="${S.tested ? "" : "on"}">All <span>${base.length}</span></button>
          ${TESTED.map(([k, l]) => `<button data-t="${k}" class="${S.tested === k ? "on" : ""}"><i class="md-dot md-t-${k}"></i>${l} <span>${tcount[k]}</span></button>`).join("")}
        </div>
        <select id="md-sort" aria-label="Sort">
          ${[["updated", "Recently updated"], ["tested", "Tested first"], ["found", "Newest first"], ["name", "Name"]]
            .map(([k, l]) => `<option value="${k}"${S.sort === k ? " selected" : ""}>${l}</option>`).join("")}
        </select>
        <label class="md-chk"><input type="checkbox" id="md-all"${S.all ? " checked" : ""}> unreachable and unverified too</label>
      </div>
      <h2 class="md-h">Loaders and platforms <span>pick one to see its mods</span></h2>
      <div class="md-loaders">
        ${ls.map(l => `<button class="md-ld${S.via === l.id ? " on" : ""}" data-v="${esc(l.id)}" title="${esc(short(l.notes, 220))}">
          <b>${esc(short(l.name, 48))}</b><span>${loaderCount(l.id) || "–"} mods · ${esc(list(l.devices).map(d => (ctx.devName[d] || d).replace(/ \(.*\)$/, "")).join(", "))}</span></button>`).join("")}
      </div>
      <h2 class="md-h">${S.via ? `Mods for ${esc(byId[S.via].name)} <button class="md-x" id="md-clear">show all</button>` : "Mods"} <span>${rows.length} shown</span></h2>
      <div class="md-grid">${rows.map(card).join("") || `<div class="empty">Nothing matches.</div>`}</div>`;

    const c = document.getElementById("count"); if (c) c.textContent = `${rows.length} of ${mods.length} mods`;
    const redraw = () => draw(root, D, ctx);
    root.querySelector(".md-seg").onclick = e => { const b = e.target.closest("button"); if (!b) return; S.tested = b.dataset.t; redraw(); };
    root.querySelector("#md-sort").onchange = e => { S.sort = e.target.value; redraw(); };
    root.querySelector("#md-all").onchange = e => { S.all = e.target.checked; redraw(); };
    root.querySelector(".md-loaders").onclick = e => { const b = e.target.closest("button"); if (!b) return; S.via = S.via === b.dataset.v ? "" : b.dataset.v; redraw(); };
    const x = root.querySelector("#md-clear"); if (x) x.onclick = () => { S.via = ""; redraw(); };
  }
  window.AggMods = {draw};
})();
