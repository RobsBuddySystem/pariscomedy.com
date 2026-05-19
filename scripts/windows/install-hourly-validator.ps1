# Install hourly ParisComedy ticket validator on Windows.
# Requires: Python 3 on PATH, Ollama running on :11434 (optional), git clone of repo at C:\pariscomedy\_repo.
# Run from an elevated PowerShell prompt.
$ErrorActionPreference = "Stop"

$TaskName  = "ParisComedy-Hourly-Validate"
$ScriptDir = "C:\pariscomedy\_repo\scripts\windows"
$Script    = Join-Path $ScriptDir "validate_tickets.ps1"
$LogDir    = "C:\pariscomedy\logs"

if (-not (Test-Path $Script))    { throw "validator script missing: $Script (clone repo to C:\pariscomedy\_repo first)" }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Confirm prereqs
Write-Host "=== Prereqs ==="
where.exe python
where.exe ollama 2>$null
where.exe git
try { (Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -UseBasicParsing).StatusCode }
catch { Write-Warning "Ollama not reachable on :11434 — validator will still run, just without LLM assist." }

# Remove old task if present
schtasks /Query /TN $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { schtasks /Delete /TN $TaskName /F | Out-Null }

# Register new hourly task (at :07)
$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
            -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`""
$trigger = New-ScheduledTaskTrigger -Once -At ([DateTime]::Today.AddHours([DateTime]::Now.Hour + 1).AddMinutes(7)) `
            -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
  -Description "Hourly Eventbrite ticket-status validation for pariscomedy.com" -User $env:USERNAME -RunLevel Limited

Write-Host "Installed task: $TaskName"
Write-Host "Logs: $LogDir\hourly.log"
Write-Host "Run now: schtasks /Run /TN $TaskName"
