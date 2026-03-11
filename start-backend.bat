@echo off
echo Starting LangFlow Backend...
cd /d "%~dp0backend"
pip install -r requirements.txt
echo.
echo Starting API server...
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
pause
