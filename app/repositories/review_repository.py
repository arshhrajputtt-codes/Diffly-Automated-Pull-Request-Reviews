from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    def create(self, db: Session, review: Review) -> Review:
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    def get_by_review_request_id(self, db: Session, review_request_id: int) -> Review | None:
        return db.query(Review).filter(Review.review_request_id == review_request_id).first()
