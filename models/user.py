from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    email: str = Field(index=True, unique=True)
    password: str
    img: Optional[str] = None
    join_date: datetime = Field(default_factory=datetime.now)

    posts: Optional[List["Post"]] = Relationship(back_populates="user")
    