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
    // extremeChart loaded via fetch
    
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
                            },
                            {
                                label: '小笠原',
                                data: dhwData.ogasawara.map(d => d.peak_dhw),
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
                                ticks: {
                                    stepSize: 2
                                }
                            }
                        }
                    }
                });
            }
            
            // Extreme Days Chart (Hot Days ≥30°C)
            const extremeCtx = document.getElementById('extremeChart');
            if (extremeCtx) {
                // Load extreme days data
                fetch('data/extreme_days.json')
                    .then(res => res.json())
                    .then(extremeData => {
                        const years = extremeData.hot_days.sesoko.map(d => d.year);
                        new Chart(extremeCtx, {
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
                    })
                    .catch(err => console.error('Error loading extreme days data:', err));
            }
            
            
            // Mini extreme chart for six-card
            const extremeMiniCtx = document.getElementById('extremeChartMini');
            if (extremeMiniCtx) {
                fetch('data/extreme_days.json')
                    .then(res => res.json())
                    .then(extremeData => {
                        const years = extremeData.hot_days.sesoko.map(d => d.year).slice(-5);
                        const sesokoData = extremeData.hot_days.sesoko.slice(-5).map(d => d.days);
                        const manzaData = extremeData.hot_days.manza.slice(-5).map(d => d.days);
                        const ogasawaraData = extremeData.hot_days.ogasawara.slice(-5).map(d => d.days);
                        
                        new Chart(extremeMiniCtx, {
                            type: 'bar',
                            data: {
                                labels: years,
                                datasets: [
                                    { data: sesokoData, backgroundColor: '#5b9a94' },
                                    { data: manzaData, backgroundColor: '#c4a35a' },
                                    { data: ogasawaraData, backgroundColor: '#7a8a9a' }
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
