@echo off
REM  Publish a new version so people can update to it.
REM
REM  This is only a launcher. The work is in release.ps1, because editing a
REM  file and running a handful of commands needs quoting that cmd mangles.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0release.ps1" %*

echo.
pause
