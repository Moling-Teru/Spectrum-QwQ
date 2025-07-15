@echo off
:: 以管理员权限运行 install_ffmpeg.py
:: set SCRIPT_DIR=%~dp0
:: powershell -Command "Start-Process $env:python -ArgumentList '%SCRIPT_DIR%install_ffmpeg.py' -Verb RunAs"
chcp 65001
set LOCATION=%~dp0
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
python %LOCATION%install_ffmpeg.py
echo 安装完成
pause
::source: https://www.cnblogs.com/ibingshan/p/11323035.html