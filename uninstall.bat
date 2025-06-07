@echo off

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

schtasks /delete /tn "Spotify_ad_blocker" /f

TASKKILL /F /IM pythonw.exe
rmdir "C:\Program Files (x86)\Spotify_ad_blocker" /s /q
