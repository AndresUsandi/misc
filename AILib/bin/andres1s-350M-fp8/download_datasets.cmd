@echo off
setlocal enabledelayedexpansion

pushd "%~dp0..\.."

echo ============================================================
echo Downloading Datasets for Model: andres1s-350M
echo ============================================================

echo.
echo ============================================================
echo [1/3] Pretraining Datasets (Training)
echo ============================================================
python download_dataset.py --model_name andres1s-350M --dataset bookcorpus cosmopedia dailydialog dialogsum personachat tinystories wikipedia writingprompts
if errorlevel 1 goto :error

echo.
echo ============================================================
echo [2/3] Fine-Tuning Datasets (Tuning)
echo ============================================================
python download_dataset.py --model_name andres1s-350M --dataset alpaca_gpt4 capybara deita_10k_sft no_robots slim_orca ultrachat_200k
if errorlevel 1 goto :error

echo.
echo ============================================================
echo [3/3] Optimization Datasets (Optimizing)
echo ============================================================
python download_dataset.py --model_name andres1s-350M --dataset dpo_mix
if errorlevel 1 goto :error

echo.
echo ============================================================
echo [SUCCESS] All datasets for andres1s-350M downloaded!
echo ============================================================
popd
exit /b 0

:error
echo.
echo ============================================================
echo [FAIL] Dataset download encountered an error.
echo ============================================================
popd
exit /b 1
