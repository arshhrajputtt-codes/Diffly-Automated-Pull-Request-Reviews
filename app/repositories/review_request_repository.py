from sqlalchemy.orm import Session

from app.models.review_request import ReviewRequest


class ReviewRequestRepository:
    def create(self, db: Session, review_request: ReviewRequest) -> ReviewRequest:
        db.add(review_request)
        db.commit()
        db.refresh(review_request)
        return review_request

    def get_by_id(self, db: Session, review_request_id: int) -> ReviewRequest | None:
        return db.query(ReviewRequest).filter(ReviewRequest.id == review_request_id).first()

    def update(self, db: Session, review_request: ReviewRequest) -> ReviewRequest:
        db.commit()
        db.refresh(review_request)
        return review_request

    def list_for_repo(self, db: Session, repo_full_name: str) -> list[ReviewRequest]:
        return (
            db.query(ReviewRequest)
            .filter(ReviewRequest.repo_full_name == repo_full_name)
            .order_by(ReviewRequest.created_at.desc())
            .all()
        )

    def list_recent(self, db: Session, limit: int = 50) -> list[ReviewRequest]:
        return db.query(ReviewRequest).order_by(ReviewRequest.created_at.desc()).limit(limit).all()
