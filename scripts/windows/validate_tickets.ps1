# Windows hourly ticket-status validator for pariscomedy.com.
# Pulls repo, runs validator + bake, commits/pushes if changed.
$ErrorActionPreference = "Continue"
$REPO    = "C:\pariscomedy\_repo"
$LOG_DIR = "C:\pariscomedy\logs"
$LOG     = Join-Path $LOG_DIR "hourly.log"

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

function Log([string]$msg) {
  $line = "$(Get-Date -Format o) $msg"
  Add-Content -Path $LOG -Value $line -Encoding utf8
}

Log "=== run start ==="

if (-not (Test-Path $REPO)) {
  Log "REPO missing at $REPO -- clone with: git clone https://github.com/RobsBuddySystem/pariscomedy.com.git $REPO"
  exit 2
}

Push-Location $REPO
try {
  try {
    $r = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -UseBasicParsing
    Log "Ollama OK ($($r.StatusCode))"
  } catch {
    Log "Ollama unreachable: $($_.Exception.Message)"
  }

  $fetch = & git fetch --quiet origin main 2>&1 | Out-String
  if ($fetch) { Log "git-fetch: $fetch" }
  $reset = & git reset --hard origin/main 2>&1 | Out-String
  Log "git-reset: $reset"

  $vout = & python scripts\validate_tickets.py 2>&1 | Out-String
  Log "validator: $vout"

  $bout = & python scripts\bake_shows.py 2>&1 | Out-String
  Log "bake: $bout"

  $diff = & git status --porcelain data/shows_generated.json data/review_queue.json index.html shows.html 2>&1 | Out-String
  if (-not $diff.Trim()) {
    Log "no-op (no diff)"
    exit 0
  }

  & git add data/shows_generated.json data/review_queue.json index.html shows.html 2>&1 | Out-Null
  $stamp = (Get-Date -Format "yyyy-MM-ddTHH:mmZ")
  $commit = & git commit -m "hourly[win]: revalidate ticket statuses ($stamp)" 2>&1 | Out-String
  Log "commit: $commit"
  $push = & git push 2>&1 | Out-String
  Log "push: $push"
} finally {
  Pop-Location
  Log "=== run end ==="
}
