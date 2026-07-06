# -*- coding: utf-8 -*-
# 読み物記事ページ + 一覧ページ(articles.html) を生成する
# 使い方: python3 build_articles.py  （salvado-website 直下で実行）
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from articles_data import ARTICLES

NAV = '''<!-- A7 トップバー（ホーム画面と同じ） -->
<div class="a7-topbar">
  <a href="index.html" class="a7-logo"><img src="img/salvado-logo.png" alt="サルベド漫画"></a>
  <button class="a7-hamburger" aria-label="メニュー" onclick="this.classList.toggle('open');document.querySelector('.a7-nav').classList.toggle('open');"><span></span><span></span><span></span></button>
  <nav class="a7-nav">
    <a href="index.html">TOP<span>ホーム</span></a>
    <a href="about.html">ABOUT<span>紹介</span></a>
    <a href="videos.html">VIDEOS<span>動画</span></a>
    <a href="blog.html">SERIES<span>作品</span></a>
    <a href="gallery.html">GALLERY<span>ギャラリー</span></a>
    <a href="game.html">GAME<span>ゲーム</span></a>
    <a href="news.html">NEWS<span>お知らせ</span></a>
  </nav>
</div>'''

FOOTER = '''<footer>
    <div class="footer-inner">
      <div class="footer-links">
        <a href="articles.html">読み物</a>
        <a href="goods.html">グッズ</a>
        <a href="ebooks.html">電子書籍</a>
        <a href="contact.html">お問い合わせ</a>
        <a href="privacy.html">プライバシーポリシー</a>
        <a href="terms.html">利用規約</a>
        <a href="company.html">会社情報</a>
      </div>
      <p class="footer-copy">&copy; 2026 サルベド漫画 All Rights Reserved.</p>
      <p class="footer-notice">このホームページに掲載されている一切の文書・図版・写真等を、手段や形態を問わず複製、転載することを禁じます。</p>
    </div>
  </footer>'''

SCROLLTOP = '''<a href="#" class="scroll-top-btn stb-emblem" id="scrollTopBtn" aria-label="ページ上部へ" onclick="window.scrollTo({top:0,behavior:'smooth'});return false;">
    <svg class="stb-ring" viewBox="0 0 100 100" aria-hidden="true"><defs><path id="stbPath" d="M50,50 m-46,0 a46,46 0 1,0 92,0 a46,46 0 1,0 -92,0"/></defs><text><textPath href="#stbPath">★ PAGE TOP ★ PAGE TOP </textPath></text></svg>
    <span class="stb-core"><img src="img/scroll-top.png" alt=""></span>
  </a>
  <script>(function(){var b=document.getElementById('scrollTopBtn');window.addEventListener('scroll',function(){if(window.scrollY>500){b.classList.add('show');}else{b.classList.remove('show');}});})();</script>'''

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

ARTICLE_CSS = '''<style>
.article-tag{display:inline-block;font-size:11px;font-weight:800;background:#6FDFD6;color:#0a3d3a;padding:3px 12px;border-radius:3px;letter-spacing:2px;margin-bottom:10px;}
.blog-article-card h3{margin-top:34px;}
.article-nav-links{display:flex;justify-content:space-between;gap:12px;margin:26px 0 10px;flex-wrap:wrap;}
.article-nav-links a{font-size:14px;}
</style>'''

PAGE_TMPL = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title} — サルベド漫画</title>
<link rel="stylesheet" href="style.css?v=12">
{css}
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4654447730346692" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E6JYMJBJDL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","G-E6JYMJBJDL");</script>
</head>
<body>

{nav}

<div class="main-wrap">
  <div class="page-content">
    <p style="margin-bottom:8px;"><a href="articles.html">&larr; 読み物一覧に戻る</a></p>
    <h1>{h1}</h1>
    <p class="blog-meta">サルベド漫画 読み物</p>

    <article class="blog-article-card" id="article-{aid}">
      <span class="article-tag">{tag}</span>
      <h2>{h1}</h2>
{body}
      <div class="comment-section" data-page="article-{aid}">
        <h4>この記事へのコメント</h4>
        <div class="comment-list"></div>
        <div class="comment-form">
          <input class="comment-name-input" placeholder="名前（省略可）" maxlength="30">
          <textarea class="comment-text-input" placeholder="コメントを書く..." maxlength="1000" rows="3"></textarea>
          <button class="comment-submit">送信</button>
        </div>
      </div>
    </article>

    <div class="article-nav-links">
      {prev}
      <a href="articles.html">読み物一覧に戻る</a>
      {next}
    </div>

    <p style="margin-top:20px;"><a href="index.html">&larr; トップページに戻る</a></p>
  </div>

  {scrolltop}

  {footer}
</div>

{comment_js}
</body>
</html>
'''

LIST_CSS = '''<style>
.articles-lead{max-width:820px;margin:0 auto 40px;font-size:14px;line-height:2;color:#444;text-align:center;}
.articles-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;max-width:1000px;margin:0 auto;}
.article-card{background:#f7fbfb;border:1px solid #e3f1f0;border-radius:12px;padding:22px 24px;box-shadow:0 4px 14px rgba(0,0,0,0.04);display:flex;flex-direction:column;text-decoration:none;color:inherit;transition:transform 0.2s,box-shadow 0.2s;}
.article-card:hover{transform:translateY(-3px);box-shadow:0 10px 24px rgba(0,0,0,0.08);}
.article-card .article-tag{display:inline-block;font-size:11px;font-weight:800;background:#6FDFD6;color:#0a3d3a;padding:3px 12px;border-radius:3px;letter-spacing:2px;margin-bottom:10px;align-self:flex-start;}
.article-card h2{font-size:16px;color:#0a3d3a;margin:0 0 10px;line-height:1.6;}
.article-card p{font-size:13px;line-height:1.9;color:#444;margin:0;flex:1;}
.article-card .more{font-size:12px;color:#0a8f86;font-weight:700;margin-top:14px;}
@media(max-width:760px){.articles-grid{grid-template-columns:1fr;gap:16px;}}
</style>'''

LIST_TMPL = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="サルベド漫画の読み物一覧 — 作品ガイド、制作の裏側、カードゲーム攻略など、動画とはひと味違うコンテンツをお届けします。">
<title>読み物 — サルベド漫画</title>
<link rel="stylesheet" href="style.css?v=12">
{css}
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4654447730346692" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E6JYMJBJDL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","G-E6JYMJBJDL");</script>
</head>
<body>

{nav}

<div class="main-wrap">
  <div class="page-content">
    <h1>読み物</h1>
    <p class="articles-lead">作品の楽しみ方ガイド、制作の裏側、カードゲームの攻略まで。動画とはひと味違う、サルベド漫画の「読む」コンテンツを集めました。初めての方は「公式サイトの歩き方」から、動画づくりの舞台裏が気になる方は「制作裏話」から読むのがおすすめです。どの記事も途中に予備知識は必要ないので、気になったものからどうぞ。</p>

    <div class="articles-grid">
{cards}
    </div>
  </div>

  {scrolltop}

  {footer}
</div>
</body>
</html>
'''

# 公開しない記事の id（データは articles_data.py に残したまま、生成物だけ外す）
# 後で公開するときは、この集合から id を外して再ビルドするだけ
EXCLUDE_IDS = set()

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    articles = [a for a in ARTICLES if a["id"] not in EXCLUDE_IDS]
    # 記事ページ
    for i, a in enumerate(articles):
        prev_a = articles[i-1] if i > 0 else None
        next_a = articles[i+1] if i < len(articles)-1 else None
        prev = '<a href="%s">&larr; %s</a>' % (prev_a["file"], prev_a["tag"]) if prev_a else '<span></span>'
        nxt = '<a href="%s">%s &rarr;</a>' % (next_a["file"], next_a["tag"]) if next_a else '<span></span>'
        html = PAGE_TMPL.format(
            desc=a["desc"], title=a["title"], h1=a["title"], aid=a["id"], tag=a["tag"],
            body=a["body"], css=ARTICLE_CSS, nav=NAV, footer=FOOTER,
            scrolltop=SCROLLTOP, comment_js=COMMENT_JS, prev=prev, next=nxt)
        open(a["file"], "w", encoding="utf-8").write(html)
        print("wrote", a["file"])
    # 除外記事の生成物が残っていれば削除
    for a in ARTICLES:
        if a["id"] in EXCLUDE_IDS and os.path.exists(a["file"]):
            os.remove(a["file"])
            print("removed (excluded)", a["file"])
    # 一覧ページ
    cards = []
    for a in articles:
        cards.append('''      <a class="article-card" href="{f}">
        <span class="article-tag">{tag}</span>
        <h2>{t}</h2>
        <p>{lead}</p>
        <span class="more">読む →</span>
      </a>'''.format(f=a["file"], tag=a["tag"], t=a["title"], lead=a["lead"]))
    html = LIST_TMPL.format(css=LIST_CSS, nav=NAV, footer=FOOTER, scrolltop=SCROLLTOP, cards="\n".join(cards))
    open("articles.html", "w", encoding="utf-8").write(html)
    print("wrote articles.html")
    print("done:", len(articles), "articles (excluded:", len(EXCLUDE_IDS), ")")

if __name__ == "__main__":
    main()
