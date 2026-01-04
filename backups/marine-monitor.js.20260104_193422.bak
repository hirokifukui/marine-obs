// Marine Monitor - Supabase Data Fetcher
(function() {
    const SUPABASE_URL = 'https://pegiuiblpliainpdggfj.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlZ2l1aWJscGxpYWlucGRnZ2ZqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDIwOTM3NCwiZXhwIjoyMDc5Nzg1Mzc0fQ.V3C2newkAdn6gW2TR_ct-_WupVKZapXKtD9Cr3aMk2M';
    
    const LOCATIONS = [
        { id: 'okinawa_sesoko', name: '瀬底', nameEn: 'Sesoko' },
        { id: 'okinawa_manza', name: '万座', nameEn: 'Manza' },
        { id: 'ogasawara', name: '小笠原', nameEn: 'Ogasawara' }
    ];
    
    const WEEKDAYS_JA = ['日', '月', '火', '水', '木', '金', '土'];
    const WEEKDAYS_EN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    function degToDirection(deg) {
        if (deg === null || deg === undefined) return '-';
        const dirs = ['北', '北東', '東', '南東', '南', '南西', '西', '北西'];
        const dirsEn = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
        const idx = Math.round(deg / 45) % 8;
        return { ja: dirs[idx], en: dirsEn[idx] };
    }
    
    function getSeaStatus(waveHeight, swellHeight, windSpeed) {
        const totalWave = (waveHeight || 0) + (swellHeight || 0);
        const wind = windSpeed || 0;
        if (totalWave >= 2.0 || wind >= 12) return { class: 'warning', textJa: '荒れ', textEn: 'Rough' };
        if (totalWave >= 1.0 || wind >= 8) return { class: 'caution', textJa: '注意', textEn: 'Caution' };
        return { class: 'good', textJa: '良好', textEn: 'Good' };
    }
    
    async function fetchMarineData() {
        const now = new Date();
        const start = new Date(now);
        start.setHours(0, 0, 0, 0);
        const end = new Date(start);
        end.setDate(end.getDate() + 4);
        
        const startISO = start.toISOString();
        const endISO = end.toISOString();
        
        const results = {};
        
        for (const loc of LOCATIONS) {
            const url = `${SUPABASE_URL}/rest/v1/marine_weather?location=eq.${loc.id}&datetime=gte.${startISO}&datetime=lt.${endISO}&order=datetime.asc&select=datetime,water_temperature,wave_height,swell_height,wind_speed,wind_direction,air_temperature,visibility`;
            
            try {
                const resp = await fetch(url, {
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                    }
                });
                const data = await resp.json();
                results[loc.id] = data;
            } catch (e) {
                console.error(`Error fetching ${loc.id}:`, e);
                results[loc.id] = [];
            }
        }
        
        return results;
    }
    
    function groupByDate(data) {
        const groups = {};
        for (const row of data) {
            const dt = new Date(row.datetime);
            const hour = dt.getUTCHours() + 9; // JST
            if (hour < 7 || hour > 17) continue; // 7:00-17:00 JST only
            
            const dateKey = dt.toISOString().slice(0, 10);
            if (!groups[dateKey]) groups[dateKey] = [];
            groups[dateKey].push({
                hour: hour,
                waterTemp: row.water_temperature,
                waveHeight: row.wave_height,
                swellHeight: row.swell_height,
                windSpeed: row.wind_speed,
                windDir: row.wind_direction,
                airTemp: row.air_temperature,
                visibility: row.visibility
            });
        }
        return groups;
    }
    
    function calcDailySummary(dayData) {
        if (!dayData || dayData.length === 0) return null;
        
        const waterTemps = dayData.map(d => d.waterTemp).filter(v => v != null);
        const waves = dayData.map(d => d.waveHeight).filter(v => v != null);
        const swells = dayData.map(d => d.swellHeight).filter(v => v != null);
        const winds = dayData.map(d => d.windSpeed).filter(v => v != null);
        const windDirs = dayData.map(d => d.windDir).filter(v => v != null);
        
        return {
            waterTemp: waterTemps.length ? (waterTemps.reduce((a,b) => a+b) / waterTemps.length) : null,
            waveMax: waves.length ? Math.max(...waves) : null,
            swellMax: swells.length ? Math.max(...swells) : null,
            windMax: winds.length ? Math.max(...winds) : null,
            windDirAvg: windDirs.length ? (windDirs.reduce((a,b) => a+b) / windDirs.length) : null
        };
    }
    
    function renderCards(data) {
        const grid = document.getElementById('marine-grid');
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
            
            // Today's summary
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
                        <span class="marine-expand-text">${isJa ? '詳細' : 'Details'}</span> <span class="marine-expand-icon">▼</span>
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
        
        // Update time
        const updateEl = document.getElementById('marine-update-time');
        if (updateEl) {
            const now = new Date();
            updateEl.textContent = isJa 
                ? `更新: ${now.getMonth()+1}/${now.getDate()} ${now.getHours()}:${String(now.getMinutes()).padStart(2,'0')}`
                : `Updated: ${now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
        }
    }
    
    function renderDetailTables(grouped, dates, isJa) {
        let html = '';
        
        for (const dateKey of dates) {
            const dayData = grouped[dateKey];
            if (!dayData || dayData.length === 0) continue;
            
            const dt = new Date(dateKey + 'T00:00:00Z');
            const wd = isJa ? WEEKDAYS_JA[dt.getUTCDay()] : WEEKDAYS_EN[dt.getUTCDay()];
            const dateLabel = `${dt.getUTCMonth()+1}/${dt.getUTCDate()} (${wd})`;
            
            html += `
            <div class="marine-day-group">
                <div class="marine-day-header">${dateLabel}</div>
                <table class="marine-table">
                    <thead>
                        <tr>
                            <th>${isJa ? '時刻' : 'Time'}</th>
                            <th>${isJa ? '波高' : 'Wave'}</th>
                            <th>${isJa ? 'うねり' : 'Swell'}</th>
                            <th>${isJa ? '風' : 'Wind'}</th>
                            <th>${isJa ? '水温' : 'Temp'}</th>
                        </tr>
                    </thead>
                    <tbody>`;
            
            for (const row of dayData) {
                const windDir = degToDirection(row.windDir);
                html += `
                        <tr>
                            <td>${row.hour}:00</td>
                            <td>${row.waveHeight?.toFixed(1) || '-'}m</td>
                            <td>${row.swellHeight?.toFixed(1) || '-'}m</td>
                            <td class="wind-dir">${row.windSpeed?.toFixed(0) || '-'}m/s <span style="color:var(--text-muted)">${isJa ? windDir.ja : windDir.en}</span></td>
                            <td>${row.waterTemp?.toFixed(1) || '-'}℃</td>
                        </tr>`;
            }
            
            html += `
                    </tbody>
                </table>
            </div>`;
        }
        
        return html;
    }
    
    // Render to a specific grid
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
                        <span class="marine-expand-text">${isJa ? '詳細' : 'Details'}</span> <span class="marine-expand-icon">▼</span>
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
    });
})();
