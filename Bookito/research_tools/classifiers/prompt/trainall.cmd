@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "CLASSIFIERS=1-TFIDF-LinearSVC 2-TFIDF-MLP 3-Word2Vec-MLP 4-SentenceEmbeddings-MLP 5-CNN 6-LSTM 7-SmallEncoderTransformer"

echo ================================================================================
echo Starting Sequential Training for All Prompt Classifiers
echo ================================================================================

for %%C in (%CLASSIFIERS%) do (
    echo.
    echo ================================================================================
    echo Training Classifier: %%C
    echo ================================================================================
    
    if exist "%SCRIPT_DIR%%%C\classifier.py" (
        cd /d "%SCRIPT_DIR%%%C"
        python classifier.py --mode Train
        if errorlevel 1 (
            echo [ERROR] Training failed for classifier: %%C
            cd /d "%SCRIPT_DIR%"
            exit /b 1
        )
        cd /d "%SCRIPT_DIR%"
    ) else (
        echo [WARNING] classifier.py not found in %%C, skipping...
    )
)

echo.
echo ================================================================================
echo All Classifiers Trained Successfully!
echo ================================================================================
