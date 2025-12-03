from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.wallets import Wallet
from app.models.schemas import UserCreate, UserLogin, UserResponse
from app.auth.hash import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
import uuid

router = APIRouter(prefix="/users", tags=["Users"])

def generate_wallet_address(prefix="WALLET"):
    return f"{prefix}_{uuid.uuid4().hex[:32]}"

@router.post("/register", response_model=UserResponse)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=data.email, password=hash_password(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    profile = Profile(user_id=new_user.id, username=data.email.split("@")[0])
    db.add(profile)
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    new_user.roles.append(admin_role)
    default_role = db.query(Role).filter(Role.name == "user").first()
    new_user.roles.append(default_role)



    networks = ["BTC", "ETH", "BSC", "TRON"]
    for net in networks:
        wallet = Wallet(
            user_id=new_user.id,
            network=net,
            address=generate_wallet_address(net)
        )
        db.add(wallet)

    db.commit()
    return new_user


@router.post("/login")
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}
