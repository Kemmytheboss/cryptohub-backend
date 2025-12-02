from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.profile import Profile

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

@router.post("/register", response_model=UserResponse)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=data.email, password=data.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # create profile for the new user
    profile = Profile(user_id=new_user.id, username=data.email.split("@")[0])
    db.add(profile)
    db.commit()

    return new_user

    profile = relationship("Profile", uselist=False, back_populates="user")
    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
