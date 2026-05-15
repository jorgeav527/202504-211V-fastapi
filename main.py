import os
from datetime import datetime

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
mongo_url = os.getenv("MONGO_URL")

client = MongoClient(mongo_url)
db = client["posts_db"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Post(BaseModel):
    title: str
    comment: str


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/posts")
def get_posts():
    posts = []
    for doc in db.posts.find():
        doc["id"] = str(doc.pop("_id"))
        posts.append(doc)
    return posts


@app.get("/posts/{post_id}")
def get_post(post_id: str):
    try:
        obj_id = ObjectId(post_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    doc = db.posts.find_one({"_id": obj_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Post not found")

    doc["id"] = str(doc.pop("_id"))
    return doc


@app.post("/posts")
def create_post(post: Post):
    now = datetime.now().isoformat()
    doc = {
        "title": post.title,
        "comment": post.comment,
        "createdAt": now,
        "updatedAt": now,
    }
    result = db.posts.insert_one(doc)
    doc.pop("_id")
    doc["id"] = str(result.inserted_id)
    return doc


@app.put("/posts/{post_id}")
def update_post(post_id: str, post: Post):
    try:
        obj_id = ObjectId(post_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    existing = db.posts.find_one({"_id": obj_id})
    if existing is None:
        raise HTTPException(status_code=404, detail="Post not found")

    now = datetime.now().isoformat()
    db.posts.update_one(
        {"_id": obj_id},
        {"$set": {"title": post.title, "comment": post.comment, "updatedAt": now}},
    )

    return {
        "id": post_id,
        "title": post.title,
        "comment": post.comment,
        "createdAt": existing["createdAt"],
        "updatedAt": now,
    }


@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    try:
        obj_id = ObjectId(post_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    result = db.posts.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"message": "Post deleted"}
