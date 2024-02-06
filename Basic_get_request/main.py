from fastapi import FastAPI

app = FastAPI()

@app.get("/") # .get for sending a respose to "get requests" from the browser at "/" path
async def root():
    return {"message":"Hello World"} #the message we are sending

# to run the server: uvicorn main:app
#main - name of the py file
#app - object of the FastAPI class created by us