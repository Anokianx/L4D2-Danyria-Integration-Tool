@echo off
rem =============================================================================
rem 自动寻找 Python 并启动外置 HUD。
rem 自动查找 Python 并启动外置 HUD。
rem =============================================================================
setlocal
cd /d "%~dp0"

pythonw --version >nul 2>nul
if not errorlevel 1 (
    start "" pythonw "%~dp0DanyriaHUD.pyw"
    goto done
)

pyw -3 --version >nul 2>nul
if not errorlevel 1 (
    start "" pyw -3 "%~dp0DanyriaHUD.pyw"
    goto done
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
    start "" py -3w "%~dp0DanyriaHUD.pyw"
    goto done
)

python --version >nul 2>nul
if not errorlevel 1 (
    start "" python "%~dp0DanyriaHUD.pyw"
    goto done
)

echo Python 3 / pythonw was not found.
echo Install Python 3, then run this file again.
pause

:done
endlocal
