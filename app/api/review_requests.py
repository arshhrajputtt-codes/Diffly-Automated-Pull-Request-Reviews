from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.review_repository import ReviewRepository
from app.repositories.review_request_repository import ReviewRequestRepository
from app.schemas.review import ReviewResponse
from app.schemas.review_request import ReviewRequestResponse

router = APIRouter(prefix="/review-requests", tags=["Review Requests"])

repository = ReviewRequestRepository()
review_repository = ReviewRepository()


@router.get("", response_model=list[ReviewRequestResponse])
def list_review_requests(db: Session = Depends(get_db)):
    return repository.list_recent(db)


@router.get("/{review_request_id}", response_model=ReviewRequestResponse)
def get_review_request(review_request_id: int, db: Session = Depends(get_db)):
    review_request = repository.get_by_id(db, review_request_id)
    if not review_request:
        raise HTTPException(status_code=404, detail="Review request not found")
    return review_request


@router.get("/{review_request_id}/review", response_model=ReviewResponse)
def get_review(review_request_id: int, db: Session = Depends(get_db)):
    review = review_repository.get_by_review_request_id(db, review_request_id)
    if not review:
        raise HTTPException(status_code=404, detail="No review generated yet for this request")
    return review
