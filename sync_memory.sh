#!/bin/bash
# Weekly memory sync — copies /root/.claude/projects/-root/memory/ to
# /root/Claude-AI-md-files/memory/ and pushes changes to GitHub.
# If nothing changed: log it and exit clean. Triggered by sync-memory.timer.
set -uo pipefail

REPO=/root/Claude-AI-md-files
SRC=/root/.claude/projects/-root/memory/
DST=$REPO/memory/
LOG=$REPO/logs/sync.log
TG_BOT_TOKEN_FILE=/root/4BotsBybit-Trading/.env

mkdir -p "$REPO/logs" "$DST"
TS=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
echo "[$TS] sync start" >> "$LOG"

cd "$REPO"

# Sync
rsync -a --delete "$SRC" "$DST" >> "$LOG" 2>&1

# Detect changes
git add -A
if git diff --cached --quiet; then
    MSG="memory sync $(date -u +%F): no changes this week"
    echo "[$TS] $MSG" >> "$LOG"
else
    # Build a short commit message listing basenames touched
    CHANGED=$(git diff --cached --name-only --diff-filter=AMD | sed 's|^memory/||' | tr '\n' ' ' | head -c 500)
    git -c commit.gpgsign=false commit -q -m "Weekly memory sync $(date -u +%F)

Touched: $CHANGED

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    PUSH_OUT=$(git push 2>&1)
    PUSH_RC=$?
    if [ $PUSH_RC -eq 0 ]; then
        N=$(echo "$CHANGED" | wc -w)
        MSG="memory sync $(date -u +%F): synced $N files, pushed"
    else
        MSG="memory sync $(date -u +%F): push FAILED — $PUSH_OUT"
    fi
    echo "[$TS] $MSG" >> "$LOG"
fi

# Telegram report (best-effort) — uses the trading control-bot creds
if [ -f "$TG_BOT_TOKEN_FILE" ]; then
    TOKEN=$(grep -m1 '^CLAUDE_BRIDGE_BOT_TOKEN=\|^TELEGRAM_REPORT_BOT_TOKEN=' "$TG_BOT_TOKEN_FILE" | head -1 | cut -d= -f2-)
    CHAT=$(grep -m1 '^CLAUDE_OPERATOR_CHAT_ID=\|^TELEGRAM_CHAT_ID=' "$TG_BOT_TOKEN_FILE" | head -1 | cut -d= -f2-)
    if [ -n "$TOKEN" ] && [ -n "$CHAT" ]; then
        curl -sS -m 10 -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
            --data-urlencode "chat_id=${CHAT}" \
            --data-urlencode "text=📦 ${MSG}" \
            >> "$LOG" 2>&1 || true
    fi
fi

echo "[$TS] sync end" >> "$LOG"
exit 0
