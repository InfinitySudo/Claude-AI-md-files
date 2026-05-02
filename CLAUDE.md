# Claude-AI-md-files

> **Перед работой прочитай `/root/.claude/MOBILE_RULES.md`.**

## Что это
Резервная копия `/root/.claude/projects/-root/memory/` в git. Public/private (узнать) репо для версионирования memory-файлов между сессиями. Из памяти `feedback_sync_memory_on_commit`: «после каждого push в основной репо — синхронизировать память сюда».

## Структура
- `projects/-root/memory/MEMORY.md` + `*.md` — копии файлов из `/root/.claude/projects/-root/memory/`

## Команды
| Действие | Команда |
|---|---|
| Синк памяти | `rsync -av /root/.claude/projects/-root/memory/ /root/Claude-AI-md-files/projects/-root/memory/` |
| Commit + push | `cd /root/Claude-AI-md-files && git add . && git commit -m 'sync memory' && git push` |

## МОЖНО
- Sync + push memory изменений

## НЕЛЬЗЯ
- Изменять memory-файлы прямо здесь — source of truth в `/root/.claude/projects/-root/memory/`. Этот репо только для backup.
- Удалять историю — это full backup памяти

## Mobile-dev specific
- Sync — однострочная операция, OK с телефона. Делай после крупных memory-изменений в основном репо.
