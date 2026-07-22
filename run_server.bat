@echo off
title Kolak ERM Backend Server
echo ===================================================
echo       Starting Kolak ERM Backend Server
echo ===================================================
echo.

:: 1. Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please run 'setup.bat' first to set up the environment.
    echo.
    pause
    exit /b 1
)

:: 2. Activate venv
call venv\Scripts\activate.bat

:: 3. Run pending migrations silently
echo [INFO] Checking for pending migrations...
python manage.py migrate --noinput >nul 2>&1

:: 4. Start Server
echo [INFO] Launching Django Dev Server on http://localhost:8000 ...
echo.
echo ===================================================
echo   Quick Links for Frontend Developers:
echo    - Base API URL:      http://localhost:8000/api/
echo    - Swagger UI Docs:   http://localhost:8000/api/docs/
echo    - ReDoc Specs:       http://localhost:8000/api/redoc/
echo    - Admin Portal:      http://localhost:8000/admin/
echo.
echo  Default Admin Credentials:
echo    Username: admin  ^|  Password: adminpassword123
echo ===================================================
echo.
echo Press Ctrl+C in this window to stop the server.
echo.

python manage.py runserver 0.0.0.0:8000
pause
