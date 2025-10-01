# What is DAF

DAF is a daily activity feed that tracks recent bug fixes and code changes in GitHub repositories enrolled in Immunefi bug bounty programs. Each day, protocols update their code to address vulnerabilities or add features. DAF brings these updates from across the Web3 ecosystem into one place.

Website (demo): [https://infosec-us-team.github.io/daf/frontend-daf/src/](https://infosec-us-team.github.io/daf/frontend-daf/src/)

> At the time of writing, there are **427 GitHub repositories** with a bug bounty program in Immunefi.

<img src="./readme-resources/ui1.png" alt="" style="width:600px; height:auto;">

# Table of Contents

- [How to use it](#how-to-use-it)
- [Architecture](#architecture)
- [Run locally](#run-locally)
- [Using a cron job to run periodically](#using-a-cron-job-to-run-periodically)
- [Maintenance](#maintenance)

# How to use it

This repo helps you generate a static site with all pull requests merged today in all GitHub repositories listed as assets in scope in Immunefi.

Monitor when protocols add new features or discover security patches by searching for the words "fix" and "bug" in the title of pull requests and commit messages.

The site includes:

- Pull requests, including their title, date, and a link to the PR
- Every commit, including its title and a link to it
- The Developer of every commit, including its name, avatar, and a link to their GitHub user
- Protocol name, avatar, and a link to the GitHub account
- The rewards ($) for every severity on the bug bounty program, and a link to it

# Architecture

DAF has a **backend** and a **frontend**.

## Backend

The **backend** automates gathering GitHub repositories listed in Immunefi, extracting bounty information, scanning pull requests and commits, and generating a static website (the frontend).

## Frontend

A static site using Tailwind CSS.

# Run locally

### Requirements

- [ibb](https://github.com/infosec-us-team/ibb/) - A CLI tool to find anything from Immunefi REST API with as few keystrokes as possible (by `infosec_us_team`)
- [jq](https://github.com/jqlang/jq) - JSON processor for command-line data manipulation
- Python 3.x environment

Clone the repository:

```bash
git clone https://github.com/infosec-us-team/daf.git
cd daf
```

To avoid hitting GitHub's API rate limit, use a [personal access token](https://github.com/settings/personal-access-tokens).

Create a `.env` file outside of the project folder (yes, outside... don't trust your .gitignore skills; better safe than sorry).
> Your file structure should look like this:

```
.env
daf/
 ├─backend-daf/
 ├─frontend-daf/
 ├─readme-resources/
 └─README.md
```

Add your personal access token to the `.env` file:

```
GITHUB_TOKEN=your_token_here
```

### Monitor all repositories

**Step 1-** Get an updated list of protocols and assets in scope from Immunefi.

```bash
# First, cd into `./backend-daf/`
cd backend-daf

./read-protocols-from-immunefi.sh
```

**Step 2:** Scan for pull requests merged today in all GitHub repositories in scope.

```bash
python3 ./scan-all-prs.py
```

**Step 3-** Generate a static site with the data.

```bash
python3 ./create-static-site-for-all-protocols.py
```

You should have a static site at `./frontend-daf/src/index.html`

**Step 4-** Run an HTTP server so you can access the site with all devices in the local network.

```bash
# cd out of backend-daf and into frontend-daf
cd ../frontend-daf/src/

# run the http server
python3 -m http.server 8000
```

### Monitor target repositories

**Step 1-** Create a list of targets at `./backend-daf/targets.json` in the following format:

```json
{
  "targets": [
    "layerzero",
    "reserve"
  ]
}
```

> Use the ID of the bug bounty program, as seen in Immunefi's API or ibb.

**Step 2-** Get an updated list of assets in scope from Immunefi.

```bash
# First, cd into `./backend-daf/`
cd backend-daf

./read-target-protocols-from-immunefi.sh
```

**Step 3:** Scan for pull requests merged today in your target's GitHub repositories.

```bash
python3 ./scan-target-prs.py
```

**Step 3-** Generate a static site with the data.

```bash
python3 ./create-static-site-for-target-protocols.py
```

You should have a static site at `./frontend-daf/src/targets.html`

**Step 4-** Run an HTTP server so you can access the site with all devices in the local network.

```bash
# cd out of backend-daf and into frontend-daf
cd ../frontend-daf/src/

# run the http server
python3 -m http.server 8000
```

# Using a cron job to run periodically

You can also create a script that runs steps 1 to 4, and use a crontab to automate the process.

Open crontab:

```bash
crontab -e
```

Add a job:

```bash
0 1 * * * /path/to/script.sh
```

This runs your script daily at 1am.

# Maintenance

There is no guarantee that the code in this repository will be maintained if Immunefi or GitHub changes their APIs.
