# Import required libraries
import requests
import time
from datetime import datetime, timedelta, timezone
import json

# Function to load GitHub token from .env file
def load_env():

    with open("../../.env") as f:
        for line in f:
            # Look for the line containing GitHub token
            if line.startswith("GITHUB_TOKEN"):
                return line.strip().split("=")[1]
    return None

# Initialize GitHub authentication
GITHUB_TOKEN = load_env()
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Fetch all merged pull requests for a given repository
def fetch_merged_prs(repo):

    url = f"https://api.github.com/repos/{repo}/pulls?state=closed&sort=updated&direction=desc"
    print(f"Fetching PRs in {repo}")

    # 0.5 seconds delay to be nice to GitHub API
    time.sleep(0.5)
    response = requests.get(url, headers=HEADERS)

    # If there was a 404 error
    if response.status_code == 404:
        print(f"404 Client Error {repo}\n")
        return []  # Proceed with an empty list
    elif response.status_code != 200:
        print(f"Error {response.status_code} for {repo}\n")
        return []  # Proceed with an empty list
    
    # Get yesterday's merged PRs
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    yesterday_date = yesterday.strftime("%Y-%m-%d")
    return [pr for pr in response.json() if pr.get("merged_at") and pr["merged_at"].startswith(yesterday_date)]

# Fetch commits with specific fields from a single merged pull request
def fetch_filtered_commits_from_pr(repo, pr_number):

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits"
    print(f"Fetching commits for PR #{pr_number} in {repo}")

    # 0.5 seconds delay to be nice to GitHub API
    time.sleep(0.5)
    response = requests.get(url, headers=HEADERS)

    # If there was a 404 error
    if response.status_code == 404:
        print(f"404 Client Error for PR #{pr_number}\n")
        return []  # Proceed with an empty list
    elif response.status_code != 200:
        print(f"Error {response.status_code} for PR #{pr_number}\n")
        return []  # Proceed with an empty list

    # Get PR commits
    filtered_commits = []
    for commit in response.json():
        filtered_commits.append({
            "message": commit["commit"]["message"],
            "html_url": commit["html_url"],
            "author_login": commit["author"]["login"] if commit.get("author") else None,
            "author_avatar_url": commit["author"]["avatar_url"] if commit.get("author") else None
        })
    return filtered_commits

# Process multiple repositories and generate JSON files with PR data
def scan_repos(protocols):

    all_data = []  # Store all PRs across all repos
    
    for protocol in protocols:
        for repo in protocol["assetUrls"]:

            # Get prs
            prs = fetch_merged_prs(repo.replace("https://github.com/", ""))

            # Skip this iteration if no prs
            if not prs:
                continue 

            if "prs" not in protocol:
                protocol["prs"] = []

            for pr in prs:

                # Clear PR body if it's from dependabot
                if pr["user"]["login"] == "dependabot[bot]":
                    pr["body"] = ""
                
                # Get first characters of body if any
                body = pr.get("body", "")
                truncated_body = body[:400] if body else ""

                # Get commits
                commits = fetch_filtered_commits_from_pr(repo.replace("https://github.com/", ""), pr["number"])

                # Extract relevant information
                pr_data = {
                        "repo": repo.replace("https://github.com/", ""),
                        "merged_at": pr["merged_at"].replace('T', ' ').replace('Z', ' '),
                        "title": pr["title"],
                        "truncated_body": truncated_body,
                        "user_login": pr["user"]["login"],
                        "user_avatar_url": pr["user"]["avatar_url"],
                        "repo_owner_avatar_url": pr["base"]["repo"]["owner"]["avatar_url"],
                        "repo_owner_login": pr["base"]["repo"]["owner"]["login"],
                        "html_link": pr["_links"]["html"],
                        "commits_link": pr["_links"]["commits"],
                        "commits": commits,
                }
                protocol["prs"].append(pr_data)

        if "prs" in protocol:
            all_data.append(protocol)

    # Save all PR data
    with open("./all_prs.json", "w") as file:
        file.write(str(json.dumps(all_data)))
    
# Script entry point
if __name__ == "__main__":

    # List of repositories to scan
    protocols = []
    with open('./all_protocols.json', 'r') as f:
        protocols = json.load(f)

    # Scan!
    scan_repos(protocols)
