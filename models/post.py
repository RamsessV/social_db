from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    text: str
    img: Optional[str] = None
    likes: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(
    back_populates="post",
    sa_relationship_kwargs={
        "cascade": "all, delete-orphan",
        "passive_deletes": True
    }
)
    likes_count: list["Like"] = Relationship(
    back_populates="post",
    sa_relationship_kwargs={
        "cascade": "all, delete-orphan",
        "passive_deletes": True
    }
)
