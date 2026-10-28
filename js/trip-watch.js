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
    const minus5 = d => { const [y, m, dd] = d.split('-').map(Number); const t = new Date(Date.UTC(y, m - 1, dd - 5)); return [t.getUTCMonth() + 1, t.getUTCDate()]; };
    let SIG = '';
    const ai = (en, ja) => (en || ja) ? `<div class="tw-ai"><p><span class="tw-aitag">${bi('AI-GENERATED', 'AI自動生成')}</span>${bi(esc(en), esc(ja))}</p><span class="sig">${SIG}</span></div>` : '';

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
        SIG = J && J.model ? bi(`Written automatically by ${esc(J.model)} at ${esc(P.generated_at)} JST · not reviewed by a person`, `${esc(J.model)} が ${esc(P.generated_at)} に自動で記述・人による確認なし`) : '';
        if (J && J.model) document.getElementById('tw-model').innerHTML = bi('Reading: ', '所見：') + esc(J.model);

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
            const [fm, fd] = minus5(J.days[0].date);
            document.getElementById('tw-farline').innerHTML = far
                ? bi(`The whole trip is still more than five days away. Stamps will start appearing from ${fd} Nov, one day at a time.`, `旅程はまだ5日より先です。判子は${fm}/${fd}から順に付きます。`) : '';
            document.getElementById('tw-days').innerHTML = J.days.map(d => {
                const s = STAMP[d.stamp] || STAMP.undecided;
                const lead = d.lead > 0 ? bi(`${d.lead} days ahead`, `${d.lead}日先`) : d.lead === 0 ? bi('today', '今日') : '';
                const [m5, d5] = minus5(d.date);
                const note = d.lead > 5
                    ? (far ? '' : bi(`Nothing can be confirmed yet. A stamp comes from ${d5} Nov.`, `まだ確定できるものはありません。判子は${m5}/${d5}から付きます。`))
                    : bi(esc(d.note_en), esc(d.note_ja));
                return `<article class="tw-day${far ? ' short' : ''}">
                    <div class="d">${day(d.date)}</div>
                    <div class="role">${ROLE[d.date] || ''}</div>
                    <div class="note">${note}</div>
                    <div class="lead">${lead}</div>
                    <div class="stamp ${d.stamp}" title="${s[0]} / ${s[1]}">${bi(s[1], s[0])}</div>
                </article>`;
            }).join('');
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
            document.getElementById('tw-days').innerHTML = `<p class="tw-muted">${bi('The reading could not be produced this time. The data below are current.', '今回は所見を作れませんでした。下のデータは最新です。')}</p>`;
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
