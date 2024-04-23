from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="pratham@0407", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connection established")
        break
    except Exception as error:
        print("Connection error:", error)
        time.sleep(2)

my_posts = []

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.get("/posts")
async def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
    created_post = cursor.fetchone()
    conn.commit()
    if post is not None:
        return {"data": created_post}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")

@app.get("/post/{id}")
async def get_single_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    post = cursor.fetchone()
    if post is not None:
        return {"data": post}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")


@app.delete("/post/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id),))
    delete_post = cursor.fetchone()
    conn.commit()
    if delete_post is not None:
        return {"data": "Post deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")

@app.post('/post/{id}')
async def update_post(id: int, post: Post):
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (post.title, post.content, post.published, str(id)))
    update_post = cursor.fetchone()
    conn.commit()
    return {"data": update_post}
