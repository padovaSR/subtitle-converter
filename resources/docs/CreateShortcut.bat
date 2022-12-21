set SHORTCUT_NAME=SubtitleConverter
set TARGET_DIR=%~dp0
set TARGET_FILE=%TARGET_DIR%SubtitleConverter.exe
oLink.WorkingDirectory=%TARGET_DIR%
oLink.IconLocation="%TARGET_DIR%resources\icons\subConvert.ico"

 
set DESKTOP=%USERPROFILE%\Desktop

echo Set oWS = WScript.CreateObject("WScript.Shell") > %TEMP%\Shortcut.vbs
echo sLinkFile = "%DESKTOP%\%SHORTCUT_NAME%.lnk" >> %TEMP%\Shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %TEMP%\Shortcut.vbs
echo oLink.TargetPath = "%TARGET_FILE%" >> %TEMP%\Shortcut.vbs
echo oLink.WorkingDirectory= "%TARGET_DIR%" >> %TEMP%\Shortcut.vbs
echo oLink.Save >> %TEMP%\Shortcut.vbs

cscript /nologo %TEMP%\Shortcut.vbs
del %TEMP%\Shortcut.vbs
