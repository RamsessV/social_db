from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    post_id: int = Field(foreign_key="posts.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship()
