@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."

echo ============================================================
echo Running Model Data Test: gpt2-774M (Format Validation)
echo ============================================================

python gpttests\data\test_gpt2_774.py
if errorlevel 1 goto :error

echo ============================================================
echo [PASS] Model Data Test: gpt2-774M
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] Model Data Test: gpt2-774M
echo ============================================================
popd
exit /b 1
