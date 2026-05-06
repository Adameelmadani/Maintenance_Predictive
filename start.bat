@echo off
echo ============================================================
echo   PredMaint AI - Predictive Maintenance Platform
echo   Starting Flask API + React Frontend
echo ============================================================
echo.

:: Start Flask API in a new window
echo [1/2] Starting Flask API on port 5000...
start "Flask API" cmd /k "cd /d %~dp0 && set PYTHONIOENCODING=utf-8 && python api/app.py"

:: Wait 4 seconds for Flask to initialize
timeout /t 4 /nobreak >nul

:: Start React frontend in another new window
echo [2/2] Starting React Frontend on port 5173...
start "React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================================
echo   Both servers are starting:
echo   API:      http://localhost:5000/api/health
echo   Dashboard: http://localhost:5173
echo ============================================================
echo.
echo Opening dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo Done! Close this window after servers start.
pause
