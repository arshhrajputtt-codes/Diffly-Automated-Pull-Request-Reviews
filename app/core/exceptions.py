class AppError(Exception):
    """Base class for domain/application errors."""


class InvalidSignatureError(AppError):
    def __init__(self):
        super().__init__("Webhook signature verification failed")


class UnsupportedEventError(AppError):
    def __init__(self, event_type: str):
        self.event_type = event_type
        super().__init__(f"Event type '{event_type}' is not handled")


class GitHubApiError(AppError):
    def __init__(self, detail: str):
        super().__init__(f"GitHub API error: {detail}")


class ProviderError(AppError):
    def __init__(self, provider: str, detail: str):
        self.provider = provider
        super().__init__(f"{provider} error: {detail}")


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(f"{entity} {entity_id} not found")
