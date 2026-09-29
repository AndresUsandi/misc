@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-compile-actchk (Compile + Act Checkpointing)
echo ============================================================

for %%F in (bin\test-compile-actchk\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (Compile + Act Checkpointing)...
python train.py --model_name test-compile-actchk --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (Compile + Act Checkpointing)...
python train.py --model_name test-compile-actchk --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (Compile + Act Checkpointing)...
python train.py --model_name test-compile-actchk --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-compile-actchk --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-compile-actchk\log.txt "[Low-VRAM Optimization] Activation / Gradient Checkpointing enabled" "Applying torch.compile(model.forward_features)" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-compile-actchk
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-compile-actchk
echo ============================================================
popd
exit /b 1
