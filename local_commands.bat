@echo off

del /Q /S c:\temp\sb

"c:\Program Files\7-Zip\7z.exe" e -oc:\temp\sb %userprofile%\Downloads\Songbeamer_Paket.zip

del /Q %userprofile%\Downloads\Songbeamer_Paket.zip

rem Bei 64 Bit Version (neuere Songbeamer Versionen ab 6.06)
rem start "c:\Program Files\SongBeamer\SongBeamer.exe" "c:\temp\sb\Schedule.col"

rem Bei 32 Bit Version (ältere Songbeamer Versionen)
start "c:\Program Files (x86)\SongBeamer\SongBeamer.exe" "c:\temp\sb\Schedule.col"