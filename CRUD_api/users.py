from fastapi import HTTPException,status
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from posts import *
import pickle

def store_log(data,write:bool):
    if write:
        with open("login_data/data.pkl",'wb') as f:
            pickle.dump(data,f)
    else:
        try:
            with open("login_data/data.pkl",'rb') as f:
                return pickle.load(f)
        except:
             with open("login_data/data.pkl",'wb') as f:
                pickle.dump(data,f)

class logged_in:
    def __init__(self) -> None:
        self.__email = False

    def user(self,email:str):
        self.__email = email
        store_log(self.__email,True)

    def user_logged_in(self):
        return store_log(None, False)

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
    def __init__(self,db) -> None:
        self.db = db
        self.cursor = db.cursor()

    def create_user(self, user_data : user) -> dict:
        try:
            user_data = user_data.dict()
            self.cursor.execute('SELECT name FROM users WHERE email_id = %s',(user_data['email_id'],))
            matches = self.cursor.fetchall()
            
            if matches == []:
                pass
            else:
                self.db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="email already registered")
            
            self.cursor.execute('INSERT INTO users (name,email_id,password,posts) VALUES (%s,%s,%s,%s) RETURNING *'
                                ,(user_data['name'],user_data['email_id'],
                                basic_encryption(key,user_data['password'],True)
                                ,user_data['posts']))
            
            user_created = self.cursor.fetchall()
            self.db.commit()
            self.user_login(user_data['email_id'],user_data['password'])
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
            if user_data == []:
                return {'message':"User not found"}
            return user_data
        except Exception as error:
            return {'message':error}
    
    def user_login(self,email_id:str, password:str):

        try:
            if login.user_logged_in():
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="A user is already logged in")
            
            self.cursor.execute('SELECT * FROM users WHERE email_id = %s',(email_id,))
            matched = self.cursor.fetchall()
            matched = matched[0]
            if matched:
                if password == basic_encryption(key, matched['password'],False):
                    self.cursor.execute('UPDATE users SET logged_in = true WHERE email_id = %s',(email_id,))
                    login.user(email_id)
                    self.db.commit()
                    return {'message':'logged in successfully'}   
                
                else:
                    self.db.rollback()
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Wrong password")
                                
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
            
        except Exception as error:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(error)[4:])        

    def user_logout(self):
        try:
            if not login.user_logged_in():
                self.db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail= "You are not logged in")
                        
            self.cursor.execute('UPDATE users SET logged_in = false WHERE email_id = %s',(login.user_logged_in(),))
            self.db.commit()
            login.user(False)
            return {'message': "the user was logged out"}


        except Exception as error:
            self.db.rollback()
            return error