@echo off
REM  Send your latest changes to GitHub.
REM
REM  Double-click it, type what you changed, done. Nothing here creates a
REM  release - that is release.bat. This just saves your work.

setlocal
cd /d "%~dp0.."

where git >nul 2>&1 || (
    echo Git is not installed, or not on PATH.
    echo Get it from https://git-scm.com/download/win
    goto :done
)

if not exist ".git" (
    echo This folder is not a git repository yet.
    echo Run tools\first-push.bat once to set it up.
    goto :done
)

echo.
git status --short
echo.

REM  Nothing staged and nothing changed means there is genuinely nothing to do.
git diff --quiet && git diff --cached --quiet
if not errorlevel 1 (
    echo No changes to send.
    goto :done
)

set "msg="
set /p "msg=Describe what changed: "
if "%msg%"=="" set "msg=Update"

git add -A || goto :failed
git commit -m "%msg%" || goto :failed

echo.
echo Pushing...
git push || goto :failed

echo.
echo Sent. https://github.com/stamp020/RomSrx
goto :done

:failed
echo.
echo Something went wrong - read the message above.
echo Nothing was lost; your changes are still here.

:done
echo.
pause
endlocal
