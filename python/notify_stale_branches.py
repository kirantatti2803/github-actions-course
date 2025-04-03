import os
import requests
import smtplib
from email.mime.text import MIMEText

# GitHub API & Auth
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")

# Email Configuration
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# Constants
EXCLUDED_BRANCHES = ["main", "develop"]  # Branches to ignore
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_branches():
    """Fetch all branches from GitHub."""
    url = f"https://api.github.com/repos/{REPO_NAME}/branches"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print("❌ Failed to fetch branches:", response.json())
        return []
    
    return response.json()

def get_commit_author(branch_name):
    """Fetch the commit author's email for a given branch."""
    url = f"https://api.github.com/repos/{REPO_NAME}/commits/{branch_name}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"⚠️ Failed to fetch commit data for branch {branch_name}")
        return None, None

    commit_data = response.json()
    author_name = commit_data.get("commit", {}).get("author", {}).get("name")
    author_email = commit_data.get("commit", {}).get("author", {}).get("email")

    if not author_email or "noreply" in author_email:
        print(f"⚠️ Email for {branch_name} is private or missing.")
        return author_name, None

    return author_name, author_email

def send_email(recipient, branch_name):
    """Send email to the branch owner."""
    subject = f"🚨 Stale Branch Notification: {branch_name}"
    body = f"""
    Hi,

    The branch '{branch_name}' in the repository '{REPO_NAME}' has been identified.
    Please review or delete it if it is no longer needed.

    Thanks,
    GitHub Admin
    """

    msg = MIMEText(body)
    msg["From"] = GMAIL_USER
    msg["To"] = recipient
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, recipient, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {recipient} for branch {branch_name}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def main():
    """Main script execution."""
    branches = get_branches()
    for branch in branches:
        branch_name = branch["name"]

        # Skip main and develop branches
        if branch_name in EXCLUDED_BRANCHES:
            continue

        author_name, author_email = get_commit_author(branch_name)

        if author_email:
            send_email(author_email, branch_name)
        else:
            print(f"⚠️ No valid email found for {branch_name}")

if __name__ == "__main__":
    main()
