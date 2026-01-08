#!/usr/bin/env python3
"""
ナビゲーション一括置換スクリプト
"""
import os
import re
import glob

BASE_DIR = "/Users/hirokifukui/Dropbox (個人)/Scripts/marine-obs"

# 新しいデスクトップナビ
NEW_NAV_DESKTOP = '''            <nav class="nav-desktop">
                <ul class="nav-links">
                    <li class="nav-item has-dropdown">
                        <a href="#" class="nav-link">
                            <span data-lang="en">Details</span>
                            <span data-lang="ja">データ詳細</span>
                            <svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="sst.html"><span data-lang="en">Sea Surface Temperature</span><span data-lang="ja">海水温</span></a></li>
                            <li><a href="extreme.html"><span data-lang="en">Extreme Temperature Days</span><span data-lang="ja">極端水温日数</span></a></li>
                            <li><a href="dhw.html"><span data-lang="en">Degree Heating Weeks</span><span data-lang="ja">積算熱ストレス</span></a></li>
                            <li><a href="turbidity.html"><span data-lang="en">Turbidity</span><span data-lang="ja">濁度観測</span><span class="nav-badge">計画中</span></a></li>
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

# 新しいモバイルサイドバー
NEW_NAV_SIDEBAR = '''    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="sidebar-title">Menu</span>
            <button class="sidebar-close" id="sidebar-close" aria-label="Close menu">
                <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
        </div>
        <ul class="sidebar-menu">
            <li class="sidebar-section">
                <span class="sidebar-section-title">
                    <span data-lang="en">Details</span>
                    <span data-lang="ja">データ詳細</span>
                </span>
                <ul class="sidebar-submenu">
                    <li><a href="sst.html"><span data-lang="en">Sea Surface Temperature</span><span data-lang="ja">海水温</span></a></li>
                    <li><a href="extreme.html"><span data-lang="en">Extreme Temperature Days</span><span data-lang="ja">極端水温日数</span></a></li>
                    <li><a href="dhw.html"><span data-lang="en">Degree Heating Weeks</span><span data-lang="ja">積算熱ストレス</span></a></li>
                    <li><a href="turbidity.html"><span data-lang="en">Turbidity</span><span data-lang="ja">濁度観測</span><span class="nav-badge-mobile">計画中</span></a></li>
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


def replace_nav_desktop(content):
    """デスクトップナビを置換"""
    pattern = r'<nav class="nav-desktop">.*?</nav>'
    return re.sub(pattern, NEW_NAV_DESKTOP, content, flags=re.DOTALL)


def replace_nav_sidebar(content):
    """モバイルサイドバーを置換"""
    pattern = r'<nav class="sidebar" id="sidebar">.*?</nav>\s*(?=\n\s*<main|\n\s*<!--|\n\s*<div class="page-container")'
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        return content[:match.start()] + NEW_NAV_SIDEBAR + content[match.end():]
    return content


def process_file(filepath):
    """ファイルを処理"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ナビがあるか確認
    if 'nav-desktop' not in content:
        return False, "No nav found"
    
    original = content
    
    # デスクトップナビ置換
    content = replace_nav_desktop(content)
    
    # サイドバー置換
    content = replace_nav_sidebar(content)
    
    if content == original:
        return False, "No changes"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, "Updated"


def main():
    html_files = glob.glob(os.path.join(BASE_DIR, "*.html"))
    
    results = []
    for filepath in sorted(html_files):
        filename = os.path.basename(filepath)
        success, msg = process_file(filepath)
        results.append((filename, success, msg))
        status = "✅" if success else "⏭️"
        print(f"{status} {filename}: {msg}")
    
    updated = sum(1 for _, s, _ in results if s)
    print(f"\n合計: {updated}/{len(results)} ファイル更新")


if __name__ == "__main__":
    main()
