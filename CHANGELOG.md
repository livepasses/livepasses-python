# Changelog

All notable changes to the Livepasses Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
