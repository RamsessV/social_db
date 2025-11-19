from sqlmodel import SQLModel, Session, create_engine
from models.post import Post
from models.user import User
from models.comment import Comment
from models.like import Like


engine = create_engine(
    "mysql+pymysql://back:back@ls-9bad9371f72fd62d2920af4e2d9808be31f2f0b3.cr6cw0802aam.us-east-2.rds.amazonaws.com:3306/social_db",
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
