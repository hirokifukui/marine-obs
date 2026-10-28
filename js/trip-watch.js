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
        '2026-11-05': bi('Fly in · ANA87', '移動・ANA87'),
        '2026-11-06': bi('Dive day 1', '潜水 1日目'),
        '2026-11-07': bi('Dive day 2', '潜水 2日目'),
        '2026-11-08': bi('Dive day 3 (last)', '潜水 3日目（最終）'),
        '2026-11-09': bi('Fly out · ANA88', '移動・ANA88')
    };

    async function load() {
        const url = `${SUPABASE_URL}/rest/v1/trip_watch?select=created_at,payload&trip_id=eq.${TRIP}&order=created_at.desc&limit=1`;
        const r = await fetch(url, { headers: { apikey: ANON, Authorization: `Bearer ${ANON}` } });
        const rows = await r.json();
        if (!rows.length) return;
        render(rows[0].payload);
    }

    function render(P) {
        const J = P.judgment;
        document.getElementById('tw-updated').textContent = P.generated_at + ' JST';
        if (J && J.model) document.getElementById('tw-model').innerHTML = bi('Reading: ', '所見：') + esc(J.model);

        // 警報バー
        const W = P.warnings;
        const ab = document.getElementById('tw-alertbar');
        if (W && W.active && W.active.length) {
            ab.innerHTML = `<div class="tw-alertbar">${bi('In force for Miyakojima City: ', '宮古島市に発表中：')}${W.active.map(a => bi(esc(a.en), esc(a.ja))).join(' / ')}</div>`;
        }

        // 日ごとの判子
        if (J && J.days) {
            document.getElementById('tw-days').innerHTML = J.days.map(d => {
                const s = STAMP[d.stamp] || STAMP.undecided;
                const lead = d.lead > 0 ? bi(`${d.lead} days ahead`, `${d.lead}日先`) : d.lead === 0 ? bi('today', '今日') : '';
                return `<article class="tw-day">
                    <div class="d">${day(d.date)}</div>
                    <div class="role">${ROLE[d.date] || ''}</div>
                    <div class="note">${bi(esc(d.note_en), esc(d.note_ja))}</div>
                    <div class="lead">${lead}</div>
                    <div class="stamp ${d.stamp}" title="${s[0]} / ${s[1]}">${bi(s[1], s[0])}</div>
                </article>`;
            }).join('');
            document.getElementById('tw-karte').innerHTML = `
                <h3>${bi('Reading', '所見')}</h3>
                <p>${bi(esc(J.summary_en), esc(J.summary_ja))}</p>
                <p class="change"><strong>${bi('What would change this: ', '判断が変わるとき：')}</strong>${bi(esc(J.change_en), esc(J.change_ja))}</p>
                <p class="sig">${bi('Written by ', '記述：')}${esc(J.model)} · ${esc(P.generated_at)} JST</p>`;
        } else {
            document.getElementById('tw-days').innerHTML = `<p class="tw-muted">${bi('The reading could not be produced this time. The data below are current.', '今回は所見を作れませんでした。下のデータは最新です。')}</p>`;
            document.getElementById('tw-karte').innerHTML = '';
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

        // 強風の確率
        document.getElementById('tw-bars').innerHTML = (P.ensemble || []).map(r => {
            const trip = r.day >= '2026-11-05';
            return `<div class="tw-bar"><span style="${trip ? 'font-weight:600' : ''}">${day(r.day)}</span>
                <span class="track"><span class="p10" style="width:${r.p10}%"></span><span class="p15" style="width:${r.p15}%"></span><span class="p25" style="width:${r.p25}%"></span></span>
                <span>${Math.round(r.p15)}%</span></div>`;
        }).join('') + `<div class="tw-legend" style="margin-top:0.2rem">${bi('right-hand figure = chance of ≥15 m/s', '右の数字＝15m/s以上の確率')}</div>`;

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

        // 飛行機と警報
        document.getElementById('tw-flights').innerHTML = `
            <p>${bi('Thu 5 Nov', '11/5（木）')}　<strong>ANA87</strong>　${bi('Haneda 12:00 → Miyako 15:15', '羽田 12:00 → 宮古 15:15')}<br>
               ${bi('Mon 9 Nov', '11/9（月）')}　<strong>ANA88</strong>　${bi('Miyako 16:10 → Haneda 18:45', '宮古 16:10 → 羽田 18:45')}</p>
            <p><a href="https://www.ana.co.jp/fs/dom/jp/" target="_blank" rel="noopener">${bi('ANA flight status', 'ANA 運航状況')} ↗</a>　·
               <a href="https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=4721400" target="_blank" rel="noopener">${bi('JMA warnings for Miyakojima City', '気象庁 宮古島市の警報・注意報')} ↗</a></p>
            <p class="tw-muted">${W ? bi('JMA, ' + esc(W.report) + ': ', '気象庁 ' + esc(W.report) + '：') + esc(W.headline || '') : ''}</p>`;
    }

    load().catch(e => console.error(e));
})();
