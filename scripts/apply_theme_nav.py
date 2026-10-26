#!/usr/bin/env python3
"""Apply the 2026-10 visual system to every page:
  * add the serif fonts and css/theme.css (last stylesheet)
  * replace desktop nav and mobile sidebar with the 4-group navigation
  * add an About link to the header controls
Idempotent: re-running rewrites the nav blocks and skips already-inserted links.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GROUPS = [
    (('Observe', '観測'), [
        ('sst.html', 'Sea Surface Temperature', '海水温'),
        ('extreme.html', 'Extreme Temperature Days', '極端水温日数'),
        ('dhw.html', 'Degree Heating Weeks', '積算熱ストレス（DHW）'),
        ('light-adjusted-dhw.html', 'Light-Adjusted DHW', '光補正DHW'),
        ('enso.html', 'ENSO and Onna Outlook', 'ENSOと恩納村の見通し'),
        ('climate-drivers.html', 'Climate Drivers', '気候ドライバー'),
        ('climate-trend.html', 'Climate Trend', '長期トレンド'),
        ('field-monitoring.html', 'Field Monitoring', '現場モニタリング'),
    ]),
    (('Research', '研究'), [
        ('publications.html', 'Publications', '研究成果'),
        ('moni1000.html', 'Moni1000', 'モニ1000'),
        ('moni1000/data-overview.html', 'Moni1000 Data Overview', 'モニ1000 データ概要'),
        ('moni1000/sst-validation.html', 'Satellite SST Validation', '衛星水温の検証'),
        ('vulnerability.html', 'Species Vulnerability', '種別脆弱性'),
        ('chlorophyll-bleaching.html', 'Chlorophyll & Bleaching', 'クロロフィルと白化'),
        ('dissolved-oxygen-bleaching.html', 'Dissolved Oxygen & Bleaching', '溶存酸素と白化'),
        ('datasources.html', 'Data Sources', 'データソース'),
    ]),
    (('Learn', '学ぶ'), [
        ('bleaching.html', 'What is Bleaching', '白化とは'),
        ('japan-bleaching.html', 'Bleaching in Japan', '日本の白化'),
        ('global-bleaching.html', 'Global Bleaching', '世界の白化'),
        ('coral-basics.html', 'Coral Basics', 'サンゴとは'),
        ('species-guide.html', 'Species Guide', 'サンゴ図鑑'),
        ('spawning.html', 'Coral Spawning', 'サンゴ産卵予測'),
        ('glossary.html', 'Glossary', '用語解説'),
    ]),
    (('Dive', '潜る'), [
        ('conditions.html', 'Sea Conditions', '海況'),
        ('weather.html', 'Weather Map', '天気図'),
        ('diving-population.html', 'Diving Population', 'ダイビング人口'),
        ('immersion-pulmonary-edema.html', 'Immersion Pulmonary Edema', '浸水性肺水腫'),
        ('instructor-health.html', 'Instructor Health', 'インストラクターの健康'),
    ]),
]
ARROW = '<svg class="dropdown-arrow" viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>'
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">'


def desktop(pre):
    out = ['            <nav class="nav-desktop">', '                <ul class="nav-links">']
    for (en, ja), items in GROUPS:
        out += ['                    <li class="nav-item has-dropdown">',
                '                        <a href="#" class="nav-link">',
                f'                            <span data-lang="en">{en}</span>',
                f'                            <span data-lang="ja">{ja}</span>',
                f'                            {ARROW}',
                '                        </a>',
                '                        <ul class="dropdown-menu">']
        for href, ien, ija in items:
            out.append(f'                            <li><a href="{pre}{href}"><span data-lang="en">{ien}</span><span data-lang="ja">{ija}</span></a></li>')
        out += ['                        </ul>', '                    </li>']
    out += ['                </ul>', '            </nav>']
    return '\n'.join(out)


def sidebar(pre):
    out = ['        <ul class="sidebar-menu">']
    for (en, ja), items in GROUPS:
        out += ['            <li class="sidebar-section">',
                '                <span class="sidebar-section-title">',
                f'                    <span data-lang="en">{en}</span>',
                f'                    <span data-lang="ja">{ja}</span>',
                '                </span>',
                '                <ul class="sidebar-submenu">']
        for href, ien, ija in items:
            out.append(f'                    <li><a href="{pre}{href}"><span data-lang="en">{ien}</span><span data-lang="ja">{ija}</span></a></li>')
        out += ['                </ul>', '            </li>']
    out += ['            <li class="sidebar-section">',
            '                <ul class="sidebar-submenu">',
            f'                    <li><a href="{pre}about.html"><span data-lang="en">About</span><span data-lang="ja">このサイトについて</span></a></li>',
            f'                    <li><a href="{pre}contact.html"><span data-lang="en">Contact</span><span data-lang="ja">お問い合わせ</span></a></li>',
            '                </ul>', '            </li>',
            '        </ul>']
    return '\n'.join(out)


def apply(path):
    s = path.read_text()
    if 'nav-desktop' not in s:
        return 'skip (no nav)'
    pre = '../' if path.parent.name == 'moni1000' else ''
    # desktop nav block
    a = s.index('            <nav class="nav-desktop">') if '            <nav class="nav-desktop">' in s else s.index('<nav class="nav-desktop">')
    b = s.index('</nav>', a) + len('</nav>')
    s = s[:a] + desktop(pre) + s[b:]
    # sidebar menu block
    a = s.index('<ul class="sidebar-menu">')
    a = s.rfind('\n', 0, a) + 1
    b = s.index('\n    </nav>', a)
    s = s[:a] + sidebar(pre) + s[b:]
    # about link in header controls
    if 'class="nav-about"' not in s and '<div class="header-controls">' in s:
        s = s.replace('<div class="header-controls">',
                      f'<div class="header-controls">\n                <a class="nav-about" href="{pre}about.html"><span data-lang="en">About</span><span data-lang="ja">このサイトについて</span></a>', 1)
    # fonts + theme
    if 'Shippori+Mincho' not in s:
        s = s.replace('</head>', f'    {FONTS}\n</head>', 1)
    if 'css/theme.css' not in s:
        s = s.replace('</head>', f'    <link rel="stylesheet" href="{pre}css/theme.css">\n</head>', 1)
    path.write_text(s)
    return 'ok'


if __name__ == '__main__':
    files = sorted(list(ROOT.glob('*.html')) + list(ROOT.glob('moni1000/*.html')))
    for f in files:
        print(f.relative_to(ROOT), apply(f))
