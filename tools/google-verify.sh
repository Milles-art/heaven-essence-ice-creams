#!/usr/bin/env bash
# Install Google Search Console HTML-file verification on the live server.
# Usage: bash tools/google-verify.sh abc123TOKEN
set -euo pipefail

TOKEN="${1:-}"
if [[ -z "$TOKEN" ]]; then
  echo "Usage: bash tools/google-verify.sh <verification-token>" >&2
  exit 1
fi

FILE="google${TOKEN}.html"
TMP="$(mktemp)"
printf 'google-site-verification: %s\n' "$FILE" > "$TMP"

for D in /home/afyabgzo/heavenessence.co.tz /home/afyabgzo/family-choice/backend/public; do
  scp -o BatchMode=yes "$TMP" "afyaguard:${D}/${FILE}" && ssh -o BatchMode=yes afyaguard "chmod 644 ${D}/${FILE}"
done

rm -f "$TMP"
echo "Installed ${FILE}. Now click Verify in Google Search Console."
