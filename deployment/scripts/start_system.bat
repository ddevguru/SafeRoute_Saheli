@echo off
title SafeRoute Saheli Ecosystem Launcher
echo ==============================================================================
echo                 SAFEROUTE SAHELI — LOCAL ECOSYSTEM LAUNCHER
echo ==============================================================================
echo.

set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..\..

echo [1/3] Checking Dependencies...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH!
    pause
    exit /b 1
)

node -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found in PATH!
    pause
    exit /b 1
)

echo.
echo [2/3] Starting Python Flask Backend on http://127.0.0.1:5000...
start "SafeRoute Saheli Backend" cmd /k "cd /d %ROOT_DIR% && python backend/run.py"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting React Admin Command Center on http://localhost:3000...
start "SafeRoute Saheli Admin Panel" cmd /k "cd /d %ROOT_DIR%\admin_panel && npm run dev"

echo.
echo ==============================================================================
echo   ALL SYSTEMS ONLINE:
echo   - REST API & WebSockets: http://127.0.0.1:5000/api
echo   - Admin Operations Center: http://localhost:3000
echo   - Flutter App: flutter run (inside flutter_app/)
echo   - ESP32 Wearable: pio run -t upload (inside firmware/esp32/)
echo   - ESP32-CAM: pio run -t upload (inside firmware/esp32_cam/)
echo ==============================================================================
echo.
pause
