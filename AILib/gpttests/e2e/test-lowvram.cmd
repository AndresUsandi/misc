@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-lowvram (Activation Checkpointing + Recompute LM Head + Freeze Embeddings + Chunk Size + Accumulation)
echo ============================================================

for %%F in (bin\test-lowvram\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (activation checkpointing + recompute_lmhead, no compile)...
python train.py --model_name test-lowvram --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (+ freeze_embeddings, chunk_size 128, batch 2 x accum 4, max_length 256)...
python train.py --model_name test-lowvram --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (+ freeze_embeddings, batch 1 x accum 4, max_length 256)...
python train.py --model_name test-lowvram --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-lowvram --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-lowvram\log.txt "[Low-VRAM Optimization] Activation / Gradient Checkpointing enabled" "[Low-VRAM Optimization] Token and position embeddings frozen (requires_grad = False)." "[Gradient Accumulation] Accumulating gradients over 4 sub-steps before optimizer update." "FINE-TUNING COMPLETED" "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-lowvram
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-lowvram
echo ============================================================
popd
exit /b 1
