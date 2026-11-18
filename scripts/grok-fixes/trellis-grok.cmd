@echo off
call "%~dp0invoke-git-bash.cmd" "%~dp0trellis-grok" %*
exit /b %ERRORLEVEL%
