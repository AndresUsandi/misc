@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-cpu (--device cpu on a tiny model, Muon on CPU / Muon CUDA fallback)
echo ============================================================

for %%F in (bin\test-cpu\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (cpu, Muon)...
python train.py --model_name test-cpu --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (cpu, Muon requested, falls back to AdamW)...
python train.py --model_name test-cpu --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (cpu, policy and reference on cpu)...
python train.py --model_name test-cpu --training_process Optimizing || goto :error

echo [4/4] Running Inference (cpu)...
python infer.py --model_name test-cpu --prompt "what is the capital of france?" --device cpu || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-cpu\log.txt "Device: cpu | Active GPUs: 1 | Precision: FP16 | Model Dtype: torch.float32 | AMP: Disabled" "Optimizers Configured: 2 ([CustomMuon (2D matrices), Fused AdamW (1D/Norms)])" "[Optimizer Warning] CustomMuon requires CUDA; falling back to AdamW." "Policy Device: cpu | Ref Device: cpu" "TRAINING COMPLETED" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-cpu
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-cpu
echo ============================================================
popd
exit /b 1
