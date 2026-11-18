@echo off
setlocal EnableExtensions
rem Launch a bash script with Git for Windows bash.exe.
rem Never uses C:\Windows\System32\bash.exe (that starts WSL).
rem Usage: invoke-git-bash.cmd <script> [args...]

set "SCRIPT=%~1"
if not defined SCRIPT (
  echo error: invoke-git-bash.cmd needs the bash script path 1>&2
  exit /b 2
)
if not exist "%SCRIPT%" (
  echo error: bash script not found: %SCRIPT% 1>&2
  exit /b 2
)

set "BASH="
if exist "%ProgramFiles%\Git\bin\bash.exe" set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not defined BASH if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" set "BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not defined BASH if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" set "BASH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
if not defined BASH call :bash_from_git
if not defined BASH (
  echo error: Git for Windows bash.exe was not found. 1>&2
  echo        Install Git for Windows. This launcher does not use C:\Windows\System32\bash.exe. 1>&2
  exit /b 2
)
echo %BASH% | findstr /I /C:"\System32\bash.exe" >nul
if not errorlevel 1 (
  echo error: refusing C:\Windows\System32\bash.exe. Install Git for Windows and use its bin\bash.exe. 1>&2
  exit /b 2
)

rem SHIFT does not update %*, so copy arguments after the script path.
set "TAIL="
:collect
if "%~2"=="" goto :run
set TAIL=%TAIL% %2
shift
goto :collect

:run
rem Forward slashes keep UNC paths (\\wsl$\...) from losing a leading slash
rem inside Git Bash. User arguments stay as cmd received them.
set "SCRIPT_RUN=%SCRIPT:\=/%"
"%BASH%" --noprofile --norc "%SCRIPT_RUN%" %TAIL%
exit /b %ERRORLEVEL%

:bash_from_git
for /f "delims=" %%G in ('where git 2^>nul') do (
  if not defined BASH if exist "%%~dpG..\bin\bash.exe" set "BASH=%%~dpG..\bin\bash.exe"
)
exit /b 0
