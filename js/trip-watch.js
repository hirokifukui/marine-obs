// Trip Watch: latest row of trip_watch (Supabase) → page
(function () {
    const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
    const ANON = document.currentScript.dataset.anon;
    const TRIP = document.currentScript.dataset.trip;
    const STAMP = {
        normal: ['平常', 'Normal'], monitor: ['監視', 'Monitor'], watch: ['注意', 'Watch'],
        alert: ['警報', 'Alert'], undecided: ['未定', 'TBD']
    };
    const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const bi = (en, ja) => `<span data-lang="en">${en}</span><span data-lang="ja">${ja}</span>`;
    const wdJa = '日月火水木金土', wdEn = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const day = d => {
        const [y, m, dd] = d.split('-').map(Number);
        const w = new Date(Date.UTC(y, m - 1, dd)).getUTCDay();
        return bi(`${wdEn[w]} ${dd} Nov`, `${m}/${dd}（${wdJa[w]}）`);
    };
    const ROLE = {
        '2026-11-05': bi('Arrival day', '到着日'),
        '2026-11-06': bi('Dive day 1 · some arrive', '潜水 1日目・到着の人も'),
        '2026-11-07': bi('Dive day 2', '潜水 2日目'),
        '2026-11-08': bi('Dive day 3 (last)', '潜水 3日目（最終）'),
        '2026-11-09': bi('Departure day', '出発日')
    };
    const AIRLINES = [
        ['ANA', 'ANA', 'https://www.ana.co.jp/fs/dom/jp/'],
        ['JAL · JTA · RAC', 'JAL・JTA・RAC', 'https://www.jal.co.jp/jp/ja/dom/service/skynavi/'],
        ['Skymark', 'スカイマーク', 'https://www.skymark.co.jp/ja/'],
        ['Jetstar', 'ジェットスター', 'https://www.jetstar.com/jp/ja/'],
        ['Peach', 'ピーチ', 'https://www.flypeach.com/'],
        ['Shimojishima Airport', '下地島空港', 'https://shimojishima.jp/'],
        ['Naha Airport', '那覇空港', 'https://www.naha-airport.co.jp/']
    ];
    const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const minus5 = d => { const [y, m, dd] = d.split('-').map(Number); const t = new Date(Date.UTC(y, m - 1, dd - 5)); return [t.getUTCMonth() + 1, t.getUTCDate(), MON[t.getUTCMonth()]]; };
    let SIG = '';
    const ai = (en, ja) => (en || ja) ? `<div class="tw-ai"><p><span class="tw-aitag">${bi('AI-GENERATED', 'AI自動生成')}</span>${bi(esc(en), esc(ja))}</p><span class="sig">${SIG}</span></div>` : '';


    // 日ごとの風（自前キャンバス：Windy風の連続色＋流線）
    const CMAP = [[0, [98, 113, 183]], [3, [57, 97, 159]], [5, [74, 148, 169]], [7, [77, 141, 123]], [10, [83, 165, 83]], [13, [53, 159, 53]],
        [15, [167, 157, 81]], [17, [159, 127, 58]], [20, [161, 108, 92]], [25, [129, 58, 78]], [30, [175, 80, 136]], [40, [117, 74, 147]]];
    const cmap = v => {
        if (v <= CMAP[0][0]) return CMAP[0][1];
        for (let i = 1; i < CMAP.length; i++) if (v <= CMAP[i][0]) {
            const [a, ca] = CMAP[i - 1], [b, cb] = CMAP[i], f = (v - a) / (b - a);
            return ca.map((c, k) => Math.round(c + (cb[k] - c) * f));
        }
        return CMAP[CMAP.length - 1][1];
    };
    const EXT = { w: 108, e: 151.5, s: 8, n: 39.5 }, KX = Math.cos(24 * Math.PI / 180);
    const DIR16 = ['北', '北北東', '北東', '東北東', '東', '東南東', '南東', '南南東', '南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西'];
    const DIR16E = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const PLACES = [[24.79, 125.13, '宮古島', 'Miyako', true], [26.21, 127.68, '那覇', 'Naha'], [25.03, 121.56, '台北', 'Taipei'],
        [35.68, 139.77, '東京', 'Tokyo'], [31.23, 121.47, '上海', 'Shanghai'], [14.6, 120.98, 'マニラ', 'Manila'], [33.59, 130.4, '福岡', 'Fukuoka'], [27.09, 142.19, '父島', 'Chichijima']];
    let LAND = null;
    async function loadLand() {
        if (LAND || !window.topojson) return LAND;
        try {
            const t = await (await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-50m.json')).json();
            LAND = topojson.feature(t, t.objects.land);
        } catch (e) { console.error(e); }
        return LAND;
    }
    async function dailyMap(P) {
        const M = P.windmap, wrap = document.getElementById('tw-dwrap');
        if (!wrap) return;
        if (!M) { wrap.parentElement.innerHTML = `<p class="tw-muted">${bi('Daily wind map unavailable this time.', '今回は日ごとの風の地図を取得できませんでした。')}</p>`; return; }
        const fc = document.getElementById('tw-dfield'), tc = document.getElementById('tw-dtrail'), rd = document.getElementById('tw-dread');
        const nx = M.lons.length, ny = M.lats.length, step = M.lons[1] - M.lons[0];
        document.getElementById('tw-cbar').style.background = 'linear-gradient(to right,' + CMAP.filter(c => c[0] <= 30).map(([v, c]) => `rgb(${c}) ${v / 30 * 100}%`).join(',') + ')';
        await loadLand();
        let W = 0, H = 0, k = 1, dpr = Math.min(window.devicePixelRatio || 1, 2), cur = null, U = null, V = null, S = null, anim = null;
        const px = (lat, lon) => [(lon - EXT.w) * KX * k, (EXT.n - lat) * k];
        const ll = (x, y) => [EXT.n - y / k, EXT.w + x / (KX * k)];
        const sample = (A, lat, lon) => {
            const fx = (lon - M.lons[0]) / step, fy = (lat - M.lats[0]) / step;
            const x0 = Math.max(0, Math.min(nx - 2, Math.floor(fx))), y0 = Math.max(0, Math.min(ny - 2, Math.floor(fy)));
            const tx = Math.max(0, Math.min(1, fx - x0)), ty = Math.max(0, Math.min(1, fy - y0));
            const g = (i, j) => A[(y0 + j) * nx + (x0 + i)];
            const a = g(0, 0), b = g(1, 0), c = g(0, 1), d = g(1, 1);
            if ([a, b, c, d].some(v => v == null || Number.isNaN(v))) return [a, b, c, d].find(v => v != null && !Number.isNaN(v)) ?? null;
            return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty;
        };
        const lang = () => document.body.classList.contains('ja') ? 'ja' : 'en';
        function landPath(ctx) {
            if (!LAND) return;
            ctx.beginPath();
            for (const f of LAND.features) {
                const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
                for (const poly of polys) for (const ring of poly) {
                    let inb = ring.some(([lo, la]) => lo > EXT.w - 5 && lo < EXT.e + 5 && la > EXT.s - 5 && la < EXT.n + 5);
                    if (!inb) continue;
                    ring.forEach(([lo, la], i) => { const [x, y] = px(la, lo); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
                    ctx.closePath();
                }
            }
        }
        function drawField() {
            const ctx = fc.getContext('2d');
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            const img = ctx.createImageData(Math.ceil(W * dpr), Math.ceil(H * dpr)), D = img.data, iw = img.width;
            for (let y = 0; y < img.height; y += 2) for (let x = 0; x < iw; x += 2) {
                const [la, lo] = ll(x / dpr, y / dpr), v = sample(S, la, lo);
                const c = v == null ? [60, 70, 90] : cmap(v);
                for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
                    const o = ((y + dy) * iw + (x + dx)) * 4; if (o >= D.length) continue;
                    D[o] = c[0]; D[o + 1] = c[1]; D[o + 2] = c[2]; D[o + 3] = 255;
                }
            }
            ctx.putImageData(img, 0, 0);
            // 陸：少し暗く、海岸線を黒く
            landPath(ctx); ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fill('evenodd');
            ctx.lineWidth = 0.9; ctx.strokeStyle = 'rgba(15,15,20,0.85)'; ctx.stroke();
            // 台風
            for (const t of P.typhoons || []) {
                ctx.setLineDash([5, 4]); ctx.lineWidth = 1.6; ctx.strokeStyle = 'rgba(255,255,255,0.9)';
                ctx.beginPath(); t.points.forEach((p, i) => { const [x, y] = px(p.lat, p.lng); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.stroke();
                ctx.setLineDash([2, 3]); ctx.lineWidth = 1;
                for (const p of t.points) {
                    const [x, y] = px(p.lat, p.lng), r = (p.prob_km || 0) / 111 * k;
                    if (r > 0) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.stroke(); }
                    ctx.beginPath(); ctx.arc(x, y, 2.8, 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.fill();
                }
                ctx.setLineDash([]);
                const last = t.points[t.points.length - 1], [lx, ly] = px(last.lat, last.lng);
                ctx.font = '600 12px system-ui, sans-serif'; ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,0.8)'; ctx.shadowBlur = 3;
                ctx.fillText((lang() === 'ja' ? t.label : 'TY ' + t.label.replace(/\D/g, '')) + ' ' + last.time.slice(5, 10).replace('-', '/'), lx + 6, ly - 6);
                ctx.shadowBlur = 0;
            }
            // 地名
            ctx.font = '12px system-ui, sans-serif';
            for (const [la, lo, ja, en, main] of PLACES) {
                const [x, y] = px(la, lo); if (x < 0 || x > W || y < 0 || y > H) continue;
                if (W < 520 && !main && (en === 'Taipei' || en === 'Naha')) continue;
                ctx.beginPath(); ctx.arc(x, y, main ? 4.5 : 2.5, 0, Math.PI * 2); ctx.fillStyle = main ? '#fff' : 'rgba(255,255,255,0.85)'; ctx.fill();
                if (main) { ctx.lineWidth = 2; ctx.strokeStyle = '#0a5c74'; ctx.stroke(); }
                ctx.shadowColor = 'rgba(0,0,0,0.85)'; ctx.shadowBlur = 3; ctx.fillStyle = '#fff';
                ctx.font = main ? '700 13px system-ui, sans-serif' : '12px system-ui, sans-serif';
                ctx.fillText(lang() === 'ja' ? ja : en, x + 6, y + 4); ctx.shadowBlur = 0;
            }
        }
        function startParticles() {
            if (anim) cancelAnimationFrame(anim);
            const ctx = tc.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
            const N = Math.round(W * H / 700), parts = [];
            const spawn = p => { p.x = Math.random() * W; p.y = Math.random() * H; p.age = Math.random() * 80; return p; };
            for (let i = 0; i < N; i++) parts.push(spawn({}));
            const speed = 0.045 * k / 10;
            const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
            const frame = () => {
                ctx.globalCompositeOperation = 'destination-in'; ctx.fillStyle = 'rgba(0,0,0,0.88)'; ctx.fillRect(0, 0, W, H);
                ctx.globalCompositeOperation = 'source-over'; ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth = 1.1; ctx.beginPath();
                for (const p of parts) {
                    const [la, lo] = ll(p.x, p.y), u = sample(U, la, lo), v = sample(V, la, lo);
                    if (u == null || v == null || p.age++ > 60) { spawn(p); p.age = 0; continue; }
                    const nx2 = p.x + u * speed * 10 * KX / KX, ny2 = p.y - v * speed * 10;
                    ctx.moveTo(p.x, p.y); ctx.lineTo(nx2, ny2); p.x = nx2; p.y = ny2;
                    if (p.x < 0 || p.x > W || p.y < 0 || p.y > H) spawn(p);
                }
                ctx.stroke();
                if (!reduce) anim = requestAnimationFrame(frame);
            };
            if (reduce) { for (let i = 0; i < 40; i++) frame(); } else anim = requestAnimationFrame(frame);
        }
        function layout() {
            W = wrap.clientWidth; k = W / ((EXT.e - EXT.w) * KX); H = Math.round((EXT.n - EXT.s) * k);
            for (const c of [fc, tc]) { c.width = Math.ceil(W * dpr); c.height = Math.ceil(H * dpr); c.style.height = H + 'px'; }
            tc.style.width = W + 'px';
        }
        const days = Object.keys(M.days).sort();
        const lead = d => (J0 && J0.days ? (J0.days.find(x => x.date === d) || {}).lead : null);
        function show(d) {
            cur = d; const D = M.days[d];
            S = D.ws; U = D.ws.map((s, i) => s == null || D.wd[i] == null ? null : -s * Math.sin(D.wd[i] * Math.PI / 180));
            V = D.ws.map((s, i) => s == null || D.wd[i] == null ? null : -s * Math.cos(D.wd[i] * Math.PI / 180));
            const l = lead(d); wrap.classList.toggle('far', l == null || l > 5);
            document.querySelectorAll('#tw-dtabs button').forEach(b => b.classList.toggle('on', b.dataset.d === d));
            drawField(); startParticles();
            const [mx, my] = px(24.79, 125.13); readAt(mx, my);
        }
        function readAt(x, y) {
            const [la, lo] = ll(x, y), s = sample(S, la, lo), u = sample(U, la, lo), v = sample(V, la, lo);
            if (s == null) { rd.textContent = ''; return; }
            const from = (Math.atan2(-u, -v) * 180 / Math.PI + 360) % 360, i = Math.round(from / 22.5) % 16;
            rd.textContent = lang() === 'ja' ? `${s.toFixed(0)} m/s　${DIR16[i]}の風（${la.toFixed(1)}N ${lo.toFixed(1)}E）` : `${s.toFixed(0)} m/s ${DIR16E[i]} (${la.toFixed(1)}N ${lo.toFixed(1)}E)`;
        }
        const pointer = e => { const r = wrap.getBoundingClientRect(); readAt(e.clientX - r.left, e.clientY - r.top); };
        wrap.addEventListener('mousemove', pointer); wrap.addEventListener('click', pointer);
        document.getElementById('tw-dtabs').innerHTML = days.map(d => { const l = lead(d); return `<button type="button" data-d="${d}" class="${l == null || l > 5 ? 'far' : ''}">${day(d)}</button>`; }).join('');
        document.querySelectorAll('#tw-dtabs button').forEach(b => b.addEventListener('click', () => show(b.dataset.d)));
        ['lang-en', 'lang-ja'].forEach(id => { const b = document.getElementById(id); if (b) b.addEventListener('click', () => setTimeout(() => cur && show(cur), 0)); });
        let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { layout(); cur && show(cur); }, 200); });
        window.__twShow = d => { if (M.days[d]) show(d); };
        layout(); show(days[0]);
    }
    let J0 = null, PREV = null;
    async function load() {
        const url = `${SUPABASE_URL}/rest/v1/trip_watch?select=created_at,payload&trip_id=eq.${TRIP}&order=created_at.desc&limit=8`;
        const r = await fetch(url, { headers: { apikey: ANON, Authorization: `Bearer ${ANON}` } });
        const rows = await r.json();
        if (!rows.length) return;
        J0 = rows[0].payload.judgment;
        const t0 = new Date(rows[0].created_at).getTime();
        const prevRow = rows.slice(1).find(r => t0 - new Date(r.created_at).getTime() >= 2.5 * 3600e3) || rows[1];
        PREV = prevRow ? prevRow.payload : null;
        render(rows[0].payload);
        try { dailyMap(rows[0].payload); } catch (e) { console.error(e); }
    }

    function render(P) {
        const J = P.judgment;
        document.getElementById('tw-updated').textContent = P.generated_at + ' JST';
        SIG = J && J.model ? bi(`Written automatically by ${esc(J.model)} at ${esc(P.generated_at)} JST · not reviewed by a person`, `${esc(J.model)} が ${esc(P.generated_at)} に自動で記述・人による確認なし`) : '';
        if (J && J.model) document.getElementById('tw-model').innerHTML = bi('Reading: ', '所見：') + esc(J.model);
        const SG = document.getElementById('tw-sig'); if (SG) SG.innerHTML = bi('All text tagged AI-GENERATED on this page: ', 'このページの「AI自動生成」の文章はすべて、') + SIG;

        // 警報バー
        const W0 = P.warnings || {};
        const W = W0.active ? { miyako: { ...W0, ja: '宮古島市', en: 'Miyakojima City' } } : W0;
        const ab = document.getElementById('tw-alertbar');
        const hot = Object.values(W).filter(w => w.active && w.active.length);
        if (hot.length) {
            ab.innerHTML = `<div class="tw-alertbar">${hot.map(w => bi(`In force for ${esc(w.en)}: ` + w.active.map(a => esc(a.en)).join(', '), `${esc(w.ja)}に発表中：` + w.active.map(a => esc(a.ja)).join('、'))).join('<br>')}</div>`;
        }

        // 日ごとの判子
        if (J && J.days) {
            const far = J.days.every(d => d.lead > 5);
            const [fm, fd, fmo] = minus5(J.days[0].date);
            document.getElementById('tw-farline').innerHTML = far
                ? bi(`The whole trip is still more than five days away. Stamps will start appearing from ${fd} ${fmo}, one day at a time.`, `旅程はまだ5日より先です。判子は${fm}/${fd}から順に付きます。`) : '';
            const stampCard = d => {
                const s = STAMP[d.stamp] || STAMP.undecided;
                const lead = d.lead > 0 ? bi(`${d.lead} days ahead`, `${d.lead}日先`) : d.lead === 0 ? bi('today', '今日') : '';
                const [m5, d5, mo5] = minus5(d.date);
                const note = d.lead > 5 ? bi(`Nothing can be confirmed yet. A stamp comes from ${d5} ${mo5}.`, `まだ確定できるものはありません。判子は${m5}/${d5}から付きます。`) : bi(esc(d.note_en), esc(d.note_ja));
                return `<article class="tw-day short"><div class="d">${day(d.date)}</div><div class="role">${ROLE[d.date] || ''}</div>
                    <div class="note">${note}</div><div class="lead">${lead}</div>
                    <div class="stamp ${d.stamp}" title="${s[0]} / ${s[1]}">${bi(s[1], s[0])}</div></article>`;
            };
            document.getElementById('tw-days').innerHTML = J.days.filter(d => ['2026-11-05', '2026-11-06', '2026-11-09'].includes(d.date)).map(stampCard).join('');
            const K = document.getElementById('tw-karte');
            K.classList.add('tw-ai-frame');
            K.innerHTML = `
                <h3><span class="tw-aitag">${bi('AI-GENERATED', 'AI自動生成')}</span>${bi('Reading', '所見')}</h3>
                <p class="disclose">${bi('This reading is written automatically every three hours by a generative AI (Anthropic’s Claude) from the numbers on this page. It is not written by the site owner and has not been checked by a person. Whether boats go out is decided by the dive shop.',
                    'この所見は、生成AI（Anthropic の Claude）が3時間ごとに、このページの数値から自動で書いたものです。サイト運営者が書いたものではなく、人による確認も経ていません。出航の可否は現地ショップが決めます。')}</p>
                <p>${bi(esc(J.summary_en), esc(J.summary_ja))}</p>
                <p class="change"><strong>${bi('What would change this: ', '判断が変わるとき：')}</strong>${bi(esc(J.change_en), esc(J.change_ja))}</p>
                <p class="sig">${SIG}</p>`;
        } else {
            document.getElementById('tw-days').innerHTML = '';
            document.getElementById('tw-hero').innerHTML = `<p class="tw-muted">${bi('The reading could not be produced this time. The data below are current.', '今回は所見を作れませんでした。下のデータは最新です。')}</p>`;
            document.getElementById('tw-karte').innerHTML = '';
        }
        const C = (J && J.comments) || {};
        for (const k of ['typhoon', 'wind', 'waves']) {
            const el = document.getElementById('tw-c-' + k);
            if (el && C[k]) el.innerHTML = ai(C[k].en, C[k].ja);
        }

        // 台風
        const T = document.getElementById('tw-typhoon');
        if (!P.typhoon_ok) {
            T.innerHTML = `<p class="tw-muted">${bi('JMA typhoon data unavailable this time.', '気象庁の台風情報を今回は取得できませんでした。')}</p>`;
        } else if (!P.typhoons.length) {
            T.innerHTML = `<p>${bi('No active typhoons (JMA).', '発生中の台風はありません（気象庁）。')}</p>`;
        } else {
            T.innerHTML = P.typhoons.map(t => {
                const num = t.label.replace(/\D/g, '');
                const head = bi(`Typhoon No. ${num}${t.name ? ' (' + esc(t.name) + ')' : ''}`, `${esc(t.label)}${t.name ? '（' + esc(t.name) + '）' : ''}`);
                const c = t.closest;
                const still = t.still ? bi(' — the last forecast point, still closing in', '（予報の最終時刻。この先さらに近づく進路）') : '';
                const verdict = t.storm_hit ? `<span class="tw-hit">${bi('Storm-warning area reaches Miyako', '暴風警戒域が宮古島にかかる予報')}</span>`
                    : c.dist <= 800 ? `<span class="tw-split">${bi('Within 800 km', '800km以内に接近')}</span>` : bi('Out of range for now', '現時点では影響圏外');
                const rows = t.points.map(p => `<tr><td>${p.hours === 0 ? bi('now', '実況') : '+' + p.hours + 'h'}</td><td>${esc(p.time.slice(5))}</td>
                    <td>${p.lat.toFixed(1)}N ${p.lng.toFixed(1)}E</td><td>${esc(p.pressure)} hPa / ${esc(p.wind || '–')} m/s</td>
                    <td>${Math.round(p.prob_km)} / ${Math.round(p.storm_km)} km</td>
                    <td class="${p.in_storm ? 'tw-hit' : ''}">${Math.round(p.dist)} km${p.in_storm ? ' ⚠' : ''}</td></tr>`).join('');
                return `<p><strong>${head}</strong> · ${bi('issued', '発表')} ${esc(t.issue)}<br>
                    ${bi('Closest to Miyako', '宮古島に最も近づくのは')} ${esc(c.time)}, ${bi('about', '約')} ${c.dist} km${still}. ${verdict}</p>
                    <div class="tw-scroll"><table class="tw-table"><thead><tr>
                    <th>${bi('Step', '区分')}</th><th>${bi('Time (JST)', '時刻')}</th><th>${bi('Centre', '中心')}</th>
                    <th>${bi('Pressure / max wind', '気圧／最大風速')}</th><th>${bi('Forecast circle / storm radius', '予報円／暴風半径')}</th><th>${bi('To Miyako', '宮古島まで')}</th>
                    </tr></thead><tbody>${rows}</tbody></table></div>`;
            }).join('<hr style="border:0;border-top:1px solid var(--border);margin:1.2rem 0">') +
                `<p class="tw-muted" style="margin-top:0.6rem">${bi('⚠ = forecast circle plus storm radius (≈ storm-warning area) includes Miyako. JMA forecasts reach five days.', '⚠＝予報円＋暴風半径（≒暴風警戒域）が宮古島を含む。気象庁の予報は5日先まで。')}</p>`;
        }

        // 潜れそうか（凪・穏やか・波あり・荒れ）
        const OD = P.dive_odds || [];
        const OC = [['nagi', '#4fa3c7', 'Calm', '凪'], ['futsu', '#8cc9a0', 'Moderate', '穏やか'], ['girigiri', '#e9c46a', 'Choppy', '波あり'], ['dame', '#e76f51', 'Rough', '荒れ']];
        const leadD = d => { const t0 = new Date(P.generated_at.slice(0, 10) + 'T00:00:00Z'), t1 = new Date(d + 'T00:00:00Z'); return Math.round((t1 - t0) / 864e5); };
        const PO = (PREV && PREV.dive_odds) || [];
        const HERO = ['2026-11-06', '2026-11-07', '2026-11-08'];
        const hero = document.getElementById('tw-hero');
        if (OD.length) {
            hero.innerHTML = HERO.map(dd => {
                const r = OD.find(x => x.day === dd); if (!r) return '';
                const ok = (r.nagi || 0) + (r.futsu || 0), l = leadD(dd), far = l > 5;
                const p = PO.find(x => x.day === dd), pok = p ? (p.nagi || 0) + (p.futsu || 0) : null;
                const dl = pok == null ? '' : ok - pok;
                const delta = pok == null ? '' : dl === 0 ? bi('same as 3 h ago', '3時間前と同じ') : `<span class="${dl > 0 ? 'up' : 'down'}">${dl > 0 ? '↑' : '↓'}${Math.abs(dl)}</span> ${bi('vs 3 h ago', '3時間前比')}`;
                const jd = (J && J.days || []).find(x => x.date === dd) || { stamp: 'undecided' };
                const s = STAMP[jd.stamp] || STAMP.undecided;
                const sn = l > 5 ? bi('stamp from ' + minus5(dd)[1] + ' ' + minus5(dd)[2], '判子は' + minus5(dd)[0] + '/' + minus5(dd)[1] + 'から') : bi(esc(jd.note_en || ''), esc(jd.note_ja || ''));
                const segs = OC.map(([k, c]) => r[k] ? `<span style="width:${r[k]}%;background:${c}"></span>` : '').join('');
                return `<button type="button" class="tw-hcard${far ? ' far' : ''}" data-d="${dd}">
                    <div class="hd"><span class="d">${day(dd)}</span><span class="role">${ROLE[dd] || ''}</span></div>
                    <div class="big">${ok}<small>%</small></div><div class="lbl">${bi('chance of diving', '潜れそう')}${r.wave_cap ? ' 🌊' : ''}</div>
                    <div class="hbar">${segs}</div>
                    <div class="meta">${far ? `<span>${bi('ref. · ' + l + ' days ahead', '参考・' + l + '日先')}</span>` : `<span>${bi(l + ' days ahead', l + '日先')}</span>`}${delta ? `<span>${delta}</span>` : ''}</div>
                    <div class="stampline"><span class="chip ${jd.stamp}">${bi(s[1], s[0])}</span><span class="n">${sn}</span></div>
                </button>`;
            }).join('');
            hero.querySelectorAll('.tw-hcard').forEach(b => b.addEventListener('click', () => {
                if (window.__twShow) window.__twShow(b.dataset.d);
                const m = document.getElementById('daily-wind'); if (m) m.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }));
        } else hero.innerHTML = `<p class="tw-muted">${bi('Ensemble data unavailable this time.', '今回はアンサンブルを取得できませんでした。')}</p>`;
        document.getElementById('tw-bars').innerHTML = OD.length ? OD.filter(r => r.day >= '2026-11-05').map(r => {
            const far = leadD(r.day) > 5, ok = (r.nagi || 0) + (r.futsu || 0);
            const segs = OC.map(([k, c, en, ja]) => r[k] ? `<span style="width:${r[k]}%;background:${c}" title="${ja} ${r[k]}% / ${en}"></span>` : '').join('');
            return `<div class="tw-orow${far ? ' far' : ''}"><span>${day(r.day)}${far ? `<span class="tag">${bi('ref.', '参考')}</span>` : ''}</span>
                <span class="track">${segs}</span>
                <span class="ok">${bi('Diveable ', '潜れそう ')}<b>${ok}%</b>${r.wave_cap ? ' 🌊' : ''}</span></div>`;
        }).join('') + `<p class="tw-legend" style="margin:0.3rem 0 0">${bi('Diveable = Calm + Moderate. 🌊 = swell over 2.5 m caps the day.', '潜れそう＝凪＋穏やか。🌊＝波高2.5m超のため上限「波あり」。')}</p>`
            : `<p class="tw-muted">${bi('Ensemble data unavailable this time.', '今回はアンサンブルを取得できませんでした。')}</p>`;

        // 波のモデル比較
        const M = P.marine || {}, S = P.stormglass || {};
        const days = Object.keys(M).sort();
        const sgSrc = ['noaa', 'meteo', 'sg'].filter(k => days.some(d => S[d] && S[d].waveHeight && S[d].waveHeight[k] != null));
        const om = ['ECMWF', 'NOAA GFS', 'Météo-France'];
        const head = `<tr><th>${bi('Day', '日付')}</th>${om.map(m => `<th>${m}</th>`).join('')}${sgSrc.map(k => `<th>SG·${k}</th>`).join('')}<th>${bi('Spread', '差')}</th><th>${bi('Wind (SG max)', '風（SG最大）')}</th></tr>`;
        const body = days.map(d => {
            const vals = om.map(m => M[d][m] ? M[d][m].hs_max : null).concat(sgSrc.map(k => S[d] && S[d].waveHeight ? S[d].waveHeight[k] : null));
            const ok = vals.filter(v => v != null);
            const spread = ok.length > 1 ? Math.max(...ok) - Math.min(...ok) : 0;
            const ws = S[d] && S[d].windSpeed ? Math.max(...Object.values(S[d].windSpeed)) : null;
            return `<tr class="${d >= '2026-11-05' ? 'trip' : ''}"><td>${day(d)}</td>${vals.map(v => `<td>${v == null ? '–' : v.toFixed(1)}</td>`).join('')}
                <td class="${spread > 1 ? 'tw-split' : ''}">${ok.length > 1 ? spread.toFixed(1) : '–'}</td><td>${ws == null ? '–' : ws.toFixed(0) + ' m/s'}</td></tr>`;
        }).join('');
        document.getElementById('tw-waves').innerHTML = `<table class="tw-table"><thead>${head}</thead><tbody>${body}</tbody></table>`;

        // 移動（到着・出発）
        const A = P.airports || [], TA = P.typhoon_airports || [];
        const TD = ['2026-11-05', '2026-11-06', '2026-11-09'];
        const leadOf = d => (J && J.days ? (J.days.find(x => x.date === d) || {}).lead : null);
        const near = d => { const l = leadOf(d); return l != null && l <= 5; };
        const fmtW = w => {
            if (!w) return '–';
            const bits = [`${w.wind_max ?? '–'} / ${w.gust_max ?? '–'}`];
            if (w.thunder_h) bits.push('⚡' + w.thunder_h + 'h');
            if (w.vis_min_km != null && w.vis_min_km < 3) bits.push(bi('vis ', '視程') + w.vis_min_km + 'km');
            const cls = (w.gust_max >= 20 || w.thunder_h >= 3) ? 'tw-hit' : (w.gust_max >= 15 || w.thunder_h) ? 'tw-split' : '';
            return `<span class="${cls}">${bits.join(' · ')}</span>`;
        };
        let html = '';
        if (A.length) {
            const anyNear = TD.some(near);
            const rows = A.map(ap => `<tr><td>${bi(esc(ap.en), esc(ap.ja))} <span class="tw-muted">${esc(ap.code)}</span></td>${TD.map(d => `<td>${near(d) ? fmtW(ap.days[d]) : '<span class="tw-muted">–</span>'}</td>`).join('')}</tr>`).join('');
            html += `<div class="tw-scroll"><table class="tw-table"><thead><tr><th>${bi('Airport', '空港')}</th>${TD.map(d => `<th>${day(d)}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table></div>
                <p class="tw-muted" style="margin-top:0.5rem">${anyNear
                    ? bi('Wind / gust maximum (m/s), 06–21 local time, Open-Meteo. ⚡ = hours with thunderstorms. Amber = gusts ≥15 m/s or thunder; red = gusts ≥20 m/s or 3+ hours of thunder.', '風速／最大瞬間風速（m/s）の6〜21時の最大。Open-Meteo。⚡＝雷雨の時間数。黄＝突風15m/s以上か雷、赤＝20m/s以上か雷3時間以上。')
                    : bi('Airport weather is shown from five days before each travel day. Nothing can be confirmed yet.', '空港の天気は、それぞれの移動日の5日前から表示します。まだ確定できるものはありません。')}</p>`;
        }
        if (TA.length) {
            html += `<p class="tw-sub">${bi('Typhoon: closest forecast point to each airport (JMA)', '台風：各空港に最も近づく予報点（気象庁）')}</p>` + TA.map(t => {
                const cells = A.map(ap => { const x = t.airports[ap.code]; if (!x) return ''; const hit = x.dist <= (x.prob_km || 0) + (x.storm_km || 0);
                    return `<tr><td>${bi(esc(ap.en), esc(ap.ja))}</td><td class="${hit ? 'tw-hit' : x.dist <= 800 ? 'tw-split' : ''}">${x.dist} km${hit ? ' ⚠' : ''}</td><td>${esc((x.time || '').slice(5))}</td></tr>`; }).join('');
                return `<p style="margin:0.3rem 0"><strong>${bi('Typhoon No. ' + esc(t.label.replace(/\D/g, '')), esc(t.label))}</strong></p><div class="tw-scroll"><table class="tw-table"><thead><tr><th>${bi('Airport', '空港')}</th><th>${bi('Closest', '最接近')}</th><th>${bi('Time (JST)', '時刻')}</th></tr></thead><tbody>${cells}</tbody></table></div>`;
            }).join('');
        }
        const wl = Object.values(W).map(w => w.active && w.active.length
            ? bi(`${esc(w.en)}: ` + w.active.map(a => esc(a.en)).join(', ') + ` (JMA ${esc(w.report)})`, `${esc(w.ja)}：` + w.active.map(a => esc(a.ja)).join('、') + `（気象庁 ${esc(w.report)}）`)
            : bi(`${esc(w.en)}: no warnings or advisories in force (last JMA bulletin ${esc(w.report)})`, `${esc(w.ja)}：発表中の警報・注意報はありません（気象庁の最終発表 ${esc(w.report)}）`)).join('<br>');
        html += `<p class="tw-sub">${bi('JMA warnings', '気象庁の警報・注意報')}</p><p class="tw-muted" style="margin:0">${wl}</p>
            <p class="tw-sub">${bi('Airline and airport status', '航空会社・空港の運航情報')}</p>
            <div class="tw-links">${AIRLINES.map(([en, ja, u]) => `<a href="${u}" target="_blank" rel="noopener">${bi(en, ja)} ↗</a>`).join('')}
            <a href="https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=4721400" target="_blank" rel="noopener">${bi('JMA Miyakojima ↗', '気象庁 宮古島市 ↗')}</a>
            <a href="https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=4720100" target="_blank" rel="noopener">${bi('JMA Naha ↗', '気象庁 那覇市 ↗')}</a></div>
            <p class="tw-muted" style="margin-top:0.6rem">${bi('Individual flight status is not tracked here. Please check your own airline.', '個別の便の運航状況はここでは追っていません。ご自身の航空会社でご確認ください。')}</p>`;
        html += C.travel ? ai(C.travel.en, C.travel.ja) : '';
        document.getElementById('tw-flights').innerHTML = html;
    }

    load().catch(e => console.error(e));
})();
