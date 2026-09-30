@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   奉仕用美少女アンドロイド「ユリ」 原稿 公開ツール
echo ============================================
echo.
echo [1/2] 原稿をHTMLに変換し、プレビューを開きます...
echo.
python "_yuri_publish.py"
echo.
echo ============================================
echo  ブラウザで開いたプレビューを確認してください。
echo.
echo    Y = GitHubに公開する
echo    N = 公開しない（中止）
echo ============================================
echo.
choice /c YN /m "公開しますか"
if errorlevel 2 goto cancel

echo.
echo [2/2] GitHubに公開しています...
python "_yuri_publish.py" --push
echo.
echo 完了しました。Enterキーで閉じます。
pause >nul
goto end

:cancel
echo.
echo 公開を中止しました。（変換だけ済んでいます。pushしていません）
echo Enterキーで閉じます。
pause >nul

:end
