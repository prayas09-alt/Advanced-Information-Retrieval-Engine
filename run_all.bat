@echo off
echo Starting Argus Information Retrieval Search Engine (Full Stack)...
start "Argus IR Backend (FastAPI)" cmd /k "cd /d %~dp0 && python backend/main.py"
timeout /t 3 /nobreak >nul
start "Argus IR Frontend (Vite React)" cmd /k "cd /d %~dp0frontend && npm run dev"
echo Both services launched! Navigate to http://localhost:5173 in your browser.
pause
