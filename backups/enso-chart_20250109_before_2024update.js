/**
 * enso-chart.js - ONI (Oceanic Niño Index) チャート
 * 
 * データソース: Supabase oni_monthly テーブル
 * 表示範囲: 1980年〜現在
 */

(function() {
    const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlZ2l1aWJscGxpYWlucGRnZ2ZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQyMDkzNzQsImV4cCI6MjA3OTc4NTM3NH0.r9dBAsMLoXbgZL93lvA756r74U6YfCCfftHHlxYqZIw';

    // 白化イベント年（グローバルまたは日本）
    const bleachingYears = [1998, 2007, 2010, 2016, 2017, 2022, 2023, 2024];

    // Season順序（グラフのX軸用）
    const seasonOrder = ['DJF', 'JFM', 'FMA', 'MAM', 'AMJ', 'MJJ', 'JJA', 'JAS', 'ASO', 'SON', 'OND', 'NDJ'];

    let chartInstance = null;

    async function fetchONIData() {
        try {
            const response = await fetch(
                `${SUPABASE_URL}/rest/v1/oni_monthly?year=gte.1980&select=year,season,anomaly&order=year.asc,id.asc`,
                {
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to fetch ONI data:', error);
            return null;
        }
    }

    function getONIColor(value) {
        if (value >= 0.5) return '#ef4444';  // El Niño - red
        if (value <= -0.5) return '#3b82f6'; // La Niña - blue
        return '#9ca3af';                     // Neutral - gray
    }

    function getENSOStatus(value) {
        const isJa = document.body.classList.contains('ja');
        if (value >= 2.0) return { text: isJa ? '非常に強いEl Niño' : 'Very Strong El Niño', class: 'el-nino' };
        if (value >= 1.5) return { text: isJa ? '強いEl Niño' : 'Strong El Niño', class: 'el-nino' };
        if (value >= 1.0) return { text: isJa ? '中程度El Niño' : 'Moderate El Niño', class: 'el-nino' };
        if (value >= 0.5) return { text: isJa ? '弱いEl Niño' : 'Weak El Niño', class: 'el-nino' };
        if (value <= -2.0) return { text: isJa ? '非常に強いLa Niña' : 'Very Strong La Niña', class: 'la-nina' };
        if (value <= -1.5) return { text: isJa ? '強いLa Niña' : 'Strong La Niña', class: 'la-nina' };
        if (value <= -1.0) return { text: isJa ? '中程度La Niña' : 'Moderate La Niña', class: 'la-nina' };
        if (value <= -0.5) return { text: isJa ? '弱いLa Niña' : 'Weak La Niña', class: 'la-nina' };
        return { text: isJa ? '中立' : 'Neutral', class: 'neutral' };
    }

    function updateCurrentStatus(latestData) {
        const statusEl = document.getElementById('oni-current-status');
        if (!statusEl || !latestData) return;

        const status = getENSOStatus(latestData.anomaly);
        statusEl.className = `oni-status ${status.class}`;
        statusEl.innerHTML = `<strong>${latestData.season} ${latestData.year}</strong>: ${latestData.anomaly.toFixed(1)} (${status.text})`;
    }

    function createChart(data) {
        const ctx = document.getElementById('oni-chart');
        if (!ctx) return;

        // 年単位で集約（各年の最大絶対値を採用）
        const yearlyData = {};
        data.forEach(d => {
            if (!yearlyData[d.year] || Math.abs(d.anomaly) > Math.abs(yearlyData[d.year].anomaly)) {
                yearlyData[d.year] = d;
            }
        });

        const years = Object.keys(yearlyData).sort((a, b) => a - b);
        const values = years.map(y => yearlyData[y].anomaly);
        const colors = values.map(v => getONIColor(v));

        // 白化イベント年のアノテーション
        const annotations = {};
        bleachingYears.forEach(year => {
            if (yearlyData[year]) {
                annotations[`bleaching${year}`] = {
                    type: 'point',
                    xValue: year.toString(),
                    yValue: yearlyData[year].anomaly,
                    backgroundColor: 'rgba(220, 38, 38, 0.8)',
                    borderColor: '#fff',
                    borderWidth: 2,
                    radius: 6,
                };
            }
        });

        // El Niño / La Niña 閾値線
        annotations.elNinoLine = {
            type: 'line',
            yMin: 0.5,
            yMax: 0.5,
            borderColor: 'rgba(239, 68, 68, 0.5)',
            borderWidth: 1,
            borderDash: [5, 5],
        };
        annotations.laNinaLine = {
            type: 'line',
            yMin: -0.5,
            yMax: -0.5,
            borderColor: 'rgba(59, 130, 246, 0.5)',
            borderWidth: 1,
            borderDash: [5, 5],
        };

        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: years,
                datasets: [{
                    label: 'ONI',
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 2,
                    barPercentage: 0.9,
                    categoryPercentage: 0.9,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                const year = context[0].label;
                                const isBleaching = bleachingYears.includes(parseInt(year));
                                return isBleaching ? `${year} ⚠️ Bleaching Year` : year;
                            },
                            label: function(context) {
                                const value = context.parsed.y;
                                const status = getENSOStatus(value);
                                return `ONI: ${value.toFixed(1)} (${status.text})`;
                            }
                        }
                    },
                    annotation: {
                        annotations: annotations
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 0,
                            autoSkip: true,
                            maxTicksLimit: 15,
                            font: {
                                size: 10
                            }
                        }
                    },
                    y: {
                        min: -2.5,
                        max: 3,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 0.5,
                            font: {
                                size: 10
                            },
                            callback: function(value) {
                                return value.toFixed(1);
                            }
                        },
                        title: {
                            display: true,
                            text: 'ONI (°C)',
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    }
                }
            }
        });
    }

    async function init() {
        const data = await fetchONIData();
        if (!data || data.length === 0) {
            const wrapper = document.querySelector('.oni-chart-wrapper');
            if (wrapper) {
                wrapper.innerHTML = '<div class="chart-loading">Failed to load ONI data</div>';
            }
            return;
        }

        // 最新データでステータス更新
        const latestData = data[data.length - 1];
        updateCurrentStatus(latestData);

        // チャート作成
        createChart(data);
    }

    // 言語切替時にステータス再描画
    document.addEventListener('langChanged', async function() {
        const data = await fetchONIData();
        if (data && data.length > 0) {
            updateCurrentStatus(data[data.length - 1]);
        }
    });

    // DOM Ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
