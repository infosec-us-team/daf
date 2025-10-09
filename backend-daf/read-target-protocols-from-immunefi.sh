#!/bin/bash

# Use IBB to create a list with GitHub repositories for specified protocols in targets.json
echo "Creating a list with GitHub repositories for target protocols from targets.json:"

# Read target protocols from targets.json
if [[ ! -f "targets.json" ]]; then
  echo "Error: targets.json file not found!" >&2
  exit 1
fi

# Extract protocol names from targets.json (assuming format: {"targets": ["protocol1", "protocol2", ...]})
targets_json=$(jq -r '.targets // empty' targets.json)
if [[ -z "$targets_json" ]]; then
  echo "Error: targets.json must contain a 'targets' array!" >&2
  exit 1
fi

# Convert JSON array to bash array
mapfile -t target_protocols < <(jq -r '.targets[]' targets.json)

# Check if we have any targets
if [[ ${#target_protocols[@]} -eq 0 ]]; then
  echo "Error: No target protocols found in targets.json!" >&2
  exit 1
fi

echo "Target protocols: ${target_protocols[*]}"

# Initialize the JSON array by writing the opening bracket
echo "[" >target_protocols.json

# Get all available protocols from ibb
all_protocols=$(ibb | jq -r '.[]')

# Loop through each target protocol
for target_name in "${target_protocols[@]}"; do
  # Check if the target protocol exists in the available protocols
  if echo "$all_protocols" | grep -Fxq "$target_name"; then
    echo "Processing protocol: $target_name"

    # Fetch URLs from 'ibb' for the protocol
    echo "Fetching the URLs of all assets in scope for $target_name"
    urls=$(ibb "$target_name" assets url | grep -oP 'https://github\.com(?:/[^/]+){2}' | tr -d ',"' | sort | uniq)

    if [[ -z $urls ]]; then
      urls=""
    fi

    echo "Fetching BBP rewards for $target_name"
    # Get reward information for the protocol
    rewards=$(ibb "$target_name" rewards | jq '[.[] | {severity, maxReward, minReward, fixedReward, payout, assetType, level}]')
    logo=$(ibb "$target_name" logo | jq '.[]' | tr -d '"')

    # Create protocol data as a JSON object
    protocol_data=$(jq -n \
      --arg name "$target_name" \
      --arg logo "$logo" \
      --argjson rewards "$rewards" \
      --argjson urls "$([[ -z $urls ]] && echo '[]' || printf '%s\n' "$urls" | uniq | jq -R . | jq -s .)" \
      '{
        protocol: $name,
        logo: $logo,
        rewards: $rewards,
        assetUrls: $urls
      }')

    # Add protocol data to the JSON array
    echo "$protocol_data," >>target_protocols.json
  else
    echo "Warning: Protocol '$target_name' not found in available protocols, skipping..."
  fi
done

# Remove the trailing comma from the last entry in the JSON array (if file is not empty)
if [[ -s target_protocols.json ]]; then
  # Check if the file only contains "[" (no protocols processed)
  if [[ "$(cat target_protocols.json)" == "[" ]]; then
    echo "]" >target_protocols.json
  else
    sed -i '$ s/,$//' target_protocols.json
    # Close the JSON array with a closing bracket
    echo "]" >>target_protocols.json
  fi
else
  # If file doesn't exist or is empty, create empty array
  echo "[]" >target_protocols.json
fi

echo "Processing complete. Results saved to target_protocols.json"
