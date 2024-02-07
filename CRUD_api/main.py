from fastapi import FastAPI
from fastapi.params import Body


app = FastAPI()

@app.get("/") # .get for sending a respose to "get requests" from the browser at "/" path
async def root():
    return {"message":"Hello World"} #the message we are sending

@app.post("/create_post")
def create_post(payLoad : dict = Body(...)):
    print(payLoad)
    return {"Message":f"Title: {payLoad['title']},   Content: {payLoad['content']}"}


# to run the server: uvicorn main:app
#main - name of the py file
#app - object of the FastAPI class created by us