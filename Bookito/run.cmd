@echo off
SETLOCAL EnableDelayedExpansion

echo Starting Bookito Environment...
echo Checking if Docker daemon is running...
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not running or not installed. Please start Docker Desktop first.
    exit /b 1
)

echo Starting OpenSearch and OpenSearch Dashboards containers...
docker compose up -d

echo Waiting for OpenSearch to be ready at http://localhost:9200 ...
powershell -Command ^
    "$maxAttempts = 30; " ^
    "$attempt = 0; " ^
    "do { " ^
    "  try { " ^
    "    $response = Invoke-WebRequest -Uri 'http://localhost:9200' -UseBasicParsing -TimeoutSec 2; " ^
    "    if ($response.StatusCode -eq 200) { " ^
    "      Write-Host 'OpenSearch is ready!'; " ^
    "      break; " ^
    "    } " ^
    "  } catch {} " ^
    "  $attempt++; " ^
    "  Start-Sleep -Seconds 2; " ^
    "} while ($attempt -lt $maxAttempts)"

echo.
echo ===================================================
echo Bookito Development Environment is running!
echo ===================================================
echo OpenSearch API:        http://localhost:9200
echo OpenSearch Dashboards: http://localhost:5601
echo ===================================================
echo.
