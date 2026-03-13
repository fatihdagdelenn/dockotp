@echo off
echo DockOTP baslatiliyor...
docker compose up -d
start http://localhost:8080
