from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    bio = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
