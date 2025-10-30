from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.user import User
from database import get_session
from schemas.users import UserCreate, UserRead, UserLogin
from security.password import hash_password, verify_password
from security.auth import create_access_token, verify_access_token

router = APIRouter()

def get_current_user(id_user: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    user = session.get(User, id_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@router.post("/signup", status_code=201)
async def signup(user: UserCreate, session: Session = Depends(get_session)):
    hashed_password = hash_password(user.password)
    db_user = User(name=user.name, age=user.age, email=user.email, img=user.img, password=hashed_password)
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
async def get_user_by_name(name: str, session: Session = Depends(get_session)):
    users = session.exec(select(User).where(User.name == name)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found with this name")
    return users


@router.patch("/me", status_code=200, response_model=UserRead)
async def update_user(updated_user: UserCreate, current_user: UserRead = Depends(get_current_user), session: Session = Depends(get_session)):
    db_user = session.get(User, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        db_user.name = updated_user.name
        db_user.age = updated_user.age
        db_user.email = updated_user.email
        db_user.img = updated_user.img
        db_user.password = hash_password(updated_user.password)
    except Exception:
        raise HTTPException(status_code=400, detail="Error updating user")
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user