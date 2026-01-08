/**
 * charts.js - 全カードのチャート初期化（7地点対応版）
 * 
 * データソース:
 * - data/sst_card.json       → SSTカード
 * - data/extreme_days.json   → 極端日数カード  
 * - data/dhw_card.json       → DHWカード
 * - data/dhw_annual_peak.json → DHW詳細チャート
 * 
 * モニタリング7地点:
 * - 串本: 日本最北端のサンゴ分布域
 * - 小笠原: 黒潮の影響を受けない独立生態系
 * - 奄美: 北部琉球の代表地点
 * - 瀬底: 沖縄本島北部・研究拠点
 * - 万座: 沖縄本島中部・観光地
 * - 慶良間: 国立公園・高透明度
 * - 石西礁湖: 日本最大のサンゴ礁
 */

(function() {
    // Chart.js default settings
    Chart.defaults.font.family = "'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.font.size = 11;
    
    // 7地点の色定義
    const chartColors = {
        kushimoto: '#6366f1',   // インディゴ
        ogasawara: '#2f855a',   // グリーン
        amami: '#0891b2',       // シアン
        sesoko: '#2b6cb0',      // ブルー
        manza: '#c05621',       // オレンジ
        kerama: '#7c3aed',      // パープル
        sekisei: '#dc2626'      // レッド
    };
    
    // 地点名定義（短縮版・カード用）
    const siteNamesShort = {
        en: { kushimoto: 'Ksh', ogasawara: 'Oga', amami: 'Ama', sesoko: 'Ses', manza: 'Man', kerama: 'Ker', sekisei: 'Sek' },
        ja: { kushimoto: '串', ogasawara: '小', amami: '奄', sesoko: '瀬', manza: '万', kerama: '慶', sekisei: '石' }
    };
    
    // 地点名定義（フル）
    const siteNames = {
        en: { kushimoto: 'Kushimoto', ogasawara: 'Ogasawara', amami: 'Amami', sesoko: 'Sesoko', manza: 'Manza', kerama: 'Kerama', sekisei: 'Sekisei' },
        ja: { kushimoto: '串本', ogasawara: '小笠原', amami: '奄美', sesoko: '瀬底', manza: '万座', kerama: '慶良間', sekisei: '石西礁湖' }
    };
    
    // 7地点の配列（北から南の順）
    const ALL_SITES = ['kushimoto', 'ogasawara', 'amami', 'sesoko', 'manza', 'kerama', 'sekisei'];

    // Supabase設定
    const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlZ2l1aWJscGxpYWlucGRnZ2ZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQyMDkzNzQsImV4cCI6MjA3OTc4NTM3NH0.r9dBAsMLoXbgZL93lvA756r74U6YfCCfftHHlxYqZIw';

    // SST最新値をSupabaseから取得（7地点）
    async function loadSSTLatestFromSupabase() {
        try {
            const response = await fetch(
                `${SUPABASE_URL}/rest/v1/sst_daily?select=date,site_code,sst&order=date.desc&limit=50`,
                { headers: { 'apikey': SUPABASE_ANON_KEY } }
            );
            if (!response.ok) throw new Error('Supabase fetch failed');
            const data = await response.json();
            
            // 最新日付のデータを整形（7地点）
            const latest = {};
            let publishedDate = null;
            data.forEach(row => {
                if (ALL_SITES.includes(row.site_code) && !latest[row.site_code]) {
                    latest[row.site_code] = row.sst;
                    if (!publishedDate) publishedDate = row.date;
                }
            });
            
            // 衛星観測日は公開日の約3日前と推定
            const pubDateObj = new Date(Date.UTC(
                ...publishedDate.split('-').map(Number).map((v, i) => i === 1 ? v - 1 : v)
            ));
            // データ日付をそのまま使用
            const dataJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            
            // 表示用フォーマット
            const pubJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            
            
            const enEl = document.getElementById('sst-latest-en');
            const jaEl = document.getElementById('sst-latest-ja');
            
            // 7地点のSST値を表示
            const sstValues = ALL_SITES.map(s => latest[s]?.toFixed(1) || '--').join(' / ');
            
            if (enEl) {
                enEl.innerHTML = `${sstValues}°C<br><small style="opacity:0.7">Data: ${dataJa}</small>`;
            }
            if (jaEl) {
                jaEl.innerHTML = `${sstValues}°C<br><small style="opacity:0.7">データ: ${dataJa}</small>`;
            }
            
            // バッジと説明文を動的更新
            updateSSTStatus(latest, pubDateObj.getUTCMonth() + 1);
            
            console.log('✅ SST latest loaded from Supabase:', publishedDate);
        } catch (e) {
            console.error('❌ Failed to load SST from Supabase:', e);
        }
    }

    // SSTステータスを動的更新（バッジ・説明文）
    function updateSSTStatus(sstData, currentMonth) {
        const values = ALL_SITES.map(s => sstData[s] || null).filter(v => v !== null);
        const maxSST = Math.max(...values);
        const minSST = Math.min(...values);
        const maxSite = ALL_SITES.find(s => sstData[s] === maxSST);
        const minSite = ALL_SITES.find(s => sstData[s] === minSST);
        
        // 夏季: 6-10月、冬季: 11-5月
        const isSummer = currentMonth >= 6 && currentMonth <= 10;
        
        const cardEl = document.getElementById('sst-card');
        const badgeEl = document.getElementById('sst-badge');
        const badgeEnEl = document.getElementById('sst-badge-en');
        const badgeJaEl = document.getElementById('sst-badge-ja');
        const descEnEl = document.getElementById('sst-desc-en');
        const descJaEl = document.getElementById('sst-desc-ja');
        
        let isWarning = false;
        let descEn = '';
        let descJa = '';
        
        if (isSummer && maxSST >= 29) {
            isWarning = true;
            descEn = `${siteNames.en[maxSite]} at ${maxSST.toFixed(1)}°C—bleaching threshold.`;
            descJa = `${siteNames.ja[maxSite]}が${maxSST.toFixed(1)}°C—白化閾値に接近。`;
        } else if (!isSummer && minSST <= 18) {
            isWarning = true;
            descEn = `${siteNames.en[minSite]} at ${minSST.toFixed(1)}°C—cold stress.`;
            descJa = `${siteNames.ja[minSite]}が${minSST.toFixed(1)}°C—低温ストレス。`;
        } else if (isSummer) {
            descEn = `All sites below 29°C. Normal summer range.`;
            descJa = `全地点29°C未満。夏季の平常水温。`;
        } else {
            descEn = `All sites above 18°C. Normal winter range.`;
            descJa = `全地点18°C超。冬季の平常水温。`;
        }
        
        if (isWarning) {
            if (cardEl) cardEl.className = 'six-card status-warning';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-watch';
            if (badgeEnEl) badgeEnEl.textContent = 'Watch';
            if (badgeJaEl) badgeJaEl.textContent = '注意';
        } else {
            if (cardEl) cardEl.className = 'six-card status-safe';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-safe';
            if (badgeEnEl) badgeEnEl.textContent = 'Safe';
            if (badgeJaEl) badgeJaEl.textContent = '安全';
        }
        
        if (descEnEl) descEnEl.textContent = descEn;
        if (descJaEl) descJaEl.textContent = descJa;
    }

    // 極端日数をSupabaseから取得（7地点）
    async function loadExtremeDaysFromSupabase() {
        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/get_extreme_days`, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Supabase RPC failed');
            const data = await response.json();
            
            // 日付計算
            const pubDateObj = new Date(Date.UTC(
                ...data.latest_date.split('-').map(Number).map((v, i) => i === 1 ? v - 1 : v)
            ));
            // データ日付をそのまま使用
            const dataJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            
            const pubJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            
            
            const hot24 = data.hot_2024 || {};
            const hot25 = data.hot_2025 || {};
            const cold25 = data.cold_winter_2025 || {};
            const cold26 = data.cold_winter_2026 || {};
            
            const enEl = document.getElementById('extreme-latest-en');
            const jaEl = document.getElementById('extreme-latest-ja');
            
            // 7地点の値を表示
            const hot24Vals = ALL_SITES.map(s => hot24[s] || 0).join(' / ');
            const hot25Vals = ALL_SITES.map(s => hot25[s] || 0).join(' / ');
            const cold26Vals = ALL_SITES.map(s => cold26[s] || 0).join(' / ');
            
            if (enEl) {
                enEl.innerHTML = `🔥24: ${hot24Vals}<br>　25: ${hot25Vals}<br>❄️W26: ${cold26Vals}<br><small style="opacity:0.7">Data: ${dataJa}</small>`;
            }
            if (jaEl) {
                jaEl.innerHTML = `🔥24: ${hot24Vals}<br>　25: ${hot25Vals}<br>❄️26冬: ${cold26Vals}<br><small style="opacity:0.7">データ: ${dataJa}</small>`;
            }
            
            updateExtremeStatus(hot25, cold26);
            
            console.log('✅ Extreme days loaded from Supabase RPC');
        } catch (e) {
            console.error('❌ Failed to load extreme days from Supabase:', e);
        }
    }

    // 極端日数ステータスを動的更新
    function updateExtremeStatus(hot2025, cold2026) {
        const hotValues = ALL_SITES.map(s => hot2025[s] || 0);
        const coldValues = ALL_SITES.map(s => cold2026[s] || 0);
        const maxHotDays = Math.max(...hotValues);
        const maxColdDays = Math.max(...coldValues);
        const maxHotSite = ALL_SITES[hotValues.indexOf(maxHotDays)];
        const maxColdSite = ALL_SITES[coldValues.indexOf(maxColdDays)];
        
        const cardEl = document.getElementById('extreme-card');
        const badgeEl = document.getElementById('extreme-badge');
        const badgeEnEl = document.getElementById('extreme-badge-en');
        const badgeJaEl = document.getElementById('extreme-badge-ja');
        const descEnEl = document.getElementById('extreme-desc-en');
        const descJaEl = document.getElementById('extreme-desc-ja');
        
        const isWarning = maxHotDays >= 20 || maxColdDays >= 30;
        
        if (isWarning) {
            if (cardEl) cardEl.className = 'six-card status-warning';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-watch';
            if (badgeEnEl) badgeEnEl.textContent = 'Watch';
            if (badgeJaEl) badgeJaEl.textContent = '注意';
            
            if (maxHotDays >= maxColdDays && maxHotDays >= 20) {
                if (descEnEl) descEnEl.textContent = `2025: ${siteNames.en[maxHotSite]} ${maxHotDays} hot days.`;
                if (descJaEl) descJaEl.textContent = `2025年: ${siteNames.ja[maxHotSite]}で${maxHotDays}日の高温。`;
            } else {
                if (descEnEl) descEnEl.textContent = `W26: ${siteNames.en[maxColdSite]} ${maxColdDays} cold days.`;
                if (descJaEl) descJaEl.textContent = `26冬: ${siteNames.ja[maxColdSite]}で${maxColdDays}日の低温。`;
            }
        } else {
            if (cardEl) cardEl.className = 'six-card status-safe';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-safe';
            if (badgeEnEl) badgeEnEl.textContent = 'Safe';
            if (badgeJaEl) badgeJaEl.textContent = '安全';
            
            const totalHot = hotValues.reduce((a, b) => a + b, 0);
            const totalCold = coldValues.reduce((a, b) => a + b, 0);
            if (descEnEl) descEnEl.textContent = `2025 hot: ${totalHot}d. W26 cold: ${totalCold}d. Normal.`;
            if (descJaEl) descJaEl.textContent = `2025高温${totalHot}日・26冬低温${totalCold}日。正常範囲。`;
        }
    }

    // DHWピークをSupabaseから取得（7地点）
    async function loadDHWFromSupabase() {
        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/get_dhw_all_years`, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Supabase RPC failed');
            const data = await response.json();
            
            const get2024 = (site) => data[site]?.find(d => d.year === 2024)?.peak_dhw || 0;
            const get2025 = (site) => data[site]?.find(d => d.year === 2025)?.peak_dhw || 0;
            
            const peak2024 = {};
            const peak2025 = {};
            ALL_SITES.forEach(s => {
                peak2024[s] = get2024(s);
                peak2025[s] = get2025(s);
            });
            
            const pubDateObj = new Date(Date.UTC(
                ...data.latest_date.split('-').map(Number).map((v, i) => i === 1 ? v - 1 : v)
            ));
            // データ日付をそのまま使用
            const dataJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            
            const pubJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            
            
            const enEl = document.getElementById('dhw-latest-en');
            const jaEl = document.getElementById('dhw-latest-ja');
            
            const dhw24Vals = ALL_SITES.map(s => Math.round(peak2024[s])).join(' / ');
            const dhw25Vals = ALL_SITES.map(s => Math.round(peak2025[s])).join(' / ');
            
            if (enEl) {
                enEl.innerHTML = `'24: ${dhw24Vals}<br>'25: ${dhw25Vals}<br><small style="opacity:0.7">Data: ${dataJa}</small>`;
            }
            if (jaEl) {
                jaEl.innerHTML = `'24: ${dhw24Vals}<br>'25: ${dhw25Vals}<br><small style="opacity:0.7">データ: ${dataJa}</small>`;
            }
            
            window.dhwAllYearsData = data;
            updateDHWStatus(peak2025);
            
            console.log('✅ DHW peaks loaded from Supabase RPC');
            return data;
        } catch (e) {
            console.error('❌ Failed to load DHW from Supabase:', e);
            return null;
        }
    }

    // DHWステータスを動的更新
    function updateDHWStatus(peak2025) {
        const values = ALL_SITES.map(s => peak2025[s]);
        const maxDHW = Math.max(...values);
        const maxSite = ALL_SITES[values.indexOf(maxDHW)];
        
        const cardEl = document.getElementById('dhw-card');
        const badgeEl = document.getElementById('dhw-badge');
        const badgeEnEl = document.getElementById('dhw-badge-en');
        const badgeJaEl = document.getElementById('dhw-badge-ja');
        const descEnEl = document.getElementById('dhw-desc-en');
        const descJaEl = document.getElementById('dhw-desc-ja');
        
        if (maxDHW >= 8) {
            if (cardEl) cardEl.className = 'six-card status-alert';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-alert';
            if (badgeEnEl) badgeEnEl.textContent = 'Alert';
            if (badgeJaEl) badgeJaEl.textContent = '警報';
            if (descEnEl) descEnEl.textContent = `2025: ${siteNames.en[maxSite]} DHW ${maxDHW.toFixed(1)}. Severe risk.`;
            if (descJaEl) descJaEl.textContent = `2025: ${siteNames.ja[maxSite]}がDHW ${maxDHW.toFixed(1)}。深刻なリスク。`;
        } else if (maxDHW >= 4) {
            if (cardEl) cardEl.className = 'six-card status-alert';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-alert';
            if (badgeEnEl) badgeEnEl.textContent = 'Alert';
            if (badgeJaEl) badgeJaEl.textContent = '警報';
            if (descEnEl) descEnEl.textContent = `2025: ${siteNames.en[maxSite]} DHW ${maxDHW.toFixed(1)}. Bleaching possible.`;
            if (descJaEl) descJaEl.textContent = `2025: ${siteNames.ja[maxSite]}がDHW ${maxDHW.toFixed(1)}。白化の可能性。`;
        } else {
            if (cardEl) cardEl.className = 'six-card status-safe';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-safe';
            if (badgeEnEl) badgeEnEl.textContent = 'Safe';
            if (badgeJaEl) badgeJaEl.textContent = '安全';
            if (descEnEl) descEnEl.textContent = `2025: All sites below DHW 4. Low stress year.`;
            if (descJaEl) descJaEl.textContent = `2025: 全地点DHW 4未満。低ストレス年。`;
        }
    }

    async function initAllCharts() {
        try {
            const [sstData, extremeData, dhwCardData, dhwPeakData] = await Promise.all([
                fetch('data/sst_card.json').then(r => r.json()).catch(() => null),
                fetch('data/extreme_days.json').then(r => r.json()).catch(() => null),
                fetch('data/dhw_card.json').then(r => r.json()).catch(() => null),
                fetch('data/dhw_annual_peak.json').then(r => r.json()).catch(() => null)
            ]);

            // ========================================
            // SST カード（月別比較チャート）- 串本を表示
            // ========================================
            const sstCtx = document.getElementById('chart-sst-compare');
            if (sstCtx && sstData) {
                const sst = sstData.chart.kushimoto || sstData.chart.manza;
                new Chart(sstCtx, {
                    type: 'line',
                    data: {
                        labels: sstData.chart.labels,
                        datasets: [
                            {
                                label: '2025',
                                data: sst['2025'],
                                borderColor: '#a65d5d',
                                backgroundColor: 'rgba(231,76,60,0.1)',
                                fill: true,
                                tension: 0.4,
                                pointRadius: 0,
                                borderWidth: 2
                            },
                            {
                                label: '2024',
                                data: sst['2024'],
                                borderColor: '#3498db',
                                borderDash: [5, 5],
                                fill: false,
                                tension: 0.4,
                                pointRadius: 0,
                                borderWidth: 2
                            },
                            {
                                label: 'MMM',
                                data: Array(12).fill(sst.mmm),
                                borderColor: '#3d7a73',
                                borderDash: [2, 2],
                                fill: false,
                                pointRadius: 0,
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'bottom',
                                labels: { boxWidth: 10, font: { size: 9 }, padding: 8 }
                            }
                        },
                        scales: {
                            y: {
                                min: 14,
                                max: 32,
                                grid: { color: 'rgba(0,122,108,0.08)' },
                                ticks: { font: { size: 9 }, color: '#666' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 9 }, color: '#666', maxRotation: 0 }
                            }
                        }
                    }
                });
                console.log('✅ SST card chart initialized');
            }

            await loadSSTLatestFromSupabase();
            await loadExtremeDaysFromSupabase();
            await loadDHWFromSupabase();

            // ========================================
            // 極端日数 カード（ミニチャート）- 7地点
            // ========================================
            const extremeMiniCtx = document.getElementById('extremeChartMini');
            if (extremeMiniCtx && extremeData) {
                const years = extremeData.hot_days.manza.map(d => d.year).slice(-5);
                
                const datasets = ALL_SITES.map(site => ({
                    data: extremeData.hot_days[site]?.slice(-5).map(d => d.days) || [],
                    backgroundColor: chartColors[site] + '99',
                    borderColor: chartColors[site],
                    borderWidth: 0.5
                }));
                
                new Chart(extremeMiniCtx, {
                    type: 'bar',
                    data: { labels: years, datasets },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { display: true, grid: { display: false }, ticks: { font: { size: 9 } } },
                            y: { display: false, min: 0 }
                        }
                    }
                });
                console.log('✅ Extreme days mini chart initialized (7 sites)');
            }

            // ========================================
            // DHW カード（直近5年・7地点チャート）
            // ========================================
            const dhwTrendCtx = document.getElementById('chart-dhw-trend');
            if (dhwTrendCtx && window.dhwAllYearsData) {
                const dhwData = window.dhwAllYearsData;
                const recentYears = [2021, 2022, 2023, 2024, 2025];
                
                const datasets = ALL_SITES.map(site => ({
                    label: siteNames.en[site],
                    data: recentYears.map(y => dhwData[site]?.find(d => d.year === y)?.peak_dhw || 0),
                    backgroundColor: chartColors[site] + '99',
                    borderColor: chartColors[site],
                    borderWidth: 0.5
                }));
                
                new Chart(dhwTrendCtx, {
                    type: 'bar',
                    data: { labels: recentYears, datasets },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 16,
                                grid: { color: 'rgba(0,122,108,0.08)' },
                                ticks: { font: { size: 9 }, color: '#666' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 9 }, color: '#666' }
                            }
                        }
                    }
                });
                console.log('✅ DHW card chart initialized (7 sites)');
            }

            // ========================================
            // 光補正DHW カード（DHW vs 光補正DHW 比較）
            // ========================================
            const ladhwCtx = document.getElementById('chart-ladhw');
            if (ladhwCtx) {
                const ladhwData = {
                    labels: ['串', '小', '奄', '瀬', '万', '慶', '石'],
                    dhw: [7.2, 8.3, 9.1, 10.8, 12.6, 11.2, 10.5],
                    ladhw: [6.1, 7.8, 7.5, 9.2, 10.8, 9.5, 8.9]
                };
                new Chart(ladhwCtx, {
                    type: 'bar',
                    data: {
                        labels: ladhwData.labels,
                        datasets: [
                            { label: 'DHW', data: ladhwData.dhw, backgroundColor: 'rgba(239, 68, 68, 0.7)', borderWidth: 0 },
                            { label: '光補正', data: ladhwData.ladhw, backgroundColor: 'rgba(59, 130, 246, 0.7)', borderWidth: 0 }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: true, position: 'bottom', labels: { boxWidth: 10, font: { size: 9 }, padding: 6 } } },
                        scales: {
                            y: { beginAtZero: true, max: 16, grid: { color: 'rgba(0,122,108,0.08)' }, ticks: { font: { size: 9 }, color: '#666' } },
                            x: { grid: { display: false }, ticks: { font: { size: 9 }, color: '#666' } }
                        }
                    }
                });
                console.log('✅ Light-adjusted DHW card chart initialized');
            }

            // ========================================
            // DHW 詳細ページ用チャート
            // ========================================
            const dhwDetailCtx = document.getElementById('dhwChart');
            if (dhwDetailCtx && dhwPeakData) {
                const years = dhwPeakData.manza?.map(d => d.year) || [];
                
                const datasets = ALL_SITES.filter(s => dhwPeakData[s]).map(site => ({
                    label: siteNames.ja[site],
                    data: dhwPeakData[site]?.map(d => d.peak_dhw) || [],
                    backgroundColor: chartColors[site] + '99',
                    borderColor: chartColors[site],
                    borderWidth: 1
                }));
                
                new Chart(dhwDetailCtx, {
                    type: 'bar',
                    data: { labels: years, datasets },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(2)} °C-weeks`
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: { 
                                    maxRotation: 0,
                                    callback: function(val, idx) {
                                        const year = this.getLabelForValue(val);
                                        return (year % 5 === 0) ? year : '';
                                    }
                                }
                            },
                            y: {
                                beginAtZero: true,
                                max: 16,
                                grid: { color: '#e2e8f0' },
                                ticks: { stepSize: 2 }
                            }
                        }
                    }
                });
                console.log('✅ DHW detail chart initialized');
            }

            // ========================================
            // 極端日数 詳細ページ用チャート
            // ========================================
            const extremeDetailCtx = document.getElementById('extremeChart');
            if (extremeDetailCtx && extremeData) {
                const years = extremeData.hot_days.manza.map(d => d.year);
                
                const datasets = ALL_SITES.filter(s => extremeData.hot_days[s]).map(site => ({
                    label: siteNames.ja[site],
                    data: extremeData.hot_days[site].map(d => d.days),
                    backgroundColor: chartColors[site] + '99',
                    borderColor: chartColors[site],
                    borderWidth: 1
                }));
                
                new Chart(extremeDetailCtx, {
                    type: 'bar',
                    data: { labels: years, datasets },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}日`
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: {
                                    callback: function(val, idx) {
                                        const year = years[idx];
                                        return year % 5 === 0 ? year : '';
                                    }
                                }
                            },
                            y: {
                                min: 0,
                                grid: { color: '#e2e8f0' },
                                ticks: {
                                    callback: (val) => val + '日'
                                }
                            }
                        }
                    }
                });
                console.log('✅ Extreme detail chart initialized');
            }

            console.log('✅ All charts initialized successfully');

        } catch (error) {
            console.error('❌ Chart initialization error:', error);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllCharts);
    } else {
        initAllCharts();
    }
})();
