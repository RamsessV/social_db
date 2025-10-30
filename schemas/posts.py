from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from .users import UserRead
from .comments import CommentRead

class PostRead(BaseModel):
    id: int
    user: Optional[UserRead]
    text: str
    img: str | None
    likes: int
    liked_by_me: bool = False
    created_at: datetime
    comments: list[CommentRead]

    model_config = {
        "from_attributes": True
    }

