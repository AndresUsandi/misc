@echo off
setlocal enabledelayedexpansion

:: Runs every E2E suite. Pass test names to run a subset, e.g.: run_all_test.cmd basic resume
:: Multi-GPU suites (dp, pp, pp-async) skip themselves when fewer than 2 CUDA devices are visible.
:: Each log is checked against expected\<N>gpu\test-*.txt (N = visible GPUs). After an intended behavior change,
:: re-record them with: run_all_test.cmd record [tests]
set TESTS=basic hyperparams data-text paths resume epochs stage-order muon compile-actchk precision-fp32 precision-fp8 lowvram json-precompute vocab multifile device basedir cpu tokenizer-qwen tokenizer-smollm dp pp pp-async
set E2E_RECORD=
set "ARGS=%*"
if /i "%~1"=="record" (set E2E_RECORD=1& set "ARGS=!ARGS:~7!")
if defined ARGS set TESTS=!ARGS!
set SUMMARY=%TEMP%\ailib-e2e-summary.txt
set PASS=0
set FAIL=0
set SKIP=0
echo E2E run started %DATE% %TIME% > "%SUMMARY%"

for %%T in (%TESTS%) do (
    call "%~dp0test-%%T.cmd"
    if !errorlevel! equ 0 (set /a PASS+=1 & echo [PASS] test-%%T>> "%SUMMARY%") else if !errorlevel! equ 2 (set /a SKIP+=1 & echo [SKIP] test-%%T>> "%SUMMARY%") else (set /a FAIL+=1 & echo [FAIL] test-%%T>> "%SUMMARY%")
)

echo.
echo ============================================================
echo E2E SUMMARY: %PASS% passed, %FAIL% failed, %SKIP% skipped
if defined E2E_RECORD echo [RECORD MODE] Expected logs were recorded, not checked.
echo ============================================================
type "%SUMMARY%"
if %FAIL% gtr 0 exit /b 1
exit /b 0
