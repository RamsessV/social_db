from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    img: str | None = None
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    name: str
    age: int
    email: str
    join_date: datetime
    img: str | None = None

    model_config = {
        "from_attributes": True
    }

