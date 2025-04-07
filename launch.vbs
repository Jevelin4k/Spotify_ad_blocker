Set WshShell = CreateObject("Shell.Application")
WshShell.ShellExecute "cmd.exe", "/c {app}\launch.bat"
