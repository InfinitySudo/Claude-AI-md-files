---
name: Auto-push enabled by default (2026-05-02)
description: Артём не хочет пушить руками — Claude-сессии должны делать commit+push сразу, во всех репо включая trading
type: feedback
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
**Правило:** После любого работающего commit'а — сразу `git push`. Не «пуш делает Артём руками», не «локально только», не «спроси сначала».

**Why:** Артём 2026-05-02 явно сказал «я не буду делать это руками, нужно реализовать авто». До этого `4BotsBybit-Trading/CLAUDE.md` имел жёсткое правило `git push — только локальные коммиты` (защита от плохих авто-правок). Артём осознанно его снял — он предпочитает скорость и автоматизм над защитой через manual gating.

**How to apply:**
1. После `git commit` → сразу `git push`. Считай это атомарной парой.
2. Исключения когда НЕ пушить:
   - Локальные эксперименты в feature-ветке которая ещё не готова — спроси
   - `git push --force` к main/master — НИКОГДА без явного «force push, я знаю» от Артёма
   - Если push fails (auth/network) — не повторяй слепо в цикле, докладывай ошибку
3. Если push оказался ошибочным — `git revert` + commit + push (forward fix). НЕ `git reset --hard` + `push --force`.

**Где зафиксировано:**
- `/root/.claude/MOBILE_RULES.md` §5 «COMMIT + PUSH AS CHECKPOINT»
- `/root/4BotsBybit-Trading/CLAUDE.md` — жёсткое правило про push снято, заменено на «push разрешён, force-push к master нельзя»
- Backup `MOBILE_RULES.md` в `Claude-AI-md-files/` через `sync_memory.sh` чтобы пережить VPS-rebuild

**Trade-off, который Артём принял:** плохой автоправящий agent может зафейлиться на тесты и всё равно закоммитить + запушить. Защита теперь на уровне:
- Pre-commit: тесты должны зелёными — иначе MOBILE_RULES запрещает commit
- Pytest fail = не пуш (явно прописано в trading CLAUDE.md)
- Forward-fix через revert если плохое улетело
