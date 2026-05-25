# サルベド公式HP 開発レシピ

## 概要
YouTube漫画チャンネル「サルベド漫画」の公式ホームページ。静的サイト。

## 本番環境
- **URL**: https://sarubedo.jp
- **ホスティング**: GitHub Pages（リポジトリ直下にCNAME）
- **独自ドメイン**: sarubedo.jp
- **GA4測定ID**: G-E6JYMJBJDL

## ファイル構成
```
website/
├── CNAME              # 独自ドメイン設定（sarubedo.jp）
├── index.html         # トップページ（最新動画・特集・お知らせ）
├── about.html         # チャンネル紹介（3チャンネル解説）
├── videos.html        # 動画一覧
├── game.html          # カードゲーム紹介
├── ebooks.html        # 電子書籍一覧
├── goods.html         # グッズ（BOOTHへのリンク）
├── blog.html          # ブログ記事一覧
├── blog-sakamachi.html # ブログ記事：作画工程解説
├── news.html          # お知らせ
├── privacy.html       # プライバシーポリシー
├── style.css          # 全ページ共通スタイル
├── img-card.png       # カードゲーム特集サムネ
├── img-goods.png      # グッズ特集サムネ
└── img/blog/          # ブログ用画像
```

## 技術スタック
- 素のHTML/CSS/JS（フレームワークなし）
- サーバーサイド処理なし（完全静的）
- YouTube Data API不使用（RSSフィード経由で最新動画取得）

## デザインテーマ
- **ダークテーマ**: 背景 `#0d0d1a`、テキスト `#e0d8c0`、アクセント `#c0a860`（金色系）
- **フォント**: Hiragino Kaku Gothic Pro / Yu Gothic / Noto Sans JP
- **左サイドバー**: PC固定表示、スマホはハンバーガーメニューで開閉
- **カードUI**: 角丸 `border-radius: 8-12px`、ボーダー `#2a2a3a`、背景 `#1a1a2e`

## レイアウト構造
```
┌──────────┬──────────────────────┐
│ サイドバー │  メインコンテンツ       │
│ (220px固定) │                      │
│          │  ヒーロー（トップのみ）   │
│ ロゴ      │  セクション（max-width:1000px） │
│ ナビ      │  フッター              │
│          │                      │
└──────────┴──────────────────────┘
```

### スマホ（700px以下）
- サイドバー非表示（ハンバーガーで開閉）
- main-wrapが全幅
- グリッドが1カラムに

## 各ページの役割

### index.html（トップ）
- ヒーローセクション：タイトルのみ（シンプル）
- 最新動画：3チャンネル（本家・Emotional・Fantasy）のRSSから最新1本ずつ自動取得
  - 取得先: `https://game.sarubedo.jp/yt-feed?id={channelId}`（TCGサーバーにプロキシあり）
  - リトライ3回、失敗時は「タップして再読み込み」表示
- 特集カード3枚：グッズ（BOOTH）・カードゲーム・電子書籍
- お知らせ一覧（最新数件）

### about.html（チャンネル紹介）
- サルベド漫画（本家）/ Emotional / Fantasy の3チャンネル解説
- 各チャンネルの人気動画embed

### videos.html（動画一覧）
- チャンネル別にYouTube埋め込み

### game.html（カードゲーム）
- TCGの紹介・遊び方・リンク
- game.sarubedo.jpへの誘導

### ebooks.html（電子書籍）
- Amazon Kindleの各巻リンク+表紙画像

### blog.html / blog-sakamachi.html
- ブログ記事一覧 + 個別記事
- 坂街透の作画解説記事（画像13枚付き）
- コメント機能UI（フロントのみ、バックエンド未実装）

### goods.html
- BOOTH（sarubedo.booth.pm）へのリンク

### news.html
- お知らせ一覧（日付+タグ+リンク）

### privacy.html
- プライバシーポリシー（GA4・YouTube埋め込み等の説明）

## 外部サービス連携
| サービス | 用途 |
|---|---|
| GitHub Pages | ホスティング |
| Google Analytics 4 | アクセス解析（G-E6JYMJBJDL） |
| YouTube RSS | 最新動画取得（game.sarubedo.jpプロキシ経由） |
| BOOTH | グッズ販売（外部リンク） |
| Amazon Kindle | 電子書籍（外部リンク） |

## CSS命名規則
- BEM等のルールなし。機能ベースのクラス名
- 主要クラス：
  - `.sidebar` / `.main-wrap` — レイアウト
  - `.hero` / `.section` / `.section-dark` — セクション
  - `.video-card` / `.feature-card` / `.blog-entry` — カード型UI
  - `.news-list` / `.news-date` / `.news-tag` — お知らせ
  - `.page-content` — サブページ共通コンテンツ枠
  - `.channel-card` — チャンネル紹介カード

## 編集時の注意点
- **全ページで同じsidebar HTML**を共有（テンプレートエンジンなし、各HTMLに直書き）
  - ナビ項目を変更する場合は全HTMLを一括更新する必要がある
- **style.cssは全ページ共通**。ページ固有スタイルはない
- **最新動画の取得はTCGサーバー（game.sarubedo.jp）に依存**。サーバーが落ちてると動画が表示されない
- img-card.png、img-goods.pngはルート直下（img/ではない）
