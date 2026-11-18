@echo off
call "%~dp0invoke-git-bash.cmd" "%~dp0trellis-matt" %*
exit /b %ERRORLEVEL%
