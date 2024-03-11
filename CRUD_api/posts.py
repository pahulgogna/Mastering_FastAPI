from fastapi import HTTPException,status, Depends, APIRouter
from pydantic import BaseModel
import users
from database import get_db
# from sqlalchemy.orm import Session
# import models
from main import db,cursor

router = APIRouter(
    prefix= "/posts",
    tags=["Posts"]
)

class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    id: int = None

@router.get("/") # .get for sending a respose to "get requests" from the browser at "/posts" endpoint
def get_posts():
    try:
        # posts = db.query(models.Posts).all()
        cursor.execute("SELECT * FROM posts;")
        posts = cursor.fetchall()
        db.commit()
        return posts
    
    except Exception as error:
        print(error)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Posts could not be found")

@router.post("/",status_code=status.HTTP_201_CREATED)
def create_post(post_:Post):
    post_dict = post_.dict()

    if not users.login.user_logged_in():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You need to be logged in to create posts")
    
    try:
        cursor.execute("INSERT INTO posts (title, content, publish) VALUES (%s,%s,%s) RETURNING *;",
                    (post_dict['title'],post_dict['content'],post_dict['publish']))  # %s to prevent SQL injection attacks
        
        data = cursor.fetchall()[0]
        


        cursor.execute("UPDATE users SET posts = array_append(posts, %s) WHERE email_id = %s RETURNING *",
                                (data['id'],users.login.user_logged_in()))
        
        user_data = cursor.fetchall()[0]
        
        cursor.execute("UPDATE posts SET posted_by = %s WHERE id = %s", (user_data['user_id'], data['id']))

        
        db.commit()
        return {"Post created":post_dict}
    except Exception as error:
        db.rollback()
        HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        return {"message": f"Post could not be created due to {error}"}    

@router.get("/{id}")
def get_post(id : int):
    try:
        cursor.execute("SELECT * FROM posts WHERE id = %s;", (id,))
        found = cursor.fetchall()[0] #--> dict
        db.commit()
        return found
    except Exception as error:
        print("ERROR: ",error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    if not users.login.user_logged_in():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You need to be logged in")
    
    try:
        cursor.execute('SELECT posted_by FROM posts WHERE id = %s', (id,))
        data = cursor.fetchall()
        if data:
            data = data[0]
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        cursor.execute('SELECT email_id FROM users WHERE user_id = %s', (data['posted_by'],))
        user_data  = cursor.fetchall()

        if user_data:
            user_data = user_data[0]
        else:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You can only delete your own posts')
        
        db.commit()
        if user_data['email_id'] != users.login.user_logged_in():
            db.rollback()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You can only delete your own posts')
        
        cursor.execute("DELETE FROM posts WHERE id = %s;",(id,))
        db.commit()
        return {"message":"post deleted"}
    except Exception as error:
        db.rollback()
        raise error
    
@router.put("/{id}")
def update_posts(id : int, post:Post):
        if not users.login.user_logged_in():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You need to be logged in")

        try:
            
            cursor.execute('SELECT posted_by FROM posts WHERE id = %s', (id,))
            data = cursor.fetchall()[0]
            cursor.execute('SELECT email_id FROM users WHERE user_id = %s', (data['posted_by'],))
            user_data  = cursor.fetchall()[0]
            db.commit()
            if user_data['email_id'] != users.login.user_logged_in():
                db.rollback()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You can only update your own posts')
            
            post = post.dict()
            cursor.execute("UPDATE posts SET title=%s, content = %s,publish = %s WHERE id = %s RETURNING *;",
                            (post['title'], post['content'],post['publish'],id))
            updated_post = cursor.fetchall()
            db.commit()
            return updated_post
        except Exception as error:
            print(error)
            db.rollback()
            raise error