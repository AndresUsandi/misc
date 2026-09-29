@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-device (Explicit --device / --gpu_index / --pol_device / --ref_device specs)
echo ============================================================

for %%F in (bin\test-device\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (device "cuda", gpu_index 0)...
python train.py --model_name test-device --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (device "cuda:0", gpu_index 0)...
python train.py --model_name test-device --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (pol_device "cuda:0", ref_device "0")...
python train.py --model_name test-device --training_process Optimizing || goto :error

echo [4/4] Running Inference (device cuda:0)...
python infer.py --model_name test-device --prompt "what is the capital of france?" --device cuda:0 || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-device\log.txt "Device: cuda | Active GPUs: 1" "Device: cuda:0 | Active GPUs: 1" "Policy Device: cuda:0 | Ref Device: cuda:0" "TRAINING COMPLETED" "FINE-TUNING COMPLETED" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-device
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-device
echo ============================================================
popd
exit /b 1
