@echo off
:: Detects the visible CUDA devices once per session. Pin the suite to specific GPUs with CUDA_VISIBLE_DEVICES
:: (e.g. "set CUDA_VISIBLE_DEVICES=1" to leave GPU 0 free); multi-GPU tests skip themselves below 2 devices.
:: Repeatable GPU kernels, so the logged values can be compared exactly with the recorded expected logs.
set AILIB_DETERMINISTIC=1
set CUBLAS_WORKSPACE_CONFIG=:4096:8
if defined E2E_GPU_COUNT exit /b 0
set E2E_GPU_COUNT=0
for /f %%G in ('python -c "import torch;print(torch.cuda.device_count())"') do set E2E_GPU_COUNT=%%G
set E2E_INFER_ARGS=
if %E2E_GPU_COUNT% LSS 2 set E2E_INFER_ARGS=--gpu_index 0
exit /b 0
