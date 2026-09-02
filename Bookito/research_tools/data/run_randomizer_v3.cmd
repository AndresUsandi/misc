@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "MODELS_0=qwen3.5:9b"
set "MODELS_1=gemma4:e2b"
set "MODELS_2=granite4.1:8b"
set "MODELS_3=phi4-mini:3.8b"
set "MODELS_4=qwen3.5:4b"
set "MODELS_5=qwen3.8:latest"
set "NUM_MODELS=6"

echo ================================================================================
echo Starting 100 batches of V3 LLM prompt randomization (1,000 prompts per batch)
echo ================================================================================

for /L %%B in (0,1,99) do (
    set /a "BATCH_NUM=%%B + 1"
    set /a "START_IDX=%%B * 1000 + 1"
    set /a "END_IDX=(%%B + 1) * 1000"
    set /a "MODEL_IDX=%%B %% NUM_MODELS"
    
    for %%M in (!MODEL_IDX!) do set "CURRENT_MODEL=!MODELS_%%M!"
    
    echo.
    echo ================================================================================
    echo Running Batch !BATCH_NUM!/100: Prompts !START_IDX! to !END_IDX! with model: !CURRENT_MODEL!
    echo ================================================================================
    
    python prompt_randomizer_v3.py --index-start !START_IDX! --index-end !END_IDX! --model !CURRENT_MODEL!
    if errorlevel 1 (
        echo [ERROR] Batch !BATCH_NUM! failed for range !START_IDX!-!END_IDX! with model !CURRENT_MODEL!
        exit /b 1
    )
)

echo.
echo ================================================================================
echo All 100 batches completed successfully!
echo ================================================================================
