@echo off
REM  One-time setup: connects this folder to your empty GitHub repository and
REM  sends everything up for the first time.
REM
REM  Before running: create the repository at https://github.com/new
REM    - Name it RomSrx
REM    - Leave "Add a README" and everything else UNTICKED. An empty repo is
REM      what this expects; anything already in it will collide.
REM
REM  After this, use push.bat for changes and release.bat for releases.

setlocal
cd /d "%~dp0.."

set "REPO=https://github.com/stamp020/RomSrx.git"

where git >nul 2>&1 || (
    echo Git is not installed, or not on PATH.
    echo Get it from https://git-scm.com/download/win
    goto :done
)

git remote get-url origin >nul 2>&1
if not errorlevel 1 (
    echo This folder is already connected to GitHub - use push.bat instead.
    goto :done
)

echo Setting up %REPO%
echo.

REM  Git refuses to commit without these, and the error it gives is cryptic.
for /f "delims=" %%n in ('git config --global user.name') do set "who=%%n"
if "%who%"=="" (
    echo Git needs to know who you are. Run these two lines, then try again:
    echo.
    echo   git config --global user.name "Your Name"
    echo   git config --global user.email "you@example.com"
    goto :done
)

if not exist ".git" (git init || goto :failed)
git branch -M main || goto :failed
git add -A || goto :failed

echo.
echo These files will be sent:
git status --short
echo.
echo (romsrx.db, dist\ and build\ are deliberately left out - see .gitignore.
echo  The index is 84 MB of data that GitHub would reject anyway, and it is
echo  rebuilt with: python -m romsrx index)
echo.
set "ok="
set /p "ok=Type yes to send this to GitHub: "
if /i not "%ok%"=="yes" (
    echo Stopped. Nothing was sent. The repository still exists locally.
    goto :done
)

REM  Nothing to commit is fine here - the work may already be committed and
REM  only the remote missing.
git diff --cached --quiet || git commit -m "RomSrx"
git remote add origin "%REPO%" || goto :failed
git push -u origin main || goto :failed

echo.
echo Done. Your code is at https://github.com/stamp020/RomSrx
echo.
echo Next: run tools\release.bat to publish the first downloadable version.
goto :done

:failed
echo.
echo Something went wrong - read the message above.
echo A common one: the repository already has files in it. Either empty it on
echo GitHub, or run: git pull --rebase origin main

:done
echo.
pause
endlocal
