from sqlmodel import Relationship, SQLModel, Field
from typing import Optional

class Like(SQLModel, table=True):
    __tablename__ = "likes"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    post_id: int = Field(foreign_key="posts.id", ondelete="CASCADE")
    post: Optional["Post"] = Relationship(back_populates="likes_count")