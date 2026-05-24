---
name: project-wallets-all-endpoint
description: /api/v2/wallets-all — параллельно пуллит wallet для всех 3 sub-аккаунтов Bybit (TradingBot/Copy/AI). Подключён к cockpit COMMAND CENTER и v2.html header.
metadata: 
  node_type: memory
  type: project
  originSessionId: eeb6bcbc-09a2-4e37-b01a-7f90d2807f2c
---

С коммита `4e5d81f` (2026-05-23) в `dashboard_api_v3.py` есть endpoint
`/api/v2/wallets-all` который **параллельно** дёргает Bybit
`/v5/account/wallet-balance` для трёх sub-аккаунтов своими ключами и
возвращает единый JSON с totals.

## Mapping sub → UID → env-var
Все 3 sub под master `parentUid=100548867`:

| sub | label (Bybit note) | UID | env-var (key+secret) |
|---|---|---|---|
| sub1 | 4BotsTrading | 563399107 | `BYBIT_API_KEY` / `BYBIT_API_SECRET` |
| sub2 | CopyTradingGTE | 563470305 | `BYBIT_GERCHIK_API_KEY` / `BYBIT_GERCHIK_API_SECRET` |
| sub3 | GTETradingA | 539929753 | `BYBIT_AI_AGENT_API_KEY` / `BYBIT_AI_AGENT_API_SECRET` |

Mapping зашит в константе `_BYBIT_SUBS` в `dashboard_api_v3.py` (около
строки 5895). Если ключи в `.env` поменяются — обновить там.

## Response shape
```json
{
  "status": "ok",
  "wallets": [
    {"id":"sub1","label":"4BotsTrading","uid":563399107,
     "wallet":104.90,"equity":100.82,"upnl":-4.08,"error":null}, ...
  ],
  "totals": {"wallet":175.83,"equity":171.75,"upnl":-4.08},
  "timestamp":"..."
}
```

## Реализация
- `_bybit_signed_get_with(key, secret, ...)` — generic signer (старый
  `_bybit_signed_get` использовал hardcoded ключ).
- ThreadPoolExecutor(3) — все 3 ответа за ~250ms.
- Кеш `_wallets_all_cache` 30 сек чтобы не упереться в Bybit rate-limit.
- Если один sub отвечает с error — endpoint всё равно возвращает 200,
  поле `error` для конкретного sub содержит причину.

## Где подключено
1. **Space_Live cockpit COMMAND CENTER** (`b71680f1`):
   - Deposit/Balance = `totals.wallet/equity` (сумма 3 sub'ов).
   - Новый раздел `SUB-WALLETS` с 3 строками (#sw-sub1/2/3), tooltip = uid + wallet + uPnL.
2. **v2.html dashboard header** (`8592cfb`):
   - Equity/Cash/uPnL карты = totals (раньше только sub-1).
   - Tooltip на карточках = разбивка по 3 sub'ам.

## Известное
- `/api/v2/overview` всё ещё возвращает только sub-1 (он использует
  `BYBIT_API_KEY` напрямую). Это намеренно — `session_delta` baseline
  привязан к sub-1 cash, а не к totals. Для totals в UI используется
  `/api/v2/wallets-all`.
- `/api/v2/gerchik/wallet` всё ещё отдельный — дёргает sub-2 через
  свои ключи (это для AI_COPY_TRADING tile).
- `/api/v2/gerchik/comparison` использует sub-3.

**Связано:** [[project_bybit_3sub_architecture]] · [[project_space_live]] · [[project_dashboard_v2]]
