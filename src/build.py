"""Builds www/index.html, the single file the Android app and any static host load.

Swaps the Google Fonts link in src/index.src.html for bundled fonts (src/fonts)
so the app works fully offline.
"""
import base64, os, re

here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'index.src.html'), encoding='utf-8').read()

FONTS = [
    ('Lexend', 400, 'lexend-latin-400-normal'),
    ('Lexend', 500, 'lexend-latin-500-normal'),
    ('Lexend', 600, 'lexend-latin-600-normal'),
    ('Lexend', 700, 'lexend-latin-700-normal'),
    ('Playfair Display', 700, 'playfair-display-latin-700-normal'),
    ('Playfair Display', 800, 'playfair-display-latin-800-normal'),
    ('Barlow Condensed', 700, 'barlow-condensed-latin-700-normal'),
]

css = []
for family, weight, name in FONTS:
    data = open(os.path.join(here, 'fonts', name + '.woff2'), 'rb').read()
    b64 = base64.b64encode(data).decode()
    css.append("@font-face{font-family:'%s';font-weight:%d;font-style:normal;font-display:swap;"
               "src:url(data:font/woff2;base64,%s) format('woff2')}" % (family, weight, b64))
block = '<style>' + ''.join(css) + '</style>'

pattern = re.compile(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
                     r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">')
assert pattern.search(src), 'font link not found in src/index.src.html'
out = pattern.sub(lambda m: block, src, count=1)

os.makedirs(os.path.join(here, '..', 'www'), exist_ok=True)
with open(os.path.join(here, '..', 'www', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(out)
print('built www/index.html', len(out), 'bytes')
