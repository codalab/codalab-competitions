
ECHO Starting startup task at: >> "%TEMP%\StartupLog.txt" 2>&1
DATE /T >> "%TEMP%\StartupLog.txt" 2>&1
TIME /T >> "%TEMP%\StartupLog.txt" 2>&1

IF "%InComputeEmulator%" == "true" (
    ECHO Startup task running in compute emulator (skipping installation) >> "%TEMP%\StartupLog.txt" 2>&1
) ELSE (
    ECHO Startup task running in the cloud >> "%TEMP%\StartupLog.txt" 2>&1
    ECHO Getting Python MSI >> "%TEMP%\StartupLog.txt" 2>&1
    powershell -c "(new-object System.Net.WebClient).DownloadFile('http://python.org/ftp/python/2.7.5/python-2.7.5.amd64.msi', 'python.msi')"
    ECHO Installing Python >> "%TEMP%\StartupLog.txt" 2>&1
    start /w msiexec /i python.msi /qn /L StartupLogPython.txt
)

IF ERRORLEVEL EQU 0 (
   ECHO No error occurred.  >> "%TEMP%\StartupLog.txt" 2>&1
   EXIT /B 0
) ELSE (
   ECHO An error occurred. ERRORLEVEL = %ERRORLEVEL%.  >> "%TEMP%\StartupLog.txt" 2>&1
   EXIT %ERRORLEVEL%
)
