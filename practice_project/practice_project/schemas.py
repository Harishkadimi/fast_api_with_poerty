from pydantic import BaseModel
from typing import Optional

class Users(BaseModel):
    username: str
    password: str
    created_at: Optional[str]