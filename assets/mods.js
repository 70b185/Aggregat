// Aggregat mod browser: every mod, custom OS and loader we know, as cards with filters.
// Plain HTML; data from export/web/core.json. Exposes window.AggMods.draw(container, D, {words, dev, devName}).
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
  const TESTED = {"unit": "yes, on a unit", "partly": "partly", "emulator": "emulator only", "not-stated": "not stated"};
  const T_ORDER = ["unit", "partly", "emulator", "not-stated"];
  // a platform's own mods become ONE mod card "<platform> mods" installed via it (one entry per repo, like every
  // other collection); each mod is listed under "What is inside". scripts/build.py builds catalog/MODS.md the same way.
  function ownMods(D) {
    const order = (D.devices || []).map(d => d.slug), dn = Object.fromEntries((D.devices || []).map(d => [d.slug, d.name.replace(/ \(.*\)$/, "")]));
    return D.projects.filter(p => own(p).length).map(p => {
      const ms = own(p), pdev = list(p.devices), mdev = m => m.devices || pdev;
      let devs = order.filter(d => ms.some(m => mdev(m).includes(d))); if (!devs.length) devs = pdev;
      const label = m => m.name + (m.author && m.author !== p.author ? ` (${m.author})` : "");
      const body = devs.length > 1 && ms.some(m => m.devices)
        ? devs.map(d => `${dn[d] || d}: ${ms.filter(m => mdev(m).includes(d)).map(label).join(", ")}`).join("; ")
        : ms.map(label).join(", ");
      const ts = Object.fromEntries(T_ORDER.map(t => [t, ms.filter(m => (m.tested || "not-stated") === t).map(m => m.name)]));
      const used = T_ORDER.filter(t => ts[t].length);
      const tested = used.length === 1 ? used[0] : ts.unit.length || ts.partly.length ? "partly" : ts.emulator.length ? "emulator" : "not-stated";
      return {id: `${p.id}--own`, name: p.name.replace(/\s*\(.*\)$/, "") + " mods", author: p.author, kind: "mod", list: "mods",
        devices: devs.join(","), status: p.status, notes: `${ms.length} mods of its own: ${body}`, tested,
        tested_note: used.length === 1 ? "" : used.map(t => `${TESTED[t]}: ${ts[t].join(", ")}`).join("; "),
        contains: ms.map(m => `${m.name}${m.version ? " " + m.version : ""}: ${m.what} [${TESTED[m.tested] || "not stated"}]`).join("; "),
        base_os: "", last_activity: p.last_activity, pushed: p.pushed, first_seen: p.first_seen, links: "{}",
        repo: p.repo, platform: p.id};
    });
  }

  // The one list of mods every view counts from (mods tab, finder, device bar): catalogue mods plus one card per
  // platform's own mods, without loaders; unreachable repos and unverified leads only when asked for.
  const HIDDEN = ["unreachable", "unverified", "request"];
  function catalogue(D, withHidden) {
    const all = D.projects.filter(isMod).concat(ownMods(D)).filter(p => !isLoader(p) && !own(p).length);
    return withHidden ? all : all.filter(p => !HIDDEN.includes(p.status));
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
    let mods = catalogue(D, true);
    const nHidden = mods.length - catalogue(D, false).length;
    const words = ctx.words || [];
    // device and search filter first: the counts on the chips follow them
    let base = mods.filter(p => ctx.devOk(list(p.devices)));
    if (!S.all) base = base.filter(p => !HIDDEN.includes(p.status));
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
    const nNew = catalogue(D, false).filter(p => found(p) > cutNew).length;
    const total = catalogue(D, S.all).length;

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
          <a class="md-perma" href="?p=${esc(p.platform || p.id)}" title="Page of this entry, with a link you can share">details</a><span class="md-date">${esc(updated(p) || "")}</span></div>
        <h3>${p.repo ? `<a href="${esc(p.repo)}">${esc(p.name)}</a>` : esc(p.name)}</h3>
        <div class="md-by">${esc(short(p.author, 60))}</div>
        <p>${esc(short(p.notes, 190))}</p>
        ${p.contains ? `<details><summary>What is inside</summary><div>${esc(p.contains)}</div></details>` : ""}
        <div class="md-foot">${devs(p)}<span class="md-via">via ${esc(via(p))}</span></div>
        ${os ? `<div class="md-os">${esc(os)}</div>` : ""}
      </article>`;
    };

    root.innerHTML = `
      <p class="md-lead">${total} mods and custom OS builds, ${nNew} new in the last 7 days${S.all ? "" : nHidden ? ` (${nHidden} more are unreachable or not yet checked by us; tick the box below to see them)` : ""}.
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
          <b>${esc(short(l.name, 48))}</b><span>${loaderCount(l.id) || "–"} ${loaderCount(l.id) === 1 ? "mod" : "mods"} · ${esc(list(l.devices).map(d => (ctx.devName[d] || d).replace(/ \(.*\)$/, "")).join(", "))}</span></button>`).join("")}
      </div>
      <h2 class="md-h">${S.via ? `Mods for ${esc(byId[S.via].name)} <button class="md-x" id="md-clear">show all</button>` : "Mods"} <span>${rows.length} shown</span></h2>
      <div class="md-grid">${rows.map(card).join("") || `<div class="empty">Nothing matches.</div>`}</div>`;

    const c = document.getElementById("count"); if (c) c.textContent = rows.length === total ? `${total} mods` : `${rows.length} of ${total} mods`;
    const redraw = () => draw(root, D, ctx);
    root.querySelector("#md-sort").onchange = e => { S.sort = e.target.value; redraw(); };
    root.querySelector("#md-all").onchange = e => { S.all = e.target.checked; (ctx.rerender || redraw)(); };   // the device bar counts follow
    root.querySelector(".md-loaders").onclick = e => { const b = e.target.closest("button"); if (!b) return; S.via = S.via === b.dataset.v ? "" : b.dataset.v; redraw(); };
    const x = root.querySelector("#md-clear"); if (x) x.onclick = () => { S.via = ""; redraw(); };
  }
  window.AggMods = {draw, ownMods, catalogue, showsHidden: () => S.all};
})();
