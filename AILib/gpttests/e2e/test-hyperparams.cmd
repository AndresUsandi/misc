@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-hyperparams (Warmup, Min LR, Weight Decay, Eval Freq/Iter, Save Interval, Step Limit, Beta)
echo ============================================================

for %%F in (bin\test-hyperparams\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (Warmup Steps + Min LR + Weight Decay + Periodic Saves)...
python train.py --model_name test-hyperparams --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (Warmup Ratio + Min LR + Eval Iter + Periodic Saves)...
python train.py --model_name test-hyperparams --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (Warmup Ratio + Min LR + Beta 0.2 + Periodic Saves)...
python train.py --model_name test-hyperparams --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-hyperparams --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-hyperparams\log.txt "Warmup Steps: 2" "[Checkpointing] Periodic saves enabled every 2 steps" "Saved TRAIN checkpoint (Step 2)" "Saved TUNE checkpoint (Step 2)" "Saved TUNE checkpoint (Step 4)" "Beta: 0.2" "Saved OPTIMIZE checkpoint (Step 2)" "Saved OPTIMIZE checkpoint (Step 4)" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-hyperparams
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-hyperparams
echo ============================================================
popd
exit /b 1
