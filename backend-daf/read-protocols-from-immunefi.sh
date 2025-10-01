#!/bin/bash

# Use IBB to create a list with all GitHub repositories that have an asset listed in Immunefi
echo "Creating a list with all GitHub repositories listed in Immunefi and BBP info:"
# Initialize the JSON array by writing the opening bracket
echo "[" >all_protocols.json
# Loop through each protocol name using 'ibb' to get the data
ibb | jq -r '.[]' | while read -r name; do
  # Fetch URLs from 'ibb' for the protocol
  echo "Fetching the URLs of all assets in scope for $name"
  urls=$(ibb "$name" assets url | grep -oP 'https://github\.com(?:/[^/]+){2}' | tr -d ',"' | sort | uniq)
  # If URLs are found, fetch the rewards and program overview
  if [[ -n $urls ]]; then
    echo "Fetching BBP rewards for $name"
    # Get reward information for the protocol
    rewards=$(ibb "$name" rewards | jq '[.[] | {severity, maxReward, minReward, fixedReward, payout, assetType, level}]')
    logo=$(ibb "$name" logo | jq '.[]' | tr -d '"')
    # Create protocol data as a JSON object
    protocol_data=$(jq -n \
      --arg name "$name" \
      --arg logo "$logo" \
      --argjson rewards "$rewards" \
      --argjson urls "$(printf '%s\n' "$urls" | uniq | jq -R . | jq -s .)" \
      '{
        protocol: $name,
        logo: $logo,
        rewards: $rewards,
        assetUrls: $urls
      }')
    # Add protocol data to the JSON array
    echo "$protocol_data," >>all_protocols.json
  fi
done
# Remove the trailing comma from the last entry in the JSON array
sed -i '$ s/.$//' all_protocols.json
# Close the JSON array with a closing bracket
echo "]" >>all_protocols.json
