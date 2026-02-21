$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'

if (-not (Test-Path -LiteralPath $pythonExe)) {
	Write-Error "Python executable not found at: $pythonExe"
	exit 1
}

function Stop-PortProcess([int]$port) {
	$conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
	if (-not $conns) { return }

	$pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
	foreach ($processId in $pids) {
		Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
	}
}

Stop-PortProcess 8000
Stop-PortProcess 5173

$backendCommand = @"
Set-Location '$projectRoot/backend'
`$env:DATABASE_URL='sqlite:///./prosensia_local.db'
`$hosts = @('127.0.0.1', '0.0.0.0', '::1')
`$started = `$false
foreach (`$bindHost in `$hosts) {
	Write-Host "Starting backend on `$bindHost:8000..."
	& '$pythonExe' -m uvicorn main:socket_app --host `$bindHost --port 8000
	if (`$LASTEXITCODE -eq 0) {
		`$started = `$true
		break
	}
	Write-Warning "Backend failed on host `$bindHost (exit code: `$LASTEXITCODE). Trying next host..."
}

if (-not `$started) {
	Write-Error 'Backend failed to start on all fallback hosts.'
}
"@

$frontendCommand = @"
Set-Location '$projectRoot/frontend'
`$env:VITE_API_URL='http://localhost:8000'
`$env:VITE_SOCKET_URL='http://localhost:8000'
npm run dev -- --host 127.0.0.1 --port 5173
"@

Start-Process powershell -ArgumentList '-NoExit', '-Command', $backendCommand | Out-Null
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList '-NoExit', '-Command', $frontendCommand | Out-Null

Write-Host ''
Write-Host 'Started local development servers in two new terminals:' -ForegroundColor Green
Write-Host '- Backend:  http://localhost:8000' -ForegroundColor Cyan
Write-Host '- Frontend: http://localhost:5173' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Health check URL: http://localhost:8000/health' -ForegroundColor Yellow
