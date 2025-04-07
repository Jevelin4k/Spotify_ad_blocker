Set WshShell = CreateObject("WScript.Shell")
strPath = WScript.ScriptFullName
strFolder = Left(strPath, Len(strPath) - Len(WScript.ScriptName))
WshShell.Run Chr(34) & strFolder & "launch.bat" & Chr(34), 0, False
