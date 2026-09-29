@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-paths (Data Path Overrides: directory and single file)
echo ============================================================

for %%F in (bin\test-paths\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (override_data_folder = directory)...
python train.py --model_name test-paths --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (override_data_folder = single file)...
python train.py --model_name test-paths --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (override_data_folder = directory)...
python train.py --model_name test-paths --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-paths --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-paths\log.txt "Training Data Path: bin\test-basic\data\Training" "Instruction Data: bin\test-basic\data\Tuning\ch07_instruction\combined_1.txt (1 file(s))" "Preference Data: bin\test-basic\data\Optimizing (1 file(s))" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-paths
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-paths
echo ============================================================
popd
exit /b 1
