// Dive sites map: data/dive-points/<site>.json → Leaflet
(function () {
    const SITE = document.currentScript.dataset.site;
    const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const bi = (en, ja) => `<span data-lang="en">${en}</span><span data-lang="ja">${ja}</span>`;
    const COLORS = ['#0a5c74', '#d0613d', '#2a8a5c', '#7a5cc2', '#c58a00', '#b3261e', '#3a7ca5', '#8a6d3b', '#5b8c85', '#a04a7a'];
    let map, layers = {}, markers = {}, data;

    function detail(p) {
        const near = p.precision === 'near';
        document.getElementById('dp-detail').innerHTML = `
            <h2>${esc(p.name)}</h2>${p.alias ? `<div class="alias">${bi('also: ', '別名：')}${esc(p.alias)}</div>` : ''}
            <dl>
                <dt>${bi('Area', 'エリア')}</dt><dd>${esc(p.area)}</dd>
                <dt>${bi('Max depth', '最大水深')}</dt><dd>${esc(p.depth || '–')}</dd>
                <dt>${bi('Features', '特徴')}</dt><dd>${esc(p.features || '–')}</dd>
                <dt>${bi('Position', '位置')}</dt><dd>${near ? bi('near ' + esc(p.position_note), esc(p.position_note) + 'の近く（目安）') : bi('approximate, within ' + esc(p.position_note), 'エリア内の目安（' + esc(p.position_note) + '）')}</dd>
            </dl>
            <div class="ph">${bi('Photos and video: in preparation (openly licensed only, with credits).', '写真・動画：準備中（再利用が許可されたものだけを、撮影者の表示つきで載せます）。')}</div>
            <div class="ph">${bi('Notes by Claude: in preparation.', 'Claude の解説：準備中。')}</div>
            <div class="src">${bi('Sources: ', '出典：')}${p.sources.map(s => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)} ↗</a>`).join('')}</div>`;
    }
    function popup(p) {
        return `<div class="dp-pop"><b>${esc(p.name)}</b>${p.precision === 'area' ? `<span class="dp-tag">${bi('approx.', '位置は目安')}</span>` : ''}
            <div class="f">${esc(p.features || '')}${p.depth ? ' · ' + esc(p.depth) : ''}</div>
            <button type="button" data-i="${data.points.indexOf(p)}">${bi('More', '詳しく')}</button></div>`;
    }
    function select(i, fly) {
        const p = data.points[i];
        detail(p);
        if (fly) { map.flyTo([p.lat, p.lng], Math.max(map.getZoom(), 13), { duration: 0.6 }); markers[i].openPopup(); }
        if (window.innerWidth <= 900) document.getElementById('dp-detail').scrollIntoView({ behavior: 'smooth', block: 'start' });
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
            const m = L.circleMarker([p.lat, p.lng], { radius: p.precision === 'near' ? 7 : 6, color: '#fff', weight: 1.5, fillColor: col[p.area], fillOpacity: p.precision === 'near' ? 0.95 : 0.75, dashArray: p.precision === 'near' ? null : '2 2' })
                .bindPopup(popup(p)).bindTooltip(esc(p.name), { direction: 'top', offset: [0, -6] });
            m.on('click', () => detail(p));
            m.addTo(layers[p.area]); markers[i] = m;
        });
        map.on('popupopen', e => { const b = e.popup.getElement().querySelector('button[data-i]'); if (b) b.onclick = () => select(+b.dataset.i, false); });
        const B = L.latLngBounds(data.points.map(p => [p.lat, p.lng])).pad(0.05);
        map.fitBounds(B);
        setTimeout(() => { map.invalidateSize(); map.fitBounds(B); }, 300);
        const chips = document.getElementById('dp-chips');
        chips.innerHTML = areas.map(a => `<button type="button" data-a="${esc(a)}"><i style="background:${col[a]}"></i>${esc(a)}（${data.points.filter(p => p.area === a).length}）</button>`).join('');
        chips.querySelectorAll('button').forEach(b => b.onclick = () => {
            const a = b.dataset.a, on = map.hasLayer(layers[a]);
            on ? map.removeLayer(layers[a]) : map.addLayer(layers[a]); b.classList.toggle('off', on);
        });
        document.getElementById('dp-list').innerHTML = areas.map(a => `<section><h3><i style="background:${col[a]}"></i>${esc(a)}</h3>${
            data.points.map((p, i) => p.area === a ? `<a data-i="${i}">${esc(p.name)}</a>` : '').join('')}</section>`).join('');
        document.querySelectorAll('#dp-list a').forEach(x => x.onclick = () => { document.getElementById('dp-map').scrollIntoView({ behavior: 'smooth' }); select(+x.dataset.i, true); });
    }
    init().catch(e => console.error(e));
})();
