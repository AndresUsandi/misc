@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-pp-async (Pipeline Parallelism: uneven split, async PCIe, no micro-batching / 1F1B)
echo ============================================================
if %E2E_GPU_COUNT% LSS 2 (echo [SKIP] test-pp-async needs 2 visible CUDA devices, found %E2E_GPU_COUNT%. & popd & exit /b 2)

for %%F in (bin\test-pp-async\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (PP: uneven layers, micro-batching disabled, async PCIe, primary GPU 1)...
python train.py --model_name test-pp-async --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (PP: even layers, primary GPU 1)...
python train.py --model_name test-pp-async --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (policy on cuda:1, reference on cuda:0)...
python train.py --model_name test-pp-async --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-pp-async --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-pp-async\log.txt "MultiGpuGptModelPP across 2 GPUs (Layers: uneven (60" "GPU 1, default), async_pcie=True, micro_batching=disabled, 1f1b=False, primary=cuda:1)" "MultiGpuGptModelPP across 2 GPUs (Layers: even (50" "GPU 1), primary=cuda:1)" "Policy Device: cuda:1 | Ref Device: cuda:0" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-pp-async
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-pp-async
echo ============================================================
popd
exit /b 1
