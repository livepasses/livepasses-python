# Changelog

All notable changes to the Livepasses Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-09-28

### Changed (breaking)
- The API now answers every refusal with a real HTTP status (`400`/`403`/`404`/`409`/`422`/`429`/`500`/`502`/`503`) and the `{success:false,data:null,error:{...}}` envelope, instead of sometimes returning `200` with `success:false`. The SDK now raises a typed error from **any** status or body — including a status-only error response with no parseable body (a challenge `401`, a proxy `5xx`) — so a `success` check on the returned value is no longer needed or possible. A `2xx` with an empty body (a `204`) is a success and returns `None`.
- **5xx responses are now retried only for idempotent methods** (`GET`, `HEAD`, `PUT`, `DELETE`). A `POST` that hits a `5xx` fails immediately instead of being retried, since no SDK sends an `Idempotency-Key` to make a retry safe. `429` and network-error retry behavior is unchanged.
- `ValidationError` gained a `fields: dict[str, list[str]] | None` attribute (also added to `ApiError`), populated only for `VALIDATION_ERROR` — the field -> validation messages map the API now includes on that error. Its keys are the API's camelCase field paths exactly as sent (for example `operations[0].path`); they are deliberately **not** converted to snake_case, so they match the request body.
- A `401` is now always an `AuthenticationError` and a `403` always a `ForbiddenError`, whatever the code: a `403` carrying `UNAUTHORIZED` is a permission refusal, not a bad API key. After that the error code decides, then the status (`400`/`404`/`422`/`429`); a `409` with no mapped code is a plain `LivepassesError`. `status` on every error is the response's real HTTP status — `QuotaExceededError.status` is `422`.
- `UpdatePassParams` now matches what `PUT /api/passes/{id}` reads: `updated_fields`, `reason`, `message_header`, `message_body` and `notify`. The old `business_data` and `status` were never read by the API, so `passes.update()` changed nothing while answering success; the API now refuses them with a `400`. Send a non-empty `updated_fields`, a non-empty `message_body`, or both.
- `notes` removed from `RedeemPassParams`, `CheckInParams` and `RedeemCouponParams`. The API never read it and now refuses it with a `400`; put free text in `metadata`. The params gained the fields the API does read (`accepted_types`, `redemption_method`, `redemption_channel`, `confirmation_code`, `gate`, `section`, `location_id`, `transaction_amount`, `transaction_currency`, `promo_code`, `metadata`).
- `location` on those params is a `RedemptionLocation` object (`name`, `latitude`, `longitude`), not a string, and check-in coordinates now go inside it: `CheckInParams` no longer has top-level `latitude`/`longitude`, which the API refuses.
- Keys inside `updated_fields` (on `UpdatePassParams` and `PushTemplatePassesParams`) and `metadata` are sent exactly as written: they are no longer converted to camelCase, and `None` values inside them are sent rather than dropped. Use the API's field names (`validUntil`, `memberTier`); `{"gate_info": ...}` used to be rewritten to `gateInfo` and is now sent as `gate_info`.
- **Upgrade recommended.** Older SDK versions retry a failed request on any `5xx`, including a `POST`. The API now answers server-side failures with a real `500`, `502` or `503` where it used to answer `200`, so an older SDK can send the same `POST` twice — for example, generate the same passes twice. This version retries a `5xx` only for `GET`, `HEAD`, `PUT` and `DELETE`.

### Added
- `"pass.installed"` and `"pass.removed"` webhook events: the holder saved a pass to a wallet (first device), or removed its last copy. Holder-initiated removals only.
- Pass operations the API shipped since June: `passes.redeem_gift_card`, `passes.membership_check_in`, `passes.stamp`, `passes.unstamp`, `passes.redeem_by_scan`.
  `stamp` and `unstamp` send an empty JSON body rather than none: both endpoints bind a request
  DTO, and a bodyless POST carries no `Content-Type`, which the API answers with `415`.

### Removed
- **BREAKING:** the `pass.expired`, `pass.checked_in`, `batch.completed` and `batch.failed` members of `WebhookEventType`. The API rejects all four with a `400`, so no
  subscription using them could ever have worked.

### Fixed
- `passes.redeem` documented itself as generic redemption. It is single-use only: multi-use
  passes are refused with a `422`. The docstring now says so and names `stamp()`,
  `membership_check_in()`, `redeem_coupon()` and `redeem_gift_card()` as the operations to
  use instead.
- Webhook event catalogue now mirrors the server allow-list, adding `loyalty.transacted`,
  `coupon.applied`, the five `transfer.*` events and the `*` wildcard. The runnable webhook
  example no longer subscribes to events the API rejects.
- The template example and README put invented flat keys (`passType`, `hasSeating`,
  `hasGateInfo`, `supportedPlatforms`, `hasBackstageAccess`) in `business_features`, which the
  API now refuses with a `400`. They now send a nested `event` block (and `branding`).

## [0.2.0] - 2026-05-23

### Changed
- **BREAKING:** `passes.bulk_update(BulkUpdatePassesParams)` replaced by `passes.push_template(template_id, PushTemplatePassesParams)`, targeting `POST /api/passes/template/{template_id}/push` with `{ updated_fields, reason }`. `BulkUpdatePassesParams` renamed to `PushTemplatePassesParams`.

## [0.1.0] - 2026-02-27

### Added

- Initial release of the Livepasses Python SDK
- `Livepasses` client with configurable base URL, timeout, and retry settings
- **Passes resource**: `generate`, `generate_and_wait`, `list`, `list_auto_paginate`, `lookup`, `validate`, `update`, `bulk_update`, `redeem`, `check_in`, `redeem_coupon`, `loyalty_transact`, `get_batch_status`
- **Templates resource**: `list`, `get`, `create`, `update`, `activate`, `deactivate`
- **Webhooks resource**: `create`, `list`, `delete`
- Typed exception hierarchy: `AuthenticationError`, `ValidationError`, `ForbiddenError`, `NotFoundError`, `RateLimitError`, `QuotaExceededError`, `BusinessRuleError`
- `ApiErrorCodes` class with 40+ error code constants
- Automatic retry with exponential backoff for 429 and 5xx responses
- Auto-pagination via generator (`list_auto_paginate`)
- Full type annotations with `py.typed` marker (PEP 561)
- Automatic camelCase/snake_case conversion for API payloads

[0.1.0]: https://github.com/livepasses/livepasses-python/releases/tag/python-v0.1.0
