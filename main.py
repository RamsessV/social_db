from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import users, posts, likes, comments
from contextlib import asynccontextmanager
from database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Deteniendo aplicación…")



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router, prefix="/users")
app.include_router(posts.router, prefix="/posts")
app.include_router(likes.router, prefix="/likes")
app.include_router(comments.router, prefix="/comments")

@app.get('/')
async def root():
    return {"message": "Social_DB"}
