#!/usr/bin/env bash
# Run from public_html: bash set-api-base.sh https://api.yourdomain.com
set -euo pipefail

BASE="${1:-}"
if [[ -z "$BASE" ]]; then
  echo "Usage: bash set-api-base.sh https://api.yourdomain.com" >&2
  exit 1
fi

# Escape slashes for sed
ESC=$(printf '%s' "$BASE" | sed 's/[\/&]/\\&/g')

find . -name index.html -type f -print0 | while IFS= read -r -d '' f; do
  sed -i "s|<meta name=\"heaven-api-base\" content=\"[^\"]*\"/>|<meta name=\"heaven-api-base\" content=\"$ESC\"/>|" "$f"
done

echo "API base set to $BASE in all pages."
