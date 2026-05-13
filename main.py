import os
from datetime import datetime

import sqlite3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

load_dotenv()
mongo_url = os.getenv("MONGO_URL")
print(f"Mongo URL: {mongo_url}")

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/posts")
def get_posts():
    conn = sqlite3.connect("posts.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post")
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return posts


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    conn = sqlite3.connect("posts.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()
    if post is None:
        raise HTTPException(status_code=400, detail={"error": "Post not found"})
    return dict(post)


class Post(BaseModel):
    title: str
    comment: str


@app.post("/posts")
def create_post(post: Post):
    now = datetime.now().isoformat()
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO post (title, comment, createdAt, updatedAt) VALUES (?, ?, ?, ?)",
        (post.title, post.comment, now, now),
    )
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return {
        "id": post_id,
        "title": post.title,
        "comment": post.comment,
        "createdAt": now,
        "updatedAt": now,
    }


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    now = datetime.now().isoformat()
    conn = sqlite3.connect("posts.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE id = ?", (post_id,))
    existing = cursor.fetchone()

    if existing is None:
        conn.close()
        raise HTTPException(status_code=400, detail={"error": "Post not found"})

    cursor.execute(
        "UPDATE post SET title = ?, comment = ?, updatedAt = ? WHERE id = ?",
        (post.title, post.comment, now, post_id),
    )
    conn.commit()
    conn.close()
    return {
        "id": post_id,
        "title": post.title,
        "comment": post.comment,
        "createdAt": existing["createdAt"],
        "updatedAt": now,
    }


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE id = ?", (post_id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=400, detail={"error": "Post not found"})
    cursor.execute("DELETE FROM post WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return {"message": "Post deleted"}
