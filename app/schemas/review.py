from datetime import datetime

from pydantic import BaseModel


class ReviewResponse(BaseModel):
    id: int
    review_request_id: int
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    github_comment_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
