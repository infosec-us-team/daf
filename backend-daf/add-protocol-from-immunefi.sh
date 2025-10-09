#!/bin/bash

# Append a single Immunefi protocol entry to target_protocols.json
# Usage: ./add-protocol-from-immunefi.sh <protocol_name>

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <protocol_name>" >&2
  exit 1
fi

target_name="$1"
output_json="target_protocols.json"

echo "Adding protocol: $target_name"

# Ensure output file exists and is a valid JSON array
if [[ ! -f "$output_json" || ! -s "$output_json" ]]; then
  echo "[]" >"$output_json"
fi

# Validate existing JSON structure
if ! jq empty "$output_json" >/dev/null 2>&1; then
  echo "Error: $output_json is not valid JSON." >&2
  exit 1
fi

# Check if protocol already exists
if jq -e --arg name "$target_name" 'map(.protocol) | index($name) | . != null' "$output_json" >/dev/null; then
  echo "Protocol '$target_name' already present in $output_json. Skipping." >&2
  exit 0
fi

# Get all available protocols from ibb and verify the requested one exists
all_protocols=$(ibb | jq -r '.[]')
if ! echo "$all_protocols" | grep -Fxq "$target_name"; then
  echo "Error: Protocol '$target_name' not found in Immunefi programs list (ibb)." >&2
  exit 1
fi

echo "Fetching the URLs of all assets in scope for $target_name"
# Allow no matches without failing the script (grep exits 1 when no matches)
urls=$(ibb "$target_name" assets url | grep -oP 'https://github\.com(?:/[^/]+){2}' | tr -d ',"' | sort | uniq || true)
if [[ -z ${urls:-} ]]; then
  urls=""
fi
# Count urls (unique, non-empty)
url_count=0
if [[ -n "$urls" ]]; then
  url_count=$(printf '%s\n' "$urls" | sed '/^$/d' | wc -l | tr -d ' ')
fi

echo "Fetching BBP rewards for $target_name"
# Ensure rewards is always an array (even if ibb returns empty/null)
rewards=$(ibb "$target_name" rewards | jq 'map({severity, maxReward, minReward, fixedReward, payout, assetType, level}) // []')
# Safely read first logo entry or empty string
logo=$(ibb "$target_name" logo | jq -r '.[0] // ""')

# Build protocol JSON object
protocol_data=$(jq -n \
  --arg name "$target_name" \
  --arg logo "$logo" \
  --argjson rewards "$rewards" \
  --argjson urls "$( [[ -z $urls ]] && echo '[]' || printf '%s\n' "$urls" | uniq | jq -R . | jq -s . )" \
  '{
    protocol: $name,
    logo: $logo,
    rewards: $rewards,
    assetUrls: $urls
  }')

tmp_file=$(mktemp)

# Append new object to array
jq --argjson item "$protocol_data" '. + [$item]' "$output_json" >"$tmp_file"
mv "$tmp_file" "$output_json"

echo "Protocol '$target_name' added to $output_json ($url_count repositories)"


