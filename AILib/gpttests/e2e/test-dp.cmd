@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-dp (Multi-GPU Data Parallelism)
echo ============================================================
if %E2E_GPU_COUNT% LSS 2 (echo [SKIP] test-dp needs 2 visible CUDA devices, found %E2E_GPU_COUNT%. & popd & exit /b 2)

for %%F in (bin\test-dp\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (DP, primary GPU 1)...
python train.py --model_name test-dp --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (DP, primary GPU 0)...
python train.py --model_name test-dp --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (auto reference device on GPU 1)...
python train.py --model_name test-dp --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-dp --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-dp\log.txt "Wrapping model in MultiGpuGptModelDP across 2 GPUs (Data Parallelism, compile=False, primary=cuda:1)" "Wrapping model in MultiGpuGptModelDP across 2 GPUs (Data Parallelism, compile=False, primary=cuda:0)" "Policy Device: cuda:0 | Ref Device: cuda:1" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-dp
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-dp
echo ============================================================
popd
exit /b 1
