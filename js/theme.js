/* theme.js — light / dark toggle and chart colours. The early data-theme read lives
   inline in <head> so the page never flashes the wrong scheme. */
(function () {
    var root = document.documentElement;
    var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

    try {
        var q = new URLSearchParams(location.search).get('theme');
        if (q === 'dark' || q === 'light') root.dataset.theme = q;
    } catch (e) {}

    function isDark() {
        if (root.dataset.theme) return root.dataset.theme === 'dark';
        return !!(mq && mq.matches);
    }

    var MOON = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M13.5 10.2A6 6 0 0 1 5.8 2.5a6 6 0 1 0 7.7 7.7z" fill="currentColor"/></svg>';
    var SUN = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3.2" fill="currentColor"/><g stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><path d="M8 1v1.8M8 13.2V15M1 8h1.8M13.2 8H15M3 3l1.3 1.3M11.7 11.7 13 13M3 13l1.3-1.3M11.7 4.3 13 3"/></g></svg>';

    function paintButton(btn) {
        var dark = isDark();
        btn.innerHTML = dark ? SUN : MOON;
        var ja = document.body && document.body.classList.contains('ja');
        var label = dark ? (ja ? 'ライト表示に切り替え' : 'Switch to light') : (ja ? 'ダーク表示に切り替え' : 'Switch to dark');
        btn.setAttribute('aria-label', label);
        btn.title = label;
    }

    function chartDefaults() {
        if (!window.Chart || !Chart.defaults) return;
        var dark = isDark();
        Chart.defaults.color = dark ? '#A9B7BB' : '#435257';
        Chart.defaults.borderColor = dark ? 'rgba(220, 228, 230, 0.12)' : 'rgba(28, 36, 39, 0.1)';
        if (Chart.instances) {
            Object.values(Chart.instances).forEach(function (c) {
                try {
                    var sc = c.options.scales || {};
                    Object.keys(sc).forEach(function (k) {
                        if (sc[k].grid) sc[k].grid.color = Chart.defaults.borderColor;
                        if (sc[k].ticks) sc[k].ticks.color = Chart.defaults.color;
                        if (sc[k].title) sc[k].title.color = Chart.defaults.color;
                    });
                    var pl = c.options.plugins || {};
                    if (pl.legend && pl.legend.labels) pl.legend.labels.color = Chart.defaults.color;
                    c.update('none');
                } catch (e) {}
            });
        }
    }

    function metaColor() {
        var m = document.querySelector('meta[name="theme-color"]');
        if (!m) { m = document.createElement('meta'); m.name = 'theme-color'; document.head.appendChild(m); }
        m.content = isDark() ? '#09121A' : '#14283F';
    }

    function apply() {
        var b = document.querySelector('.theme-toggle');
        if (b) paintButton(b);
        chartDefaults();
        metaColor();
    }

    function mount() {
        var anchor = document.querySelector('.lang-switch');
        if (anchor && !document.querySelector('.theme-toggle')) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'theme-toggle';
            btn.addEventListener('click', function () {
                var next = isDark() ? 'light' : 'dark';
                var sys = mq && mq.matches ? 'dark' : 'light';
                if (next === sys) { delete root.dataset.theme; try { localStorage.removeItem('theme'); } catch (e) {} }
                else { root.dataset.theme = next; try { localStorage.setItem('theme', next); } catch (e) {} }
                apply();
            });
            anchor.parentNode.insertBefore(btn, anchor);
        }
        apply();
        // charts built after async fetches
        setTimeout(chartDefaults, 1500);
        setTimeout(chartDefaults, 4000);
    }

    if (mq && mq.addEventListener) mq.addEventListener('change', apply);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
    else mount();
    chartDefaults();
})();
