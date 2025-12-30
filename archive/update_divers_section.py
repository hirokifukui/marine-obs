#!/usr/bin/env python3
"""
1. Add CSS for diver CTA section
2. Add new nav item "For Divers"
3. Add CTA section after hero
4. Create new Divers page with marine monitor
5. Remove marine monitor from home page
"""

with open("/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for diver CTA section (before /* Section titles */)
diver_cta_css = '''/* Diver CTA Section */
.diver-cta {
    background: linear-gradient(135deg, rgba(91, 154, 148, 0.08) 0%, rgba(91, 154, 148, 0.03) 100%);
    border: 1px solid rgba(91, 154, 148, 0.2);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2.5rem;
}

.diver-cta-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.25rem;
}

.diver-cta-header h2 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}

.diver-cta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.diver-cta-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.diver-cta-card:hover {
    border-color: #5b9a94;
    box-shadow: 0 4px 12px rgba(91, 154, 148, 0.15);
    transform: translateY(-2px);
}

.diver-cta-card .icon {
    font-size: 1.5rem;
}

.diver-cta-card .title {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
}

.diver-cta-card .desc {
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.5;
}

.diver-cta-card.coming-soon {
    opacity: 0.6;
    pointer-events: none;
}

.diver-cta-card.coming-soon .title::after {
    content: ' (準備中)';
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: normal;
}

body:not(.ja) .diver-cta-card.coming-soon .title::after {
    content: ' (Coming Soon)';
}

        /* Section titles */'''

content = content.replace('        /* Section titles */', diver_cta_css)

# 2. Add nav item for Divers (after About)
old_nav = '''<li>
                    <a href="#" data-nav="about">
                        <span data-lang="en">About</span>
                        <span data-lang="ja">このサイトについて</span>
                    </a>
                </li>
                <li>
                    <a href="#" data-nav="glossary">'''

new_nav = '''<li>
                    <a href="#" data-nav="about">
                        <span data-lang="en">About</span>
                        <span data-lang="ja">このサイトについて</span>
                    </a>
                </li>
                <li>
                    <a href="#" data-nav="divers">
                        <span data-lang="en">For Divers</span>
                        <span data-lang="ja">ダイバー向け</span>
                    </a>
                </li>
                <li>
                    <a href="#" data-nav="glossary">'''

content = content.replace(old_nav, new_nav)

# 3. Add CTA section after hero-visual (before kpi-grid)
old_kpi_start = '''            </section>

            <section class="kpi-grid">
                <!-- SST 3地点 -->'''

new_cta_and_kpi = '''            </section>

            <!-- Diver CTA Section -->
            <section class="diver-cta">
                <div class="diver-cta-header">
                    <span>🤿</span>
                    <h2>
                        <span data-lang="en">For Divers</span>
                        <span data-lang="ja">ダイバーの方へ</span>
                    </h2>
                </div>
                <div class="diver-cta-grid">
                    <a href="#" class="diver-cta-card" onclick="showPage('divers'); return false;">
                        <span class="icon">🌊</span>
                        <span class="title">
                            <span data-lang="en">Sea Conditions</span>
                            <span data-lang="ja">海況を見る</span>
                        </span>
                        <span class="desc">
                            <span data-lang="en">Wave, wind, water temperature forecast</span>
                            <span data-lang="ja">波・風・水温の予報</span>
                        </span>
                    </a>
                    <a href="#" class="diver-cta-card coming-soon">
                        <span class="icon">📷</span>
                        <span class="title">
                            <span data-lang="en">Report Observation</span>
                            <span data-lang="ja">観察を報告</span>
                        </span>
                        <span class="desc">
                            <span data-lang="en">Share bleaching status, marine life</span>
                            <span data-lang="ja">白化状況や生物の目撃情報</span>
                        </span>
                    </a>
                    <a href="#" class="diver-cta-card coming-soon">
                        <span class="icon">📍</span>
                        <span class="title">
                            <span data-lang="en">Dive Sites</span>
                            <span data-lang="ja">ダイビングポイント</span>
                        </span>
                        <span class="desc">
                            <span data-lang="en">Site info and conditions</span>
                            <span data-lang="ja">ポイント情報と海況</span>
                        </span>
                    </a>
                </div>
            </section>

            <section class="kpi-grid">
                <!-- SST 3地点 -->'''

content = content.replace(old_kpi_start, new_cta_and_kpi)

# 4. Remove marine monitor section from home page
# Find and remove the marine monitor section
import re
marine_monitor_pattern = r'<!-- Marine Monitor Section -->.*?</section>\s*\n\s*<h2 class="section-title">'
content = re.sub(marine_monitor_pattern, '<h2 class="section-title">', content, flags=re.DOTALL)

# 5. Add Divers page (before ABOUT PAGE)
divers_page = '''        <!-- DIVERS PAGE -->
        <section class="page-section" id="page-divers">
            <section class="hero">
                <h1 data-lang="en">For Divers</h1>
                <h1 data-lang="ja">ダイバー向け情報</h1>
                <p class="hero-subtitle" data-lang="en">
                    Sea conditions, observations, and resources for divers.
                </p>
                <p class="hero-subtitle" data-lang="ja">
                    海況情報、観察報告、ダイバーのためのリソース。
                </p>
            </section>

            <!-- Marine Monitor Section -->
            <section class="marine-monitor">
                <div class="marine-monitor-header">
                    <h2 class="marine-monitor-title">
                        🌊 <span data-lang="en">Marine Conditions</span><span data-lang="ja">海況モニター</span>
                    </h2>
                    <span class="marine-monitor-update" id="marine-update-time-divers"></span>
                </div>
                <div class="marine-summary-grid" id="marine-grid-divers">
                    <div style="color: var(--text-muted); padding: 2rem; text-align: center;">
                        <span data-lang="en">Loading...</span><span data-lang="ja">読み込み中...</span>
                    </div>
                </div>
            </section>

            <!-- Future: Observation Report Form -->
            <section class="info-card" style="margin-top: 2rem;">
                <h3>
                    <span data-lang="en">📷 Report Your Observation</span>
                    <span data-lang="ja">📷 観察を報告する</span>
                </h3>
                <p data-lang="en">Coming soon: Share what you see underwater—coral bleaching, unusual marine life, or changes in the reef. Your observations help build a community-driven picture of ocean health.</p>
                <p data-lang="ja">準備中：水中で見たものを共有してください。サンゴの白化、珍しい海洋生物、リーフの変化など。あなたの観察が、海の健康状態を知るための貴重なデータになります。</p>
            </section>
        </section>

        <!-- ABOUT PAGE -->'''

content = content.replace('        <!-- ABOUT PAGE -->', divers_page)

# 6. Update marine monitor JS to support both pages
old_marine_init = '''    // Initialize
    document.addEventListener('DOMContentLoaded', async () => {
        const data = await fetchMarineData();
        renderCards(data);
        
        // Re-render on language change
        const observer = new MutationObserver(() => {
            renderCards(data);
        });
        observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    });'''

new_marine_init = '''    // Render to a specific grid
    function renderToGrid(gridId, updateId, data) {
        const grid = document.getElementById(gridId);
        if (!grid) return;
        
        const isJa = document.body.classList.contains('ja');
        let html = '';
        
        for (const loc of LOCATIONS) {
            const locData = data[loc.id] || [];
            const grouped = groupByDate(locData);
            const dates = Object.keys(grouped).sort().slice(0, 4);
            
            if (dates.length === 0) {
                html += `<div class="marine-summary-card"><div class="marine-location">${isJa ? loc.name : loc.nameEn}</div><div style="color:var(--text-muted)">No data</div></div>`;
                continue;
            }
            
            const todaySummary = calcDailySummary(grouped[dates[0]]);
            const status = todaySummary ? getSeaStatus(todaySummary.waveMax, todaySummary.swellMax, todaySummary.windMax) : { class: 'good', textJa: '-', textEn: '-' };
            const windDir = todaySummary ? degToDirection(todaySummary.windDirAvg) : { ja: '-', en: '-' };
            
            html += `
            <div class="marine-summary-card" onclick="this.classList.toggle('expanded')">
                <div class="marine-card-header">
                    <span class="marine-location">${isJa ? loc.name : loc.nameEn}</span>
                    <div class="marine-status">
                        <span class="status-dot ${status.class}"></span>
                        <span>${isJa ? status.textJa : status.textEn}</span>
                        <span class="marine-expand-icon">▼</span>
                    </div>
                </div>
                <div class="marine-summary-row">
                    <div class="marine-summary-item">
                        <span class="label">${isJa ? '水温' : 'Water'}</span>
                        <span class="value">${todaySummary?.waterTemp?.toFixed(1) || '-'}℃</span>
                    </div>
                    <div class="marine-summary-item">
                        <span class="label">${isJa ? '波' : 'Wave'}</span>
                        <span class="value">${todaySummary?.waveMax?.toFixed(1) || '-'}m</span>
                    </div>
                    <div class="marine-summary-item">
                        <span class="label">${isJa ? '風' : 'Wind'}</span>
                        <span class="value">${todaySummary?.windMax?.toFixed(0) || '-'}m/s ${isJa ? windDir.ja : windDir.en}</span>
                    </div>
                </div>
                <div class="marine-detail">
                    ${renderDetailTables(grouped, dates, isJa)}
                </div>
            </div>`;
        }
        
        grid.innerHTML = html;
        
        const updateEl = document.getElementById(updateId);
        if (updateEl) {
            const now = new Date();
            updateEl.textContent = isJa 
                ? `更新: ${now.getMonth()+1}/${now.getDate()} ${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}`
                : `Updated: ${now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
        }
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', async () => {
        const data = await fetchMarineData();
        
        // Render to divers page
        renderToGrid('marine-grid-divers', 'marine-update-time-divers', data);
        
        // Re-render on language change
        const observer = new MutationObserver(() => {
            renderToGrid('marine-grid-divers', 'marine-update-time-divers', data);
        });
        observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    });'''

content = content.replace(old_marine_init, new_marine_init)

# Also remove the old renderCards function call references
content = content.replace('renderCards(data);', '// renderCards moved to renderToGrid')

# Write back
with open("/Users/hirokifukui/Dropbox (個人)/Scripts/claude/outputs/marine-obs-pilot/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Done! Changes:")
print("1. Added Diver CTA CSS")
print("2. Added 'For Divers' nav item")
print("3. Added CTA section after hero")
print("4. Removed marine monitor from home page")
print("5. Created new Divers page with marine monitor")
print("6. Updated JS to render marine data on divers page")
