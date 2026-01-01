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
            
            // 衛星観測日は公開日の約3日前と推定（タイムゾーン非依存で計算）
            const [year, month, day] = publishedDate.split('-').map(Number);
            const obsDay = day - 3;
            const obsDateStr = `${year}-${String(month).padStart(2,'0')}-${String(obsDay).padStart(2,'0')}`;
            
            // 表示用フォーマット
            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            const pubEn = months[month - 1] + ' ' + day;
            const obsEn = months[month - 1] + ' ' + obsDay;
            const pubJa = `${month}/${day}`;
            const obsJa = `${month}/${obsDay}`;
            
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
            // DHW カード（年別推移チャート）
            // ========================================
            const dhwTrendCtx = document.getElementById('chart-dhw-trend');
            if (dhwTrendCtx && dhwCardData) {
                const dhwValues = dhwCardData.chart.manza;
                new Chart(dhwTrendCtx, {
                    type: 'bar',
                    data: {
                        labels: dhwCardData.chart.labels,
                        datasets: [{
                            data: dhwValues,
                            backgroundColor: getDHWColors(dhwValues),
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 12,
                                grid: { color: 'rgba(0,122,108,0.08)' },
                                ticks: { font: { size: 10 }, color: '#666' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 10 }, color: '#666' }
                            }
                        }
                    }
                });
                console.log('✅ DHW card chart initialized');
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
