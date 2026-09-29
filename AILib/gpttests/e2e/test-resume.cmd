@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-resume (Mid-run checkpoint resume for every stage, Muon optimizer state restore)
echo ============================================================

for %%F in (bin\test-resume\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/7] Running Pre-training (fresh, stops at step 3 mid-file)...
python train.py --model_name test-resume --training_process Training || goto :error
echo [2/7] Running Pre-training again (resumes at step 3, fast-forwards inside the file)...
python train.py --model_name test-resume --training_process Training || goto :error

echo [3/7] Running Fine-Tuning (fresh, stops at step 3)...
python train.py --model_name test-resume --training_process Fine-Tuning || goto :error
echo [4/7] Running Fine-Tuning again (resumes at step 3)...
python train.py --model_name test-resume --training_process Fine-Tuning || goto :error

echo [5/7] Running Optimizing (fresh, stops at step 3)...
python train.py --model_name test-resume --training_process Optimizing || goto :error
echo [6/7] Running Optimizing again (resumes at step 3)...
python train.py --model_name test-resume --training_process Optimizing || goto :error

echo [7/7] Running Inference...
python infer.py --model_name test-resume --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-resume\log.txt "[Resume] No existing checkpoint found for 'test-resume' (TRAIN). Starting from scratch." "[Resume] Successfully loaded active TRAIN checkpoint at Global Step 3" "[Training Plan] Resumed from step 3. Training for 3 steps -> Target step: 6." "[Resume] Fast-forwarding 3 step(s) in file 1" "Saved TRAIN checkpoint (Step 6)" "[Resume] Successfully loaded active TUNE checkpoint at Global Step 3" "[Resume] Fast-forwarding 3 step(s) in Epoch 1" "Saved TUNE checkpoint (Step 6)" "[Resume] Successfully loaded active OPTIMIZE checkpoint at Global Step 3" "[DPO Plan] Resumed from step 3. Training for 3 steps -> Target step: 6." "Saved OPTIMIZE checkpoint (Step 6)" || goto :error

echo ============================================================
echo [PASS] E2E Test: test-resume
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-resume
echo ============================================================
popd
exit /b 1
