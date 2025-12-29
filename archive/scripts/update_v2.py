#!/usr/bin/env python3
import re

file_path = "/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index_v2.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# New CSS
new_css = '''/* Six Card Section - Marine Identity */
.six-card-section {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}
.six-card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.six-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 122, 108, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s;
}
.six-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 122, 108, 0.15);
}
.six-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4ecdc4, #007a6c);
  z-index: 10;
}
.six-card.status-warning::before {
  background: linear-gradient(90deg, #f9a825, #ff8f00);
}
.six-card.status-alert::before {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
  animation: pulse-alert 2s ease-in-out infinite;
}
@keyframes pulse-alert {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
.six-card-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  z-index: 20;
}
.badge-safe {
  background: rgba(78, 205, 196, 0.15);
  color: #007a6c;
}
.badge-watch {
  background: rgba(249, 168, 37, 0.15);
  color: #f57c00;
}
.badge-alert {
  background: rgba(231, 76, 60, 0.15);
  color: #c0392b;
}
.six-card-chart {
  width: 100%;
  height: 180px;
  background: linear-gradient(180deg, rgba(78, 205, 196, 0.05) 0%, rgba(0, 122, 108, 0.1) 100%);
  position: relative;
  padding: 1rem;
  box-sizing: border-box;
}
.six-card-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 20px;
  overflow: hidden;
}
.six-card-wave svg {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 20px;
}
.six-card-chart canvas {
  width: 100% !important;
  height: calc(100% - 10px) !important;
}
.six-card-body {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #fff 0%, rgba(78, 205, 196, 0.02) 100%);
}
.six-card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}
.six-card-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #007a6c;
  margin-bottom: 0.5rem;
}
.six-card-location svg {
  width: 14px;
  height: 14px;
  fill: #007a6c;
}
.six-card-latest {
  font-size: 1.1rem;
  color: #1a1a2e;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
.six-card-latest .trend-up {
  color: #e74c3c;
  font-size: 0.85rem;
}
.six-card-latest .trend-down {
  color: #27ae60;
  font-size: 0.85rem;
}
.six-card-desc {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
  flex: 1;
}
.six-card-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 1.25rem;
  background: linear-gradient(135deg, #007a6c, #005f54);
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
  align-self: flex-start;
}
.six-card-btn:hover {
  background: linear-gradient(135deg, #005f54, #004a42);
  gap: 12px;
}
.six-card-btn svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
  transition: transform 0.2s;
}
.six-card-btn:hover svg {
  transform: translateX(2px);
}
.six-card.coming-soon {
  opacity: 0.6;
}
.six-card.coming-soon::before {
  background: linear-gradient(90deg, #bdc3c7, #95a5a6);
}
.six-card.coming-soon .six-card-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f5f5f5 0%, #e0e0e0 100%);
}
.six-card.coming-soon .coming-soon-label {
  font-size: 0.85rem;
  color: #95a5a6;
  font-weight: 600;
  letter-spacing: 1px;
}
.six-card.coming-soon .six-card-body {
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 60' opacity='0.03'%3E%3Cpath fill='%23007a6c' d='M20 60 Q25 40 20 30 Q15 20 25 10 M30 60 Q35 45 30 35 Q25 25 35 15 M45 60 Q50 50 45 40 Q40 30 50 20 M55 60 Q60 48 55 38 Q50 28 60 18 M70 60 Q75 42 70 32 Q65 22 75 12 M80 60 Q85 52 80 42 Q75 32 85 22'/%3E%3C/svg%3E") center bottom no-repeat;
  background-size: 80% auto;
}
[data-theme="dark"] .six-card {
  background: #1e1e2e;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
[data-theme="dark"] .six-card-chart {
  background: linear-gradient(180deg, rgba(78, 205, 196, 0.08) 0%, rgba(0, 122, 108, 0.15) 100%);
}
[data-theme="dark"] .six-card-body {
  background: linear-gradient(180deg, #1e1e2e 0%, rgba(78, 205, 196, 0.03) 100%);
}
[data-theme="dark"] .six-card-title {
  color: #e0e0e0;
}
[data-theme="dark"] .six-card-latest {
  color: #fff;
}
[data-theme="dark"] .six-card-desc {
  color: #a0a0a0;
}
[data-theme="dark"] .six-card-location {
  color: #4ecdc4;
}
[data-theme="dark"] .six-card-location svg {
  fill: #4ecdc4;
}
[data-theme="dark"] .badge-safe {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
}
[data-theme="dark"] .six-card-wave svg path {
  fill: #1e1e2e;
}
@media (max-width: 1100px) {
  .six-card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 700px) {
  .six-card-grid {
    grid-template-columns: 1fr;
  }
}

'''

# Replace CSS
css_pattern = r'/\*\s*Six Card Section.*?\*/.*?(?=\n\s*/\*|</style>)'
content = re.sub(css_pattern, new_css, content, flags=re.DOTALL)

# New HTML
new_html = '''<!-- Six Card Section - Marine Identity -->
<section class="six-card-section">
  <div class="six-card-grid">
    <!-- Card 1: Annual DHW Trend - ALERT status -->
    <div class="six-card status-alert">
      <span class="six-card-badge badge-alert">
        <span data-lang="en">Alert</span>
        <span data-lang="ja">警報</span>
      </span>
      <div class="six-card-chart">
        <canvas id="chart-dhw-trend"></canvas>
        <div class="six-card-wave">
          <svg viewBox="0 0 1200 20" preserveAspectRatio="none">
            <path d="M0,10 Q150,0 300,10 T600,10 T900,10 T1200,10 L1200,20 L0,20 Z" fill="#ffffff"/>
          </svg>
        </div>
      </div>
      <div class="six-card-body">
        <div class="six-card-title">
          <span data-lang="en">Degree Heating Weeks</span>
          <span data-lang="ja">積算熱ストレス (DHW)</span>
        </div>
        <div class="six-card-location">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          <span data-lang="en">Sesoko Island, Okinawa</span>
          <span data-lang="ja">沖縄県 瀬底島</span>
        </div>
        <div class="six-card-latest">
          <span data-lang="en">8.2°C-weeks <span class="trend-up">↑ 58%</span></span>
          <span data-lang="ja">8.2°C-weeks <span class="trend-up">↑ 58%</span></span>
        </div>
        <div class="six-card-desc">
          <span data-lang="en">Exceeded Alert Level 2 threshold (8°C-weeks). Mass bleaching likely in progress.</span>
          <span data-lang="ja">警報レベル2の閾値（8°C-weeks）を超過。大規模白化が進行中の可能性。</span>
        </div>
        <a href="#" class="six-card-btn">
          <span data-lang="en">Explore data</span>
          <span data-lang="ja">データを見る</span>
          <svg viewBox="0 0 24 24"><path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/></svg>
        </a>
      </div>
    </div>
    <!-- Card 2: Monthly SST - WARNING status -->
    <div class="six-card status-warning">
      <span class="six-card-badge badge-watch">
        <span data-lang="en">Watch</span>
        <span data-lang="ja">注意</span>
      </span>
      <div class="six-card-chart">
        <canvas id="chart-sst-compare"></canvas>
        <div class="six-card-wave">
          <svg viewBox="0 0 1200 20" preserveAspectRatio="none">
            <path d="M0,10 Q150,0 300,10 T600,10 T900,10 T1200,10 L1200,20 L0,20 Z" fill="#ffffff"/>
          </svg>
        </div>
      </div>
      <div class="six-card-body">
        <div class="six-card-title">
          <span data-lang="en">Sea Surface Temperature</span>
          <span data-lang="ja">海水温 (SST)</span>
        </div>
        <div class="six-card-location">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          <span data-lang="en">Sesoko Island, Okinawa</span>
          <span data-lang="ja">沖縄県 瀬底島</span>
        </div>
        <div class="six-card-latest">
          <span data-lang="en">30.2°C <span class="trend-up">+1.1°C vs 2023</span></span>
          <span data-lang="ja">30.2°C <span class="trend-up">+1.1°C（前年比）</span></span>
        </div>
        <div class="six-card-desc">
          <span data-lang="en">August 2024 recorded the highest monthly SST. Coral bleaching threshold exceeded.</span>
          <span data-lang="ja">2024年8月に月間最高水温を記録。サンゴ白化閾値を超過。</span>
        </div>
        <a href="#" class="six-card-btn">
          <span data-lang="en">Explore data</span>
          <span data-lang="ja">データを見る</span>
          <svg viewBox="0 0 24 24"><path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/></svg>
        </a>
      </div>
    </div>
    <!-- Card 3: Site Comparison - SAFE status -->
    <div class="six-card">
      <span class="six-card-badge badge-safe">
        <span data-lang="en">Normal</span>
        <span data-lang="ja">平常</span>
      </span>
      <div class="six-card-chart">
        <canvas id="chart-site-compare"></canvas>
        <div class="six-card-wave">
          <svg viewBox="0 0 1200 20" preserveAspectRatio="none">
            <path d="M0,10 Q150,0 300,10 T600,10 T900,10 T1200,10 L1200,20 L0,20 Z" fill="#ffffff"/>
          </svg>
        </div>
      </div>
      <div class="six-card-body">
        <div class="six-card-title">
          <span data-lang="en">Site Comparison</span>
          <span data-lang="ja">観測地点の比較</span>
        </div>
        <div class="six-card-location">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          <span data-lang="en">Manza & Sesoko, Okinawa</span>
          <span data-lang="ja">沖縄県 万座・瀬底</span>
        </div>
        <div class="six-card-latest">
          <span data-lang="en">Δ 0.3°C between sites</span>
          <span data-lang="ja">地点間差 0.3°C</span>
        </div>
        <div class="six-card-desc">
          <span data-lang="en">Sesoko shows slightly higher temperatures due to local current patterns.</span>
          <span data-lang="ja">瀬底がやや高温。潮流パターンが熱ストレスに影響。</span>
        </div>
        <a href="#" class="six-card-btn">
          <span data-lang="en">Explore data</span>
          <span data-lang="ja">データを見る</span>
          <svg viewBox="0 0 24 24"><path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/></svg>
        </a>
      </div>
    </div>
    <!-- Card 4: Monitoring Sites 1000 (Coming Soon) -->
    <div class="six-card coming-soon">
      <div class="six-card-chart">
        <span class="coming-soon-label">COMING SOON</span>
      </div>
      <div class="six-card-body">
        <div class="six-card-title">
          <span data-lang="en">Monitoring Sites 1000</span>
          <span data-lang="ja">モニタリングサイト1000</span>
        </div>
        <div class="six-card-location">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          <span data-lang="en">Nationwide, Japan</span>
          <span data-lang="ja">全国</span>
        </div>
        <div class="six-card-desc">
          <span data-lang="en">Integration with Japan's national coral reef monitoring network.</span>
          <span data-lang="ja">環境省モニタリングサイト1000サンゴ礁調査との連携。</span>
        </div>
      </div>
    </div>
    <!-- Card 5: Turbidity Monitoring (Coming Soon) -->
    <div class="six-card coming-soon">
      <div class="six-card-chart">
        <span class="coming-soon-label">COMING SOON</span>
      </div>
      <div class="six-card-body">
        <div class="six-card-title">
          <span data-lang="en">Turbidity</span>
          <span data-lang="ja">濁度観測</span>
        </div>
        <div class="six-card-location">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          <span data-lang="en">Okinawa coastal stations</span>
          <span data-lang="ja">沖縄沿岸観測点</span>
        </div>
        <div class="six-card-desc">
          <span data-lang="en">Real-time water clarity data affecting coral photosynthesis.</span>
          <span data-lang="ja">サンゴの光合成に影響する水の透明度データ。</span>
        </div>
      </div>
    </div>
    <!-- Card 6: Ogasawara (Coming Soon) -->
    <div class="six-card coming-soon">
      <div class="six-card-chart">
        <span class="coming-soon-label">COMING SOON</span>
      </div>
      <div class="six-card-body">
        <div class="six-card-title">
          <span data-lang="en">Ogasawara Islands</span>
          <span data-lang="ja">小笠原諸島</span>
        </div>
        <div class="six-card-location">
          <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          <span data-lang="en">UNESCO World Heritage Site</span>
          <span data-lang="ja">UNESCO世界自然遺産</span>
        </div>
        <div class="six-card-desc">
          <span data-lang="en">Thermal stress monitoring for isolated Pacific coral ecosystems.</span>
          <span data-lang="ja">太平洋の孤立したサンゴ生態系の熱ストレス観測。</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Six Card Charts Script -->
<script>
document.addEventListener('DOMContentLoaded', function() {
  const ctxDHW = document.getElementById('chart-dhw-trend');
  if (ctxDHW) {
    new Chart(ctxDHW, {
      type: 'bar',
      data: {
        labels: ['2020', '2021', '2022', '2023', '2024'],
        datasets: [{
          data: [2.1, 3.4, 4.8, 5.2, 8.2],
          backgroundColor: ['#4ecdc4', '#4ecdc4', '#f9a825', '#f9a825', '#e74c3c'],
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 10, grid: { color: 'rgba(0,122,108,0.08)' }, ticks: { font: { size: 10 }, color: '#666' } },
          x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#666' } }
        }
      }
    });
  }

  const ctxSST = document.getElementById('chart-sst-compare');
  if (ctxSST) {
    new Chart(ctxSST, {
      type: 'line',
      data: {
        labels: ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
        datasets: [
          {
            label: '2024',
            data: [22.5, 22.1, 23.2, 25.1, 27.3, 28.9, 29.8, 30.2, 29.1, 27.2, 25.1, 23.4],
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231,76,60,0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          },
          {
            label: '2023',
            data: [22.1, 21.8, 22.9, 24.8, 26.9, 28.2, 29.1, 29.1, 28.4, 26.8, 24.8, 23.1],
            borderColor: '#3498db',
            borderDash: [5, 5],
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          },
          {
            label: 'MMM',
            data: [29.1, 29.1, 29.1, 29.1, 29.1, 29.1, 29.1, 29.1, 29.1, 29.1, 29.1, 29.1],
            borderColor: '#007a6c',
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

  const ctxSite = document.getElementById('chart-site-compare');
  if (ctxSite) {
    new Chart(ctxSite, {
      type: 'bar',
      data: {
        labels: ['Jun', 'Jul', 'Aug', 'Sep'],
        datasets: [
          {
            label: 'Manza',
            data: [28.2, 29.1, 29.8, 28.6],
            backgroundColor: '#3498db',
            borderRadius: 4
          },
          {
            label: 'Sesoko',
            data: [28.5, 29.5, 30.1, 28.9],
            backgroundColor: '#4ecdc4',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true, position: 'bottom', labels: { boxWidth: 10, font: { size: 9 }, padding: 8 } } },
        scales: {
          y: { min: 26, max: 32, grid: { color: 'rgba(0,122,108,0.08)' }, ticks: { font: { size: 9 }, color: '#666' } },
          x: { grid: { display: false }, ticks: { font: { size: 9 }, color: '#666' } }
        }
      }
    });
  }
});
</script>'''

# Replace HTML section
html_pattern = r'<!-- Six Card Section - Met Office Style -->.*?</script>'
content = re.sub(html_pattern, new_html, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

import os
print(f"Updated: {os.path.getsize(file_path):,} bytes")
