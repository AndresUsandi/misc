@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-basic (Basic Baseline, single GPU)
echo ============================================================

for %%F in (bin\test-basic\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training...
python train.py --model_name test-basic --training_process Training || goto :error

echo [2/4] Running Fine-Tuning...
python train.py --model_name test-basic --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (DPO, policy and reference on one GPU)...
python train.py --model_name test-basic --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-basic --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-basic\log.txt "Optimizer Configured: 1 ([Single Fused AdamW for all layers, default])" "TRAINING COMPLETED" "[modelio] Successfully saved clean final model" "[Resume] Loaded base pre-trained weights for TUNE. Starting TUNE from Step 0." "FINE-TUNING COMPLETED" "Policy Device: cuda:0 | Ref Device: cuda:0" "[Reference Model] Initialized frozen reference model from SFT checkpoint" "[Resume] Loaded base SFT weights for OPTIMIZE. Starting OPTIMIZE from Step 0." "[Step Limit Reached] Reached target step 5. Pausing DPO optimization cleanly." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-basic
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-basic
echo ============================================================
popd
exit /b 1
