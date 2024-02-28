from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel
import users

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

    def create_post(self,post):
        post_dict = post.dict()

        if not users.login.user_logged_in():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You need to be logged in to create posts")
        
        try:
            self.cursor.execute("INSERT INTO posts (title, content, publish) VALUES (%s,%s,%s) RETURNING *;",
                        (post_dict['title'],post_dict['content'],post_dict['publish']))  # %s to prevent SQL injection attacks
            
            data = self.cursor.fetchall()[0]
            


            self.cursor.execute("UPDATE users SET posts = array_append(posts, %s) WHERE email_id = %s RETURNING *",
                                 (data['id'],users.login.user_logged_in()))
            
            user_data = self.cursor.fetchall()[0]
            
            self.cursor.execute("UPDATE posts SET posted_by = %s WHERE id = %s", (user_data['user_id'], data['id']))

            
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
        if not users.login.user_logged_in():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You need to be logged in")
        
        try:
            self.cursor.execute('SELECT posted_by FROM posts WHERE id = %s', (id,))
            data = self.cursor.fetchall()
            if data:
               data = data[0]
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            
            self.cursor.execute('SELECT email_id FROM users WHERE user_id = %s', (data['posted_by'],))
            user_data  = self.cursor.fetchall()

            if user_data:
               user_data = user_data[0]
            else:
                self.db.rollback()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You can only delete your own posts')
            
            self.db.commit()
            if user_data['email_id'] != users.login.user_logged_in():
                self.db.rollback()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You can only delete your own posts')
            
            self.cursor.execute("DELETE FROM posts WHERE id = %s;",(id,))
            self.db.commit()
            return {"message":"post deleted"}
        except Exception as error:
            self.db.rollback()
            raise error
        
    def update_posts(self,id : int, post):
        if not users.login.user_logged_in():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You need to be logged in")

        try:
            
            self.cursor.execute('SELECT posted_by FROM posts WHERE id = %s', (id,))
            data = self.cursor.fetchall()[0]
            self.cursor.execute('SELECT email_id FROM users WHERE user_id = %s', (data['posted_by'],))
            user_data  = self.cursor.fetchall()[0]
            self.db.commit()
            if user_data['email_id'] != users.login.user_logged_in():
                self.db.rollback()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='You can only update your own posts')
            
            post = post.dict()
            self.cursor.execute("UPDATE posts SET title=%s, content = %s,publish = %s WHERE id = %s RETURNING *;",
                            (post['title'], post['content'],post['publish'],id))
            updated_post = self.cursor.fetchall()
            self.db.commit()
            return updated_post
        except Exception as error:
            print(error)
            self.db.rollback()
            raise error