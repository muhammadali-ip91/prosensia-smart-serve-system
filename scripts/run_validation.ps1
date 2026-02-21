$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$pythonExe = Join-Path $repoRoot ".venv/Scripts/python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Python venv not found at $pythonExe"
}

function Test-PortOpen([int]$port) {
    $ipv4 = Test-NetConnection -ComputerName 127.0.0.1 -Port $port -WarningAction SilentlyContinue
    if ([bool]$ipv4.TcpTestSucceeded) { return $true }

    $localhost = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    return [bool]$localhost.TcpTestSucceeded
}

function Wait-BackendHealth([int]$timeoutSeconds = 12) {
    $deadline = (Get-Date).AddSeconds($timeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 2
            if ($resp.StatusCode -eq 200) { return $true }
        } catch {}
        Start-Sleep -Milliseconds 500
    }

    return $false
}

$script:BackendApiUrl = 'http://127.0.0.1:8000'

function Stop-PortProcess([int]$port) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
}

function Start-Backend([string]$dbUrl) {
    Stop-PortProcess 8000
    $backendPath = Join-Path $repoRoot 'backend'
    $env:PYTHONPATH = $backendPath
    $env:DATABASE_URL = $dbUrl
    $env:REDIS_URL = 'redis://localhost:6379/0'

    Start-Process -FilePath $pythonExe -ArgumentList @('-m','uvicorn','main:socket_app','--host','127.0.0.1','--port','8000') -WorkingDirectory $backendPath -WindowStyle Hidden | Out-Null

    Start-Sleep -Seconds 2
    if (Wait-BackendHealth) {
        $script:BackendApiUrl = 'http://127.0.0.1:8000'
        return
    }

    Stop-PortProcess 8000
    Start-Process -FilePath $pythonExe -ArgumentList @('-m','uvicorn','main:socket_app','--host','0.0.0.0','--port','8000') -WorkingDirectory $backendPath -WindowStyle Hidden | Out-Null

    Start-Sleep -Seconds 2
    if (Wait-BackendHealth) {
        $script:BackendApiUrl = 'http://127.0.0.1:8000'
        return
    }

    Stop-PortProcess 8000
    Start-Process -FilePath $pythonExe -ArgumentList @('-m','uvicorn','main:socket_app','--host','::1','--port','8000') -WorkingDirectory $backendPath -WindowStyle Hidden | Out-Null

    Start-Sleep -Seconds 2
    $script:BackendApiUrl = 'http://[::1]:8000'
    if (-not (Wait-BackendHealth)) { throw 'Backend failed to start on port 8000' }
}

function Start-Frontend {
    Stop-PortProcess 3000
    $frontendPath = Join-Path $repoRoot 'frontend'
    $env:VITE_API_URL = $script:BackendApiUrl
    Start-Process -FilePath 'npm.cmd' -ArgumentList @('run','dev','--','--host','127.0.0.1','--port','3000') -WorkingDirectory $frontendPath -WindowStyle Hidden | Out-Null

    Start-Sleep -Seconds 4
    if (-not (Test-PortOpen 3000)) { throw 'Frontend failed to start on port 3000' }
}

$dockerAvailable = $false
try {
    $null = (Get-Command docker -ErrorAction Stop)
    $dockerAvailable = $true
} catch {}

$dbPort = Test-PortOpen 5432
$redisPort = Test-PortOpen 6379
$infraMode = 'fallback-sqlite'

if ($dockerAvailable -and -not ($dbPort -and $redisPort)) {
    try {
        docker compose up -d db redis | Out-Null
        Start-Sleep -Seconds 5
        $dbPort = Test-PortOpen 5432
        $redisPort = Test-PortOpen 6379
    } catch {}
}

if ($dbPort -and $redisPort) { $infraMode = 'postgres-redis' }

if ($infraMode -eq 'postgres-redis') {
    $dbUrl = 'postgresql://prosensia_user:prosensia_pass@localhost:5432/prosensia'
} else {
    $dbFile = Join-Path $repoRoot 'prosensia_test.db'
    Remove-Item -ErrorAction SilentlyContinue $dbFile
    $dbPath = $dbFile.Replace('\\','/')
    $dbUrl = "sqlite:///$dbPath"
}

$env:PYTHONPATH = (Join-Path $repoRoot 'backend')
$env:DATABASE_URL = $dbUrl
$env:LOGIN_RATE_LIMIT_PER_15MIN = '1000'

& $pythonExe -c "from database.connection import create_tables; create_tables(); print('tables-created')" | Out-Host
& $pythonExe -c "from database.seed_data import seed_all; seed_all(); print('seed-complete')" | Out-Host
& $pythonExe -c "from database.session import SessionLocal; from services.kitchen_settings_service import update_kitchen_hours, set_kitchen_force_closed; from datetime import datetime; db=SessionLocal(); h=datetime.now().hour; open_hour=(h-1)%24; close_hour=(h+2)%24; update_kitchen_hours(db, open_hour, close_hour); set_kitchen_force_closed(db, False, apply_to_all_menu=False); db.close(); print('kitchen-open-for-tests')" | Out-Host

Start-Backend -dbUrl $dbUrl
Start-Frontend

$integrationExit = 1
$e2eExit = 1

& $pythonExe -m pytest tests/integration -q
$integrationExit = $LASTEXITCODE

Set-Location (Join-Path $repoRoot 'frontend')
npm run cypress:run -- --project ../tests/e2e
$e2eExit = $LASTEXITCODE
Set-Location $repoRoot

$integrationStatus = if ($integrationExit -eq 0) { 'PASS' } else { 'FAIL' }
$e2eStatus = if ($e2eExit -eq 0) { 'PASS' } else { 'FAIL' }
$backendStatus = if (Test-PortOpen 8000) { 'PASS' } else { 'FAIL' }
$frontendStatus = if (Test-PortOpen 3000) { 'PASS' } else { 'FAIL' }

Write-Host ""
Write-Host "===== Validation Matrix ====="
Write-Host "Infra Mode      : $infraMode"
Write-Host "Backend (8000)  : $backendStatus"
Write-Host "Frontend (3000) : $frontendStatus"
Write-Host "Integration     : $integrationStatus"
Write-Host "Cypress E2E     : $e2eStatus"
Write-Host "============================="

if ($integrationExit -ne 0 -or $e2eExit -ne 0) {
    exit 1
}
exit 0
