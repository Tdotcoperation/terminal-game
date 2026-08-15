@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 terminal_arcade.py
  goto :end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python terminal_arcade.py
  goto :end
)
echo.
echo Python 3 is required to run Terminal Arcade.
echo Install Python 3, then run this file again.
echo.
pause
:end
endlocal
