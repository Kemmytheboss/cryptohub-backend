from fastapi import FastAPI
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Backend running successfully!"}
