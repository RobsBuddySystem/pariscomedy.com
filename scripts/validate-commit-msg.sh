#!/usr/bin/env bash
# validate-commit-msg.sh — enforce the pariscomedy.com commit message standard.
# Usage: validate-commit-msg.sh <path-to-commit-msg-file>
# Standard: YYYY-MM-DD HH:MM TZ | area | summary
#   area = frontend | backend | data | infra | docs
# Exit 0 if valid, 1 if not.

set -u

msg_file="${1:-}"
if [ -z "$msg_file" ] || [ ! -f "$msg_file" ]; then
  echo "validate-commit-msg: no commit message file given" >&2
  exit 1
fi

first_line="$(grep -v '^#' "$msg_file" | sed '/^[[:space:]]*$/d' | head -1)"

# Allow merge/revert commits through untouched.
case "$first_line" in
  "Merge "*|"Revert "*) exit 0 ;;
esac

pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} [A-Za-z][A-Za-z0-9+-]+ \| (frontend|backend|data|infra|docs) \| .+'

if echo "$first_line" | grep -qE "$pattern"; then
  exit 0
fi

cat >&2 <<EOF
✗ Commit message REJECTED — does not match the pariscomedy.com standard.

  Required : YYYY-MM-DD HH:MM TZ | area | summary
  area     : frontend | backend | data | infra | docs
  Example  : 2026-05-22 20:30 CEST | backend | add venue delete endpoint

  Got      : ${first_line:-<empty>}

Tip: date "+%Y-%m-%d %H:%M %Z"
EOF
exit 1
