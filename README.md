# Livepasses Python SDK

Official Python SDK for the [Livepasses API](https://livepasses.com) — the leading API-first digital wallet pass platform.

Generate and manage Apple Wallet and Google Wallet passes for events, loyalty programs, coupons, and more.

## Installation

```bash
pip install livepasses
```

**Requirements**: Python 3.10+

## Quick Start

```python
from livepasses import Livepasses, GeneratePassesParams, PassRecipient, CustomerInfo, BusinessData

client = Livepasses("your-api-key")

result = client.passes.generate(GeneratePassesParams(
    template_id="tmpl-001",
    passes=[PassRecipient(
        customer=CustomerInfo(first_name="Alice", last_name="Smith", email="alice@example.com"),
        business_data=BusinessData(section_info="VIP", row_info="A", seat_number="1"),
    )],
))

for p in result.passes:
    print(f"Pass: {p.id} — Apple: {p.platforms.apple.add_to_wallet_url}")
```

## Authentication

Get your API key from the [Livepasses Dashboard](https://dashboard.livepasses.com).

```python
from livepasses import Livepasses

client = Livepasses("lp_live_your_api_key")
```

## Pass Generation

### Single Pass

```python
from livepasses import (
    GeneratePassesParams, PassRecipient, CustomerInfo, BusinessData, BusinessContext, EventContext
)

result = client.passes.generate(GeneratePassesParams(
    template_id="tmpl-001",
    business_context=BusinessContext(
        event=EventContext(event_name="Concert", event_date="2026-06-15T20:00:00Z"),
    ),
    passes=[PassRecipient(
        customer=CustomerInfo(first_name="John", last_name="Doe", email="john@example.com"),
        business_data=BusinessData(section_info="Floor", row_info="B", seat_number="15"),
    )],
))
```

### Batch Generation with Polling

For large batches, the API processes passes asynchronously. `generate_and_wait` handles polling automatically:

```python
from livepasses import GenerateAndWaitOptions

result = client.passes.generate_and_wait(
    GeneratePassesParams(
        template_id="tmpl-001",
        passes=[...],  # hundreds of recipients
    ),
    options=GenerateAndWaitOptions(
        poll_interval=2.0,
        max_attempts=150,
        on_progress=lambda status: print(f"Progress: {status.progress_percentage}%"),
    ),
)

print(f"Generated {len(result.passes)} passes")
```

### Batch Status (Manual Polling)

If you need more control over polling, use `generate` + `get_batch_status`:

```python
initial = client.passes.generate(GeneratePassesParams(
    template_id="tmpl-001",
    passes=[...],
))

if initial.batch_operation:
    import time
    batch_id = initial.batch_operation.batch_id
    status = client.passes.get_batch_status(batch_id)
    while not status.is_completed:
        time.sleep(2)
        status = client.passes.get_batch_status(batch_id)
        print(f"Progress: {status.progress_percentage}%")
    print(f"Completed: {status.statistics.successful} successful, {status.statistics.failed} failed")
```

## Pass Lifecycle

### Lookup

```python
from livepasses import LookupPassParams

pass_info = client.passes.lookup(LookupPassParams(pass_id="pass-001"))
print(f"Valid: {pass_info.is_valid}, Status: {pass_info.status}")
```

### Validate

```python
validation = client.passes.validate("pass-001")
print(f"Can redeem: {validation.can_be_redeemed}")
```

### Redeem

```python
from livepasses import RedeemPassParams, RedemptionLocation

# Generic redemption
result = client.passes.redeem("pass-001")

# Redemption with location
result = client.passes.redeem("pass-001", RedeemPassParams(
    location=RedemptionLocation(name="Store #1", latitude=4.6097, longitude=-74.0817),
    notes="Walk-in customer",
))
```

### Check-in (Events)

```python
from livepasses import CheckInParams

result = client.passes.check_in("pass-001", CheckInParams(
    location="Main Gate",
    latitude=4.6097,
    longitude=-74.0817,
))
```

### Redeem Coupon

```python
from livepasses import RedeemCouponParams

result = client.passes.redeem_coupon("pass-001", RedeemCouponParams(
    location=RedemptionLocation(name="Store #42"),
    notes="Applied to order #12345",
))
```

### Update a Pass

Update business data or context on an existing pass:

```python
from livepasses import UpdatePassParams, BusinessContext, LoyaltyContext

client.passes.update("pass-001", UpdatePassParams(
    business_data=BusinessData(current_points=750, member_tier="Platinum"),
    business_context=BusinessContext(
        loyalty=LoyaltyContext(program_update="Congratulations on reaching Platinum!"),
    ),
))
```

### Bulk Update

Update multiple passes at once:

```python
from livepasses import BulkUpdatePassesParams

client.passes.bulk_update(BulkUpdatePassesParams(
    pass_ids=["pass-001", "pass-002", "pass-003"],
    business_data=BusinessData(member_tier="Gold"),
    business_context=BusinessContext(
        loyalty=LoyaltyContext(seasonal_message="Happy holidays from our team!"),
    ),
))
```

## Pass Types

### Event Tickets

```python
business_data = BusinessData(
    section_info="VIP", row_info="A", seat_number="1",
    ticket_type="VIP", price=150.00, currency="USD",
)
```

### Loyalty Cards

```python
from livepasses import LoyaltyTransactionParams

business_data = BusinessData(
    membership_number="MEM-12345",
    current_points=500,
    member_tier="Gold",
)

# Earn points
result = client.passes.loyalty_transact("pass-001", LoyaltyTransactionParams(
    transaction_type="earn", points=100, description="Purchase at Store #42",
))

# Spend points
result = client.passes.loyalty_transact("pass-001", LoyaltyTransactionParams(
    transaction_type="spend", points=50, description="Redeemed: Free coffee",
))
```

### Coupons

```python
business_data = BusinessData(
    promo_code="SUMMER2026",
    campaign_id="camp-001",
    max_usage_count=1,
)
```

## Templates

### List and get

```python
from livepasses import ListTemplatesParams

# List
templates = client.templates.list(ListTemplatesParams(status="Active"))

# Get details
detail = client.templates.get("tmpl-001")
```

### Create a template

```python
from livepasses import CreateTemplateParams

template = client.templates.create(CreateTemplateParams(
    name="VIP Event Pass",
    description="Premium event ticket template",
    business_features={
        "passType": "event",
        "hasSeating": True,
        "supportedPlatforms": ["apple", "google"],
    },
))
print(f"Created: {template.id} — {template.name}")
```

### Update a template

```python
from livepasses import UpdateTemplateParams

updated = client.templates.update("tmpl-001", UpdateTemplateParams(
    name="VIP Event Pass v2",
    description="Updated premium event ticket template",
))
```

### Activate / Deactivate

```python
client.templates.activate("tmpl-001")
client.templates.deactivate("tmpl-001")
```

## Webhooks

```python
from livepasses import CreateWebhookParams

webhook = client.webhooks.create(CreateWebhookParams(
    url="https://your-app.com/webhooks/livepasses",
    events=["pass.generated", "pass.redeemed", "batch.completed"],
))
print(f"Secret: {webhook.secret}")  # use this to verify webhook signatures

# List all
webhooks = client.webhooks.list()

# Delete
client.webhooks.delete(webhook.id)
```

## Error Handling

The SDK raises typed exceptions that map to API error categories:

```python
from livepasses import (
    LivepassesError,
    AuthenticationError,
    ValidationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    QuotaExceededError,
    BusinessRuleError,
)

try:
    result = client.passes.generate(params)
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation failed: {e.details}")
except ForbiddenError:
    print("Insufficient permissions for this operation")
except NotFoundError:
    print("Template or pass not found")
except RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except QuotaExceededError:
    print("API quota exceeded — upgrade your plan")
except BusinessRuleError as e:
    print(f"Business rule violation: {e}")
except LivepassesError as e:
    # Catch-all for any other API error
    print(f"API error [{e.code}]: {e} (HTTP {e.status})")
```

### Error codes

Use `ApiErrorCodes` for programmatic error code comparisons:

```python
from livepasses import LivepassesError, ApiErrorCodes

try:
    client.passes.redeem("pass-001")
except LivepassesError as e:
    if e.code == ApiErrorCodes.PASS_ALREADY_USED:
        print("This pass has already been redeemed")
    elif e.code == ApiErrorCodes.PASS_EXPIRED:
        print("This pass has expired")
    elif e.code == ApiErrorCodes.TEMPLATE_INACTIVE:
        print("The template for this pass is inactive")
    else:
        print(f"Unhandled error: {e.code}")
```

### Exception hierarchy

| Exception | HTTP Status | When |
|-----------|------------|------|
| `AuthenticationError` | 401 | Invalid, expired, or revoked API key |
| `ValidationError` | 400 | Request validation failed |
| `ForbiddenError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `RateLimitError` | 429 | Rate limit exceeded |
| `QuotaExceededError` | 403 | API quota or subscription limit exceeded |
| `BusinessRuleError` | 422 | Business rule violation (pass expired, already used, etc.) |

## Pagination

### Manual pagination

```python
from livepasses import ListPassesParams

page1 = client.passes.list(ListPassesParams(page=1, page_size=50))
print(f"Page 1 of {page1.pagination.total_pages} ({page1.pagination.total_items} total)")

# Get next page
if page1.pagination.current_page < page1.pagination.total_pages:
    page2 = client.passes.list(ListPassesParams(page=2, page_size=50))
```

### Auto-pagination

Iterate over all passes without manual page management:

```python
for p in client.passes.list_auto_paginate():
    print(f"{p.id}: {p.status}")
```

## Configuration

```python
client = Livepasses(
    "your-api-key",
    base_url="https://api.livepasses.com",  # default
    timeout=30.0,                            # seconds, default
    max_retries=3,                           # default
)
```

### Automatic Retries

The SDK automatically retries:
- **429 Too Many Requests** — honors `Retry-After` header
- **5xx Server Errors** — exponential backoff with jitter

## Type Checking

This package ships with a `py.typed` marker (PEP 561) and is fully compatible with `mypy` and `pyright`.

```bash
mypy your_app.py   # full type safety
```

## Examples

See the [`examples/`](./examples/) directory for runnable scripts:

- **[generate_passes.py](./examples/generate_passes.py)** — End-to-end pass generation, lookup, validation, and check-in
- **[loyalty_workflow.py](./examples/loyalty_workflow.py)** — Loyalty card lifecycle: generate, earn points, spend points, update tier
- **[coupon_workflow.py](./examples/coupon_workflow.py)** — Coupon pass generation and redemption
- **[template_management.py](./examples/template_management.py)** — CRUD operations on pass templates
- **[webhook_setup.py](./examples/webhook_setup.py)** — Register, list, and manage webhooks

Run any example with:
```bash
export LIVEPASSES_API_KEY="your-api-key"
python examples/generate_passes.py
```

## License

MIT
