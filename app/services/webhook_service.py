from sqlalchemy.orm import Session

from app.models.review_request import ReviewRequest, ReviewStatus
from app.repositories.review_request_repository import ReviewRequestRepository
from app.schemas.webhook import PullRequestWebhookPayload

# Only these actions mean "there's new or changed code that needs review" —
# GitHub sends pull_request webhooks for lots of other actions too (labeled,
# assigned, closed, review_requested, ...) that this module deliberately
# ignores rather than storing noise.
RELEVANT_ACTIONS = {"opened", "synchronize", "reopened"}


class WebhookService:
    def __init__(self, repository: ReviewRequestRepository | None = None):
        self.repository = repository or ReviewRequestRepository()

    def handle_pull_request_event(
        self, db: Session, payload: PullRequestWebhookPayload
    ) -> ReviewRequest | None:
        if payload.action not in RELEVANT_ACTIONS:
            return None

        review_request = ReviewRequest(
            repo_full_name=payload.repository.full_name,
            pr_number=payload.pull_request.number,
            pr_title=payload.pull_request.title,
            pr_url=payload.pull_request.html_url,
            head_sha=payload.pull_request.head.sha or "",
            base_ref=payload.pull_request.base.ref,
            action=payload.action,
            author_login=payload.pull_request.user.login,
            status=ReviewStatus.RECEIVED,
        )
        return self.repository.create(db, review_request)
