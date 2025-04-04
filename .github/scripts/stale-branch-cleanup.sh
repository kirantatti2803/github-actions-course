#!/bin/bash

PROTECTED_BRANCHES=("main" "develop" "test")
TODAY=$(date +%s)
CLEANUP_FILE="stale_branches.csv"

touch "$CLEANUP_FILE"

echo "Checking for stale branches in $REPO..."

gh api repos/$REPO/branches --paginate --jq '.[] | {name: .name, date: .commit.commit.author.date, author: .commit.commit.author.name}' | \
while read -r branch; do
    NAME=$(echo "$branch" | jq -r '.name')
    LAST_COMMIT_DATE=$(echo "$branch" | jq -r '.date')
    AUTHOR=$(echo "$branch" | jq -r '.author')

    [[ " ${PROTECTED_BRANCHES[*]} " =~ " ${NAME} " ]] && continue
    [[ "$LAST_COMMIT_DATE" == "null" ]] && continue

    COMMIT_TIMESTAMP=$(date -d "$LAST_COMMIT_DATE" +%s)
    AGE=$(( (TODAY - COMMIT_TIMESTAMP) / 86400 ))

    if [[ $AGE -gt $STALE_DAYS ]]; then
        EMAIL=$(gh api users/$AUTHOR --jq '.email')
        if [[ -z "$EMAIL" || "$EMAIL" == "null" ]]; then
            echo "No valid email for $AUTHOR. Skipping..."
            continue
        fi

        # Check if already notified
        if grep -q "$NAME" "$CLEANUP_FILE"; then
            NOTIFIED_AT=$(grep "$NAME" "$CLEANUP_FILE" | cut -d',' -f3)
            if [[ $TODAY -gt $NOTIFIED_AT ]]; then
                echo "Deleting stale branch $NAME (age: $AGE days)..."
                gh api -X DELETE repos/$REPO/git/refs/heads/$NAME
                echo "Deleted branch: $NAME at $(date)"
            fi
        else
            echo "Notifying $EMAIL about stale branch '$NAME'..."
            SUBJECT="⚠️ Stale Branch Notice: '$NAME'"
            BODY="Hi $AUTHOR,\n\nBranch '$NAME' in $REPO is stale ($AGE days old).\nLink: https://github.com/$REPO/tree/$NAME\nIt will be deleted in $GRACE_PERIOD days unless updated.\n\n- DevSecOps Bot"

            curl --url "smtp://$SMTP_SERVER:$SMTP_PORT" --ssl-reqd \
                --mail-from "$EMAIL_SENDER" --mail-rcpt "$EMAIL" \
                --user "$EMAIL_SENDER:$EMAIL_PASSWORD" \
                -T <(echo -e "From: GitHub Bot <$EMAIL_SENDER>\nTo: $EMAIL\nSubject: $SUBJECT\n\n$BODY")

            # Log it
            echo "$NAME,$EMAIL,$((TODAY + GRACE_PERIOD * 86400))" >> "$CLEANUP_FILE"
        fi
    fi
done
