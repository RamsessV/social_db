from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.like import Like
from database import get_session
from security.auth import verify_access_token

router = APIRouter()

async def get_liked(token: int, session: Session = Depends(get_session)):
    likes = session.exec(select(Like.post_id).where(Like.user_id == token)).all()
    return likes
    
@router.post("/")
async def create(post_id: int, token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    existing_like = session.exec(
        select(Like).where(Like.user_id == token, Like.post_id == post_id)
    ).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Like already exists")
    try:
        new_like = Like(user_id=token, post_id=post_id)
        session.add(new_like)
        session.commit()
        session.refresh(new_like)
        return {"message": "Like created successfully"}
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.delete("/")
async def delete(post_id: int, token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    existing_like = session.exec(
        select(Like).where(Like.user_id == token, Like.post_id == post_id)
    ).first()
    if not existing_like:
        raise HTTPException(status_code=404, detail="Like not found")
    try:
        session.delete(existing_like)
        session.commit()
        return {"message": "Like deleted successfully"}
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")