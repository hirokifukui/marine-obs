// Dive sites map: data/dive-points/<site>.json → Leaflet
(function () {
    const SITE = document.currentScript.dataset.site;
    const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const bi = (en, ja) => `<span data-lang="en">${en}</span><span data-lang="ja">${ja}</span>`;
    const COLORS = ['#0a5c74', '#d0613d', '#2a8a5c', '#7a5cc2', '#c58a00', '#b3261e', '#3a7ca5', '#8a6d3b', '#5b8c85', '#a04a7a'];
    let map, layers = {}, markers = {}, data;

    const AREA_MEDIA_KEY = a => ({ 'ビーチ': '宮古島南・来間', 'ビーチ（東）': '宮古島南・来間', 'ビーチ（池間）': '宮古島北（狩俣）' })[a] || a;
    function fig(m) {
        return `<figure><a href="${esc(m.page)}" target="_blank" rel="noopener"><img loading="lazy" src="${esc(m.src)}" alt="${esc(m.title)}"></a>
            <figcaption>© ${esc(m.author || 'unknown')} · ${m.license_url ? `<a href="${esc(m.license_url)}" target="_blank" rel="noopener">${esc(m.license)}</a>` : esc(m.license)} · ${esc(m.via)}</figcaption></figure>`;
    }
    function mediaHtml(p) {
        const own = (p.media || []).filter(m => !m.area);
        if (own.length) return `<div class="dp-media">${own.map(fig).join('')}</div>`;
        const am = ((data.area_media || {})[AREA_MEDIA_KEY(p.area)] || []).slice(0, 4);
        if (!am.length) return `<p class="dp-media-note">${bi('No openly licensed photos found for this site yet.', 'このポイントの、再利用が許可された写真はまだ見つかっていません。')}</p>`;
        return `<p class="dp-media-note">${bi('No openly licensed photo of this site was found. Below: photos from the same area (not necessarily underwater) — not this site.', 'このポイントの再利用可能な写真は見つかりませんでした。下は同じエリアの写真（水中とは限りません）で、このポイントそのものではありません。')}</p><div class="dp-media">${am.map(fig).join('')}</div>`;
    }
    function commentaryHtml(p) {
        if (!p.commentary_ja && !p.commentary_en) return `<div class="ph">${bi('Notes by Claude: in preparation.', 'Claude の解説：準備中。')}</div>`;
        return `<div class="dp-ai"><span class="tag">${bi('AI-GENERATED', 'AI自動生成')}</span>${bi(esc(p.commentary_en), esc(p.commentary_ja))}
            <span class="sig">${bi('Written by Claude (Anthropic) from the facts collected from the sources below; not checked on site.', '下の出典から集めた事実をもとに Claude（Anthropic）が書いた解説です。現地で確かめたものではありません。')}</span></div>`;
    }
    function detail(p) {
        const near = p.precision === 'near';
        document.getElementById('dp-detail').innerHTML = `<button type="button" class="close" aria-label="close" onclick="window.__dpClose()">×</button>
            <h2>${esc(p.name)}</h2>${p.alias ? `<div class="alias">${bi('also: ', '別名：')}${esc(p.alias)}</div>` : ''}
            <dl>
                <dt>${bi('Area', 'エリア')}</dt><dd>${esc(p.area)}</dd>
                <dt>${bi('Max depth', '最大水深')}</dt><dd>${esc(p.depth || '–')}</dd>
                <dt>${bi('Features', '特徴')}</dt><dd>${esc(p.features || '–')}</dd>
                <dt>${bi('Position', '位置')}</dt><dd>${p.lat == null ? bi('unknown (not on the map)', '不明（地図には置いていません）') : near ? bi('near ' + esc(p.position_note), esc(p.position_note) + 'の近く（目安）') : bi('approximate, within ' + esc(p.position_note), 'エリア内の目安（' + esc(p.position_note) + '）')}</dd>
            </dl>
            ${commentaryHtml(p)}
            ${mediaHtml(p)}
            <div class="src">${bi('Sources: ', '出典：')}${p.sources.map(s => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)} ↗</a>`).join('')}</div>`;
    }
    function popup(p) {
        return `<div class="dp-pop"><b>${esc(p.name)}</b>${p.precision === 'area' ? `<span class="dp-tag">${bi('approx.', '位置は目安')}</span>` : ''}
            <div class="f">${esc(p.features || '')}${p.depth ? ' · ' + esc(p.depth) : ''}</div>
            <button type="button" data-i="${data.points.indexOf(p)}">${bi('More', '詳しく')}</button></div>`;
    }
    function openDetail(i) {
        detail(data.points[i]);
        const m = document.getElementById('dp-modal'); m.classList.add('open'); m.scrollTop = 0; document.body.classList.add('dp-lock');
    }
    window.__dpClose = () => { document.getElementById('dp-modal').classList.remove('open'); document.body.classList.remove('dp-lock'); };
    function select(i, fly) {
        const p = data.points[i];
        if (fly) { map.flyTo([p.lat, p.lng], Math.max(map.getZoom(), 13), { duration: 0.6 }); setTimeout(() => markers[i].openPopup(), 650); }
    }
    async function init() {
        data = await (await fetch(`../data/dive-points/${SITE}.json`)).json();
        const areas = [...new Set(data.points.map(p => p.area))];
        const col = Object.fromEntries(areas.map((a, i) => [a, COLORS[i % COLORS.length]]));
        document.getElementById('dp-count').textContent = `（${data.points.length}）`;
        map = L.map('dp-map', { scrollWheelZoom: false }).setView(data.center, 11);
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { attribution: 'Imagery © Esri, Maxar, Earthstar Geographics', maxZoom: 18 }).addTo(map);
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18, opacity: 0.8 }).addTo(map);
        window.__dpMap = map;
        areas.forEach(a => layers[a] = L.layerGroup().addTo(map));
        data.points.forEach((p, i) => {
            if (p.lat == null) return;
            const m = L.circleMarker([p.lat, p.lng], { radius: p.precision === 'near' ? 7 : 6, color: '#fff', weight: 1.5, fillColor: col[p.area], fillOpacity: p.precision === 'near' ? 0.95 : 0.75, dashArray: p.precision === 'near' ? null : '2 2' })
                .bindPopup(popup(p)).bindTooltip(esc(p.name), { direction: 'top', offset: [0, -6] });
            m.addTo(layers[p.area]); markers[i] = m;
        });
        map.on('popupopen', e => { const b = e.popup.getElement().querySelector('button[data-i]'); if (b) b.onclick = () => openDetail(+b.dataset.i); });
        document.getElementById('dp-modal').addEventListener('click', e => { if (e.target.id === 'dp-modal') window.__dpClose(); });
        document.addEventListener('keydown', e => { if (e.key === 'Escape') window.__dpClose(); });
        const B = L.latLngBounds(data.points.filter(p => p.lat != null).map(p => [p.lat, p.lng])).pad(0.05);
        map.fitBounds(B);
        setTimeout(() => { map.invalidateSize(); map.fitBounds(B); }, 300);
        const chips = document.getElementById('dp-chips');
        chips.innerHTML = areas.filter(a => data.points.some(p => p.area === a && p.lat != null)).map(a => `<button type="button" data-a="${esc(a)}"><i style="background:${col[a]}"></i>${esc(a)}（${data.points.filter(p => p.area === a).length}）</button>`).join('');
        chips.querySelectorAll('button').forEach(b => b.onclick = () => {
            const a = b.dataset.a, on = map.hasLayer(layers[a]);
            on ? map.removeLayer(layers[a]) : map.addLayer(layers[a]); b.classList.toggle('off', on);
        });
        document.getElementById('dp-list').innerHTML = areas.map(a => `<section><h3><i style="background:${col[a]}"></i>${esc(a)}</h3>${
            data.points.map((p, i) => p.area === a ? `<a data-i="${i}">${esc(p.name)}</a>` : '').join('')}</section>`).join('');
        document.querySelectorAll('#dp-list a').forEach(x => x.onclick = () => { const i = +x.dataset.i; if (data.points[i].lat == null) { openDetail(i); return; } document.getElementById('dp-map').scrollIntoView({ behavior: 'smooth' }); select(i, true); });
    }
    init().catch(e => console.error(e));
})();
