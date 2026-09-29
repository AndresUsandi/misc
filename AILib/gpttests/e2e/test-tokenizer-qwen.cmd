@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-tokenizer-qwen (per-model tokenizer: Qwen2.5 tokenizer.json, 151,665 tokens, vocab_size 151,936)
echo ============================================================

for %%F in (bin\test-tokenizer-qwen\*.*) do (
    @echo %%~nxF | findstr /i /r /c:"options-" /c:"model-params" /c:"^tokenizer\.json" >nul || @del /f /q "%%F" 2>nul
)

echo [0/4] Fetching the tokenizer declared in model-params.json (first run only, kept across runs)...
python -c "import json, sys; sys.path.insert(0, '.'); from argsutil import ModelArgs; from gptinfer.inference import get_tokenizer; get_tokenizer(json.load(open('bin/test-tokenizer-qwen/test-tokenizer-qwen.model-params.json')), ModelArgs(model_name='test-tokenizer-qwen'))" >nul || goto :error

echo [1/4] Running Pre-training...
python train.py --model_name test-tokenizer-qwen --training_process Training || goto :error

echo [2/4] Running Fine-Tuning...
python train.py --model_name test-tokenizer-qwen --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (DPO)...
python train.py --model_name test-tokenizer-qwen --training_process Optimizing || goto :error

echo [4/4] Running Inference...
python infer.py --model_name test-tokenizer-qwen --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-tokenizer-qwen\log.txt "[Tokenizer] Loaded tokenizer.json (151,665 tokens, <|endoftext|>=151643, model vocab_size=151,936)." "Vocab: 151,936" "TRAINING COMPLETED" "FINE-TUNING COMPLETED" "DPO OPTIMIZATION COMPLETED" "[modelio] Successfully loaded model weights from: bin\test-tokenizer-qwen\test-tokenizer-qwen.pth" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-tokenizer-qwen
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-tokenizer-qwen
echo ============================================================
popd
exit /b 1
