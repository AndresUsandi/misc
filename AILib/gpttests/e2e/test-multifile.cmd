@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-multifile (Two dataset files per stage, precompute_total_steps, test_mode)
echo ============================================================

for %%F in (bin\test-multifile\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/4] Running Pre-training (2 text files, precompute_total_steps, train_ratio 0.8)...
python train.py --model_name test-multifile --training_process Training || goto :error

echo [2/4] Running Fine-Tuning (2 instruction files)...
python train.py --model_name test-multifile --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (2 preference files, test_mode truncates to 1)...
python train.py --model_name test-multifile --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-multifile --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-multifile\log.txt "Total training files found: 2" "[Precompute] Verifying/calculating exact tokens across 2 dataset file(s)" "[Steps Cache] Loaded complete steps cache" "[Prefetch] Tokenizing next file in background: bin\test-multifile\data\Training\TheVeredict\the-verdict-part1.txt" "Tokenizing file 2 of 2" "(2 file(s))" "SFT validation buffer" "across 2 file(s)." "[Test Mode] Truncated dataset to 1 file (preference_combined_1.json)." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-multifile
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-multifile
echo ============================================================
popd
exit /b 1
