---
name: Wrestling Camp Payment Flow
description: Camp оплата через Square checkout link с двусторонней confirm-flow (без Square Webhooks API)
type: project
originSessionId: 8b62aa6d-07b7-48fd-83ea-86cb1467abae
---
**Что работает (с 2026-04-26):**
- `clubs.default_payment_link` — Constant club уже настроен на Square checkout `https://checkout.square.site/merchant/ML27GPRB8HJWD/checkout/YWIML5SFSM5R6TGJKRN4YMNO?src=sheet`. Кемпы клуба автоматически подхватывают эту ссылку если коуч не вписал свою.
- `camp_signups.payment_marked_at` / `payment_confirmed_at` — две timestamp-колонки для honor-system flow.

**Flow:**
1. Atлет approved → видит на карточке "💳 Pay $X" + "I Paid" кнопку.
2. Жмёт "Pay" → открывает Square в новой вкладке → платит.
3. Возвращается, жмёт "I Paid" → POST `/api/camps/{cid}/signups/{sid}/mark-paid` → notification создателю кемпа ("💳 Payment claimed: ... — verify in Square then confirm").
4. Коуч в Manage panel у approved атлета видит amber `⏳ Confirm` кнопку → проверяет деньги в Square → жмёт.
5. POST `/api/camps/{cid}/signups/{sid}/confirm-payment` → notification атлету ("✅ Payment confirmed").
6. Atлет видит зелёный "Paid ✓".

**Почему honor-system, а не webhooks:**
Square Checkout Links не шлют webhooks (нужно Square API + merchant credentials + sandbox). Pattern идентичен Sparring e-Transfer flow (markPaymentSent / confirmPayment). Если Артём захочет автоматизировать — нужно регистрировать Square API app, хранить merchant access token, слушать `payment.created` webhook на public endpoint.

**Каноническая логика fallback:** `body.payment_link or club.default_payment_link or None` — sparring (tournaments) уже имел этот pattern, добавил в camps на parity.

**How to apply:**
- Если Артём хочет такой же flow для другого клуба → SET `clubs.default_payment_link` в БД.
- Если просит "автоматический" Square confirm — объясни ограничение, предложи Square API integration как отдельный проект (не minor patch).
