---
name: project_pumpdump_semiauto
description: "PumpDumpAI перешёл на полуавтомат — дашборд-торговля (график, ордер-тикет, подсказки, drag SL/TP); старый детектор выключен"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9b16d2b5-05ef-4976-9e59-f7b97b28c149
---

2026-06-08: PumpDumpAI ([[project_pumpdump_agent]], [[project_pumpdump_selftuning]]) переведён на **полуавтоматическую торговлю** через дашборд `/var/www/dashboard/pumpdump.html` (зеркало Space_Live/public; работает ТОЛЬКО на `:8080`, НЕ на `:443`/ontime — там `/pumpdump/*` кроме webhook не проксируется). Всё PAPER (sub-4).

**Решение:** старый WS-детектор (vol×5+3%) ОТКЛЮЧЁН от авто-входа (`detection.auto_enabled=false`) — давал 95% SL (TP=5R недостижим, median MFE 0.8%; only 2 TP3 на 559 сделок). Детектор крутится только для live-цен/статистики. Торговля = reversal-подсказки + ручные.

**Что реализовано (всё за этот день, много коммитов):**
- **График** TradingView Lightweight Charts (self-hosted `lightweight-charts.js`): клик по символу → свечи+объём+маркеры входов/выходов (цвет по source) + тултип с rationale; инструменты (fullscreen ВСЕЙ секции, гор.линии, **линейка** drag с Δ%/Δ/бары, EMA20/50); живое авто-обновление 5с (setData без fitContent); TF 1m/5m/15m/30m/1h/2h/4h/1D; авто-rescale при смене монеты; precision под мелкие цены.
- **Ордер-тикет** (📈/📉): Market (налив по live) / Limit (очередь pending, исполняется по достижению цены, /pending-cancel); размер от risk/margin/notional/qty; редактируемые SL/TP/BE; live qty/notional/margin/risk + прибыль при TP / убыток при SL / R:R; кнопка «SL=5м свеча» (медиана 12 не-аномальных 5м-свечей, аномалии <0.5× / >1.8× медианы). Floor **TP1 ≥ 3R** (`tp.tp1_min_R`).
- **Подсказки Take/Skip** (suggest-режим сканера): карточки с чек-листом критериев + rationale; Take открывает source=suggested.
- **Перетаскиваемые SL/TP на графике** (ByBit-style): drag линий открытой позиции, live −$убыток/+$прибыль; commit → `/position-update` (PAPER лог / REAL пушит на Bybit через executor.set_sl_tp).
- **Панель «Открытые позиции»** — live нереализованный PnL ($/R/%), объём, плечо, до SL/TP.
- **Скриншот-канал** (см. [[project_pumpdump_selftuning]]): `data/screenshots/latest.png`.

**Эндпоинты агента (http_server):** /klines, /symbol-trades, /symbols, /manual-trade, /suggestion-act, /pending-cancel, /position-update, /screenshot, /tune-now, /rollback-tuning (+ /stats несёт positions, pending_orders, suggestions, recent_signals с исходом). trade_open несёт `source` (detector/signal/suggested/manual/limit) + `rationale`.

**Баг-фиксы:** webhook/manual фейк-филл (фантомы BEAT@2.2 — curl-тест из сессии); BE больше не закрывает остаток мгновенно после TP1 на тесном SL (армится только если be_px на защитной стороне цены). **be_arm_mode сейчас `peak_r`** (BE после be_activation_R=3, не сразу после TP1). Статистика очищена 2026-06-08 (старый журнал в `data/archive/`).
