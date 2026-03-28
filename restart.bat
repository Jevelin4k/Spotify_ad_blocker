@echo off

TASKKILL /F /IM pythonw.exe

schtasks /run /tn "Spotify_ad_blocker"