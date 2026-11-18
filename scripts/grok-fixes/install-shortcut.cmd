@echo off
call "%~dp0invoke-git-bash.cmd" "%~dp0install-shortcut.sh" %*
exit /b %ERRORLEVEL%
