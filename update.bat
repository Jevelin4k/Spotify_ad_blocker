@echo off

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

schtasks /delete /tn "Spotify_ad_blocker" /f

TASKKILL /F /IM pythonw.exe
rmdir "C:\Program Files (x86)\Spotify_ad_blocker" /s /q



winget install python3.11 --accept-source-agreements --silent
python.exe -m pip install --upgrade pip

mkdir "C:\Program Files (x86)\Spotify_ad_blocker"
cd "C:\Program Files (x86)\Spotify_ad_blocker"
git clone https://github.com/Jevelin4k/Spotify_ad_blocker.git


pip install -r "C:\Program Files (x86)\Spotify_ad_blocker\Spotify_ad_blocker\requirements.txt"

schtasks /create /tn "Spotify_ad_blocker" /tr "\"C:\Windows\System32\wscript.exe\" \"C:\Program Files (x86)\Spotify_ad_blocker\Spotify_ad_blocker\launch.vbs\"" /sc onlogon /rl highest /f


schtasks /run /tn "Spotify_ad_blocker"

pause