from pydantic import BaseModel

class Auth(BaseModel):
    useremail: str
    password: str