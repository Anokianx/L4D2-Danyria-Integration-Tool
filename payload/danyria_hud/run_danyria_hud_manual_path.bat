@echo off
rem =============================================================================
rem 手动输入 left4dead2 路径后启动外置 HUD。
rem 手动输入 left4dead2 路径后启动外置 HUD。
rem =============================================================================
setlocal
cd /d "%~dp0"
echo Enter your left4dead2 folder path, then press Enter.
echo Example: D:\SteamLibrary\steamapps\common\Left 4 Dead 2\left4dead2
set /p L4D2PATH=Path: 

pythonw "%~dp0DanyriaHUD.pyw" "%L4D2PATH%"
if errorlevel 1 pyw -3 "%~dp0DanyriaHUD.pyw" "%L4D2PATH%"
if errorlevel 1 py -3 "%~dp0DanyriaHUD.pyw" "%L4D2PATH%"
if errorlevel 1 python "%~dp0DanyriaHUD.pyw" "%L4D2PATH%"

endlocal
pause
