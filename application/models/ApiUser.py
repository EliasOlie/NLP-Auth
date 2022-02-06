from pydantic import BaseModel
from typing import Any

class ApiUser(BaseModel):
    user_name: str
    user_email: str
    user_password: str

class UserChange(BaseModel):
    field: str
    value: Any
    
class UserConfirm(BaseModel):
    randstring: str