# -*- coding: utf-8 -*-
"""
奉仕用美少女アンドロイド「ユリ」 原稿フォルダ 常駐ウォッチャー
--------------------------------------
Google Drive の原稿フォルダを静かに見張り、
docx に「新着・更新・削除」があった時だけ自動公開（_yuri_publish.py --auto）を走らせる。

・普段はほぼCPUを使わず待機（60秒ごとに状態を確認するだけ）
・変化が無ければ何もしない＝無駄なコミットは出ない
・PCログイン時に自動起動（スタートアップフォルダのショートカットで設定）

手動で止めたい時：スタートアップフォルダの「ユリ_ウォッチャー」ショートカットを削除、
または現在動いている pythonw プロセスを終了。
"""
import os, sys, time, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLISH = os.path.join(ROOT, '_yuri_publish.py')

# 原稿フォルダ（_yuri_config.txt があればそれを使う）
_CFG = os.path.join(ROOT, '_yuri_config.txt')
if os.path.isfile(_CFG):
    with open(_CFG, 'r', encoding='utf-8') as _f:
        _p = _f.readline().strip().strip('"')
    DRAFTS = _p if _p else os.path.join(ROOT, '_yuri_drafts')
else:
    DRAFTS = os.path.join(ROOT, '_yuri_drafts')

CHECK_INTERVAL = 60   # 何秒ごとに状態を確認するか
SETTLE_WAIT = 8       # 変化検知後、同期が落ち着くまで待つ秒数

def signature():
    """原稿フォルダ内 docx の状態スナップショット（名前・サイズ・更新時刻）"""
    sig = {}
    try:
        for f in os.listdir(DRAFTS):
            if f.lower().endswith('.docx') and not f.startswith('~$'):
                p = os.path.join(DRAFTS, f)
                try:
                    st = os.stat(p)
                    sig[f] = (st.st_size, int(st.st_mtime))
                except OSError:
                    pass
    except OSError:
        pass
    return sig

def run_publish():
    """自動公開を実行（変更が無ければ publish 側が何もしない）"""
    try:
        subprocess.run([sys.executable, PUBLISH, '--auto'], cwd=ROOT,
                       capture_output=True, text=True, encoding='utf-8', timeout=300)
    except Exception:
        pass

def main():
    # 起動時に一度チェック（PCオフ中にアップされた分を拾う）
    run_publish()
    last = signature()
    while True:
        time.sleep(CHECK_INTERVAL)
        now = signature()
        if now != last:
            # 変化を検知 → 同期が落ち着くまで少し待ってから再確認
            time.sleep(SETTLE_WAIT)
            now = signature()
            run_publish()
            last = now

if __name__ == '__main__':
    main()
