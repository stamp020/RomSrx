@echo off
REM  One-time GitHub setup. Launcher only - see first-push.ps1.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0first-push.ps1" %*

echo.
pause
