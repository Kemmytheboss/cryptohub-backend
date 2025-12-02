from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes.user import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Backend running successfully!"}
app.include_router(user_router)