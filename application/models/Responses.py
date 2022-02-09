from pydantic import BaseModel
from .Preprocess import Preprocess

class User(BaseModel):
    user_name: str
    user_email: str
    created_at: str
    api_key: list[str]
    is_active: bool
    verified: bool
    
class UserPayload(Preprocess):
    def __init__(self, user_name, user_email, created_at, api_key, is_active, verified) -> None:
        self.user_name = user_name
        self.user_email = user_email
        self.created_at = created_at
        self.api_key = api_key
        self.is_active = is_active
        self.verified = verified

class Message(BaseModel):
    message: str