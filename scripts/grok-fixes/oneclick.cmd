@echo off
call "%~dp0invoke-git-bash.cmd" "%~dp0oneclick.sh" %*
exit /b %ERRORLEVEL%
