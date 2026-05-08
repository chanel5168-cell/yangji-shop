@echo off
cd /d "%~dp0"
start "" "http://localhost:8000/admin.html"
python -X utf8 start-server.py
pause
