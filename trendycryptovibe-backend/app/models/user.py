from sqlalchemy import column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base)::
    __tablename__ = "users"

    id = column(Integer, primary_key=True, index=True)
    email = column(String, unique=True, index=True, nullable=False)
    hashed_password = column(String, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
