# one to one relationship with User model
# back_populates is used to define the reverse relationship in User model
# uselist=False indicates one-to-one relationship
    
from sqlalchemy iport column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class UserProfile(Base)::
    __tablename__ = "user_profiles"

    id = column(Integer, primary_key=True, index=True)
    user_id = column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = column(String, nullable=True)
    bio = column(String, nullable=True)

    user = relationship("User", back_populates="profile")
    
    