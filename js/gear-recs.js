(function() {
    const GEAR_RECS = {
        ja: [
            { min: 28, gear: '3mm または ラッシュガード', note: '暖かい海' },
            { min: 26, gear: '3mm ウェット', note: '快適' },
            { min: 24, gear: '5mm ウェット', note: '標準的な保温' },
            { min: 22, gear: '5mm + フードベスト', note: '保温強化' },
            { min: 20, gear: '5mm ツーピース', note: '重ね着推奨' },
            { min: 0, gear: 'ドライスーツ', note: '低水温' }
        ],
        en: [
            { min: 28, gear: '3mm / rashguard', note: 'Warm' },
            { min: 26, gear: '3mm wetsuit', note: 'Comfortable' },
            { min: 24, gear: '5mm wetsuit', note: 'Standard' },
            { min: 22, gear: '5mm + hood vest', note: 'Extra warmth' },
            { min: 20, gear: '5mm two-piece', note: 'Layer up' },
            { min: 0, gear: 'Dry suit', note: 'Cold' }
        ]
    };

    function getGearRec(temp, lang) {
        const recs = GEAR_RECS[lang] || GEAR_RECS.en;
        for (const r of recs) if (temp >= r.min) return r;
        return recs[recs.length - 1];
    }

    // Extract data from existing marine monitor cards
    function extractMarineData() {
        const cards = document.querySelectorAll('#marine-grid-divers .marine-summary-card');
        const data = [];
        cards.forEach(card => {
            const locEl = card.querySelector('.marine-location');
            const items = card.querySelectorAll('.marine-summary-item');
            if (!locEl || items.length < 3) return;
            
            const loc = locEl.textContent.trim();
            let temp = null, wave = null, wind = null;
            
            items.forEach(item => {
                const val = item.querySelector('.value')?.textContent || '';
                const label = item.querySelector('.label')?.textContent || '';
                if (label.includes('水温') || label.includes('Water')) temp = parseFloat(val);
                else if (label.includes('波') || label.includes('Wave')) wave = parseFloat(val);
                else if (label.includes('風') || label.includes('Wind')) wind = parseFloat(val);
            });
            
            if (loc && temp !== null) {
                data.push({ loc, temp, wave: wave || 0, wind: wind || 0 });
            }
        });
        return data;
    }

    async function renderCoralStress(isJa) {
        const coralGrid = document.getElementById('coral-stress-grid');
        if (!coralGrid) return;
        
        try {
            // Load SST and DHW data
            const [sstData, dhwData] = await Promise.all([
                fetch('data/sst_recent.json').then(r => r.json()),
                fetch('data/dhw_annual_peak.json').then(r => r.json())
            ]);
            
            const locs = [
                { id: 'sesoko', ja: '瀬底', en: 'Sesoko', mmm: 29.0 },
                { id: 'manza', ja: '万座', en: 'Manza', mmm: 29.0 },
                { id: 'ogasawara', ja: '小笠原', en: 'Ogasawara', mmm: 28.5 }
            ];
            
            let html = '';
            
            for (const loc of locs) {
                const sstArr = sstData[loc.id] || [];
                const latestSST = sstArr.length > 0 ? sstArr[sstArr.length - 1] : null;
                
                // 2024 peak DHW
                const dhwArr = dhwData[loc.id] || [];
                const dhw2024 = dhwArr.find(d => d.year === 2024);
                
                const name = isJa ? loc.ja : loc.en;
                const currentSST = latestSST ? latestSST.sst.toFixed(1) : '-';
                const diffFromMMM = latestSST ? (latestSST.sst - loc.mmm).toFixed(1) : '-';
                const peakDHW = dhw2024 ? dhw2024.peak_dhw.toFixed(1) : '-';
                
                // Status based on current SST vs MMM
                let statusCls = 'safe';
                let statusTxt = isJa ? '低リスク' : 'Low Risk';
                if (latestSST && latestSST.sst > loc.mmm + 1) {
                    statusCls = 'warning';
                    statusTxt = isJa ? '要注意' : 'Watch';
                } else if (latestSST && latestSST.sst > loc.mmm) {
                    statusCls = 'watch';
                    statusTxt = isJa ? '注意' : 'Monitor';
                }
                
                html += `
                <div class="coral-stress-card">
                    <div class="coral-stress-location">${name}</div>
                    <div class="coral-stress-row">
                        <div class="coral-stress-metric">
                            <span class="coral-stress-value">${currentSST}°C</span>
                            <span class="coral-stress-label">${isJa ? '現在SST' : 'Current SST'}</span>
                        </div>
                        <div class="coral-stress-metric">
                            <span class="coral-stress-value ${parseFloat(diffFromMMM) > 0 ? 'warm' : ''}">${diffFromMMM > 0 ? '+' : ''}${diffFromMMM}°C</span>
                            <span class="coral-stress-label">${isJa ? 'vs MMM' : 'vs MMM'}</span>
                        </div>
                    </div>
                    <div class="coral-stress-row">
                        <div class="coral-stress-metric">
                            <span class="coral-stress-value">${peakDHW}</span>
                            <span class="coral-stress-label">${isJa ? '2024最大DHW' : '2024 Peak DHW'}</span>
                        </div>
                        <div class="coral-stress-status ${statusCls}">${statusTxt}</div>
                    </div>
                </div>`;
            }
            
            coralGrid.innerHTML = html;
            
        } catch (err) {
            console.error('Coral stress error:', err);
            coralGrid.innerHTML = `<div style="color:var(--text-muted)">${isJa ? 'データ読み込みエラー' : 'Error loading data'}</div>`;
        }
    }

    function renderGearGuide(marineData, isJa) {
        const gearGrid = document.getElementById('gear-guide-grid');
        if (!gearGrid || marineData.length === 0) return;
        
        const okinawa = marineData.find(d => d.loc.includes('瀬底') || d.loc.includes('万座') || d.loc.includes('Sesoko') || d.loc.includes('Manza'));
        const ogasawara = marineData.find(d => d.loc.includes('小笠原') || d.loc.includes('Ogasawara'));
        
        let html = '';
        if (okinawa) {
            const rec = getGearRec(okinawa.temp, isJa ? 'ja' : 'en');
            html += `<div class="gear-location"><div class="gear-location-name">${isJa ? '沖縄' : 'Okinawa'} <span class="gear-location-temp">${okinawa.temp.toFixed(1)}°C</span></div><div class="gear-recommendation"><strong>${rec.gear}</strong><br>${rec.note}</div></div>`;
        }
        if (ogasawara) {
            const rec = getGearRec(ogasawara.temp, isJa ? 'ja' : 'en');
            html += `<div class="gear-location"><div class="gear-location-name">${isJa ? '小笠原' : 'Ogasawara'} <span class="gear-location-temp">${ogasawara.temp.toFixed(1)}°C</span></div><div class="gear-recommendation"><strong>${rec.gear}</strong><br>${rec.note}</div></div>`;
        }
        gearGrid.innerHTML = html || `<div style="color:var(--text-muted)">${isJa ? 'データなし' : 'No data'}</div>`;
    }

    function render() {
        const isJa = document.body.classList.contains('ja');
        const marineData = extractMarineData();
        
        if (marineData.length === 0) {
            setTimeout(render, 1000);
            return;
        }
        
        renderCoralStress(isJa);
        renderGearGuide(marineData, isJa);
    }

    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(render, 1500);
        const observer = new MutationObserver(() => setTimeout(render, 500));
        observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    });
})();
