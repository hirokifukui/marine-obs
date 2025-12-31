const CHART_DATA = {
  dhw_trend: {
    labels: ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024'],
    datasets: {
      sesoko: [0.3, 8.3, 9.7, 0.3, 0.6, 3.1, 0.8, 5.0, 2.1, 9.8],
      manza: [0.8, 8.6, 9.7, 1.2, 1.7, 3.3, 1.0, 5.1, 2.4, 10.9],
      ogasawara: [0.3, 0.3, 2.9, 2.3, 1.1, 9.6, 3.4, 4.5, 1.4, 4.1]
    }
  },
  sst_monthly: {
    labels: ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
    sesoko: {
      '2024': [23.1, 22.7, 22.1, 23.2, 24.7, 26.5, 29.8, 29.9, 29.5, 28.1, 26.9, 24.7],
      '2023': [22.1, 21.7, 22.4, 23.0, 24.7, 26.6, 28.9, 28.2, 29.1, 27.5, 25.8, 24.1],
      mmm: 29.0
    },
    manza: {
      '2024': [22.5, 22.1, 21.6, 23.0, 24.7, 26.0, 29.7, 30.2, 29.4, 28.3, 26.5, 24.1],
      '2023': [21.9, 21.3, 21.9, 22.8, 24.2, 26.5, 29.0, 28.1, 29.2, 27.6, 25.5, 23.7],
      mmm: 29.0
    }
  },
  site_compare: {
    labels: ['Jun', 'Jul', 'Aug', 'Sep'],
    sesoko: [26.5, 29.8, 29.9, 29.5],
    manza: [26.0, 29.7, 30.2, 29.4],
    ogasawara: [26.3, 29.0, 28.4, 28.0]
  }
};

// DHW色分け（閾値: 4未満=緑, 4-8=黄, 8以上=赤）
function getDHWColors(values) {
  return values.map(v => v >= 8 ? '#a65d5d' : v >= 4 ? '#c4a35a' : '#5b9a94');
}

document.addEventListener('DOMContentLoaded', function() {
  // DHW年別推移（万座）
  const ctxDHW = document.getElementById('chart-dhw-trend');
  if (ctxDHW) {
    const dhwData = CHART_DATA.dhw_trend.datasets.manza;
    new Chart(ctxDHW, {
      type: 'bar',
      data: {
        labels: CHART_DATA.dhw_trend.labels,
        datasets: [{
          data: dhwData,
          backgroundColor: getDHWColors(dhwData),
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 12, grid: { color: 'rgba(0,122,108,0.08)' }, ticks: { font: { size: 10 }, color: '#666' } },
          x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#666' } }
        }
      }
    });
  }

  // SST月別比較（万座 2024 vs 2023）
  const ctxSST = document.getElementById('chart-sst-compare');
  if (ctxSST) {
    const sst = CHART_DATA.sst_monthly.manza;
    new Chart(ctxSST, {
      type: 'line',
      data: {
        labels: CHART_DATA.sst_monthly.labels,
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
        plugins: { legend: { display: true, position: 'bottom', labels: { boxWidth: 10, font: { size: 9 }, padding: 8 } } },
        scales: {
          y: { min: 20, max: 32, grid: { color: 'rgba(0,122,108,0.08)' }, ticks: { font: { size: 9 }, color: '#666' } },
          x: { grid: { display: false }, ticks: { font: { size: 9 }, color: '#666', maxRotation: 0 } }
        }
      }
    });
  }

  // 地点間比較（2024年夏季、3地点）
  const ctxSite = document.getElementById('chart-site-compare');
  if (ctxSite) {
    const sc = CHART_DATA.site_compare;
    new Chart(ctxSite, {
      type: 'bar',
      data: {
        labels: sc.labels,
        datasets: [
          { label: 'Sesoko', data: sc.sesoko, backgroundColor: '#5b9a94', borderRadius: 4 },
          { label: 'Manza', data: sc.manza, backgroundColor: '#3498db', borderRadius: 4 },
          { label: 'Ogasawara', data: sc.ogasawara, backgroundColor: '#9b59b6', borderRadius: 4 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true, position: 'bottom', labels: { boxWidth: 10, font: { size: 9 }, padding: 8 } } },
        scales: {
          y: { min: 24, max: 32, grid: { color: 'rgba(0,122,108,0.08)' }, ticks: { font: { size: 9 }, color: '#666' } },
          x: { grid: { display: false }, ticks: { font: { size: 9 }, color: '#666' } }
        }
      }
    });
  }
});
