#!/usr/bin/env bash
# dev-check.sh — local pre-commit sanity checks for the frontend repo.
# Run before pushing. Exit 0 only if all checks pass.

set -u
cd "$(git rev-parse --show-toplevel)"
fail=0
ok()  { echo "  ok    $1"; }
bad() { echo "  FAIL  $1"; fail=1; }

echo "== frontend dev-check =="

# 1. api-config.json must point at production (not localhost)
if grep -q 'api.pariscomedy.com' api-config.json 2>/dev/null; then
  ok "api-config.json → production API"
else
  bad "api-config.json does NOT point at https://api.pariscomedy.com"
fi

# 2. Shell scripts are executable + have a shebang
for s in scripts/*.sh; do
  [ -e "$s" ] || continue
  head -1 "$s" | grep -q '^#!' || bad "$s missing shebang"
  [ -x "$s" ] || bad "$s not executable (chmod +x)"
done
[ "$fail" -eq 0 ] && ok "shell scripts well-formed"

# 3. No secret-ish files staged
if git diff --cached --name-only | grep -qE '\.env$|backend/env$'; then
  bad "env/secret file staged for commit"
else
  ok "no secret files staged"
fi

# 4. gitleaks if available
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --no-banner 2>&1 | grep -q "no leaks found" && ok "gitleaks clean" || bad "gitleaks found secrets"
else
  echo "  skip  gitleaks not installed locally (CI still runs it)"
fi

echo
[ "$fail" -eq 0 ] && echo "dev-check: PASS" || echo "dev-check: FAIL"
exit "$fail"
