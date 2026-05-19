#!/usr/bin/env bash
# Diagnose openclawpc reachability + pipeline state.
# Auto-detects Windows vs *nix and uses appropriate commands.
set -u
HOST="openclawpc"

echo "=== tailscale status ==="
tailscale status 2>&1 | head -30
echo
echo "=== ssh $HOST 'echo ok' ==="
ssh -o ConnectTimeout=8 -o BatchMode=yes "$HOST" "echo ok" 2>&1
echo

# Detect OS via uname (fails on Windows → fall through to powershell branch)
OS=$(ssh -o ConnectTimeout=8 -o BatchMode=yes "$HOST" "uname -s 2>/dev/null || echo Windows" 2>/dev/null)
echo "=== detected OS: $OS ==="
echo

if [[ "$OS" == "Windows" || "$OS" == *"MINGW"* || "$OS" == *"CYGWIN"* ]]; then
  echo "=== processes (PowerShell) ==="
  ssh "$HOST" "powershell -NoProfile -Command \"Get-Process | Where-Object { \$_.ProcessName -match 'ollama|python|node|openclaw' } | Select-Object ProcessName,Id,CPU | Format-Table -AutoSize\"" 2>&1
  echo
  echo "=== scheduled tasks ==="
  ssh "$HOST" "powershell -NoProfile -Command \"Get-ScheduledTask | Where-Object { \$_.TaskName -match 'paris|comedy|openclaw|ollama' } | Select-Object TaskName,State | Format-Table -AutoSize\"" 2>&1
  echo
  echo "=== services ==="
  ssh "$HOST" "powershell -NoProfile -Command \"Get-Service | Where-Object { \$_.Name -match 'ssh|tailscale|ollama' } | Select-Object Name,Status,StartType | Format-Table -AutoSize\"" 2>&1
  echo
  echo "=== where python / ollama ==="
  ssh "$HOST" "where python 2>&1; where ollama 2>&1" 2>&1
else
  echo "=== processes ==="
  ssh "$HOST" "ps aux | grep -iE 'ollama|python|pipeline' | grep -v grep" 2>&1
  echo
  echo "=== crontab ==="
  ssh "$HOST" "crontab -l" 2>&1
fi
