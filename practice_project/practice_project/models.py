from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base
from typing import Optional
from pydantic import BaseModel

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True,index=True)
    username = Column(String)
    password = Column(String)
    created_at = Column(String)
    