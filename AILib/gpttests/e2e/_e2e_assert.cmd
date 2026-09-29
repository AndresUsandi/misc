@echo off
:: Usage: call _e2e_assert.cmd <log.txt> ["expected literal text" ...]
:: Fails when the log shows a NaN loss or a crash-recovery save, when it differs from the recorded expected log
:: (see _e2e_logcheck.py), or when any expected literal is missing.
set "E2E_LOG=%~1"
if not exist "%E2E_LOG%" (echo [ASSERT] Log file not found: %E2E_LOG% & exit /b 1)
findstr /i /l /c:"Train nan" /c:"Val nan" /c:"Loss : nan" /c:"Loss   : nan" /c:"[Crash Recovery]" "%E2E_LOG%" >nul && (echo [ASSERT] NaN loss or crash recovery found in %E2E_LOG% & exit /b 1)
python "%~dp0_e2e_logcheck.py" "%E2E_LOG%" || exit /b 1
:next
shift
if "%~1"=="" exit /b 0
findstr /l /c:"%~1" "%E2E_LOG%" >nul || (echo [ASSERT] Expected log text not found: "%~1" & exit /b 1)
goto :next
