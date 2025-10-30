from datetime import datetime
from pydantic import BaseModel
from .users import UserRead

class CommentRead(BaseModel):
    id: int
    text: str
    created_at: datetime
    commented_by_me: bool = False
    user: UserRead

    model_config = {
        "from_attributes": True
    }

class CommentCreate(BaseModel):
    text: str
    post_id: int