@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-vocab (Unpadded 50,257 vocabulary vs. --vocab_padded, checkpoint vocab adaptation)
echo ============================================================

for %%F in (bin\test-vocab\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/5] Running Pre-training (--vocab_padded false: 50,257 vocab)...
python train.py --model_name test-vocab --training_process Training --vocab_padded false || goto :error

echo [2/5] Running Fine-Tuning (default padding: 50,304 model loads the 50,257 checkpoint)...
python train.py --model_name test-vocab --training_process Fine-Tuning || goto :error

echo [3/5] Running Optimizing (default padding)...
python train.py --model_name test-vocab --training_process Optimizing || goto :error

echo [4/5] Running Pre-training again (--vocab_padded true: resumes the 50,257 checkpoint into a 50,304 model)...
python train.py --model_name test-vocab --training_process Training --vocab_padded true || goto :error

echo [5/5] Running Inference (50,257 model loads the exported weights)...
python infer.py --model_name test-vocab --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-vocab\log.txt "Vocab: 50,257 | Context: 512" "Vocab: 50,304 | Context: 512" "TRAINING COMPLETED" "FINE-TUNING COMPLETED" "[Resume Notice] Checkpoint has already completed 1 epochs" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-vocab
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-vocab
echo ============================================================
popd
exit /b 1
