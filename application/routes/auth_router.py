from application.models.ApiAuthSchema import Auth
from application.models.Responses import User
from datetime import datetime, timedelta
from decouple import config
from fastapi import APIRouter
from fastapi.param_functions import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from application.infra.DB.database import Users
from passlib.context import CryptContext
from application.models.security.SecurityUtils import compare_digest

import json
import os
import jwt

if os.getenv("ENV"):
    ENV = os.getenv("ENV")
    JWT_SECRET = os.getenv("JWT_SECRET")
else:
    ENV = config("ENV")
    JWT_SECRET = config("JWT_SECRET")

router = APIRouter(
    tags=['Security'],
    prefix='/security'
)

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = JWT_SECRET
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password, hashed_password):
        return compare_digest(plain_password, hashed_password)
    
    def encode_token(self, user):
        payload={
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )
        
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms='HS256')
            return payload['sub']
        except jwt.exceptions.ExpiredSignatureError:
            return JSONResponse(status_code = 401, content={"Message": "Signature expired"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code = 401, content={"Message": "Invalid token"})
        
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        try:
            return json.loads(self.decode_token(auth.credentials))
        except TypeError:
            return self.decode_token(auth.credentials)

auth_handler = AuthHandler()
    
@router.post("/login")
def login(u: Auth):
    transaction = Users.read({"user_email": u.useremail}, {"_id": 0})
    if not transaction:
        return JSONResponse(status_code = 404, content={"Message": "User not found"})
    elif auth_handler.verify_password(u.password, transaction['user_password']):
        user = User(**transaction).json()
        token = auth_handler.encode_token(user)
    else:
        return JSONResponse(status_code=403, content={"Message": "Invalid Credentials"})
            
    return JSONResponse(status_code=200, content={'token': token})