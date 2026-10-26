"""Rewrite hard-coded colour literals as light-dark(orig, dark) so pages follow the
site's dark scheme. Idempotent: values already inside light-dark() are skipped.

Rules (by property role and lightness of the original colour):
  background  light (L>=.5)  -> dark paper range;   dark backgrounds kept (heroes, header)
  text/fill   dark  (L<=.55) -> light ink range;    light text kept (it sits on dark surfaces)
  border      light -> dark rule;  dark -> light rule
Saturated mid colours (accents) are lifted for contrast instead of inverted.
"""
import colorsys, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAMED = {'white': '#ffffff', 'black': '#000000'}
COL = re.compile(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)|\bwhite\b|\bblack\b')
DECL = re.compile(r'(?P<prop>(?<![\w-])(?:--[\w-]+|background(?:-color)?|color|border(?:-(?:top|right|bottom|left))?(?:-color)?|outline(?:-color)?|fill|stroke|box-shadow))\s*:\s*(?P<val>[^;{}"]+)')
# DECL value stops at ; { } and at a double quote (inline style attribute end)


def parse(c):
    c = NAMED.get(c.lower(), c)
    if c.startswith('#'):
        h = c[1:]
        if len(h) == 3:
            h = ''.join(x * 2 for x in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)), None
    nums = re.findall(r'[\d.]+', c)
    rgb = tuple(int(float(x)) for x in nums[:3])
    a = nums[3] if len(nums) > 3 else None
    return rgb, a


def fmt(rgb, a):
    if a is None:
        return '#%02x%02x%02x' % rgb
    return 'rgba(%d, %d, %d, %s)' % (*rgb, a)


def hls(rgb):
    return colorsys.rgb_to_hls(*(x / 255 for x in rgb))


def to_rgb(h, l, s):
    return tuple(max(0, min(255, round(x * 255))) for x in colorsys.hls_to_rgb(h, l, s))


def dark_of(rgb, role):
    h, l, s = hls(rgb)
    if role == 'bg':
        if l < 0.5:
            return None
        # very light -> 0.11..0.20 ; tinted boxes keep a trace of hue
        nl = 0.11 + (1 - l) * 0.55
        ns = min(s, 0.45) * (0.55 if s > 0.15 else 1)
        return to_rgb(h, min(nl, 0.30), ns)
    if role == 'text':
        if l > 0.55:
            return None
        if s > 0.30 and 0.25 < l:          # accent colour: lift
            return to_rgb(h, max(0.66, min(0.78, 1.15 - l)), min(s, 0.65))
        return to_rgb(h, min(0.92, max(0.70, 1.0 - l * 0.9)), min(s, 0.25))
    if role == 'border':
        if l >= 0.6:
            return to_rgb(h, 0.11 + (1 - l) * 0.9, min(s, 0.3))
        if l <= 0.4:
            return to_rgb(h, 0.78 - l * 0.3, min(s, 0.3))
        return to_rgb(h, max(l, 0.55), s)
    return None


ROLE = {'background': 'bg', 'background-color': 'bg', 'color': 'text', 'fill': 'text',
        'stroke': 'border', 'box-shadow': 'shadow'}


def role_of(prop):
    if prop.startswith('--'):
        if re.search(r'bg|background|paper|surface|card', prop): return 'bg'
        if re.search(r'text|ink', prop): return 'text'
        if re.search(r'border|rule|line', prop): return 'border'
        return None
    if prop in ROLE:
        return ROLE[prop]
    if prop.startswith('border') or prop.startswith('outline'):
        return 'border'
    return None


def convert_value(prop, val):
    if 'light-dark(' in val:
        return val
    role = role_of(prop)
    if role is None or role == 'shadow':
        return val
    if prop == 'fill' and 'url(' in val:
        return val
    out, last = [], 0
    for m in COL.finditer(val):
        rgb, a = parse(m.group(0))
        # translucent backgrounds are overlays on photos or dark surfaces: leave them
        d = None if (role == 'bg' and a is not None and float(a) < 1) else dark_of(rgb, role)
        out.append(val[last:m.start()])
        if d is None:
            out.append(m.group(0))
        else:
            out.append('light-dark(%s, %s)' % (m.group(0), fmt(d, a)))
        last = m.end()
    out.append(val[last:])
    return ''.join(out)


UNWRAP = re.compile(r'light-dark\((rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*([\d.]+)\s*\)),\s*rgba\([^)]*\)\)')


def unwrap_bg(prop, val):
    if role_of(prop) != 'bg':
        return val
    return UNWRAP.sub(lambda m: m.group(1) if float(m.group(2)) < 1 else m.group(0), val)


def convert_css(text):
    def rep(m):
        v = unwrap_bg(m.group('prop').lower(), m.group('val'))
        return m.group('prop') + ': ' + convert_value(m.group('prop').lower(), v)
    def _unused(m):
        return m.group('prop') + ': ' + convert_value(m.group('prop').lower(), m.group('val'))
    return DECL.sub(rep, text)


STYLE_BLOCK = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.S | re.I)
STYLE_ATTR = re.compile(r'(\sstyle=")([^"]*)(")', re.I)


def convert_html(text):
    text = STYLE_BLOCK.sub(lambda m: m.group(1) + convert_css(m.group(2)) + m.group(3), text)
    text = STYLE_ATTR.sub(lambda m: m.group(1) + convert_css(m.group(2)) + m.group(3), text)
    return text


def main():
    changed = 0
    skip_dirs = {'archive', 'node_modules', '.git', 'backup', '_backup'}
    for p in sorted(ROOT.rglob('*')):
        if p.suffix not in ('.css', '.html') or skip_dirs & set(p.relative_to(ROOT).parts):
            continue
        if p.name == 'theme.css':
            continue
        s = p.read_text(encoding='utf-8')
        n = convert_css(s) if p.suffix == '.css' else convert_html(s)
        if n != s:
            p.write_text(n, encoding='utf-8')
            changed += 1
    print('files changed:', changed)


if __name__ == '__main__':
    main()
