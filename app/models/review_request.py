import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class ReviewStatus(str, enum.Enum):
    RECEIVED = "received"      # webhook stored, not yet picked up (Module 1)
    QUEUED = "queued"          # handed to a background worker (Module 2)
    PROCESSING = "processing"  # LLM review in progress (Module 2)
    COMPLETED = "completed"    # comment posted back to GitHub (Module 2/3)
    FAILED = "failed"


class ReviewRequest(Base):
    __tablename__ = "review_requests"

    id = Column(Integer, primary_key=True, index=True)

    repo_full_name = Column(String, nullable=False, index=True)  # e.g. "octocat/hello-world"
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(String, nullable=False)
    pr_url = Column(String, nullable=False)

    head_sha = Column(String, nullable=False)   # commit the review should target
    base_ref = Column(String, nullable=False)   # branch the PR merges into
    action = Column(String, nullable=False)     # opened / synchronize / reopened
    author_login = Column(String, nullable=False)

    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.RECEIVED, index=True)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
