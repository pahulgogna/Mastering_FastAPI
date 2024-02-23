from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from users import *

#connecting to the database
while True:
    try:
        db = psycopg2.connect(host='localhost', database='fastAPI', user = 'postgres',
                            password='pahul123', cursor_factory=RealDictCursor)
        cursor = db.cursor()
        print("\nConnected to Database!!\n")
        break
    except Exception as error:
        print("Connection Failed!")
        print("Error: ", error)
        time.sleep(2)

class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    id: int = None

app = FastAPI()

users = Users(db,app)

@app.post('/users/login')
def login_user(payLoad:login_details):
    payLoad = payLoad.dict()
    email = payLoad['email_id']
    password = payLoad['password']
    return users.user_login(email,password)

@app.post('/users/logout')
def logout_user():
    return users.user_logout()

@app.post('/users/create')
def create_user(user_data:user):
    return users.create_user(user_data)

@app.get('/users')
def get_users():
    return users.get_all_users()

@app.get('/users/{id}')
def get_a_user(id:int):
    return users.get_users(id)



@app.get("/posts") # .get for sending a respose to "get requests" from the browser at "/" path 
def get_posts():
    try:
        cursor.execute("SELECT * FROM posts;")
        posts = cursor.fetchall()
        db.commit()
        return posts
    except Exception as error:
        print(error)
        db.rollback()
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return {"message":"Posts could not be found"} #the message we are sending in case of failure

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_post(post : Post):
    post_dict = post.dict()
    try:
        cursor.execute("INSERT INTO posts (title, content, publish) VALUES (%s,%s,%s) RETURNING *;",
                    (post_dict['title'],post_dict['content'],post_dict['publish']))  # %s to prevent SQL injection attacks
        db.commit()
        return {"Post created":post_dict}
    except Exception as error:
        db.rollback()
        HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        return {"message": f"Post could not be created due to {error}"}    

@app.get("/posts/{id}")
def get_post(id : int):
    try:
        cursor.execute("SELECT * FROM posts WHERE id = %s;", (id,))
        found = cursor.fetchall()[0] #--> dict
        db.commit()
        return found
    except Exception as error:
        print("ERROR: ",error)
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return {"Message":"Post not found"}


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    try:
        cursor.execute("DELETE FROM posts WHERE id = %s;",(id,))
        db.commit()
        return {"message":"post deleted"}
    except Exception as error:
        db.rollback()
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return {"message":error}

@app.put("/posts/{id}")
def update_posts(id : int, post : Post):
    try:
        post = post.dict()
        cursor.execute("UPDATE posts SET title=%s, content = %s,publish = %s WHERE id = %s RETURNING *;",
                        (post['title'], post['content'],post['publish'],id))
        updated_post = cursor.fetchall()
        db.commit()
        return updated_post
    except Exception as error:
        print(error)
        db.rollback()
        HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return {"message": "Post could not be found"}
    
 
# to run the server: uvicorn main:app
#main - name of the py file
#app - object of the FastAPI class created by us