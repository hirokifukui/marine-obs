/**
 * charts.js - 全カードのチャート初期化（JSON統一版）
 * 
 * データソース:
 * - data/sst_card.json       → SSTカード
 * - data/extreme_days.json   → 極端日数カード  
 * - data/dhw_card.json       → DHWカード
 * - data/dhw_annual_peak.json → DHW詳細チャート
 * - data/spawning_card.json  → 産卵予測カード（将来）
 */

(function() {
    // Chart.js default settings
    Chart.defaults.font.family = "'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.font.size = 11;
    
    const chartColors = {
        sesoko: '#2b6cb0',
        manza: '#c05621', 
        ogasawara: '#2f855a'
    };

    // Supabase設定
    const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlZ2l1aWJscGxpYWlucGRnZ2ZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQyMDkzNzQsImV4cCI6MjA3OTc4NTM3NH0.r9dBAsMLoXbgZL93lvA756r74U6YfCCfftHHlxYqZIw';

    // SST最新値をSupabaseから取得
    async function loadSSTLatestFromSupabase() {
        try {
            const response = await fetch(
                `${SUPABASE_URL}/rest/v1/sst_daily?select=date,site_code,sst&order=date.desc&limit=3`,
                { headers: { 'apikey': SUPABASE_ANON_KEY } }
            );
            if (!response.ok) throw new Error('Supabase fetch failed');
            const data = await response.json();
            
            // 最新日付のデータを整形
            const latest = {};
            data.forEach(row => { latest[row.site_code] = row.sst; });
            const publishedDate = data[0]?.date;
            
            // 衛星観測日は公開日の約3日前と推定（月またぎ対応）
            const pubDateObj = new Date(Date.UTC(
                ...publishedDate.split('-').map(Number).map((v, i) => i === 1 ? v - 1 : v)
            ));
            const obsDateObj = new Date(pubDateObj);
            obsDateObj.setUTCDate(obsDateObj.getUTCDate() - 3);
            
            // 表示用フォーマット
            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            const pubEn = months[pubDateObj.getUTCMonth()] + ' ' + pubDateObj.getUTCDate();
            const obsEn = months[obsDateObj.getUTCMonth()] + ' ' + obsDateObj.getUTCDate();
            const pubJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            const obsJa = `${obsDateObj.getUTCMonth() + 1}/${obsDateObj.getUTCDate()}`;
            
            const enEl = document.getElementById('sst-latest-en');
            const jaEl = document.getElementById('sst-latest-ja');
            
            if (enEl) {
                enEl.innerHTML = `SST: ${latest.manza?.toFixed(1) || '--'} / ${latest.sesoko?.toFixed(1) || '--'} / ${latest.ogasawara?.toFixed(1) || '--'}°C<br><small style="opacity:0.8">Observed: ${obsEn} | Published: ${pubEn}</small>`;
            }
            if (jaEl) {
                jaEl.innerHTML = `SST: ${latest.manza?.toFixed(1) || '--'} / ${latest.sesoko?.toFixed(1) || '--'} / ${latest.ogasawara?.toFixed(1) || '--'}°C<br><small style="opacity:0.8">観測: ${obsJa} | 公開: ${pubJa}</small>`;
            }
            console.log('✅ SST latest loaded from Supabase:', publishedDate);
        } catch (e) {
            console.error('❌ Failed to load SST from Supabase:', e);
        }
    }
    // 極端日数をSupabaseから取得
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
            const obsDateObj = new Date(pubDateObj);
            obsDateObj.setUTCDate(obsDateObj.getUTCDate() - 3);
            
            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            const pubEn = months[pubDateObj.getUTCMonth()] + ' ' + pubDateObj.getUTCDate();
            const obsEn = months[obsDateObj.getUTCMonth()] + ' ' + obsDateObj.getUTCDate();
            const pubJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            const obsJa = `${obsDateObj.getUTCMonth() + 1}/${obsDateObj.getUTCDate()}`;
            
            // 値取得（nullの場合は0）
            const hot24 = data.hot_2024 || {};
            const hot25 = data.hot_2025 || {};
            const cold25 = data.cold_winter_2025 || {};
            const cold26 = data.cold_winter_2026 || {};
            
            const enEl = document.getElementById('extreme-latest-en');
            const jaEl = document.getElementById('extreme-latest-ja');
            
            if (enEl) {
                enEl.innerHTML = `🔥 2024: ${hot24.manza||0}/${hot24.sesoko||0}/${hot24.ogasawara||0} | 2025: ${hot25.manza||0}/${hot25.sesoko||0}/${hot25.ogasawara||0}<br>❄️ W25: ${cold25.manza||0}/${cold25.sesoko||0}/${cold25.ogasawara||0} | W26: ${cold26.manza||0}/${cold26.sesoko||0}/${cold26.ogasawara||0}<br><small style="opacity:0.8">Obs: ${obsEn} | Pub: ${pubEn}</small>`;
            }
            if (jaEl) {
                jaEl.innerHTML = `🔥 2024: ${hot24.manza||0}/${hot24.sesoko||0}/${hot24.ogasawara||0} | 2025: ${hot25.manza||0}/${hot25.sesoko||0}/${hot25.ogasawara||0}<br>❄️ 25冬: ${cold25.manza||0}/${cold25.sesoko||0}/${cold25.ogasawara||0} | 26冬: ${cold26.manza||0}/${cold26.sesoko||0}/${cold26.ogasawara||0}<br><small style="opacity:0.8">観測: ${obsJa} | 公開: ${pubJa}</small>`;
            }
            
            // バッジと説明文を動的更新（2025年夏 + 2025-26年冬基準）
            updateExtremeStatus(hot25, cold26);
            
            console.log('✅ Extreme days loaded from Supabase RPC');
        } catch (e) {
            console.error('❌ Failed to load extreme days from Supabase:', e);
        }
    }

    // 極端日数ステータスを動的更新（バッジ・説明文）
    function updateExtremeStatus(hot2025, cold2026) {
        const siteNamesEn = { manza: 'Manza', sesoko: 'Sesoko', ogasawara: 'Ogasawara' };
        const siteNamesJa = { manza: '万座', sesoko: '瀬底', ogasawara: '小笠原' };
        const sites = ['manza', 'sesoko', 'ogasawara'];
        
        // 2025年夏の高温日合計
        const totalHot = (hot2025.manza||0) + (hot2025.sesoko||0) + (hot2025.ogasawara||0);
        const maxHotSite = sites.reduce((a, b) => (hot2025[a]||0) > (hot2025[b]||0) ? a : b);
        const maxHotDays = hot2025[maxHotSite] || 0;
        
        // 2025-26年冬の低温日合計
        const totalCold = (cold2026.manza||0) + (cold2026.sesoko||0) + (cold2026.ogasawara||0);
        const maxColdSite = sites.reduce((a, b) => (cold2026[a]||0) > (cold2026[b]||0) ? a : b);
        const maxColdDays = cold2026[maxColdSite] || 0;
        
        const cardEl = document.getElementById('extreme-card');
        const badgeEl = document.getElementById('extreme-badge');
        const badgeEnEl = document.getElementById('extreme-badge-en');
        const badgeJaEl = document.getElementById('extreme-badge-ja');
        const descEnEl = document.getElementById('extreme-desc-en');
        const descJaEl = document.getElementById('extreme-desc-ja');
        
        // 判定: 高温20日以上 or 低温30日以上 → 注意
        const isWarning = maxHotDays >= 20 || maxColdDays >= 30;
        
        if (isWarning) {
            if (cardEl) cardEl.className = 'six-card status-warning';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-watch';
            if (badgeEnEl) badgeEnEl.textContent = 'Watch';
            if (badgeJaEl) badgeJaEl.textContent = '注意';
            
            // どちらが多いかで説明文を変える
            if (maxHotDays >= maxColdDays && maxHotDays >= 20) {
                if (descEnEl) descEnEl.textContent = `2025 summer: ${siteNamesEn[maxHotSite]} had ${maxHotDays} hot days (≥30°C). Heat stress risk.`;
                if (descJaEl) descJaEl.textContent = `2025年夏: ${siteNamesJa[maxHotSite]}で${maxHotDays}日の高温（30°C以上）。熱ストレスリスクあり。`;
            } else {
                if (descEnEl) descEnEl.textContent = `2025-26 winter: ${siteNamesEn[maxColdSite]} had ${maxColdDays} cold days (≤20°C). Cold stress risk.`;
                if (descJaEl) descJaEl.textContent = `2025-26年冬: ${siteNamesJa[maxColdSite]}で${maxColdDays}日の低温（20°C以下）。低温ストレスリスクあり。`;
            }
        } else {
            if (cardEl) cardEl.className = 'six-card status-safe';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-safe';
            if (badgeEnEl) badgeEnEl.textContent = 'Safe';
            if (badgeJaEl) badgeJaEl.textContent = '安全';
            
            if (totalHot === 0 && totalCold === 0) {
                if (descEnEl) descEnEl.textContent = '2025-26 winter: No extreme days recorded. Monitoring continues.';
                if (descJaEl) descJaEl.textContent = '2025-26年冬: 極端水温日なし。観測継続中。';
            } else {
                if (descEnEl) descEnEl.textContent = `2025 summer: ${totalHot} hot days total. 2025-26 winter: ${totalCold} cold days. Within normal range.`;
                if (descJaEl) descJaEl.textContent = `2025年夏: 高温${totalHot}日。2025-26年冬: 低温${totalCold}日。正常範囲内。`;
            }
        }
    }

    // DHWピークをSupabaseから取得
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
            
            // 2024年と2025年のピーク値を取得
            const get2024 = (site) => data[site]?.find(d => d.year === 2024)?.peak_dhw || 0;
            const get2025 = (site) => data[site]?.find(d => d.year === 2025)?.peak_dhw || 0;
            
            const peak2024 = { manza: get2024('manza'), sesoko: get2024('sesoko'), ogasawara: get2024('ogasawara') };
            const peak2025 = { manza: get2025('manza'), sesoko: get2025('sesoko'), ogasawara: get2025('ogasawara') };
            
            // 日付計算
            const pubDateObj = new Date(Date.UTC(
                ...data.latest_date.split('-').map(Number).map((v, i) => i === 1 ? v - 1 : v)
            ));
            const obsDateObj = new Date(pubDateObj);
            obsDateObj.setUTCDate(obsDateObj.getUTCDate() - 3);
            
            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            const pubEn = months[pubDateObj.getUTCMonth()] + ' ' + pubDateObj.getUTCDate();
            const obsEn = months[obsDateObj.getUTCMonth()] + ' ' + obsDateObj.getUTCDate();
            const pubJa = `${pubDateObj.getUTCMonth() + 1}/${pubDateObj.getUTCDate()}`;
            const obsJa = `${obsDateObj.getUTCMonth() + 1}/${obsDateObj.getUTCDate()}`;
            
            const enEl = document.getElementById('dhw-latest-en');
            const jaEl = document.getElementById('dhw-latest-ja');
            
            if (enEl) {
                enEl.innerHTML = `2024: ${peak2024.manza.toFixed(1)} / ${peak2024.sesoko.toFixed(1)} / ${peak2024.ogasawara.toFixed(1)}<br>2025: ${peak2025.manza.toFixed(1)} / ${peak2025.sesoko.toFixed(1)} / ${peak2025.ogasawara.toFixed(1)}<br><small style="opacity:0.8">Obs: ${obsEn} | Pub: ${pubEn}</small>`;
            }
            if (jaEl) {
                jaEl.innerHTML = `2024: ${peak2024.manza.toFixed(1)} / ${peak2024.sesoko.toFixed(1)} / ${peak2024.ogasawara.toFixed(1)}<br>2025: ${peak2025.manza.toFixed(1)} / ${peak2025.sesoko.toFixed(1)} / ${peak2025.ogasawara.toFixed(1)}<br><small style="opacity:0.8">観測: ${obsJa} | 公開: ${pubJa}</small>`;
            }
            
            // グローバルに保存（チャート描画用）
            window.dhwAllYearsData = data;
            
            // バッジと説明文を動的更新（2025年基準）
            updateDHWStatus(peak2025);
            
            console.log('✅ DHW peaks loaded from Supabase RPC');
            return data;
        } catch (e) {
            console.error('❌ Failed to load DHW from Supabase:', e);
            return null;
        }
    }

    // DHWステータスを動的更新（バッジ・説明文）
    function updateDHWStatus(peak2025) {
        const maxDHW = Math.max(peak2025.manza, peak2025.sesoko, peak2025.ogasawara);
        const sites = ['manza', 'sesoko', 'ogasawara'];
        const siteNamesEn = { manza: 'Manza', sesoko: 'Sesoko', ogasawara: 'Ogasawara' };
        const siteNamesJa = { manza: '万座', sesoko: '瀬底', ogasawara: '小笠原' };
        
        // 最大値のサイトを特定
        const maxSite = sites.find(s => peak2025[s] === maxDHW);
        
        const cardEl = document.getElementById('dhw-card');
        const badgeEl = document.getElementById('dhw-badge');
        const badgeEnEl = document.getElementById('dhw-badge-en');
        const badgeJaEl = document.getElementById('dhw-badge-ja');
        const descEnEl = document.getElementById('dhw-desc-en');
        const descJaEl = document.getElementById('dhw-desc-ja');
        
        if (maxDHW >= 8) {
            // 危険レベル（DHW >= 8）
            if (cardEl) cardEl.className = 'six-card status-alert';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-alert';
            if (badgeEnEl) badgeEnEl.textContent = 'Alert';
            if (badgeJaEl) badgeJaEl.textContent = '警報';
            if (descEnEl) descEnEl.textContent = `2025: ${siteNamesEn[maxSite]} reached Alert Level 2 (DHW ≥8). Severe bleaching likely.`;
            if (descJaEl) descJaEl.textContent = `2025年: ${siteNamesJa[maxSite]}が警報レベル2（DHW ≥8）に到達。深刻な白化の可能性。`;
        } else if (maxDHW >= 4) {
            // 注意レベル（DHW >= 4）
            if (cardEl) cardEl.className = 'six-card status-alert';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-alert';
            if (badgeEnEl) badgeEnEl.textContent = 'Alert';
            if (badgeJaEl) badgeJaEl.textContent = '警報';
            if (descEnEl) descEnEl.textContent = `2025: ${siteNamesEn[maxSite]} exceeded Watch Level (DHW ≥4). Bleaching possible.`;
            if (descJaEl) descJaEl.textContent = `2025年: ${siteNamesJa[maxSite]}が注意レベル（DHW ≥4）を超過。白化の可能性あり。`;
        } else {
            // 安全（DHW < 4）
            if (cardEl) cardEl.className = 'six-card status-safe';
            if (badgeEl) badgeEl.className = 'six-card-badge badge-safe';
            if (badgeEnEl) badgeEnEl.textContent = 'Safe';
            if (badgeJaEl) badgeJaEl.textContent = '安全';
            if (descEnEl) descEnEl.textContent = `2025: All sites below Watch Level (DHW <4). Low thermal stress year.`;
            if (descJaEl) descJaEl.textContent = `2025年: 全地点で注意レベル（DHW 4）未満。熱ストレスの低い年。`;
        }
    }

    // DHW色分け（閾値: 4未満=緑, 4-8=黄, 8以上=赤）
    function getDHWColors(values) {
        return values.map(v => v >= 8 ? '#a65d5d' : v >= 4 ? '#c4a35a' : '#5b9a94');
    }

    async function initAllCharts() {
        try {
            // 全JSONを並列読み込み
            const [sstData, extremeData, dhwCardData, dhwPeakData] = await Promise.all([
                fetch('data/sst_card.json').then(r => r.json()).catch(() => null),
                fetch('data/extreme_days.json').then(r => r.json()).catch(() => null),
                fetch('data/dhw_card.json').then(r => r.json()).catch(() => null),
                fetch('data/dhw_annual_peak.json').then(r => r.json()).catch(() => null)
            ]);

            // ========================================
            // SST カード（月別比較チャート）
            // ========================================
            const sstCtx = document.getElementById('chart-sst-compare');
            if (sstCtx && sstData) {
                const sst = sstData.chart.manza;
                new Chart(sstCtx, {
                    type: 'line',
                    data: {
                        labels: sstData.chart.labels,
                        datasets: [
                            {
                                label: '2024',
                                data: sst['2024'],
                                borderColor: '#a65d5d',
                                backgroundColor: 'rgba(231,76,60,0.1)',
                                fill: true,
                                tension: 0.4,
                                pointRadius: 0,
                                borderWidth: 2
                            },
                            {
                                label: '2023',
                                data: sst['2023'],
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
                                min: 20,
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

            // ========================================
            // SST カード最新値（Supabaseから動的取得）
            // ========================================
            await loadSSTLatestFromSupabase();

            // ========================================
            // 極端日数 カード最新値（Supabaseから動的取得）
            // ========================================
            await loadExtremeDaysFromSupabase();

            // ========================================
            // DHW カード最新値（Supabaseから動的取得）
            // ========================================
            await loadDHWFromSupabase();

            // ========================================
            // 極端日数 カード（ミニチャート）
            // ========================================
            const extremeMiniCtx = document.getElementById('extremeChartMini');
            if (extremeMiniCtx && extremeData) {
                const years = extremeData.hot_days.sesoko.map(d => d.year).slice(-5);
                const sesokoData = extremeData.hot_days.sesoko.slice(-5).map(d => d.days);
                const manzaData = extremeData.hot_days.manza.slice(-5).map(d => d.days);
                const ogasawaraData = extremeData.hot_days.ogasawara.slice(-5).map(d => d.days);
                
                new Chart(extremeMiniCtx, {
                    type: 'bar',
                    data: {
                        labels: years,
                        datasets: [
                            { data: sesokoData, backgroundColor: chartColors.sesoko + '99' },
                            { data: manzaData, backgroundColor: chartColors.manza + '99' },
                            { data: ogasawaraData, backgroundColor: chartColors.ogasawara + '99' }
                        ]
                    },
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
                console.log('✅ Extreme days mini chart initialized');
            }

            // ========================================
            // DHW カード（直近5年・3地点チャート - Supabaseから）
            // ========================================
            const dhwTrendCtx = document.getElementById('chart-dhw-trend');
            if (dhwTrendCtx && window.dhwAllYearsData) {
                const dhwData = window.dhwAllYearsData;
                const recentYears = [2021, 2022, 2023, 2024, 2025];
                
                const getRecentData = (site) => recentYears.map(y => 
                    dhwData[site]?.find(d => d.year === y)?.peak_dhw || 0
                );
                
                new Chart(dhwTrendCtx, {
                    type: 'bar',
                    data: {
                        labels: recentYears,
                        datasets: [
                            {
                                label: 'Manza',
                                data: getRecentData('manza'),
                                backgroundColor: chartColors.manza + '99',
                                borderColor: chartColors.manza,
                                borderWidth: 1
                            },
                            {
                                label: 'Sesoko',
                                data: getRecentData('sesoko'),
                                backgroundColor: chartColors.sesoko + '99',
                                borderColor: chartColors.sesoko,
                                borderWidth: 1
                            },
                            {
                                label: 'Ogasawara',
                                data: getRecentData('ogasawara'),
                                backgroundColor: chartColors.ogasawara + '99',
                                borderColor: chartColors.ogasawara,
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 10,
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
                console.log('✅ DHW card chart initialized (5 years, 3 sites)');
            }

            // ========================================
            // DHW 詳細ページ用チャート（3地点比較）
            // ========================================
            const dhwDetailCtx = document.getElementById('dhwChart');
            if (dhwDetailCtx && dhwPeakData) {
                const years = dhwPeakData.sesoko.map(d => d.year);
                
                new Chart(dhwDetailCtx, {
                    type: 'bar',
                    data: {
                        labels: years,
                        datasets: [
                            {
                                label: '瀬底',
                                data: dhwPeakData.sesoko.map(d => d.peak_dhw),
                                backgroundColor: chartColors.sesoko + '99',
                                borderColor: chartColors.sesoko,
                                borderWidth: 1
                            },
                            {
                                label: '万座',
                                data: dhwPeakData.manza.map(d => d.peak_dhw),
                                backgroundColor: chartColors.manza + '99',
                                borderColor: chartColors.manza,
                                borderWidth: 1
                            },
                            {
                                label: '小笠原',
                                data: dhwPeakData.ogasawara.map(d => d.peak_dhw),
                                backgroundColor: chartColors.ogasawara + '99',
                                borderColor: chartColors.ogasawara,
                                borderWidth: 1
                            }
                        ]
                    },
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
                                max: 10,
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
                const years = extremeData.hot_days.sesoko.map(d => d.year);
                new Chart(extremeDetailCtx, {
                    type: 'bar',
                    data: {
                        labels: years,
                        datasets: [
                            {
                                label: '瀬底',
                                data: extremeData.hot_days.sesoko.map(d => d.days),
                                backgroundColor: chartColors.sesoko + '99',
                                borderColor: chartColors.sesoko,
                                borderWidth: 1
                            },
                            {
                                label: '万座',
                                data: extremeData.hot_days.manza.map(d => d.days),
                                backgroundColor: chartColors.manza + '99',
                                borderColor: chartColors.manza,
                                borderWidth: 1
                            },
                            {
                                label: '小笠原',
                                data: extremeData.hot_days.ogasawara.map(d => d.days),
                                backgroundColor: chartColors.ogasawara + '99',
                                borderColor: chartColors.ogasawara,
                                borderWidth: 1
                            }
                        ]
                    },
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

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllCharts);
    } else {
        initAllCharts();
    }
})();
