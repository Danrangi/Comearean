@echo off
title Exam Arena Server Launcher
color 0A

echo ==========================================
echo        EXAM ARENA CBT SERVER
echo ==========================================
echo.

echo Getting local IP...
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /C:"IPv4 Address"') do (
  set IP=%%A
)
set IP=%IP:~1%

echo ------------------------------------------
echo Students should open:
echo http://%IP%:8080
echo ------------------------------------------
echo.

echo Starting server...
start "" "%~dp0ExamArenaServer.exe"

echo.
echo If firewall popup shows, click ALLOW (Private Network).
echo DO NOT close this window during the exam.
echo.
pause
