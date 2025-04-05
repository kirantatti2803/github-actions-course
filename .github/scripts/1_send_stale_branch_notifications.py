# 1_send_stale_branch_notifications.py

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

REPO = "kirantatti2803/github-actions-course"
PROTECTED_BRANCHES = ["main", "development", "test"]
STALE_DAYS = 1
GRACE_PERIOD_DAYS = 7

GITHUB_TOKEN = ${{ vars.GIT_CLI_TOKEN }}
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def fetch_branches():
    url = f"https://api.github.com/repos/{REPO}/branches"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Failed to fetch branches: {resp.status_code}")
        return []
    return resp.json()

def get_commit_info(branch):
    sha = branch["commit"]["sha"]
    url = f"https://api.github.com/repos/{REPO}/commits/{sha}"
    resp = requests.get(url, headers=headers).json()
    author = resp.get("commit", {}).get("author", {}).get("name", "")
    email = resp.get("commit", {}).get("author", {}).get("email", "")
    date = resp.get("commit", {}).get("author", {}).get("date", "")
    return author, email, date

def main():
    today = datetime.utcnow()
    branches = fetch_branches()

    report_lines = []

    for branch in branches:
        name = branch["name"]
        if name in PROTECTED_BRANCHES:
            continue

        author, email, date_str = get_commit_info(branch)
        if not email or not date_str:
            continue

        last_commit = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        age = (today - last_commit).days

        if age > STALE_DAYS:
            delete_date = today + timedelta(days=GRACE_PERIOD_DAYS)
            report_lines.append(
                f"{name},{email},{author},{age} days old, Delete on {delete_date.date()}"
            )
            with open("stale_branches.csv", "a") as f:
                f.write(f"{name},{email},{delete_date.date()}\n")

    # Write to a file to be sent as an attachment
    if report_lines:
        os.makedirs("_github_workflow", exist_ok=True)
        with open("_github_workflow/stale_branch_report.txt", "w") as report:
            report.write("Branch Name,Email,Author,Age,Deletion Date\n")
            report.write("\n".join(report_lines))

if __name__ == "__main__":
    main()


