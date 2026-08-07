@echo off
REM  Publish a new version so people can update to it.
REM
REM  What happens: the version in romsrx\__init__.py is bumped, committed and
REM  tagged, then the tag is pushed. GitHub Actions notices the tag, builds
REM  Windows and Linux, and attaches both to a new release. Takes about five
REM  minutes, and you can watch it at:
REM
REM      https://github.com/stamp020/RomSrx/actions
REM
REM  The version and the tag must agree - that is how the app knows an update
REM  exists - which is why this script sets both rather than trusting you to.

setlocal EnableDelayedExpansion
cd /d "%~dp0.."

where git >nul 2>&1 || (echo Git is not installed, or not on PATH. & goto :done)
if not exist ".git" (echo Not a git repository yet - run tools\first-push.bat. & goto :done)

REM  Refuse to release on top of unsaved work: whatever is uncommitted would
REM  not be in the build, which is a confusing way to lose a change.
git diff --quiet && git diff --cached --quiet
if errorlevel 1 (
    echo.
    echo You have changes that have not been sent yet:
    echo.
    git status --short
    echo.
    echo Run tools\push.bat first, then come back.
    goto :done
)

for /f "tokens=2 delims=' " %%v in ('findstr /r "^__version__" romsrx\__init__.py') do set "current=%%v"
echo.
echo Current version: !current!
set "next="
set /p "next=New version (e.g. 0.2.0): "
if "!next!"=="" (echo Nothing entered - stopping. & goto :done)

REM  A tag that already exists would be rejected by the push, after the commit
REM  has been made - easier to catch it now.
git rev-parse -q --verify "refs/tags/v!next!" >nul
if not errorlevel 1 (echo Version v!next! has already been released. & goto :done)

echo.
echo This will publish v!next! and offer it to everyone running RomSrx.
set "ok="
set /p "ok=Type yes to continue: "
if /i not "!ok!"=="yes" (echo Stopped. Nothing was changed. & goto :done)

powershell -NoProfile -Command ^
  "$p='romsrx/__init__.py'; $t=Get-Content $p -Raw;" ^
  "$t=[regex]::Replace($t,'__version__ = \"[^\"]*\"','__version__ = \"!next!\"');" ^
  "Set-Content $p $t -NoNewline -Encoding utf8" || goto :failed

git add romsrx/__init__.py || goto :failed
git commit -m "Release v!next!" || goto :failed
git tag "v!next!" || goto :failed
git push || goto :failed
git push origin "v!next!" || goto :failed

echo.
echo Tagged v!next! and pushed.
echo GitHub is building it now - about five minutes:
echo   https://github.com/stamp020/RomSrx/actions
echo.
echo When it finishes the release appears here:
echo   https://github.com/stamp020/RomSrx/releases
goto :done

:failed
echo.
echo Something went wrong - read the message above.
echo If the tag was made but not pushed, undo it with:
echo   git tag -d v!next!

:done
echo.
pause
endlocal
