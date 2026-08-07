@echo off
REM  Send your latest changes to GitHub. Launcher only - see push.ps1.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0push.ps1" %*

echo.
pause
