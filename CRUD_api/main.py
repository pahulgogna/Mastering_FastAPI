from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from users import *
from posts import *
import keys

#connecting to the database
while True:
    try:
        db = psycopg2.connect(host='localhost', database='fastAPI', user = 'postgres',
                            password = keys.dbPassword, cursor_factory=RealDictCursor)
        cursor = db.cursor()
        print("\nConnected to Database!!\n")
        break
    except Exception as error:
        print("Connection Failed!")
        print("Error: ", error)
        time.sleep(2)


app = FastAPI()
users = Users(db)
posts = Posts(db)

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

@app.get("/posts") # .get for sending a respose to "get requests" from the browser at "/posts" endpoint
def get_all_posts():
    return posts.get_posts()

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_a_post(post: Post):
    return posts.create_post(post)

@app.get("/posts/{id}")
def get_a_post(id:int):
    return posts.get_post(id)

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    return posts.delete_post(id)

@app.put("/posts/{id}")
def update_a_post(id:int, post:Post):
    return posts.update_posts(id, post)



# to run the server: uvicorn main:app
#main - name of the py file
#app - object of the FastAPI class created by us