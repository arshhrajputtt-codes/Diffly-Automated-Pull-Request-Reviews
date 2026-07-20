from datetime import datetime

from pydantic import BaseModel

from app.models.review_request import ReviewStatus


class ReviewRequestResponse(BaseModel):
    id: int
    repo_full_name: str
    pr_number: int
    pr_title: str
    pr_url: str
    head_sha: str
    base_ref: str
    action: str
    author_login: str
    status: ReviewStatus
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
