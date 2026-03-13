@echo off

echo ==========================
echo DockOTP Installer
echo ==========================

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker bulunamadi.
    echo Lutfen Docker Desktop kurun:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit
)

echo Docker bulundu.

echo Container baslatiliyor...

docker compose up -d --build

echo.
echo DockOTP baslatildi.
echo Tarayici aciliyor...

start http://localhost:8080

pause
