from datetime import datetime
from pydantic import BaseModel

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

