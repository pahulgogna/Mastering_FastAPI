from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel
from users import *

class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    id: int = None

app = FastAPI()

class Posts:
    def __init__(self,db) -> None:
        self.db = db
        self.cursor = self.db.cursor()

    def get_posts(self):
        try:
            self.cursor.execute("SELECT * FROM posts;")
            posts = self.cursor.fetchall()
            self.db.commit()
            return posts
        except Exception as error:
            print(error)
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Posts could not be found")

    def create_post(self,post : Post):
        post_dict = post.dict()
        try:
            self.cursor.execute("INSERT INTO posts (title, content, publish) VALUES (%s,%s,%s) RETURNING *;",
                        (post_dict['title'],post_dict['content'],post_dict['publish']))  # %s to prevent SQL injection attacks
            self.db.commit()
            return {"Post created":post_dict}
        except Exception as error:
            self.db.rollback()
            HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
            return {"message": f"Post could not be created due to {error}"}    

    def get_post(self,id : int):
        try:
            self.cursor.execute("SELECT * FROM posts WHERE id = %s;", (id,))
            found = self.cursor.fetchall()[0] #--> dict
            self.db.commit()
            return found
        except Exception as error:
            print("ERROR: ",error)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")


    def delete_post(self,id : int):
        try:
            self.cursor.execute("DELETE FROM posts WHERE id = %s;",(id,))
            self.db.commit()
            return {"message":"post deleted"}
        except Exception as error:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= error)

    def update_posts(self,id : int, post : Post):
        try:
            post = post.dict()
            self.cursor.execute("UPDATE posts SET title=%s, content = %s,publish = %s WHERE id = %s RETURNING *;",
                            (post['title'], post['content'],post['publish'],id))
            updated_post = self.cursor.fetchall()
            self.db.commit()
            return updated_post
        except Exception as error:
            print(error)
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post could not be found")