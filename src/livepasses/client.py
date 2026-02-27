"""Main Livepasses client."""

from __future__ import annotations

from livepasses._http import HttpClient, HttpClientConfig
from livepasses.resources.passes import PassesResource
from livepasses.resources.templates import TemplatesResource
from livepasses.resources.webhooks import WebhooksResource

DEFAULT_BASE_URL = "https://api.livepasses.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


class Livepasses:
    """Official Livepasses API client.

    Usage::

        from livepasses import Livepasses

        client = Livepasses("your-api-key")
        templates = client.templates.list()
    """

    passes: PassesResource
    templates: TemplatesResource
    webhooks: WebhooksResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError(
                "API key is required. Get yours at https://dashboard.livepasses.com"
            )

        http = HttpClient(
            HttpClientConfig(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
            )
        )

        self.passes = PassesResource(http)
        self.templates = TemplatesResource(http)
        self.webhooks = WebhooksResource(http)
