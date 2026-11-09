// Aggregat mod browser: every mod, custom OS and loader we know, as cards with filters.
// Plain HTML; data from export/aggregat.json. Exposes window.AggMods.draw(container, D, {words, dev, devName}).
(function () {
  "use strict";
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const list = s => String(s || "").split(",").filter(Boolean);
  const DAY = 864e5;
  // what the user picked, kept while the page is open
  const S = {via: "", sort: "updated", all: false};

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
  // mods a loader or platform ships itself (projects.yml own_mods), stored as a JSON list
  const own = p => { try { return JSON.parse(p.own_mods || "[]"); } catch (e) { return []; } };
  const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  // each own mod becomes a mod card of its own, installed via its platform
  function ownMods(D) {
    const out = [];
    D.projects.forEach(p => own(p).forEach(m => out.push({
      id: `${p.id}--${slug(m.name)}`, name: m.name, author: m.author || p.author, kind: "mod", list: "mods",
      devices: m.devices ? m.devices.join(",") : p.devices, status: p.status, notes: m.what, tested: m.tested,
      tested_note: m.note, version: m.version, base_os: m.version ? `version ${m.version}` : "", last_activity: p.last_activity,
      pushed: p.pushed, first_seen: p.first_seen, links: "{}", contains: "", platform: p.id,
      repo: m.path && /github\.com/.test(p.repo || "") ? `${p.repo.replace(/\/$/, "")}/tree/HEAD/${m.path}` : p.repo})));
    return out;
  }

  function draw(root, D, ctx) {
    const extra = ownMods(D);
    const byId = Object.fromEntries(D.projects.concat(extra).map(p => [p.id, p]));
    const hosts = {};  // mod id -> [loader ids]
    D.relations.forEach(r => { if (r.type === "mod_for") (hosts[r.project] = hosts[r.project] || []).push(r.target); });
    extra.forEach(m => { hosts[m.id] = [m.platform]; });
    const via = p => p.install || (hosts[p.id] || []).map(h => byId[h] ? byId[h].name.replace(/\s*\(.*\)$/, "") : h).join(", ")
      || (["firmware", "loader"].includes(p.kind) || p.links && p.links !== "{}" ? "own patcher" : "see repo");
    const checked = D.meta.checked, cutNew = [new Date(Date.parse(checked) - 7 * DAY).toISOString().slice(0, 10), "2026-11-03"].sort().pop();  // BULK_UNTIL in build.py

    const all = D.projects.filter(isMod).concat(extra);
    // loaders: mod loaders and patchers, plus any platform that ships mods of its own (e.g. digikit)
    const loaders = D.projects.filter(p => (isMod(p) && isLoader(p)) || own(p).length);
    let mods = all.filter(p => !isLoader(p) && !own(p).length);
    const words = ctx.words || [];
    // device and search filter first: the counts on the chips follow them
    let base = mods.filter(p => ctx.devOk(list(p.devices)));
    if (!S.all) base = base.filter(p => !["unreachable", "unverified"].includes(p.status));
    if (words.length) base = base.filter(p => words.every(w => [p.id, p.name, p.author, p.notes, p.contains, p.base_os, p.version, via(p)]
      .join(" ").toLowerCase().includes(w)));
    if (S.via) base = base.filter(p => (hosts[p.id] || []).includes(S.via));
    let rows = base;
    const SORT = {
      updated: (a, b) => updated(b).localeCompare(updated(a)),
      found: (a, b) => found(b).localeCompare(found(a)),
      name: (a, b) => a.name.localeCompare(b.name, "en", {sensitivity: "base"})
    };
    rows = rows.slice().sort(SORT[S.sort]);
    const nNew = mods.filter(p => p.status !== "unverified" && found(p) > cutNew).length;

    const loaderCount = id => mods.filter(p => (hosts[p.id] || []).includes(id)).length;
    const ls = loaders.filter(l => ctx.devOk(list(l.devices)))
      .sort((a, b) => loaderCount(b.id) - loaderCount(a.id) || a.name.localeCompare(b.name));

    const devs = p => list(p.devices).map(d => `<span class="md-tag" style="--dc:var(--c-${esc(d)})">${esc((ctx.devName[d] || d).replace(/ \(.*\)$/, ""))}</span>`).join("");
    const card = p => {
      const isNew = p.status !== "unverified" && found(p) > cutNew;
      const st = ["active", "unverified"].includes(p.status) ? "" : `<span class="md-st">${esc(p.status)}</span>`;
      const os = p.base_os ? short(p.base_os, 70) : "";
      return `<article style="--dc:var(--c-${esc(list(p.devices)[0] || "")})" class="md-card md-k-${esc(p.kind)}${["unreachable", "unverified"].includes(p.status) ? " md-dim" : ""}">
        <div class="md-top"><span class="md-kind">${esc(p.kind === "firmware" ? "custom OS" : p.kind)}</span>${isNew ? `<span class="md-new">new</span>` : ""}${p.status === "unverified" ? `<span class="md-st">unverified lead</span>` : st}
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
      <p class="md-lead">${mods.length} mods and custom OS builds, ${nNew} new in the last 7 days.
        Mods are unofficial: <a href="https://github.com/70b185/aggregat/blob/master/hardware/common/recovery.md">read the recovery notes</a> before you flash anything.</p>
      <div class="md-ctl">
        <select id="md-sort" aria-label="Sort">
          ${[["updated", "Recently updated"], ["found", "Newest first"], ["name", "Name"]]
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
    root.querySelector("#md-sort").onchange = e => { S.sort = e.target.value; redraw(); };
    root.querySelector("#md-all").onchange = e => { S.all = e.target.checked; redraw(); };
    root.querySelector(".md-loaders").onclick = e => { const b = e.target.closest("button"); if (!b) return; S.via = S.via === b.dataset.v ? "" : b.dataset.v; redraw(); };
    const x = root.querySelector("#md-clear"); if (x) x.onclick = () => { S.via = ""; redraw(); };
  }
  window.AggMods = {draw, ownMods};
})();
