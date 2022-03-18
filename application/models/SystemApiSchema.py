from typing import Any
from pydantic import BaseModel

class SystemUser(BaseModel):
    usr_api: str
    
class SystemInternal(BaseModel):
    usr_api: str
    password: str

class ValidReq(BaseModel):
    callback_url: str
    data: Any
    
class CoreCallback(BaseModel):
    usr_api: str
    process_output: dict