@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-data-text (Data Ratios, Max Length, Chunk Size, Mask Prompt, Sampling, Verbose)
echo ============================================================

for %%F in (bin\test-data-text\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (Chunk Size + Ratios + Sampling Temperature/Top-K + Save Timeout)...
python train.py --model_name test-data-text --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (Mask Prompt off + Max Length 256 + Chunk Size 128 + Ratios + Verbose)...
python train.py --model_name test-data-text --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (Beta 0.2 + Max Length clamped from 1024 + Ratios + Verbose + Resume off)...
python train.py --model_name test-data-text --training_process Optimizing || goto :error

echo [4/4] Running Inference (Sampling Temp/Top-K/Top-P + ChatML)...
python infer.py --model_name test-data-text --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-data-text\log.txt "Sample: Every effort moves you" "[Sample]:" "[Policy Model] Resume disabled. Initialized policy weights from base SFT checkpoint (.sft.chk)." "[Sample Response]:" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-data-text
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-data-text
echo ============================================================
popd
exit /b 1
