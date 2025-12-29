#!/usr/bin/env python3
"""Chart.js初期化スクリプトを追加"""

input_file = '/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html'

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Chart.js初期化スクリプト
chart_init_script = '''
<!-- Chart.js Data Initialization -->
<script>
(function() {
    // Chart.js default settings
    Chart.defaults.font.family = "'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.font.size = 11;
    
    const chartColors = {
        sesoko: '#2b6cb0',
        manza: '#c05621', 
        ogasawara: '#2f855a'
    };
    
    let dhwChart = null;
    let sstChart = null;
    
    async function initCharts() {
        try {
            // Load JSON data
            const [dhwData, climData] = await Promise.all([
                fetch('data/dhw_annual_peak.json').then(r => r.json()),
                fetch('data/monthly_clim.json').then(r => r.json())
            ]);
            
            // DHW Chart
            const dhwCtx = document.getElementById('dhwChart');
            if (dhwCtx) {
                const years = dhwData.sesoko.map(d => d.year);
                
                dhwChart = new Chart(dhwCtx, {
                    type: 'bar',
                    data: {
                        labels: years,
                        datasets: [
                            {
                                label: '瀬底',
                                data: dhwData.sesoko.map(d => d.peak_dhw),
                                backgroundColor: chartColors.sesoko + '99',
                                borderColor: chartColors.sesoko,
                                borderWidth: 1
                            },
                            {
                                label: '万座',
                                data: dhwData.manza.map(d => d.peak_dhw),
                                backgroundColor: chartColors.manza + '99',
                                borderColor: chartColors.manza,
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
                                ticks: {
                                    stepSize: 2
                                }
                            }
                        }
                    }
                });
            }
            
            // SST Monthly Climatology Chart
            const sstCtx = document.getElementById('sstChart');
            if (sstCtx) {
                const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
                
                sstChart = new Chart(sstCtx, {
                    type: 'line',
                    data: {
                        labels: months,
                        datasets: [
                            {
                                label: '瀬底',
                                data: climData.sesoko.map(d => d.avg_sst),
                                borderColor: chartColors.sesoko,
                                backgroundColor: 'transparent',
                                borderWidth: 2,
                                tension: 0.3,
                                pointRadius: 2
                            },
                            {
                                label: '万座',
                                data: climData.manza.map(d => d.avg_sst),
                                borderColor: chartColors.manza,
                                backgroundColor: 'transparent',
                                borderWidth: 2,
                                tension: 0.3,
                                pointRadius: 2
                            },
                            {
                                label: '小笠原',
                                data: climData.ogasawara.map(d => d.avg_sst),
                                borderColor: chartColors.ogasawara,
                                backgroundColor: 'transparent',
                                borderWidth: 2,
                                tension: 0.3,
                                pointRadius: 2
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
                                    label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}°C`
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: {
                                    callback: function(val, idx) {
                                        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                                        return monthNames[idx];
                                    }
                                }
                            },
                            y: {
                                min: 20,
                                max: 30,
                                grid: { color: '#e2e8f0' },
                                ticks: {
                                    stepSize: 2,
                                    callback: (val) => val + '°C'
                                }
                            }
                        }
                    }
                });
            }
            
            console.log('✅ Charts initialized');
        } catch (error) {
            console.error('Chart initialization error:', error);
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCharts);
    } else {
        initCharts();
    }
})();
</script>
'''

# </body>の直前に挿入
if '</body>' in content:
    content = content.replace('</body>', chart_init_script + '</body>')
    print("✅ Chart.js初期化スクリプトを追加しました")
else:
    print("❌ </body>が見つかりません")
    exit(1)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 保存完了")
