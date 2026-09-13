@echo off
title CiteX Desktop Launcher
echo ========================================================
echo Starting CiteX Local Agent Server...
echo ========================================================
start /B python -m uvicorn app.main:app --port 8000 --reload
timeout /t 2 >nul
echo Opening CiteX in Standalone App Window...
start "" "chrome.exe" --app="http://127.0.0.1:8000" --user-data-dir="%LOCALAPPDATA%\CiteX\Profile"
exit
