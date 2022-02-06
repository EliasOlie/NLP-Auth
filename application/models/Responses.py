from pydantic import BaseModel

class User(BaseModel):
    user_name: str
    user_email: str
    created_at: str
    is_active: bool
    verified: bool

class Message(BaseModel):
    message: str