from fastapi import HTTPException
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from posts import *

class logged_in:
    def __init__(self) -> None:
        self.email = None
    def user(self,email):
        self.email = email

    def user_logged_in(self):
        if self.email:
            return self.email
        else:
            return False

login = logged_in()

class user(BaseModel):
    name: str
    email_id: str
    password: str
    posts : list = []
    user_id : int = None

class login_details(BaseModel):
    email_id : str
    password : str

key = 1423

def basic_encryption(n:int,password:str,hash:bool) -> str: 
    if hash:
        out = ''
        for i in password:
            out += f"{chr(ord(i) + n)}"
    else:
        out = ''
        for i in password:
            out += f"{chr(ord(i) - n)}"
    return out

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
            else:
                self.db.rollback()
                return {'message':"email already registered"}
            
            self.cursor.execute('INSERT INTO users (name,email_id,password,posts,logged_in) VALUES (%s,%s,%s,%s,true) RETURNING *'
                                ,(user_data['name'],user_data['email_id'],
                                basic_encryption(key,user_data['password'],True)
                                ,user_data['posts']))
            
            user_created = self.cursor.fetchall()
            login.user(user_data['email_id'])
            self.db.commit()
            return user_created
        
        except Exception as error:
            self.db.rollback()
            print(error)
            return  error

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
    
    def user_login(self,email_id:str, password:str):
        try:
            self.cursor.execute('SELECT * FROM users WHERE logged_in = true')
            data = self.cursor.fetchall()
            if data != []:
                self.db.rollback()
                return {"message": "A user is already logged in"}
            
            self.cursor.execute('SELECT * FROM users WHERE email_id = %s',(email_id,))
            matched = self.cursor.fetchall()
            print(matched)
            if matched != []:
                if password == basic_encryption(key, matched['password'],False):
                    self.cursor.execute('UPDATE users SET logged_in = true WHERE email_id = %s',(email_id,))
                    login.user(email_id)
                    self.db.commit()
                    print('logged in')
                    return {'message':'logged in successfully'}
                
                else:
                    self.db.rollback()
                    print('else')
                    return {"message":"Wrong password"}

            else:
                print('outsude')
                self.db.rollback()
                return {"message":"user not found"}
            
        except Exception as error:
            self.db.rollback()
            return {"message": error}
        

    def user_logout(self):
        try:
            self.cursor.execute('SELECT * FROM users WHERE logged_in = true')
            data = self.cursor.fetchall()
            if data == []:
                self.db.rollback()
                return {"message": "No user is logged in"}
            
            self.cursor.execute('UPDATE users SET logged_in = false WHERE logged_in = true')
            self.db.commit()
            return {'message': "the user was logged out"}


        except Exception as error:
            self.db.rollback()
            return {"message": error}