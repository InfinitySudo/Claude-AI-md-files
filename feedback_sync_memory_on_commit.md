---
name: Memory checkpoint + sync on every commit
description: Перед/после git push — записать в memory всё новое из сессии, потом синхронизировать в Claude-AI-md-files
type: feedback
originSessionId: 13ab97bb-8dfe-4655-b013-e399065cc3ba
---
**Правило**: каждый раз когда я делаю `git commit + git push` в любой основной репо, ОБЯЗАТЕЛЬНО:

1. **Checkpoint сессии в memory** — пройти по тому что только что сделал и решить:
   - Появилась новая фича / поменялся контракт API / изменилась архитектура → создать или обновить **project** memory
   - Артём дал явное указание ("делай так", "не делай этак", "вот это правильно") → создать **feedback** memory
   - Вылезли подводные камни / нюансы которые нужны в будущих сессиях → **feedback** memory с **Why:/How to apply:**
   - Новый внешний ресурс (бот, дашборд, эндпоинт) — **reference** memory
   - НЕ записывать: чистый code-pattern, банальный fix, что есть в `git log` или в коде
2. **Обновить `MEMORY.md` index** — каждой новой/изменённой memory одна строка с понятным якорем
3. **Синхронизировать в backup-репо**:
   ```
   cp /root/.claude/projects/-root/memory/*.md /root/Claude-AI-md-files/
   cd /root/Claude-AI-md-files && git add -A && git commit -m "Sync memory: <тема>" && git push
   ```

**Why:** Артём хочет, чтобы каждая сессия оставляла след в долговременной памяти, а не растворялась после `/clear`. Бэкап-репо (`InfinitySudo/Claude-AI-md-files`) — single source of truth для cross-machine sync.

**How to apply:** Делать молча, без подтверждений. Если ничего checkpoint-достойного в сессии не было — всё равно сделать sync (память могла измениться в других файлах).
