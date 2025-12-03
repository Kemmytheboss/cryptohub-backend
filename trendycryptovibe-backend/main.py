from fastapi import FastAPI
from app.db.database import engine, Base, SessionLocal
from app.models.role import Role
from app.routes.user import router as user_router
from app.routes.wallet import router as wallet_router
from app.routes.roles import router as roles_router
from app.routes.transactions import router as transactions_router
from app.routes.predict import router as predict_router
from app.routes.trading_bot import router as trading_bot_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Backend running successfully!"}
app.include_router(user_router)
app.include_router(wallet_router)
app.include_router(roles_router)
app.include_router(transactions_router)
app.include_router(predict_router)
app.include_router(trading_bot_router)

@app.on_event("startup")
def create_default_roles():
    db = SessionLocal()
    default_roles = ["user", "admin", "support"]

    for role_name in default_roles:
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if not existing_role:
            db.add(Role(name=role_name))
    db.commit()
    db.close()