@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-epochs (Full epoch completion without step limit, completed-epochs notice)
echo ============================================================

for %%F in (bin\test-epochs\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/6] Running Pre-training (2 full epochs, final .pth export)...
python train.py --model_name test-epochs --training_process Training || goto :error
echo [2/6] Running Pre-training again (checkpoint already completed the requested epochs)...
python train.py --model_name test-epochs --training_process Training || goto :error

echo [3/6] Running Fine-Tuning (2 full epochs)...
python train.py --model_name test-epochs --training_process Fine-Tuning || goto :error
echo [4/6] Running Fine-Tuning again (checkpoint already completed the requested epochs)...
python train.py --model_name test-epochs --training_process Fine-Tuning || goto :error

echo [5/6] Running Optimizing (1 full epoch)...
python train.py --model_name test-epochs --training_process Optimizing || goto :error

echo [6/6] Running Inference...
python infer.py --model_name test-epochs --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

call "%~dp0_e2e_assert.cmd" bin\test-epochs\log.txt "Starting Epoch 2/2" "[Resume Notice] Checkpoint has already completed 2 epochs" "Starting Fine-Tuning Epoch 2/2" "[Sample Response @ Epoch 2]" "[Plot] Saved fine-tuning loss curves" "[Sample Model Response @ Epoch 1]" "[Plot] Saved DPO telemetry curves" || goto :error
for %%F in (trn.chk sft.chk dpo.chk pth) do if not exist "bin\test-epochs\test-epochs.%%F" (echo [FAIL] Missing expected output test-epochs.%%F & goto :error)

echo ============================================================
echo [PASS] E2E Test: test-epochs
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-epochs
echo ============================================================
popd
exit /b 1
