import json

# Script entry point
if __name__ == "__main__":

    # Read all PRs
    with open('./target_prs.json', 'r') as file:
        prs_data = json.load(file)

    # Read template files
    with open('../frontend-daf/src/base-template.html', 'r') as file:
        base_template = file.read()
    with open('../frontend-daf/src/rewards-template.html', 'r') as file:
        rewards_template = file.read()
    with open('../frontend-daf/src/content-template.html', 'r') as file:
        content_template = file.read()
    with open('../frontend-daf/src/pr-template.html', 'r') as file:
        pr_template = file.read()
    with open('../frontend-daf/src/commit-template.html', 'r') as file:
        commit_template = file.read()

    content = ""

    # Replace placeholders with actual data from the PRs JSON file
    for protocol in prs_data:

        pr_activity = ""
        repo_owner_login = ""
        protocol_avatar = protocol['logo']

        for pr in protocol["prs"]:
            commit_activity = ""
            # Commit activity per PR
            for commit in pr["commits"]:
                commit_entry = commit_template.format(
                    commit_link=commit.get('html_url', 'empty_placeholder'),
                    commit_title=commit.get('message', 'empty_placeholder'),
                    github_user_avatar=commit.get('author_avatar_url') or 'https://i.pravatar.cc/20?img=6',
                    github_user_link="https://github.com/"+str(commit.get('author_login') or ''),
                    github_user_name=commit.get('author_login', 'empty_placeholder'),
                )
                commit_activity += commit_entry
            # PR activity
            pr_entry = pr_template.format(
                pull_request_link=pr.get('html_link', {}).get('href', 'empty_placeholder'),
                pull_request_title=pr.get('title', 'empty_placeholder'),
                github_user_avatar=pr.get('user_avatar_url', 'empty_placeholder'),
                github_user_link="https://github.com/"+pr.get('user_login', 'empty_placeholder'),
                github_user_name=pr.get('user_login', 'empty_placeholder'),
                repo_link="https://github.com/"+pr.get('repo_owner_login', 'empty_placeholder'),
                repo=pr.get('repo', 'empty_placeholder'),
                merge_timestamp=pr.get('merged_at', 'empty_placeholder'),
                commit_activity=commit_activity,
            )
            pr_activity += pr_entry
            repo_owner_login = pr.get('repo_owner_login', '')

        # Rewards data
        rewards_data = protocol.get("rewards",{})
        reward_categories = {'smart_contract':[], 'websites_and_applications': [], 'blockchain_dlt': []}
        for entry in rewards_data:
            reward_categories[entry['assetType']].append(entry)
        reward_activity = ""
        rewards_entry = ""
        for assetType in reward_categories:
            if not reward_categories[assetType]:
                continue

            low_reward = "$0"
            medium_reward = "$0"
            high_reward = "$0"
            critical_reward = "$0"
            amount = "$0"

            type_of_reward = "Custom"
            if assetType == "blockchain_dlt":
                type_of_reward = "Blockchain DLT"
            elif assetType == "smart_contract":
                type_of_reward = "Smart Contract"
            elif assetType == "websites_and_applications":
                type_of_reward = "Websites and Applications"

            for reward in reward_categories[assetType]:
                # Amount
                if "maxReward" in reward and reward["maxReward"]:
                    amount = f"<${reward['maxReward']:,.0f}"
                elif "fixedReward" in reward and reward["fixedReward"]:
                    amount = f"${reward['fixedReward']:,.0f}"
                # Amount Backwards-Compatibility (Immunefi used to use "Payout" instead of "fixedReward" and "maxReward")
                elif "payout" in reward and reward["payout"]:
                    amount = reward["payout"]
                # Severity
                if reward["severity"] == "critical":
                    critical_reward = amount
                elif reward["severity"] == "high":
                    high_reward = amount
                elif reward["severity"] == "medium":
                    medium_reward = amount
                elif reward["severity"] == "low":
                    low_reward = amount
                # Severity Backwards-Compatibility (Immunefi used to use "Level" instead of "severity")
                elif reward["level"] == "critical":
                    critical_reward = amount
                elif reward["level"] == "high":
                    high_reward = amount
                elif reward["level"] == "medium":
                    medium_reward = amount
                elif reward["level"] == "low":
                    low_reward = amount
            rewards_entry = rewards_template.format(
                    low_reward = low_reward,
                    medium_reward = medium_reward,
                    high_reward = high_reward,
                    critical_reward = critical_reward,
                    type_of_reward = type_of_reward
                    )
            reward_activity += rewards_entry
                
        # Setup template
        content_entry = content_template.format(
            protocol_link = "https://github.com/"+repo_owner_login,
            protocol_avatar=protocol_avatar,
            rewards=reward_activity,
            bbp_link="https://immunefi.com/bug-bounty/"+protocol.get('protocol',''),
            protocol_name=protocol.get('protocol','').upper(),
            pr_activity=pr_activity,
        )
        content += content_entry

    # Insert the entries into the HTML template
    final_html = base_template.format(content_template=content)
    # Write the final HTML to a file
    with open('../frontend-daf/src/targets.html', 'w') as output_file:
        output_file.write(final_html)

