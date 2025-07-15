chcp 65001
set LOCATION=%1
%1 start "" mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
::mkdir "C:\Windows\ffmpeg\bin"
mklink "C:\Windows\ffmpeg.exe" "%LOCATION%\bin\ffmpeg.exe"
mklink "C:\Windows\ffprobe.exe" "%LOCATION%\bin\ffprobe.exe"
mklink "C:\Windows\ffplay.exe" "%LOCATION%\bin\ffplay.exe"
echo 软链接创建完成
pause