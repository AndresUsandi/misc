@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-precision-fp32 (Full FP32, no AMP)
echo ============================================================

for %%F in (bin\test-precision-fp32\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (fp32)...
python train.py --model_name test-precision-fp32 --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (fp32)...
python train.py --model_name test-precision-fp32 --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (fp32)...
python train.py --model_name test-precision-fp32 --training_process Optimizing || goto :error

echo [4/4] Running Inference (fp32)...
python infer.py --model_name test-precision-fp32 --prompt "what is the capital of france?" --precision fp32 %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-precision-fp32\log.txt "Precision: FP32 | Model Dtype: torch.float32 | AMP: Disabled" "TRAINING COMPLETED" "FINE-TUNING COMPLETED" "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-precision-fp32
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-precision-fp32
echo ============================================================
popd
exit /b 1
