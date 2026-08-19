# Changelog

All notable changes to the Livepasses Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
