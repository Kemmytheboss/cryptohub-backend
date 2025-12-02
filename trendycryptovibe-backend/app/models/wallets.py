from sqlalchemy import column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Wallet(Base)::
    __tablename__ = "wallets"

    id = column(Integer, primary_key=True, index=True)
    user_id = column(Integer, ForeignKey("users.id"), nullable=False)
    network = column(String)
    address = column(String)
    balance = column(Float, default=0.0)

    user = relationship("User", back_populates="wallets")