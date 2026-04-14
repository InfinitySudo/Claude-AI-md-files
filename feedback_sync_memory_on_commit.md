---
name: Sync memory to GitHub on every commit
description: При каждом git commit в 4BotsBybit-Trading — копировать md-файлы памяти в Claude-AI-md-files и пушить
type: feedback
originSessionId: 13ab97bb-8dfe-4655-b013-e399065cc3ba
---
При каждом `git commit + push` в основной репо (`/root/4BotsBybit-Trading`), сразу после пуша синхронизировать память:

```
cp /root/.claude/projects/-root/memory/*.md /root/Claude-AI-md-files/
cd /root/Claude-AI-md-files && git add -A && git commit -m "Sync memory" && git push
```

**Why:** Артём хочет бэкап памяти на GitHub (InfinitySudo/Claude-AI-md-files) всегда актуальный.
**How to apply:** Делать это автоматически после каждого пуша в основной репо, не спрашивая подтверждения.
