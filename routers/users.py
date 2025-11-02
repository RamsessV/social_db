import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.params import Form
from sqlmodel import Session, select, func
from models.user import User
from database import get_session
from schemas.users import UserRead, UserLogin
from security.password import hash_password, verify_password
from security.auth import create_access_token, verify_access_token

router = APIRouter()

async def save_file(img: UploadFile = File(None)):
    UPLOAD_DIR = "static/images/profiles"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    if not img:
        return None
    if not img.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    file_extension = img.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        buffer.write(await img.read())

    return f"http://localhost:8000/static/images/profiles/{file_name}"



def get_current_user(id_user: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    user = session.get(User, id_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@router.post("/signup", status_code=201)
async def signup(name: str = Form(...), age: int = Form(...), email: str = Form(...), img: str | None = Depends(save_file), password: str = Form(...), session: Session = Depends(get_session)):
    hashed_password = hash_password(password)
    db_user = User(name=name, age=age, email=email, img=img, password=hashed_password)
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except Exception as e:
            session.rollback()
            raise HTTPException(status_code=409, detail="User with this email already exists.")
    
    token = create_access_token(db_user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", status_code=200)
async def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(db_user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", status_code=200)
async def get_user(user: UserRead = Depends(get_current_user)):
    return user


@router.get("/{user_id}", status_code=200, response_model=UserRead)
async def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", status_code=200, response_model=list[UserRead])
async def get_user_by_name(name: str, current_user: UserRead = Depends(get_current_user),  session: Session = Depends(get_session)):
    pattern = f"{name.lower()}%"
    users = session.exec(
        select(User)
        .where(func.lower(User.name).like(pattern), User.id != current_user.id)
    ).all()
    return users



@router.patch("/me", status_code=200, response_model=UserRead)
async def update_user(
    current_password: str = Form(...),
    name: str | None = Form(None),
    age: int | None = Form(None),
    email: str | None = Form(None),
    password: str | None = Form(None),
    img: str | None = Depends(save_file),
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    db_user = session.get(User, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(current_password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect current password")
    if name:
        db_user.name = name
    if age:
        db_user.age = age
    if email:
        db_user.email = email
    if img:
        db_user.img = img
    if password:
        db_user.password = hash_password(password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
