from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.transactions import Transaction
from app.auth.jwt_handler import get_current_user
from app.auth.permissions import admin_required

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# user creates deposit
@router.get("/deposit")
def create_deposit(
    amount: float,
    currency: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_transaction = Transaction(
        user_id=current_user.id,
        type="deposit",
        amount=amount,
        currency=currency,
        status="pending"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return {"message": "Deposit created", "transaction": new_transaction}

    # user request withdrawal
@router.post("/withdraw")
def create_withdrawal(
    amount: float,
    currency: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_transaction = Transaction(
        user_id=current_user.id,
        type="withdrawal",
        amount=amount,
        currency=currency,
        status="pending"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return {"message": "Withdrawal request created", "transaction": new_transaction}    

# user can view own transactions
@router.get("/my")
def get_my_transactions(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return txns

# ADMIN — approve transaction
@router.post("/approve/{tx_id}")
def approve_transaction(tx_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(admin_required)):

    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.status = "approved"
    db.commit()

    return {"message": "Transaction approved", "transaction": tx}


# ADMIN — reject transaction
@router.post("/reject/{tx_id}")
def reject_transaction(tx_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(admin_required)):

    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.status = "rejected"
    db.commit()

    return {"message": "Transaction rejected", "transaction": tx}


# ADMIN — list all transactions
@router.get("/all")
def get_all_transactions(db: Session = Depends(get_db),
                         current_user: User = Depends(admin_required)):

    return db.query(Transaction).all()