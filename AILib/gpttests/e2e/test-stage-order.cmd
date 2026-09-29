@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."
call "%~dp0_e2e_env.cmd"

echo ============================================================
echo Running E2E Test: test-stage-order (Allowed weight sources per stage: .trn.chk / .sft.chk / .pth, with and without --resume)
echo ============================================================

set MDIR=bin\test-stage-order
for %%F in (%MDIR%\*.*) do (
    @echo %%~nxF | findstr /i "options- model-params" >nul || @del /f /q "%%F" 2>nul
)

echo [1/12] Pre-training from scratch (completes 1 epoch: .trn.chk + exported .pth)...
python train.py --model_name test-stage-order --training_process Training || goto :error
echo [2/12] Fine-Tuning on the pre-training checkpoint (.trn.chk)...
python train.py --model_name test-stage-order --training_process Fine-Tuning || goto :error
echo [3/12] Fine-Tuning with --resume false on the pre-training checkpoint (.trn.chk)...
python train.py --model_name test-stage-order --training_process Fine-Tuning --resume false || goto :error
echo [4/12] Optimizing with --resume false on the SFT checkpoint (.sft.chk)...
python train.py --model_name test-stage-order --training_process Optimizing --resume false || goto :error

del /f /q %MDIR%\*.sft.chk* %MDIR%\*.dpo.chk* 2>nul
echo [5/12] Optimizing directly on the pre-training checkpoint (.trn.chk, no SFT)...
python train.py --model_name test-stage-order --training_process Optimizing || goto :error

del /f /q %MDIR%\*.chk* 2>nul
echo [6/12] Fine-Tuning on the exported model only (.pth)...
python train.py --model_name test-stage-order --training_process Fine-Tuning || goto :error
del /f /q %MDIR%\*.chk* 2>nul
echo [7/12] Optimizing on the exported model only (.pth, reference model also from .pth)...
python train.py --model_name test-stage-order --training_process Optimizing || goto :error
del /f /q %MDIR%\*.chk* 2>nul
echo [8/12] Fine-Tuning with --resume false on the exported model only (.pth)...
python train.py --model_name test-stage-order --training_process Fine-Tuning --resume false || goto :error
del /f /q %MDIR%\*.chk* 2>nul
echo [9/12] Optimizing with --resume false on the exported model only (.pth)...
python train.py --model_name test-stage-order --training_process Optimizing --resume false || goto :error

echo [10/12] Pre-training again with only .pth + .dpo.chk present (must start from scratch, never from SFT/DPO weights)...
python train.py --model_name test-stage-order --training_process Training || goto :error
echo [11/12] Fine-Tuning with .trn.chk + .dpo.chk present (must take the pre-training checkpoint)...
python train.py --model_name test-stage-order --training_process Fine-Tuning || goto :error

echo [12/12] Running Inference...
python infer.py --model_name test-stage-order --prompt "what is the capital of france?" %E2E_INFER_ARGS% || goto :error

findstr /l /c:"weights for TRAIN. Starting TRAIN from Step 0." %MDIR%\log.txt >nul && (echo [FAIL] Pre-training loaded SFT/DPO checkpoint weights & goto :error)
call "%~dp0_e2e_assert.cmd" %MDIR%\log.txt "[Resume] No existing checkpoint found for 'test-stage-order' (TRAIN). Starting from scratch." "[modelio] Successfully saved clean final model" "[Resume] Loaded base pre-trained weights for TUNE. Starting TUNE from Step 0." "[Fine-Tuning] Resume disabled. Initialized model from base pre-trained checkpoint (.trn.chk). Starting Fine-Tuning from Step 0." "[Policy Model] Resume disabled. Initialized policy weights from base SFT checkpoint (.sft.chk)." "[Reference Model] Initialized frozen reference model from SFT checkpoint (.sft.chk)" "[Reference Model] Initialized frozen reference model from pre-training checkpoint (.trn.chk)" "[Resume] Loaded base pre-trained weights for OPTIMIZE. Starting OPTIMIZE from Step 0." "[Resume] No active SFT checkpoint found for 'test-stage-order'. Loaded base model weights (.pth). Starting Fine-Tuning from Step 0." "[Reference Model] No SFT/pre-training checkpoint found; initialized frozen reference model from base model weights (.pth)" "[Resume] Loaded base model weights (.pth) for policy model. Starting DPO from Step 0." "[Fine-Tuning] Resume disabled. Initialized model from base model weights (.pth). Starting Fine-Tuning from Step 0." "[Policy Model] Resume disabled. Initialized policy weights from base model (.pth)." || goto :error
for /f %%N in ('findstr /l /c:"(TRAIN). Starting from scratch." %MDIR%\log.txt ^| find /c /v ""') do if not "%%N"=="2" (echo [FAIL] Expected 2 from-scratch pre-training runs, found %%N & goto :error)

echo ============================================================
echo [PASS] E2E Test: test-stage-order
echo ============================================================
popd
exit /b 0

:error
echo ============================================================
echo [FAIL] E2E Test: test-stage-order
echo ============================================================
popd
exit /b 1
