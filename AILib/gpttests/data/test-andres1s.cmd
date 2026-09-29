@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."

echo ============================================================
echo Running Model Data Test: andres1s-350M (Format Validation)
echo ============================================================

python gpttests\data\test_andres1s.py
if errorlevel 1 goto :error

echo ============================================================
echo [PASS] Model Data Test: andres1s-350M
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] Model Data Test: andres1s-350M
echo ============================================================
popd
exit /b 1
