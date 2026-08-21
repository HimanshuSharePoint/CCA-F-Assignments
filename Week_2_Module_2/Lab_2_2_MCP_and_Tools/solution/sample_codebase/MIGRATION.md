# Migration: `logEvent` → `track`

Date: 2026-08-19

## Summary

The deprecated `logEvent(name, payload)` helper in `src/analytics.ts` has been
replaced with `track({ name, props })` at all four call sites across
`src/notifications.ts` and `src/orders.ts`.

The two functions carry the same information, so every conversion was a
mechanical reshape: the positional `name` argument became the `name` property,
and the positional `payload` argument became the `props` property. Both accept
`Record<string, unknown>`, so no payload keys or values were changed.

### Before / after

```ts
logEvent("order_delivered", { orderId });                 // deprecated
track({ name: "order_delivered", props: { orderId } });   // replacement
```

## Call sites migrated

### `src/notifications.ts`

| Function | Event name | Payload |
| --- | --- | --- |
| `sendOrderShipped` | `order_shipped_email` | `{ orderId, email }` |
| `sendReturnApproved` | `return_approved_email` | `{ orderId }` |

### `src/orders.ts`

| Function | Event name | Payload |
| --- | --- | --- |
| `markDelivered` | `order_delivered` | `{ orderId }` |
| `cancelOrder` | `order_canceled` [^1] | `{ orderId, reason }` |

[^1]: This event was named `order_cancelled` (two L) at the time of the
`logEvent` → `track` migration. It was renamed to `order_canceled` (one L) in a
separate follow-up change — see [Completed: `order_cancelled` →
`order_canceled`](#completed-order_cancelled--order_canceled) below.

## Imports updated

Both files previously imported the deprecated helper. Each import was rewritten
to pull in `track` instead:

```ts
- import { logEvent } from "./analytics";
+ import { track } from "./analytics";
```

- `src/notifications.ts` — updated
- `src/orders.ts` — updated

No other files import from `src/analytics.ts`.

## Verification

A grep for `logEvent(` across `sample_codebase/src` returns two matches, both
in `src/analytics.ts`:

- the deprecation comment on line 3
- the `export function logEvent(` declaration on line 7

Neither is an invocation, so no live call sites remain in `src`. Within that
directory `logEvent` is now dead code — still defined and exported, called by
nothing.

### Not yet verified

- **Tests have not been read or run.** `tests/notifications.test.ts` and
  `tests/orders.test.ts` both exist. If either asserts against `logEvent`
  output, it may now fail. This should be checked before the migration is
  treated as complete.
- **The grep was scoped to `src`.** References under `tests/` or elsewhere in
  the repo were not searched. The pattern `logEvent(` also would not match a
  bare `logEvent` in an import list or re-export.

## Completed: `order_cancelled` → `order_canceled`

**Status: done** (Exercise 3, 2026-08-19).

The analytics event emitted by `cancelOrder` in `src/orders.ts` was renamed from
`order_cancelled` (two L) to `order_canceled` (one L):

```ts
- track({ name: "order_cancelled", props: { orderId, reason } });
+ track({ name: "order_canceled",  props: { orderId, reason } });
```

Both spellings are preserved above deliberately: the old name is what any
historical analytics data is recorded under, and the new name is what the code
emits from this change onward.

The rename touched the event-name string literal only. The function name
`cancelOrder`, the props `{ orderId, reason }`, the `track` import, and the
`order_delivered` event on line 4 were all left unchanged.

This name was deliberately held back during the `logEvent` → `track` migration
so the two concerns stayed separate — that pass reshaped call syntax without
altering any emitted event name, and this pass altered the name without
reshaping anything.

### Downstream impact

This is a behavioural change rather than a refactor. Anything consuming the
analytics stream (dashboards, saved queries, alerts) that filters on
`order_cancelled` stopped matching as of this change and needs updating to
`order_canceled`. Events emitted before the rename remain under the old
spelling, so queries spanning the cutover need to match both.

Downstream consumers were **not** inventoried as part of this work. The greps
run here covered `sample_codebase` only, which would not surface external
analytics configuration.

## Removing `logEvent`

Deleting the deprecated function from `src/analytics.ts` is out of scope here
and has not been done. It remains exported, still annotated
`/** @deprecated Use track({ name, props }) instead. */`.
