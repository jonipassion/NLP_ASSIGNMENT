from fastapi import FastAPI

app = FastAPI(title="Educational Quiz API", version="0.1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Educational Quiz API! Only educational quizzes are generated."}
