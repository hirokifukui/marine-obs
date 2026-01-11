#!/usr/bin/env python3
"""
marine-obs ナビゲーション更新スクリプト
選択肢B: データ詳細を「モニタリング」と「気候」に分割
"""

import os
import re
from pathlib import Path

# 対象HTMLファイル
HTML_FILES = [
    'index.html', 'sst.html', 'extreme.html', 'dhw.html', 'light-adjusted-dhw.html',
    'enso.html', 'climate-drivers.html', 'climate-trend.html', 'chlorophyll-bleaching.html',
    'dissolved-oxygen-bleaching.html', 'field-monitoring.html', 'bleaching.html',
    'vulnerability.html', 'global-bleaching.html', 'japan-bleaching.html', 'coral-basics.html',
    'species-guide.html', 'spawning.html', 'conditions.html', 'weather.html',
    'about.html', 'glossary.html', 'datasources.html', 'contact.html',
]

# 新しいデスクトップナビゲーション
NAV_DESKTOP_NEW = '''            <!-- Desktop Navigation -->
            <nav class="nav-desktop">
                <ul class="nav-links">
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">Monitoring</span>
                            <span data-lang="ja">モニタリング</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="sst.html"><span data-lang="en">Sea Surface Temperature</span><span data-lang="ja">海水温</span></a></li>
                            <li><a href="extreme.html"><span data-lang="en">Extreme Temperature Days</span><span data-lang="ja">極端水温日数</span></a></li>
                            <li><a href="dhw.html"><span data-lang="en">Degree Heating Weeks</span><span data-lang="ja">積算熱ストレス</span></a></li>
                            <li><a href="light-adjusted-dhw.html"><span data-lang="en">Light-Adjusted DHW</span><span data-lang="ja">光補正DHW</span></a></li>
                            <li><a href="field-monitoring.html"><span data-lang="en">Field Monitoring</span><span data-lang="ja">現場モニタリング</span><span class="nav-badge">計画中</span></a></li>
                        </ul>
                    </li>
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">Climate</span>
                            <span data-lang="ja">気候</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="enso.html"><span data-lang="en">ENSO Monitor</span><span data-lang="ja">ENSO監視</span></a></li>
                            <li><a href="climate-drivers.html"><span data-lang="en">Climate Drivers</span><span data-lang="ja">気候ドライバー</span></a></li>
                            <li><a href="climate-trend.html"><span data-lang="en">Climate Trend</span><span data-lang="ja">長期トレンド</span></a></li>
                        </ul>
                    </li>
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">Bleaching</span>
                            <span data-lang="ja">白化</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="bleaching.html"><span data-lang="en">What is Bleaching</span><span data-lang="ja">白化とは</span></a></li>
                            <li><a href="vulnerability.html"><span data-lang="en">Species Vulnerability</span><span data-lang="ja">種別脆弱性</span></a></li>
                            <li><a href="chlorophyll-bleaching.html"><span data-lang="en">Chlorophyll &amp; Bleaching</span><span data-lang="ja">クロロフィルと白化</span></a></li>
                            <li><a href="dissolved-oxygen-bleaching.html"><span data-lang="en">Dissolved Oxygen &amp; Bleaching</span><span data-lang="ja">溶存酸素と白化</span></a></li>
                            <li><a href="global-bleaching.html"><span data-lang="en">Global Status</span><span data-lang="ja">世界の白化状況</span></a></li>
                            <li><a href="japan-bleaching.html"><span data-lang="en">Japan Status</span><span data-lang="ja">日本の白化状況</span></a></li>
                        </ul>
                    </li>
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">Learn</span>
                            <span data-lang="ja">サンゴを知る</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="coral-basics.html"><span data-lang="en">Coral Basics</span><span data-lang="ja">サンゴとは</span></a></li>
                            <li><a href="species-guide.html"><span data-lang="en">Species Guide</span><span data-lang="ja">サンゴ図鑑</span></a></li>
                            <li><a href="spawning.html"><span data-lang="en">Coral Spawning</span><span data-lang="ja">サンゴ産卵予測</span></a></li>
                        </ul>
                    </li>
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">For Divers</span>
                            <span data-lang="ja">ダイバー向け</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="conditions.html"><span data-lang="en">Conditions</span><span data-lang="ja">海況</span></a></li>
                            <li><a href="weather.html"><span data-lang="en">Weather Map</span><span data-lang="ja">天気図</span></a></li>
                        </ul>
                    </li>
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">Reference</span>
                            <span data-lang="ja">リファレンス</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="about.html"><span data-lang="en">About</span><span data-lang="ja">このサイトについて</span></a></li>
                            <li><a href="glossary.html"><span data-lang="en">Glossary</span><span data-lang="ja">用語解説</span></a></li>
                            <li><a href="datasources.html"><span data-lang="en">Data Sources</span><span data-lang="ja">データソース</span></a></li>
                            <li><a href="contact.html"><span data-lang="en">Contact</span><span data-lang="ja">お問い合わせ</span></a></li>
                        </ul>
                    </li>
                </ul>
            </nav>'''

# 新しいサイドバーナビゲーション
NAV_SIDEBAR_NEW = '''    <!-- Mobile Sidebar -->
    <div class="sidebar-overlay" id="sidebar-overlay"></div>
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="sidebar-title">Menu</span>
            <button class="sidebar-close" id="sidebar-close" aria-label="Close menu">
                <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
        </div>
        <ul class="sidebar-menu">
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">Monitoring</span>
                    <span data-lang="ja">モニタリング</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="sst.html"><span data-lang="en">Sea Surface Temperature</span><span data-lang="ja">海水温</span></a></li>
                    <li><a href="extreme.html"><span data-lang="en">Extreme Temperature Days</span><span data-lang="ja">極端水温日数</span></a></li>
                    <li><a href="dhw.html"><span data-lang="en">Degree Heating Weeks</span><span data-lang="ja">積算熱ストレス</span></a></li>
                    <li><a href="light-adjusted-dhw.html"><span data-lang="en">Light-Adjusted DHW</span><span data-lang="ja">光補正DHW</span></a></li>
                    <li><a href="field-monitoring.html"><span data-lang="en">Field Monitoring</span><span data-lang="ja">現場モニタリング</span><span class="nav-badge-mobile">計画中</span></a></li>
                </ul>
            </li>
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">Climate</span>
                    <span data-lang="ja">気候</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="enso.html"><span data-lang="en">ENSO Monitor</span><span data-lang="ja">ENSO監視</span></a></li>
                    <li><a href="climate-drivers.html"><span data-lang="en">Climate Drivers</span><span data-lang="ja">気候ドライバー</span></a></li>
                    <li><a href="climate-trend.html"><span data-lang="en">Climate Trend</span><span data-lang="ja">長期トレンド</span></a></li>
                </ul>
            </li>
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">Bleaching</span>
                    <span data-lang="ja">白化</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="bleaching.html"><span data-lang="en">What is Bleaching</span><span data-lang="ja">白化とは</span></a></li>
                    <li><a href="vulnerability.html"><span data-lang="en">Species Vulnerability</span><span data-lang="ja">種別脆弱性</span></a></li>
                    <li><a href="chlorophyll-bleaching.html"><span data-lang="en">Chlorophyll &amp; Bleaching</span><span data-lang="ja">クロロフィルと白化</span></a></li>
                    <li><a href="dissolved-oxygen-bleaching.html"><span data-lang="en">Dissolved Oxygen &amp; Bleaching</span><span data-lang="ja">溶存酸素と白化</span></a></li>
                    <li><a href="global-bleaching.html"><span data-lang="en">Global Status</span><span data-lang="ja">世界の白化状況</span></a></li>
                    <li><a href="japan-bleaching.html"><span data-lang="en">Japan Status</span><span data-lang="ja">日本の白化状況</span></a></li>
                </ul>
            </li>
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">Learn</span>
                    <span data-lang="ja">サンゴを知る</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="coral-basics.html"><span data-lang="en">Coral Basics</span><span data-lang="ja">サンゴとは</span></a></li>
                    <li><a href="species-guide.html"><span data-lang="en">Species Guide</span><span data-lang="ja">サンゴ図鑑</span></a></li>
                    <li><a href="spawning.html"><span data-lang="en">Coral Spawning</span><span data-lang="ja">サンゴ産卵予測</span></a></li>
                </ul>
            </li>
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">For Divers</span>
                    <span data-lang="ja">ダイバー向け</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="conditions.html"><span data-lang="en">Conditions</span><span data-lang="ja">海況</span></a></li>
                    <li><a href="weather.html"><span data-lang="en">Weather Map</span><span data-lang="ja">天気図</span></a></li>
                </ul>
            </li>
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">Reference</span>
                    <span data-lang="ja">リファレンス</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="about.html"><span data-lang="en">About</span><span data-lang="ja">このサイトについて</span></a></li>
                    <li><a href="glossary.html"><span data-lang="en">Glossary</span><span data-lang="ja">用語解説</span></a></li>
                    <li><a href="datasources.html"><span data-lang="en">Data Sources</span><span data-lang="ja">データソース</span></a></li>
                    <li><a href="contact.html"><span data-lang="en">Contact</span><span data-lang="ja">お問い合わせ</span></a></li>
                </ul>
            </li>
        </ul>
    </nav>'''

# 改善版ナビゲーションJS
NAV_JS_NEW = '''    <!-- Navigation JS -->
    <script>
    (function() {
        function initNavigation() {
            const hamburger = document.getElementById('hamburger');
            const sidebar = document.getElementById('sidebar');
            const sidebarOverlay = document.getElementById('sidebar-overlay');
            const sidebarClose = document.getElementById('sidebar-close');
            
            if (!hamburger || !sidebar || !sidebarOverlay) {
                console.warn('Navigation elements not found');
                return;
            }
            
            function openSidebar() {
                sidebar.classList.add('active');
                sidebarOverlay.classList.add('active');
                hamburger.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
            
            function closeSidebar() {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                hamburger.classList.remove('active');
                document.body.style.overflow = '';
            }
            
            hamburger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (sidebar.classList.contains('active')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            });
            
            hamburger.addEventListener('touchend', function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (sidebar.classList.contains('active')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            });
            
            sidebarOverlay.addEventListener('click', closeSidebar);
            sidebarOverlay.addEventListener('touchend', function(e) {
                e.preventDefault();
                closeSidebar();
            });
            
            if (sidebarClose) {
                sidebarClose.addEventListener('click', closeSidebar);
                sidebarClose.addEventListener('touchend', function(e) {
                    e.preventDefault();
                    closeSidebar();
                });
            }
            
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                    closeSidebar();
                }
            });
            
            sidebar.querySelectorAll('a').forEach(function(link) {
                link.addEventListener('click', function() {
                    closeSidebar();
                });
            });
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initNavigation);
        } else {
            initNavigation();
        }
    })();
    </script>'''


def update_file(filepath):
    """1ファイルを更新"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # デスクトップナビ更新
    pattern_desktop = r'<!-- Desktop Navigation -->.*?</nav>'
    if re.search(pattern_desktop, content, re.DOTALL):
        content = re.sub(pattern_desktop, NAV_DESKTOP_NEW, content, flags=re.DOTALL)
    else:
        pattern_desktop2 = r'<nav class="nav-desktop">.*?</nav>'
        if re.search(pattern_desktop2, content, re.DOTALL):
            content = re.sub(pattern_desktop2, NAV_DESKTOP_NEW, content, flags=re.DOTALL)
    
    # サイドバー更新
    pattern_sidebar = r'<!-- Mobile Sidebar -->.*?</nav>(?=\s*<main)'
    if re.search(pattern_sidebar, content, re.DOTALL):
        content = re.sub(pattern_sidebar, NAV_SIDEBAR_NEW, content, flags=re.DOTALL)
    else:
        pattern_sidebar2 = r'<div class="sidebar-overlay".*?</nav>(?=\s*<main)'
        if re.search(pattern_sidebar2, content, re.DOTALL):
            content = re.sub(pattern_sidebar2, NAV_SIDEBAR_NEW, content, flags=re.DOTALL)
    
    # ナビJS更新
    pattern_js = r'<!-- Navigation JS -->.*?</script>'
    if re.search(pattern_js, content, re.DOTALL):
        content = re.sub(pattern_js, NAV_JS_NEW, content, flags=re.DOTALL)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    project_dir = Path.cwd()
    updated = 0
    
    for filename in HTML_FILES:
        filepath = project_dir / filename
        if filepath.exists():
            if update_file(filepath):
                print(f"✓ {filename}")
                updated += 1
            else:
                print(f"- {filename} (変更なし)")
        else:
            print(f"✗ {filename} (存在しない)")
    
    print(f"\n完了: {updated}ファイル更新")


if __name__ == '__main__':
    main()
