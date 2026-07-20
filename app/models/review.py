from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_request_id = Column(Integer, ForeignKey("review_requests.id"), nullable=False, index=True)

    content = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)

    github_comment_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
