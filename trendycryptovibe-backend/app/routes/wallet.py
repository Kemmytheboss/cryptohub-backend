from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.jwt_handler import get_current_user
from app.models.wallets import Wallet

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.get("/")
def get_user_wallets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    wallets = db.query(Wallet).filter(Wallet.user_id == current_user.id).all()
    return wallets
