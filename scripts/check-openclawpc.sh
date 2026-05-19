#!/usr/bin/env bash
# Diagnose openclawpc reachability + pipeline state.
echo "=== tailscale status ==="
tailscale status 2>&1 | head -30
echo
echo "=== ssh openclawpc 'echo ok' ==="
ssh -o ConnectTimeout=8 -o BatchMode=yes openclawpc "echo ok" 2>&1
echo
echo "=== processes ==="
ssh -o ConnectTimeout=8 -o BatchMode=yes openclawpc "ps aux | grep -iE 'ollama|python|pipeline' | grep -v grep" 2>&1
echo
echo "=== crontab ==="
ssh -o ConnectTimeout=8 -o BatchMode=yes openclawpc "crontab -l" 2>&1
