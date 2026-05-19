#!/usr/bin/env bash
# Diagnose openclawpc reachability + pipeline state.
# Auto-detects Windows vs *nix and uses the appropriate command shell.
set -u
HOST="openclawpc"
SSH="ssh -o ConnectTimeout=8 -o BatchMode=yes $HOST"

echo "=== tailscale status ==="
tailscale status 2>&1 | head -30
echo
echo "=== ssh $HOST 'echo ok' ==="
$SSH "echo ok" 2>&1
echo

OS=$($SSH "uname -s 2>/dev/null || echo Windows" 2>/dev/null | tr -d '\r\n ')
echo "=== detected OS: $OS ==="
echo

if [[ "$OS" == "Windows" || "$OS" == *MINGW* || "$OS" == *CYGWIN* ]]; then
  echo "=== processes (Get-Process) ==="
  $SSH 'powershell -NoProfile -Command "Get-Process | ? { $_.ProcessName -match '\''ollama|python|node|openclaw'\'' } | Select ProcessName,Id,CPU | Format-Table -AutoSize"' 2>&1
  echo
  echo "=== scheduled tasks (Get-ScheduledTask) ==="
  $SSH 'powershell -NoProfile -Command "Get-ScheduledTask | ? { $_.TaskName -match '\''paris|comedy|openclaw|ollama'\'' } | Select TaskName,State | Format-Table -AutoSize"' 2>&1
  echo
  echo "=== services (Get-Service) ==="
  $SSH 'powershell -NoProfile -Command "Get-Service | ? { $_.Name -match '\''ssh|tailscale|ollama'\'' } | Select Name,Status | Format-Table -AutoSize"' 2>&1
  echo
  echo "=== where python ==="
  $SSH 'where python' 2>&1
  echo
  echo "=== where ollama ==="
  $SSH 'where ollama' 2>&1
else
  echo "=== processes ==="
  $SSH "ps aux | grep -iE 'ollama|python|pipeline' | grep -v grep" 2>&1
  echo
  echo "=== crontab ==="
  $SSH "crontab -l" 2>&1
fi
