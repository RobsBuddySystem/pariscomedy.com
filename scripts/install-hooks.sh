#!/usr/bin/env bash
# install-hooks.sh — install local git hooks for this repo.
# Installs a commit-msg hook that enforces the pariscomedy.com commit standard
# via scripts/validate-commit-msg.sh. Safe to re-run.

set -eu

repo_root="$(git rev-parse --show-toplevel)"
hooks_dir="$repo_root/.git/hooks"
mkdir -p "$hooks_dir"

cat > "$hooks_dir/commit-msg" <<'HOOK'
#!/usr/bin/env bash
# Auto-installed by scripts/install-hooks.sh — do not edit here.
repo_root="$(git rev-parse --show-toplevel)"
exec "$repo_root/scripts/validate-commit-msg.sh" "$1"
HOOK
chmod +x "$hooks_dir/commit-msg"

echo "✓ commit-msg hook installed → $hooks_dir/commit-msg"
echo "  Enforces: YYYY-MM-DD HH:MM TZ | area | summary"
