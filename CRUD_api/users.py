from fastapi import HTTPException,status,APIRouter
from pydantic import BaseModel,EmailStr
from posts import *
import pickle
from keys import key
from main import db,cursor

router = APIRouter(
    prefix= "/users",
    tags=["Users"]
)

def store_log(write:bool,data=None):
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
        store_log(True,data=self.__email)

    def user_logged_in(self):
        return store_log(False)

class user(BaseModel):
    name: str
    email_id: EmailStr
    password: str
    posts : list = []
    user_id : int = None

class login_details(BaseModel):
    email_id : EmailStr
    password : str


login = logged_in()

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


@router.post('/create')
def create_user(user_data:user):
    try:
        user_data = user_data.dict()
        cursor.execute('SELECT name FROM users WHERE email_id = %s ',(user_data['email_id'],))
        matches = cursor.fetchall()
        
        if matches == []:
            pass
        else:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="email already registered")
        
        cursor.execute('INSERT INTO users (name,email_id,password,posts) VALUES (%s,%s,%s,%s) RETURNING *'
                            ,(user_data['name'],user_data['email_id'],
                            basic_encryption(key,user_data['password'],True)
                            ,user_data['posts']))
        
        user_created = cursor.fetchall()
        db.commit()
        try:
            user_login(user_data['email_id'],user_data['password'])
        except Exception as error:
            return error
            
        return user_created
    
    except Exception as error:
        db.rollback()
        print(error)
        return  error

@router.get('/')
def get_all_users():
    try:
        cursor.execute('SELECT name,user_id,posts FROM users')
        users = cursor.fetchall()
        db.commit()
        return users
    except Exception as error:
        db.rollback()
        return {"message":error}

@router.get('/{id}')
def get_users(id: int):
    try:
        cursor.execute('SELECT name,user_id,posts FROM users WHERE user_id = %s;',(id,))
        user_data = cursor.fetchall()
        db.commit()
        if user_data == []:
            return {'message':"User not found"}
        return user_data
    except Exception as error:
        return {'message':error}

@router.post('/login')
def user_login(payLoad:login_details):
    payLoad = payLoad.dict()
    email_id = payLoad['email_id']
    password = payLoad['password']
    try:
        if login.user_logged_in():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="A user is already logged in")
        
        cursor.execute('SELECT * FROM users WHERE email_id = %s',(email_id,))
        matched = cursor.fetchall()
        matched = matched[0]
        if matched:
            if password == basic_encryption(key, matched['password'],False):
                cursor.execute('UPDATE users SET logged_in = true WHERE email_id = %s',(email_id,))
                login.user(email_id)
                db.commit()
                return {'message':'logged in successfully'}   
            
            else:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Wrong password")
                            
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
        
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(error)[4:])        
    

@router.post('/logout')
def user_logout():
        try:
            if not login.user_logged_in():
                db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail= "You are not logged in")
                        
            cursor.execute('UPDATE users SET logged_in = false WHERE email_id = %s',(login.user_logged_in(),))
            db.commit()
            login.user(False)
            return {'message': "the user was logged out"}


        except Exception as error:
            db.rollback()
            return error