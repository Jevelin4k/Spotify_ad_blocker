Set WshShell = CreateObject("Shell.Application")
WshShell.ShellExecute "cmd.exe", "/c launch.bat", "", "open", "0"
