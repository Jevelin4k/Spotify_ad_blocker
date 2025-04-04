@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

winget install python3.11 --accept-source-agreements --silent
python.exe -m pip install --upgrade pip
pip install winrt-runtime==3.0.0
pip install winrt-Windows.Foundation==3.0.0
pip install winrt-Windows.Foundation.Collections==3.0.0
pip install winrt-Windows.Media==3.0.0
pip install winrt-Windows.Media.Audio==3.0.0
pip install winrt-Windows.Media.Control==3.0.0
pip install winrt-Windows.Media.Core==3.0.0
pip install winrt-Windows.Storage==3.0.0
pip install winrt-Windows.Storage.Streams==3.0.0
pip install asyncio
pip install subprocess

mkdir "C:\Program Files (x86)\Spotify_ad_blocker"
cd "C:\Program Files (x86)\Spotify_ad_blocker"
git clone https://github.com/Jevelin4k/Spotify_ad_blocker.git

schtasks /create /tn "Spotify_ad_blocker" /tr "C:\Program Files (x86)\Spotify_ad_blocker\Spotify_ad_blocker\main.pyw" /sc onlogon /rl highest /f

schtasks /run /tn "Spotify_ad_blocker"

pause
