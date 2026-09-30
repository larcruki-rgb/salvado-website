# -*- coding: utf-8 -*-
"""
奉仕用美少女アンドロイド「ユリ」 原稿 自動公開スクリプト
----------------------------------
_yuri_drafts/ フォルダに置かれた .docx を読み取り、
各話を blog-yuri-NN.html に変換し、目次 blog-yuri.html を作り直して、
GitHub に push する。

使い方：
  1. 詭弁さんの原稿(.docx)を _yuri_drafts/ に入れる
     （ファイル名に「第3話」「第４話」など話数が入っていればOK）
  2. このスクリプトを実行（ユリ_公開.bat をダブルクリック）
"""
import os, sys, re, zipfile, subprocess, webbrowser
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
WNS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

# 原稿フォルダ：_yuri_config.txt があればその1行目のパスを使う
# （Google Drive同期フォルダを指定するため）。無ければローカルの _yuri_drafts。
_CFG = os.path.join(ROOT, '_yuri_config.txt')
if os.path.isfile(_CFG):
    with open(_CFG, 'r', encoding='utf-8') as _f:
        _p = _f.readline().strip().strip('"')
    DRAFTS = _p if _p else os.path.join(ROOT, '_yuri_drafts')
else:
    DRAFTS = os.path.join(ROOT, '_yuri_drafts')

# ---- 話数パース（全角数字・漢数字対応） ----
KANJI = {'〇':0,'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def to_int(s):
    s = s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    if s.isdigit():
        return int(s)
    # 漢数字（十まで＋十N、N十、N十N）
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
    # 「第3話」「第１話」「第十二話」などを拾う
    m = re.search(r'第\s*([0-9０-９〇零一二三四五六七八九十]+)\s*話', filename)
    if m:
        return to_int(m.group(1))
    # ファイル名末尾の数字
    m = re.search(r'(\d+)', filename.translate(str.maketrans('０１２３４５６７８９','0123456789')))
    return int(m.group(1)) if m else None

# ---- docx → 段落リスト ----
def read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    root = ET.fromstring(xml)
    lines = []
    for p in root.iter(WNS+'p'):
        lines.append(''.join(t.text or '' for t in p.iter(WNS+'t')))
    return lines

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ---- 本文 → HTML ----
def body_to_html(lines):
    # 本文開始：最初の ◆◆◆ の次から。無ければ「第n話」行の次から
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

# ---- 1話ページ生成 ----
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

# ---- コメント機能JS（他の作品連載ページと同形式・自前API） ----
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
    """既存の blog-yuri-NN.html をすべて拾って目次を作り直す"""
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
    """blog.html のユリ紹介カードの「第N話まで公開中」を実話数に同期する（カードが無ければ何もしない）"""
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

# ---- blog.html への新規シリーズカード追加（素材が揃ってから自動で一度だけ実行） ----
_CARD_CFG = os.path.join(ROOT, '_yuri_card.txt')

def read_card_cfg():
    """_yuri_card.txt からタグ・あらすじ・表紙ファイル名を読む（コメント行#・空行は無視）。
    3行揃っていない、または表紙画像がまだ img/ に無ければ None を返す（＝まだ準備中）。"""
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
    """blog.html にユリのカードがまだ無ければ新規追加する。素材（_yuri_card.txt＋表紙画像）が
    揃っていない間は何もしない＝今まで通り安全に空振りする。"""
    if not eps:
        return
    path = os.path.join(ROOT, 'blog.html')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if 'href="blog-yuri.html"' in html:
        return  # 既に追加済み
    cfg = read_card_cfg()
    if cfg is None:
        return  # 素材未準備
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

def convert(preview=True):
    """原稿フォルダの docx を HTML 化して目次を作り直す（push はしない）"""
    if not os.path.isdir(DRAFTS):
        print('⚠ 原稿フォルダが見つかりません: %s' % DRAFTS)
        return []
    # ファイル名でソート＝処理順を固定（重複時に出力がブレて無限再公開するのを防ぐ）
    docs = sorted([f for f in os.listdir(DRAFTS) if f.lower().endswith('.docx') and not f.startswith('~$')])
    if not docs:
        print('⚠ 原稿フォルダに .docx がありません。')
        print('  フォルダ: %s' % DRAFTS)
        return []
    converted = []
    skipped = []
    seen_ep = {}
    for f in docs:
        n = episode_no(f)
        if n is None:
            skipped.append(f)
            continue
        if n in seen_ep:
            print('  ⚠ 第%d話が重複しています: 「%s」は無視（先に「%s」を採用）' % (n, f, seen_ep[n]))
            continue
        seen_ep[n] = f
        lines = read_docx(os.path.join(DRAFTS, f))
        body, count = body_to_html(lines)
        out = 'blog-yuri-%02d.html' % n
        with open(os.path.join(ROOT, out), 'w', encoding='utf-8') as fh:
            fh.write(PAGE_TPL.format(n=n, nn='%02d' % n, body=body, comment_js=COMMENT_JS))
        print('  ✓ 第%d話 → %s （%d段落）' % (n, out, count))
        converted.append(n)
    if skipped:
        print('')
        print('  ⚠ 話数が分からずスキップしたファイル:')
        for f in skipped:
            print('     ・%s' % f)
        print('    → ファイル名に「第3話」のように話数を入れてください。')
    if converted:
        eps = rebuild_toc()
        print('  目次更新：第%s話' % '・'.join(str(e) for e in eps))
        if preview:
            # プレビューをブラウザで開く（目次＋変換した各話）
            urls = ['file:///' + os.path.join(ROOT, 'blog-yuri.html').replace('\\', '/')]
            for n in sorted(set(converted)):
                urls.append('file:///' + os.path.join(ROOT, 'blog-yuri-%02d.html' % n).replace('\\', '/'))
            for u in urls:
                webbrowser.open(u)
    return converted

def push():
    """git に commit して push する"""
    st = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT,
                        capture_output=True, text=True, encoding='utf-8')
    if not st.stdout.strip():
        print('変更なし（既に最新）。push は不要です。')
        return
    subprocess.run(['git', 'add', '-A'], cwd=ROOT)
    subprocess.run(['git', 'commit', '-m', 'ユリ 原稿を更新'], cwd=ROOT,
                   capture_output=True, text=True, encoding='utf-8')
    p = subprocess.run(['git', 'push'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if p.returncode == 0:
        print('🚀 公開完了！ GitHub に push しました。')
    else:
        subprocess.run(['git', 'pull', '--rebase'], cwd=ROOT)
        p2 = subprocess.run(['git', 'push'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        print('🚀 公開完了！' if p2.returncode == 0 else ('⚠ push 失敗:\n' + p.stderr + p2.stderr))

def notify(title, message):
    """Windowsのバルーン通知（自動公開を透に知らせる）"""
    try:
        ps = (
            'Add-Type -AssemblyName System.Windows.Forms;'
            '$n=New-Object System.Windows.Forms.NotifyIcon;'
            '$n.Icon=[System.Drawing.SystemIcons]::Information;'
            '$n.Visible=$true;'
            '$n.ShowBalloonTip(8000,' + repr(title).replace("'", "'") + ',' + repr(message) + ',[System.Windows.Forms.ToolTipIcon]::Info);'
            'Start-Sleep -Seconds 9;$n.Dispose()'
        )
        subprocess.Popen(['powershell', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', ps])
    except Exception:
        pass

def log(msg):
    import datetime  # noqa
    # Date.now 系は避け、ファイル追記のみ（タイムスタンプはgitログで追える）
    try:
        with open(os.path.join(ROOT, '_yuri_auto.log'), 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass

def auto():
    """完全自動モード：プレビューなしで変換し、ユリ関連ファイルだけ push する（ログイン時起動用）。
    ※ 透が別の作業を編集中でも巻き込まないよう、対象は blog-yuri*.html のみに限定。"""
    converted = convert(preview=False)
    # ユリ関連ファイルだけに変更があるか確認
    targets = ['blog-yuri.html', 'blog.html'] + ['blog-yuri-%02d.html' % n for n in sorted(set(converted))]
    # 既存の全 blog-yuri-NN.html も対象に含める（削除・他話の変化も拾う）
    for f in os.listdir(ROOT):
        if re.match(r'^blog-yuri-\d+\.html$', f) and f not in targets:
            targets.append(f)
    st = subprocess.run(['git', 'status', '--porcelain', '--'] + targets, cwd=ROOT,
                        capture_output=True, text=True, encoding='utf-8')
    if not st.stdout.strip():
        return  # ユリ関連に変更なし → 何もしない（他の作業には触れない）
    subprocess.run(['git', 'add', '--'] + targets, cwd=ROOT)
    subprocess.run(['git', 'commit', '-m', 'ユリ 原稿を自動更新', '--'] + targets, cwd=ROOT,
                   capture_output=True, text=True, encoding='utf-8')
    p = subprocess.run(['git', 'push'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        subprocess.run(['git', 'pull', '--rebase'], cwd=ROOT)
        p = subprocess.run(['git', 'push'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if p.returncode == 0:
        eps = '・'.join('第%d話' % n for n in sorted(set(converted))) if converted else '記事'
        log('[自動公開] %s を公開' % eps)
        notify('ユリ 自動公開', '%s を公開しました' % eps)
    else:
        log('[自動公開エラー] push 失敗')
        notify('ユリ 公開エラー', 'pushに失敗しました。手動で確認してください。')

if __name__ == '__main__':
    if '--auto' in sys.argv:
        auto()
    elif '--push' in sys.argv:
        push()
    else:
        convert()
