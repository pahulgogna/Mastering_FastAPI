from fastapi import FastAPI,Response,HTTPException,status
from pydantic import BaseModel
from typing import Optional
import random

class Id:
    def __init__(self) -> None:
        self.ids = [1,2] 

    def create_id(self):
        new_id = random.randint(100,10000000)
        if new_id in self.ids:
            new_id = random.randint(new_id+1,10000000)

        self.ids.append(new_id)
        return new_id


class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    rating: int = None
    id: int = None

posts = [{"title":"Title of post 1","content":"content of post 1","id":1},
         {"title":"Title of post 2","content":"content of post 2","id":2}]

def find_post(id):
    for p in posts:
        if p["id"] == int(id):
            return [p,True]
    return [f"No Post of id = {id} where found",False]

def find_post_id_index(id):
    for i,p in enumerate(posts):
        if p["id"] == id:
            return i

app = FastAPI()

id_data = Id()

def returns_ID(dict):
    return dict["id"]

for i in range(100):
    posts.append({"title": f"test post {i}","content":"content for post","id": id_data.create_id()})
    posts.sort(key=returns_ID)

@app.get("/posts") # .get for sending a respose to "get requests" from the browser at "/" path
def get_posts():
    return [{"total_posts":len(posts)},{"message":posts}] #the message we are sending

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_post(post : Post):
    post_dict = post.dict()
    post_dict["id"] = id_data.create_id()
    posts.append(post_dict)
    return {"Post created":post_dict}

@app.get("/posts/{id}")
def get_post(id : int):
    found = find_post(id)
    if not found[1]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=found[0])
        pass
    return found[0]


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    index = find_post_id_index(id)
    if index:
        posts.pop(index)
        return "Deleted post"
    raise HTTPException(status.HTTP_404_NOT_FOUND,detail="ERROR: Post Not Found")

@app.put("/posts/{id}")
def update_posts(id : int, post : Post):
    print(post)
    found = find_post(id)
    if not found[1]:
        raise HTTPException(status.HTTP_404_NOT_FOUND,f"Any Post with id {id} could not found")
    index = find_post_id_index(id)
    posts.pop(index)
    post_dict = post.dict()
    post_dict["id"] = id
    posts.insert(index,post_dict)
    return {"message":"updated post"}
 
# to run the server: uvicorn main:app
#main - name of the py file
#app - object of the FastAPI class created by us