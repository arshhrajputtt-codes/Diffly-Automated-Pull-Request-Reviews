import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidSignatureError
from app.core.security import verify_github_signature
from app.db.database import SessionLocal
from app.db.session import get_db
from app.schemas.review_request import ReviewRequestResponse
from app.schemas.webhook import PullRequestWebhookPayload
from app.services.review_service import ReviewService
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger("diffly.webhooks")

service = WebhookService()
review_service = ReviewService()


def _run_review_in_background(review_request_id: int) -> None:
    # BackgroundTasks run after the response is sent, using whatever
    # function you give it — but the request's `db` session is already
    # closed by then (same lesson learned the hard way in Vynera's
    # streaming chat endpoint), so this opens its own session rather than
    # reusing the one from the request.
    db = SessionLocal()
    try:
        review_service.run_review(db, review_request_id)
    finally:
        db.close()


@router.post("/github", status_code=status.HTTP_200_OK)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    raw_body = await request.body()

    try:
        verify_github_signature(raw_body, x_hub_signature_256, settings.GITHUB_WEBHOOK_SECRET)
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if x_github_event == "ping":
        # GitHub sends this once when a webhook is first configured, purely
        # to confirm the endpoint is reachable — no PR data included.
        return {"message": "pong"}

    if x_github_event != "pull_request":
        # Acknowledge with 200 rather than error — this is a legitimate
        # GitHub event we simply don't act on (e.g. push, issues). Erroring
        # on events we don't handle would make GitHub think the webhook is
        # broken and eventually disable it.
        logger.info("Ignoring unhandled event type: %s", x_github_event)
        return {"message": f"event '{x_github_event}' ignored"}

    payload = PullRequestWebhookPayload.model_validate_json(raw_body)
    review_request = service.handle_pull_request_event(db, payload)

    if review_request is None:
        logger.info("Ignoring pull_request action: %s", payload.action)
        return {"message": f"action '{payload.action}' ignored"}

    logger.info(
        "Recorded review request #%s for %s PR #%s — queuing review",
        review_request.id, payload.repository.full_name, payload.pull_request.number,
    )
    background_tasks.add_task(_run_review_in_background, review_request.id)

    return ReviewRequestResponse.model_validate(review_request)
