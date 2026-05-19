# Windows hourly ticket-status validator for pariscomedy.com.
# Pulls repo, runs validator + bake, commits/pushes if changed.
$ErrorActionPreference = "Continue"
$REPO    = "C:\pariscomedy\_repo"
$LOG_DIR = "C:\pariscomedy\logs"
$LOG     = Join-Path $LOG_DIR "hourly.log"

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
"=== $(Get-Date -Format o) ===" | Out-File -FilePath $LOG -Append -Encoding utf8

if (-not (Test-Path $REPO)) {
  "REPO missing at $REPO — clone with: git clone https://github.com/RobsBuddySystem/pariscomedy.com.git $REPO" |
    Out-File -FilePath $LOG -Append -Encoding utf8
  exit 2
}

Push-Location $REPO
try {
  # Ollama sanity (informational, non-fatal)
  try {
    $r = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -UseBasicParsing
    "Ollama OK ($($r.StatusCode))" | Out-File -FilePath $LOG -Append -Encoding utf8
  } catch {
    "Ollama unreachable: $($_.Exception.Message)" | Out-File -FilePath $LOG -Append -Encoding utf8
  }

  (git fetch --quiet origin main 2>&1; git reset --hard origin/main 2>&1) | Out-File -FilePath $LOG -Append -Encoding utf8

  (python scripts\validate_tickets.py 2>&1) | Out-File -FilePath $LOG -Append -Encoding utf8
  (python scripts\bake_shows.py        2>&1) | Out-File -FilePath $LOG -Append -Encoding utf8

  $diff = git status --porcelain data/shows_generated.json data/review_queue.json index.html shows.html 2>&1
  if (-not $diff) {
    "no-op (no diff)" | Out-File -FilePath $LOG -Append -Encoding utf8
    exit 0
  }

  (git add data/shows_generated.json data/review_queue.json index.html shows.html 2>&1) | Out-File -FilePath $LOG -Append -Encoding utf8
  $stamp = (Get-Date -Format "yyyy-MM-ddTHH:mmZ")
  (git commit -m "hourly[win]: revalidate ticket statuses ($stamp)" 2>&1) | Out-File -FilePath $LOG -Append -Encoding utf8
  (git push 2>&1) | Out-File -FilePath $LOG -Append -Encoding utf8
  "pushed" | Out-File -FilePath $LOG -Append -Encoding utf8
} finally {
  Pop-Location
}
