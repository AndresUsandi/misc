@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-basedir (--models_base_dir pointing outside bin/)
echo ============================================================

set E2E_BASE=%TEMP%\ailib-e2e-basedir
rd /s /q "%E2E_BASE%" 2>nul
xcopy /e /i /q /y bin\test-basedir "%E2E_BASE%\test-basedir" >nul || goto :error
for %%F in (bin\test-basedir\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/3] Running Pre-training (models_base_dir=%E2E_BASE%)...
python train.py --model_name test-basedir --models_base_dir "%E2E_BASE%" --training_process Training || goto :error

echo [2/3] Running Fine-Tuning (models_base_dir=%E2E_BASE%)...
python train.py --model_name test-basedir --models_base_dir "%E2E_BASE%" --training_process Fine-Tuning || goto :error

echo [3/3] Running Optimizing (models_base_dir=%E2E_BASE%)...
python train.py --model_name test-basedir --models_base_dir "%E2E_BASE%" --training_process Optimizing || goto :error

for %%F in (trn.chk sft.chk dpo.chk pth) do if not exist "%E2E_BASE%\test-basedir\test-basedir.%%F" (echo [FAIL] Missing test-basedir.%%F under %E2E_BASE% & goto :error)
if not exist "%E2E_BASE%\test-basedir\steps_cache.json" (echo [FAIL] steps_cache.json not written under %E2E_BASE% & goto :error)
dir /b bin\test-basedir\*.chk bin\test-basedir\*.pth bin\test-basedir\log.txt >nul 2>&1 && (echo [FAIL] Outputs leaked into the default bin\test-basedir folder & goto :error)
call "%~dp0_e2e_assert.cmd" "%E2E_BASE%\test-basedir\log.txt" "Saved TRAIN checkpoint (Step 2) to: %E2E_BASE%\test-basedir\test-basedir.trn.chk" "[Resume] Loaded base pre-trained weights for TUNE. Starting TUNE from Step 0." "[Reference Model] Initialized frozen reference model from SFT checkpoint" "[Resume] Loaded base SFT weights for OPTIMIZE. Starting OPTIMIZE from Step 0." || goto :error
rd /s /q "%E2E_BASE%" 2>nul

echo ============================================================
echo [PASS] E2E Test: test-basedir
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-basedir
echo ============================================================
popd
exit /b 1
