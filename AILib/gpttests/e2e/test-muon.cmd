@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-muon (Muon Optimizer)
echo ============================================================

for %%F in (bin\test-muon\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (Muon)...
python train.py --model_name test-muon --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (Muon)...
python train.py --model_name test-muon --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (Muon)...
python train.py --model_name test-muon --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-muon --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-muon\log.txt "Optimizers Configured: 2 ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])" "Muon LR: 0.02" "[Optimizer] Selected Hybrid CustomMuon (2D weights) + Fused AdamW (1D/Norms/Embeddings)." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-muon
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-muon
echo ============================================================
popd
exit /b 1
