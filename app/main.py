from fastapi import FastAPI, status, HTTPException, Depends
from httpx import post
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from typing import List
from . import models, schemas
from .database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="pratham@0407", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connection established")
        break
    except Exception as error:
        print("Connection error:", error)
        time.sleep(2)


@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.get("/posts", response_model=List[schemas.PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
    # created_post = cursor.fetchone()
    # conn.commit()

    
    created_post = models.Post(**post.model_dump())
    db.add(created_post)
    db.commit() # * TO commit the changes in database
    db.refresh(created_post) # ? RETURNING statmeent according to sqlalchemy
    if post is not None:
        return created_post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")


@app.get("/post/{id}", response_model=schemas.PostResponse)
async def get_single_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is not None:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")


@app.delete("/post/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()

    delete_post = db.query(models.Post).filter(models.Post.id == id)
    if delete_post is not None:
        delete_post.delete(synchronize_session=False)
        db.commit()
        return { "Post deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist")


@app.post('/post/{id}', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def update_post(id: int, payload: schemas.PostBase, db: Session = Depends(get_db)):
    # cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (post.title, post.content, post.published, str(id)))
    # update_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found with id: {id}")
    
    post_query.update(payload.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
