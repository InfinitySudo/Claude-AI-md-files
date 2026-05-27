---
name: Verify downloads before use
description: Перед использованием/запуском любого файла, скачанного из GitHub releases / HuggingFace / npm / pip / любого внешнего источника — провести базовую проверку на вирусы и валидность
type: feedback
originSessionId: 8d2f9d7c-3290-489b-addf-b57a4e9806fa
---
Скачивание ML-моделей, бинарников и пакетов из открытых источников = чужой код/данные на инфраструктуре Артёма. Базовая проверка обязательна перед `pip install`, `python serve.py` или регистрацией scheduled-task.

**Why:** Артём явно попросил "не словим ли вирусов" → закрепил как правило 2026-05-09. ПК1 — его рабочая машина, VPS — production. Один заражённый ONNX-runtime custom-op или npm postinstall = проблема. Один раз потратить 30 секунд лучше, чем потом разбирать инцидент.

**How to apply:**

Перед использованием делать минимум 3 проверки + сообщать пользователю результат:

1. **Source reputation** — проверить через GitHub API:
   ```bash
   curl -s "https://api.github.com/repos/<owner>/<repo>" | python3 -c "import sys, json; r=json.load(sys.stdin); print(f'stars={r[\"stargazers_count\"]}, license={r[\"license\"][\"spdx_id\"] if r.get(\"license\") else \"none\"}, archived={r[\"archived\"]}')"
   ```
   Минимум: license есть, ≥100 stars или известный автор/организация (huggingface, microsoft, openai, anthropic, etc), не archived.

2. **SHA256 checksum** — посчитать у скачанного файла, при возможности сверить с release notes / опубликованным hash:
   - На VPS: `sha256sum file.bin`
   - На ПК1: `Get-FileHash -Algorithm SHA256 file.bin`

3. **File type validation** — открыть файл нативным парсером (не запускать), убедиться что это то что заявлено:
   - ONNX → `onnx.load(path, load_external_data=False); print(m.ir_version, len(m.graph.node))`
   - numpy archive → `np.load(path); print(list(arr.keys())[:5])`
   - zip/tar → `unzip -l` / `tar -tf` (проверить что нет странных putdir, символических ссылок)
   - exe / dll / sh / bat → **не запускать без явного разрешения Артёма** даже если source хороший

4. **Изолированный venv** — устанавливать pip-пакеты всегда в проектный venv (`python -m venv venv`), не в системный Python.

5. **Pip-пакеты от мало-известных авторов** — открыть `setup.py` / `pyproject.toml` или `__init__.py` основного модуля, прочитать. Если `setup.py` запускает что-то странное (download шеллов, шифрованные base64 strings, network calls) — стоп.

**Когда можно проще (но всё равно сделать):**
- Files от huggingface-org official mirrors / pypi `pip` без `--index-url` / Anthropic / OpenAI / Microsoft / NVIDIA — risk минимальный, но всё равно SHA256 + type validation.
- Внутренний код Артёма из его GitHub orgs (InfinitySudo) — checks не нужны.

**Сообщать пользователю** в виде короткой таблицы (Source reputation / Checksum / File type validation / Result) до использования файла. Не ждать вопроса "не словим вирусов" — делать proactive.

**Не делать** полный antivirus scan (Defender и так гонит на ПК1), не обращаться к VirusTotal API (rate-limited, лишняя зависимость) — три проверки выше покрывают 99% реальных рисков.
