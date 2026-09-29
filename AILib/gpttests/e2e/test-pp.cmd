@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-pp (Multi-GPU Pipeline Parallelism)
echo ============================================================
if %E2E_GPU_COUNT% LSS 2 (echo [SKIP] test-pp needs 2 visible CUDA devices, found %E2E_GPU_COUNT%. & popd & exit /b 2)

for %%F in (bin\test-pp\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (PP: even layers, 1F1B, 4 micro-batches, async PCIe)...
python train.py --model_name test-pp --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (PP: uneven layers)...
python train.py --model_name test-pp --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (Dual GPU Policy/Ref)...
python train.py --model_name test-pp --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-pp --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-pp\log.txt "MultiGpuGptModelPP across 2 GPUs (Layers: even (50" "GPU 1), async_pcie=True, micro_batching=4 stages, 1f1b=True, primary=cuda:0)" "MultiGpuGptModelPP across 2 GPUs (Layers: uneven (60" "GPU 1, default), primary=cuda:0)" "Policy Device: cuda:0 | Ref Device: cuda:1" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-pp
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-pp
echo ============================================================
popd
exit /b 1
