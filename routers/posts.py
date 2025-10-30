from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import Session, select
from database import get_session
from .likes import get_liked
from schemas.posts import PostRead
from security.auth import verify_access_token
from models.post import Post
import os
import uuid


async def save_file(file: UploadFile = File(None)):
    UPLOAD_DIR = "static/images"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if not file:
        return None
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return f"http://localhost:8000/static/images/{file_name}"



router = APIRouter()





@router.get("/", status_code=200)
async def get_posts(token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    posts = session.exec(
        select(Post)
        .where(Post.user_id != token)
        .options(joinedload(Post.user),
                 selectinload(Post.comments))
        .order_by(Post.created_at.desc())
    ).all()
    res = []
    liked = await get_liked(token, session)
    for post in posts:
        post = PostRead.model_validate(post)
        post.liked_by_me = post.id in liked
        for comment in post.comments:
            comment.commented_by_me = comment.user.id == token
        res.append(post)
    return res


@router.get('/my_posts', status_code=200)
async def get_my_posts(token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    posts = session.exec(
        select(Post)
        .where(Post.user_id == token)
        .options(joinedload(Post.user),
                 selectinload(Post.comments))
        .order_by(Post.created_at.desc())
    ).all()
    res = []
    liked = await get_liked(token, session)
    for post in posts:
        post = PostRead.model_validate(post)
        post.liked_by_me = post.id in liked
        for comment in post.comments:
            comment.commented_by_me = comment.user.id == token
        res.append(post)
    return res

@router.get("/user/{user_id}", status_code=200)
async def get_user_posts(user_id: int, token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    posts = session.exec(
        select(Post)
        .where(Post.user_id == user_id)
        .options(joinedload(Post.user),
                 selectinload(Post.comments))
        .order_by(Post.created_at.desc())
    ).all()
    res = []
    liked = await get_liked(token, session)
    for post in posts:
        post = PostRead.model_validate(post)
        post.liked_by_me = post.id in liked
        for comment in post.comments:
            comment.commented_by_me = comment.user.id == token
        res.append(post)
    return res


@router.get("/{post_id}", status_code=200)
async def get_post(post_id: int, token: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    post = PostRead.model_validate(post)
    liked = await get_liked(token, session)
    post.liked_by_me = post.id in liked
    return post

@router.post("/", status_code=200)
async def create_post(text: str, img: str | None = Depends(save_file), user_id: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    new_post = Post(user_id=user_id, text=text, img=img)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return {"message": "Post creado exitosamente", "post": new_post}
    
    
@router.patch("/{post_id}", status_code=200, response_model=PostRead)
async def update_post(post_id: int, text: str, session: Session = Depends(get_session), token: int = Depends(verify_access_token)):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    if post_db.user_id != token:
        raise HTTPException(status_code=403, detail="No autorizado para actualizar este post")
    post_db.text = text
    session.add(post_db)
    session.commit()
    session.refresh(post_db)

    return post_db


@router.delete("/{post_id}", status_code=200)
async def delete_post(post_id: int, session: Session = Depends(get_session), token: int = Depends(verify_access_token)):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    if post_db.user_id != token:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este post")
    session.delete(post_db)
    session.commit()
    return {"message": "Post eliminado exitosamente"}
