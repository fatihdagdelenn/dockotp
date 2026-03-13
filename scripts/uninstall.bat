@echo off
echo DockOTP kaldiriliyor...

docker compose down

echo Container silindi.

echo Data klasoru silinsin mi? (y/n)
set /p answer=

if /I "%answer%"=="y" (
    rmdir /s /q data
    echo Data klasoru silindi.
)

pause
