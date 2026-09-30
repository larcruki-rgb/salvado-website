# -*- coding: utf-8 -*-
"""
奉仕用美少女アンドロイド「ユリ」 原稿 自動公開スクリプト（クラウド版）
----------------------------------
透のPCを経由せず、Google Drive上の「ユリ」フォルダをDrive API経由で直接読み、
各話を blog-yuri-NN.html に変換、目次 blog-yuri.html とblog.htmlのシリーズカードを
作り直す（GitHub Actionsから呼ばれる。push はワークフロー側のgitステップで行う）。

必要な環境変数：
  YURI_GDRIVE_SA_KEY     … サービスアカウントの鍵（JSON文字列そのもの）
  YURI_GDRIVE_FOLDER_ID  … 「ユリ」フォルダのID
"""
import os, sys, re, io, json, zipfile
import xml.etree.ElementTree as ET
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GARequest

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WNS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# ---- 話数パース（全角数字・漢数字対応） ----
KANJI = {'〇':0,'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def to_int(s):
    s = s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    if s.isdigit():
        return int(s)
    if s == '十': return 10
    m = re.match(r'^(.?)十(.?)$', s)
    if m and ('十' in s):
        tens = KANJI.get(m.group(1), 1) if m.group(1) else 1
        ones = KANJI.get(m.group(2), 0) if m.group(2) else 0
        return tens*10 + ones
    if len(s) == 1 and s in KANJI:
        return KANJI[s]
    return None

def episode_no(filename):
    m = re.search(r'第\s*([0-9０-９〇零一二三四五六七八九十]+)\s*話', filename)
    if m:
        return to_int(m.group(1))
    m = re.search(r'(\d+)', filename.translate(str.maketrans('０１２３４５６７８９','0123456789')))
    return int(m.group(1)) if m else None

# ---- docx(バイト列) → 段落リスト ----
def read_docx_bytes(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    root = ET.fromstring(xml)
    lines = []
    for p in root.iter(WNS+'p'):
        lines.append(''.join(t.text or '' for t in p.iter(WNS+'t')))
    return lines

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def body_to_html(lines):
    start = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s in ('◆◆◆', '◆◆'):
            start = i + 1
            break
        if i > 0 and re.search(r'第\s*[0-9０-９〇零一二三四五六七八九十]+\s*話', s) and len(s) < 12:
            start = i + 1
    blocks = []
    for line in lines[start:]:
        s = line.rstrip()
        st = s.strip()
        if not st:
            continue
        if st in ('◆◆◆', '◆◆'):
            blocks.append('<p style="text-align:center;color:#888;margin:32px 0;letter-spacing:1em;">◆ ◆ ◆</p>')
        else:
            blocks.append('<p>%s</p>' % esc(s))
    return '\n      '.join(blocks), len(blocks)

PAGE_TPL = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<script>(function(){{var w=window.innerWidth||document.documentElement.clientWidth;var h=window.innerHeight||document.documentElement.clientHeight;if(w>=768&&w<1400&&w>h){{document.write('<meta name="viewport" content="width=1280, initial-scale='+(w/1280).toFixed(3)+', maximum-scale=2.0">');}}else{{document.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">');}}}})();</script>
<meta name="description" content="奉仕用美少女アンドロイド「ユリ」 第{n}話（作：青春詭弁）— サルベド漫画">
<title>奉仕用美少女アンドロイド「ユリ」 第{n}話 — サルベド漫画</title>
<link rel="stylesheet" href="style.css?v=11">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4654447730346692" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E6JYMJBJDL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","G-E6JYMJBJDL");</script>
</head>
<body>

<div class="a7-topbar">
  <a href="index.html" class="a7-logo"><img src="img/salvado-logo.png" alt="サルベド漫画"></a>
  <button class="a7-hamburger" aria-label="メニュー" onclick="this.classList.toggle('open');document.querySelector('.a7-nav').classList.toggle('open');"><span></span><span></span><span></span></button>
  <nav class="a7-nav">
    <a href="index.html">TOP<span>ホーム</span></a>
    <a href="about.html">ABOUT<span>紹介</span></a>
    <a href="videos.html">VIDEOS<span>動画</span></a>
    <a href="blog.html" class="active">SERIES<span>作品</span></a>
    <a href="gallery.html">GALLERY<span>ギャラリー</span></a>
    <a href="game.html">GAME<span>ゲーム</span></a>
    <a href="news.html">NEWS<span>お知らせ</span></a>
  </nav>
</div>

<div class="main-wrap">
  <div class="page-content">
    <p style="margin-bottom:8px;"><a href="blog-yuri.html">&larr; 目次に戻る</a></p>
    <h1>奉仕用美少女アンドロイド「ユリ」 第{n}話</h1>
    <p class="blog-meta" style="margin-bottom:24px;color:#666;">作：青春詭弁</p>

    <article class="blog-article-card" id="article-{nn}">
      {body}

      <div class="comment-section" data-page="yuri-{nn}">
        <h4>この記事へのコメント</h4>
        <div class="comment-list"></div>
        <div class="comment-form">
          <input class="comment-name-input" placeholder="名前（省略可）" maxlength="30">
          <textarea class="comment-text-input" placeholder="コメントを書く..." maxlength="1000" rows="3"></textarea>
          <button class="comment-submit">送信</button>
        </div>
      </div>
    </article>

    <p style="margin-top:32px;"><a href="blog-yuri.html">&larr; 目次に戻る</a></p>
  </div>

  <a href="#" class="scroll-top-btn" id="scrollTopBtn" aria-label="ページ上部へ" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;">
    <img src="img/scroll-top.png" alt="">
    <span>TOP</span>
  </a>
  <script>(function(){{var b=document.getElementById('scrollTopBtn');window.addEventListener('scroll',function(){{if(window.scrollY>500){{b.classList.add('show');}}else{{b.classList.remove('show');}}}});}})();</script>

  <footer>
    <div class="footer-inner">
      <div class="footer-links">
        <a href="contact.html">お問い合わせ</a>
        <a href="privacy.html">プライバシーポリシー</a>
        <a href="terms.html">利用規約</a>
        <a href="company.html">会社情報</a>
      </div>
      <p class="footer-copy">&copy; 2026 サルベド漫画 All Rights Reserved.</p>
      <p class="footer-notice">このホームページに掲載されている一切の文書・図版・写真等を、手段や形態を問わず複製、転載することを禁じます。</p>
    </div>
  </footer>
</div>

{comment_js}
</body>
</html>
'''

COMMENT_JS = '''<script>
var COMMENT_API = 'https://game.sarubedo.jp/comments';

function renderComments(el, comments) {
  if (!comments.length) { el.innerHTML = '<p style="color:#666;font-size:14px;">まだコメントはありません</p>'; return; }
  el.innerHTML = comments.map(function(c) {
    var d = new Date(c.date);
    var ds = d.getFullYear() + '/' + (d.getMonth()+1) + '/' + d.getDate() + ' ' + d.getHours() + ':' + ('0'+d.getMinutes()).slice(-2);
    var escaped = c.text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');
    var nameEsc = c.name.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    return '<div class="comment-item"><div class="comment-header"><span class="comment-name">' + nameEsc + '</span><span class="comment-date">' + ds + '</span></div><div class="comment-body">' + escaped + '</div></div>';
  }).join('');
}

function loadComments(section) {
  var pageId = section.getAttribute('data-page');
  var listEl = section.querySelector('.comment-list');
  fetch(COMMENT_API + '?page=' + pageId).then(function(r) { return r.json(); }).then(function(comments) {
    renderComments(listEl, comments);
  }).catch(function() {
    listEl.innerHTML = '<p style="color:#666;font-size:14px;">コメントの読み込みに失敗しました</p>';
  });
}

function postComment(section) {
  var pageId = section.getAttribute('data-page');
  var name = section.querySelector('.comment-name-input').value;
  var text = section.querySelector('.comment-text-input').value;
  if (!text.trim()) return;
  fetch(COMMENT_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ page: pageId, name: name, text: text })
  }).then(function(r) {
    if (r.status === 429) { alert('連投制限中です。30秒後にお試しください。'); return; }
    return r.json();
  }).then(function(data) {
    if (!data) return;
    section.querySelector('.comment-text-input').value = '';
    loadComments(section);
  });
}

document.querySelectorAll('.comment-section').forEach(function(section) {
  loadComments(section);
  section.querySelector('.comment-submit').addEventListener('click', function() {
    postComment(section);
  });
});
</script>'''

def rebuild_toc():
    eps = []
    for f in os.listdir(ROOT):
        m = re.match(r'^blog-yuri-(\d+)\.html$', f)
        if m:
            eps.append(int(m.group(1)))
    eps.sort()
    items = []
    for n in eps:
        items.append(
            '        <li class="ep-item"><a href="blog-yuri-%02d.html">\n'
            '          <div class="ep-row"><span class="ep-num">EP.%02d</span>'
            '<span class="ep-title">第%d話</span><span class="ep-arrow">→</span></div>\n'
            '        </a></li>' % (n, n, n))
    toc = '\n'.join(items)
    idx = os.path.join(ROOT, 'blog-yuri.html')
    with open(idx, 'r', encoding='utf-8') as f:
        html = f.read()
    new = re.sub(r'(<ul class="ep-list">)(.*?)(</ul>)',
                 r'\1\n' + toc + r'\n      \3', html, flags=re.DOTALL)
    with open(idx, 'w', encoding='utf-8') as f:
        f.write(new)
    insert_series_card(eps)
    update_series_card(eps)
    return eps

def update_series_card(eps):
    if not eps:
        return
    latest = max(eps)
    path = os.path.join(ROOT, 'blog.html')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    new = re.sub(r'(href="blog-yuri\.html".*?第)\d+(話まで公開中)',
                 r'\g<1>%d\g<2>' % latest, html, count=1, flags=re.DOTALL)
    if new != html:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)

_CARD_CFG = os.path.join(ROOT, '_yuri_card.txt')

def read_card_cfg():
    if not os.path.isfile(_CARD_CFG):
        return None
    with open(_CARD_CFG, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    if len(lines) < 3:
        return None
    tag, blurb, cover = lines[0], lines[1], lines[2]
    if not os.path.isfile(os.path.join(ROOT, 'img', cover)):
        return None
    return tag, blurb, cover

def insert_series_card(eps):
    if not eps:
        return
    path = os.path.join(ROOT, 'blog.html')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if 'href="blog-yuri.html"' in html:
        return
    cfg = read_card_cfg()
    if cfg is None:
        return
    tag, blurb, cover = cfg
    latest = max(eps)
    nums = [int(n) for n in re.findall(r'<span class="blog-mag-num">(\d+)</span>', html)]
    num = (max(nums) + 1) if nums else 1
    entry = ('        <a class="blog-mag-entry" href="blog-yuri.html">'
             '<div class="blog-mag-thumb"><span class="blog-mag-num">%02d</span>'
             '<img src="img/%s" alt=""></div>'
             '<span class="blog-mag-tag">%s</span><h3>奉仕用美少女アンドロイド「ユリ」</h3>'
             '<p>%s</p>'
             '<div class="blog-mag-meta">第%d話まで公開中<span class="blog-mag-cta">読みに行く →</span></div></a>'
             % (num, cover, tag, blurb, latest))
    lines = html.split('\n')
    last_entry_i = max(i for i, l in enumerate(lines) if 'class="blog-mag-entry"' in l)
    lines.insert(last_entry_i + 1, entry)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('  ✓ blog.html にシリーズカードを新規追加しました。')

# ---- Drive API ----
def drive_headers():
    info = json.loads(os.environ['YURI_GDRIVE_SA_KEY'])
    creds = service_account.Credentials.from_service_account_info(info, scopes=DRIVE_SCOPES)
    creds.refresh(GARequest())
    return {'Authorization': 'Bearer %s' % creds.token}

def list_drafts(headers, folder_id):
    r = requests.get(
        'https://www.googleapis.com/drive/v3/files',
        headers=headers,
        params={'q': "'%s' in parents and trashed=false" % folder_id,
                'fields': 'files(id,name,mimeType)', 'pageSize': 1000},
        timeout=30)
    r.raise_for_status()
    files = r.json().get('files', [])
    return [f for f in files if f['name'].lower().endswith('.docx') and not f['name'].startswith('~$')]

def download(headers, file_id):
    r = requests.get('https://www.googleapis.com/drive/v3/files/%s' % file_id,
                      headers=headers, params={'alt': 'media'}, timeout=60)
    r.raise_for_status()
    return r.content

def main():
    folder_id = os.environ['YURI_GDRIVE_FOLDER_ID']
    headers = drive_headers()
    docs = sorted(list_drafts(headers, folder_id), key=lambda f: f['name'])
    if not docs:
        print('⚠ 原稿フォルダに .docx がありません。')
        return
    converted = []
    skipped = []
    seen_ep = {}
    for f in docs:
        n = episode_no(f['name'])
        if n is None:
            skipped.append(f['name'])
            continue
        if n in seen_ep:
            print('  ⚠ 第%d話が重複しています: 「%s」は無視（先に「%s」を採用）' % (n, f['name'], seen_ep[n]))
            continue
        seen_ep[n] = f['name']
        data = download(headers, f['id'])
        lines = read_docx_bytes(data)
        body, count = body_to_html(lines)
        out = 'blog-yuri-%02d.html' % n
        with open(os.path.join(ROOT, out), 'w', encoding='utf-8') as fh:
            fh.write(PAGE_TPL.format(n=n, nn='%02d' % n, body=body, comment_js=COMMENT_JS))
        print('  ✓ 第%d話 → %s （%d段落）' % (n, out, count))
        converted.append(n)
    if skipped:
        print('  ⚠ 話数が分からずスキップ: %s' % '、'.join(skipped))
    if converted:
        eps = rebuild_toc()
        print('  目次更新：第%s話' % '・'.join(str(e) for e in eps))

if __name__ == '__main__':
    main()
