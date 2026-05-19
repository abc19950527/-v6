@echo off
setlocal
cd /d %USERPROFILE%
if not exist .ssh mkdir .ssh
ssh-keygen -t ed25519 -C "abc19950527@github.com" -f "%USERPROFILE%\.ssh\id_ed25519" -N ""
echo.
echo === 您的公钥 (复制下面的全部内容) === 
type "%USERPROFILE%\.ssh\id_ed25519.pub"
echo.
echo === 复制完成后，按任意键退出 === 
pause >nul
