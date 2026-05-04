---
name: Grafana alerts → @infinityopenclowbot
description: Куда сейчас идут все Grafana trading alerts и как откатить
type: project
originSessionId: 28e4b48c-7bcd-4db4-aef5-c902d730ffb0
---
С 2026-05-03 все Grafana alert rules в папке `Trading Alerts` (включая `Paper drawdown > 20 USD (24h)`) уходят в `@infinityopenclowbot`, не в `@ControlByBitTradingBot`.

**Что изменилось**: contact point `TelegramOwner` → переименован в `TelegramTrades`, `bottoken` заменён с `TELEGRAM_CONTROL_BOT_TOKEN` на `TELEGRAM_TRADE_BOT_TOKEN` (он же `@infinityopenclowbot`). `chatid: 504609639` (личка Артёма) не менялся.

**Why:** ControlBot нужен под команды (старт/стоп/рестарт ботов), алерты его засоряли. Артём решил пустить весь pipeline (открытые ордера + alerts) через один бот.

**Откатить** — PUT в Grafana API с прежним bottoken:
```
curl -u admin:CpLxfoieWVw5pefVoFnt \
  -X PUT http://localhost:3000/api/v1/provisioning/contact-points/efinfliiss5q8b \
  -H "Content-Type: application/json" -H "X-Disable-Provenance: true" \
  -d '{"uid":"efinfliiss5q8b","name":"TelegramOwner","type":"telegram","disableResolveMessage":false,"settings":{"bottoken":"<TELEGRAM_CONTROL_BOT_TOKEN>","chatid":"504609639"}}'
```

**How to apply:** Если Артём попросит "перенаправить алерты в X" — узнать username бота через `getMe` для каждого `TELEGRAM_*_BOT_TOKEN` в `/root/4BotsBybit-Trading/.env`, затем тот же PUT с нужным токеном. Route обновляется автоматически когда переименован contact point.
