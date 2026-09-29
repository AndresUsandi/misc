@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-json-precompute (DPO with precomputed reference log-probs, no reference model)
echo ============================================================

set PREF=bin\test-json-precompute\data\Optimizing\ch07_preference\preference_combined_1.json
for %%F in (bin\test-json-precompute\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)
copy /y bin\test-basic\data\Optimizing\ch07_preference\preference_combined_1.json "%PREF%" >nul

echo [1/4] Running Pre-training...
python train.py --model_name test-json-precompute --training_process Training || goto :error

echo [2/4] Running Fine-Tuning...
python train.py --model_name test-json-precompute --training_process Fine-Tuning || goto :error

echo [3/4] Running Optimizing (json_precompute: annotates the dataset, then trains without a reference model)...
python train.py --model_name test-json-precompute --training_process Optimizing || goto :error
findstr /l /c:"ref_chosen_logprob" "%PREF%" >nul || (echo [FAIL] Dataset was not annotated with reference log-probs & goto :error)
copy /y bin\test-basic\data\Optimizing\ch07_preference\preference_combined_1.json "%PREF%" >nul

echo [4/4] Running Inference...
python infer.py --model_name test-json-precompute --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-json-precompute\log.txt "Precomputed Mode: Active (No Ref Model)" "[Precompute Mode] Zero Reference Model VRAM enabled (--json_precompute)." "PRECOMPUTING REFERENCE LOG-PROBABILITIES FOR DPO" "[Precompute] Initialized reference model from SFT checkpoint" "[Precompute Complete] Successfully precomputed 1,100 pairs" "[Precomputed DPO Mode] Reference model bypassed entirely" "[Step Limit Reached] Reached target step 5. Pausing Precomputed DPO optimization cleanly." || goto :error

echo ============================================================
echo [PASS] E2E Test: test-json-precompute
echo ============================================================
popd
exit /b 0

:error
copy /y bin\test-basic\data\Optimizing\ch07_preference\preference_combined_1.json "%PREF%" >nul
echo ============================================================
echo [FAIL] E2E Test: test-json-precompute
echo ============================================================
popd
exit /b 1
