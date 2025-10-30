from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.comment import Comment
from database import get_session
from schemas.comments import CommentCreate
from security.auth import verify_access_token


router = APIRouter()

@router.post('/', status_code=201)
async def create(comment: CommentCreate, token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    try:
        new_comment = Comment(text=comment.text, user_id=token, post_id=comment.post_id)
        session.add(new_comment)
        session.commit()
        session.refresh(new_comment)
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return new_comment

@router.delete('/{comment_id}', status_code=204)
async def delete(comment_id: int, token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail='Comment not found')
    if comment.user_id != token:
        raise HTTPException(status_code=403, detail='Not authorized to delete this comment')
    try:
        session.delete(comment)
        session.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")