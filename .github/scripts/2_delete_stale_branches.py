# 2_delete_stale_branches.py

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REPO = "kirantatti2803/github-actions-course"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def delete_branch(branch_name):
    url = f"https://api.github.com/repos/{REPO}/git/refs/heads/{branch_name}"
    resp = requests.delete(url, headers=headers)
    if resp.status_code == 204:
        print(f"🗑️ Deleted branch: {branch_name}")
    else:
        print(f"⚠️ Failed to delete {branch_name}: {resp.status_code}")

def main():
    today = datetime.utcnow()
    if not os.path.exists("stale_branches.csv"):
        print("📄 No stale_branches.csv found.")
        return

    with open("stale_branches.csv", "r") as f:
        lines = f.readlines()

    with open("stale_branches.csv", "w") as f:
        for line in lines:
            name, email, delete_date = line.strip().split(",")
            if datetime.strptime(delete_date, "%Y-%m-%d") <= today:
                delete_branch(name)
            else:
                f.write(line)

if __name__ == "__main__":
    main()
