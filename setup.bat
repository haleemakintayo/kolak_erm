@echo off
title Kolak ERM - Backend Initial Setup
echo ===================================================
echo     Kolak ERM Backend - Initial Setup Script
echo ===================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

:: 2. Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [INFO] Virtual environment 'venv' already exists.
)

:: 3. Activate venv and install dependencies
echo.
echo [INFO] Installing required packages from requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.

:: 4. Run migrations
echo.
echo [INFO] Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration failed.
    pause
    exit /b 1
)
echo [OK] Database migrations completed.

:: 5. Seed default roles, departments, permissions, and create admin user
echo.
echo [INFO] Seeding initial hospital roles, departments, and permissions...
python manage.py seed_roles_and_departments

echo.
echo [INFO] Ensuring default superadmin user exists...
python manage.py create_default_superadmin

echo.
echo ===================================================
echo   [SUCCESS] Setup Completed Successfully!
echo ===================================================
echo.
echo  Default Admin Login Credentials:
echo    Username: admin (or admin@kolak.com)
echo    Password: adminpassword123
echo.
echo  You can now start the server anytime by double-clicking:
echo    -> run_server.bat
echo.
pause
