@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-precision-fp8 (FP8 + compile + coordinate descent tuning; falls back to fp16 below Compute 8.9)
echo ============================================================

for %%F in (bin\test-precision-fp8\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (fp8 + compile + coordinate_descent_tuning)...
python train.py --model_name test-precision-fp8 --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (fp8 + compile)...
python train.py --model_name test-precision-fp8 --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (fp8 + compile)...
python train.py --model_name test-precision-fp8 --training_process Optimizing || goto :error

echo [4/4] Running Inference (fp8)...
python infer.py --model_name test-precision-fp8 --prompt "what is the capital of france?" --precision fp8 %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-precision-fp8\log.txt "Precision: FP8 | Model Dtype:" "TRAINING COMPLETED" "FINE-TUNING COMPLETED" "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-precision-fp8
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-precision-fp8
echo ============================================================
popd
exit /b 1
