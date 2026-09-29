@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-tokenizer-smollm (per-model tokenizer: SmolLM2 tokenizer.json, 49,152 tokens, ^<^|endoftext^|^> is id 0)
echo ============================================================

for %%F in (bin\test-tokenizer-smollm\*.*) do (
    @echo %%~nxF | findstr /i /r /c:"options-" /c:"model-params" /c:"^tokenizer\.json" >nul || @del /f /q "%%F" 2>nul
)

echo [0/4] Fetching the tokenizer declared in model-params.json (first run only, kept across runs)...
python -c "import json, sys; sys.path.insert(0, '.'); from argsutil import ModelArgs; from gptinfer.inference import get_tokenizer; get_tokenizer(json.load(open('bin/test-tokenizer-smollm/test-tokenizer-smollm.model-params.json')), ModelArgs(model_name='test-tokenizer-smollm'))" >nul || goto :error

echo [1/4] Running Pre-training...
python train.py --model_name test-tokenizer-smollm --training_process Training || goto :error

echo [2/4] Running Fine-Tuning...
python train.py --model_name test-tokenizer-smollm --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (DPO)...
python train.py --model_name test-tokenizer-smollm --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-tokenizer-smollm --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-tokenizer-smollm\log.txt "[Tokenizer] Loaded tokenizer.json (49,152 tokens, <|endoftext|>=0, model vocab_size=49,152)." "Vocab: 49,152" "TRAINING COMPLETED" "FINE-TUNING COMPLETED" "DPO OPTIMIZATION COMPLETED" "[modelio] Successfully loaded model weights from: bin\test-tokenizer-smollm\test-tokenizer-smollm.pth" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-tokenizer-smollm
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-tokenizer-smollm
echo ============================================================
popd
exit /b 1
