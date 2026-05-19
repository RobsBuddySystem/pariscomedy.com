# Windows hourly ticket-status validator for pariscomedy.com.
# Invokes the existing Python validator + bake step, then rsyncs results
# back to the Mac Studio if reachable.
$ErrorActionPreference = "Stop"
$REPO    = "C:\pariscomedy\_repo"
$LOG     = "C:\pariscomedy\logs\hourly.log"
$MAC     = "chuck@macstudio.tail6669ff.ts.net"
$MAC_REPO = "/Users/chuck/Documents/Claude/Projects/pariscomedy.com/_repo"

New-Item -ItemType Directory -Force -Path (Split-Path $LOG) | Out-Null
"=== $(Get-Date -Format o) ===" | Tee-Object -FilePath $LOG -Append

Push-Location $REPO
try {
  # Confirm Ollama is up (for any LLM-assisted classification later)
  try {
    $r = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -UseBasicParsing
    "Ollama OK ($($r.StatusCode))" | Tee-Object -FilePath $LOG -Append
  } catch {
    "Ollama NOT reachable on :11434 — $($_.Exception.Message)" | Tee-Object -FilePath $LOG -Append
  }

  # Run validator + bake
  python scripts\validate_tickets.py 2>&1 | Tee-Object -FilePath $LOG -Append
  python scripts\bake_shows.py        2>&1 | Tee-Object -FilePath $LOG -Append

  # Sync results to Mac Studio (best-effort; ssh + scp via Tailscale)
  try {
    scp -o ConnectTimeout=8 -o BatchMode=yes `
      data\shows_generated.json data\review_queue.json `
      "$MAC`:$MAC_REPO/data/" 2>&1 | Tee-Object -FilePath $LOG -Append
    "synced to Mac" | Tee-Object -FilePath $LOG -Append
  } catch {
    "Mac sync failed: $($_.Exception.Message)" | Tee-Object -FilePath $LOG -Append
  }
} finally {
  Pop-Location
}
