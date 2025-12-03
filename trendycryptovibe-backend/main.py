from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes.user import router as user_router
from app.routes.wallet import router as wallet_router
from app.routes.roles import router as roles_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Backend running successfully!"}
app.include_router(user_router)
app.include_router(wallet_router)
app.include_router(roles_router)