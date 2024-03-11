from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import keys
# import models
# from database import engine

# models.Base.metadata.create_all(bind=engine)

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

import users, posts

app = FastAPI()

app.include_router(posts.router)

app.include_router(users.router)


# to run the server: uvicorn main:app
#main - name of the py file
#app - object of the FastAPI class created by us