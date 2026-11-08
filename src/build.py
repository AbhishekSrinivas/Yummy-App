"""Builds the Android web layer into www/.

  www/index.html  small launcher: opens a downloaded update if there is one, else app.html
  www/app.html    the app, with bundled fonts and full-size photo files
  www/img/        full-resolution stock and recipe photos (from src/images); img/m/ holds smaller copies for lists
  www/version.json  build number, uploaded with every release so installed apps can find updates

src/index.src.html is also what gets published as the single-file Claude artifact,
so it still carries small inline photos. Here those are swapped for the files in src/images.
"""
import base64, json, os, re, shutil, sys, time

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..')
www = os.path.join(root, 'www')
build = int(os.environ.get('BUILD_ID') or time.time())

src = open(os.path.join(here, 'index.src.html'), encoding='utf-8').read()

# 1. bundled fonts instead of the Google Fonts link
FONTS = [
    ('Lexend', 400, 'lexend-latin-400-normal'),
    ('Lexend', 500, 'lexend-latin-500-normal'),
    ('Lexend', 600, 'lexend-latin-600-normal'),
    ('Lexend', 700, 'lexend-latin-700-normal'),
    ('Playfair Display', 700, 'playfair-display-latin-700-normal'),
    ('Playfair Display', 800, 'playfair-display-latin-800-normal'),
    ('Barlow Condensed', 700, 'barlow-condensed-latin-700-normal'),
]
css = ''
for family, weight, name in FONTS:
    data = open(os.path.join(here, 'fonts', name + '.woff2'), 'rb').read()
    css += ("@font-face{font-family:'%s';font-weight:%d;font-style:normal;font-display:swap;"
            "src:url(data:font/woff2;base64,%s) format('woff2')}" % (family, weight, base64.b64encode(data).decode()))
link = re.compile(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
                  r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">')
assert link.search(src), 'font link not found'
src = link.sub(lambda m: '<style>' + css + '</style>', src, count=1)

# 2. photos: inline base85 tiles become files in img/
a = src.index('/*LIB-START*/')
b = src.index('/*LIB-END*/')
blk = src[a + len('/*LIB-START*/'):b]
i = blk.index('[')
lib, end = json.JSONDecoder().raw_decode(blk[i:])
tail = blk[i + end:]
os.makedirs(os.path.join(www, 'img', 'm'), exist_ok=True)
for t in lib:
    f = os.path.join(here, 'images', t['id'] + '.jpg')
    assert os.path.exists(f), 'missing photo ' + t['id']
    shutil.copyfile(f, os.path.join(www, 'img', t['id'] + '.jpg'))
    shutil.copyfile(os.path.join(here, 'images', 'm', t['id'] + '.jpg'), os.path.join(www, 'img', 'm', t['id'] + '.jpg'))
    t['s'] = 'img/' + t['id'] + '.jpg'
    t['m'] = 'img/m/' + t['id'] + '.jpg'
    t.pop('z', None)
src = src[:a] + '/*LIB-START*/const LIB=' + json.dumps(lib, ensure_ascii=False, separators=(',', ':')) + tail + src[b:]
dec = re.compile(r'\(function\(\)\{const A="ABCDEF[^\n]*?URL\.createObjectURL\(new Blob\(\[a\.subarray\(0,z\)\][^\n]*?\}\}\)\}\}\)\(\);')
assert dec.search(src), 'photo decoder not found'
src = dec.sub('', src, count=1)

# 3. build number for the update check
src = src.replace('<title>Yummy</title>', '<title>Yummy</title><script>window.YUMMY_BUILD=%d</script>' % build, 1)
open(os.path.join(www, 'app.html'), 'w', encoding='utf-8').write(src)

# 4. launcher
launcher = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Yummy</title>
<style>html,body{margin:0;background:#F6F3EC}@media(prefers-color-scheme:dark){html,body{background:#000}}</style>
</head><body><script>
(function(){
var B=%d;
function run(){location.replace('app.html')}
try{
  var q=indexedDB.open('yummy-ota',1);
  q.onupgradeneeded=function(){q.result.createObjectStore('f')};
  q.onerror=run;
  q.onsuccess=function(){try{
    var g=q.result.transaction('f').objectStore('f').get('app');
    g.onerror=run;
    g.onsuccess=function(){
      var a=g.result;
      if(!a||!a.html||a.build<=B){run();return}
      var tried=localStorage.getItem('yummy-ota-try'),ok=localStorage.getItem('yummy-ota-ok');
      if(tried==String(a.build)&&ok!=String(a.build)){
        try{q.result.transaction('f','readwrite').objectStore('f').delete('app')}catch(e){}
        run();return;
      }
      localStorage.setItem('yummy-ota-try',String(a.build));
      document.open();document.write(a.html);document.close();
    };
  }catch(e){run()}};
}catch(e){run()}
})();
</script></body></html>
''' % build
open(os.path.join(www, 'index.html'), 'w', encoding='utf-8').write(launcher)

open(os.path.join(www, 'version.json'), 'w').write(json.dumps({'build': build}))
print('built build', build, 'app.html', len(src), 'bytes,', len(lib), 'photos')
