from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from pydantic import BaseModel

class user(BaseModel):
    name: str
    email_id: str
    password: str
    posts : list = []
    user_id : int = None


class Users:
    def __init__(self,db,app) -> None:
        self.db = db
        self.cursor = db.cursor()
        self.app = app

    def create_user(self, user_data : user) -> dict:
        try:
            user_data = user_data.dict()
            self.cursor.execute('SELECT name FROM users WHERE email_id = %s',(user_data['email_id'],))
            matches = self.cursor.fetchall()
            
            if matches == []:
                pass
                self.db.commit()
            else:
                self.db.rollback()
                return {'message':"email already registered"}
            self.cursor.execute('INSERT INTO users (name,email_id,password,posts) VALUES (%s,%s,%s,%s) RETURNING *'
                                ,(user_data['name'],user_data['email_id'],user_data['password'],user_data['posts']))
            user_created = self.cursor.fetchall()
            self.db.commit()
            return user_created
        
        except Exception as error:
            self.db.rollback()
            print(error)
            return {'message': error}

    def get_all_users(self):
        try:
            self.cursor.execute('SELECT name,user_id,posts FROM users')
            users = self.cursor.fetchall()
            self.db.commit()
            return users
        except Exception as error:
            self.db.rollback()
            return {"message":error}

    def get_users(self, id: int):
        try:
            self.cursor.execute('SELECT name,user_id,posts FROM users WHERE user_id = %s;',(id,))
            user_data = self.cursor.fetchall()
            self.db.commit()
            return user_data
        except Exception as error:
            return {'message':error}