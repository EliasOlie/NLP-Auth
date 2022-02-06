import string
import requests
import random
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from application.models.ApiUser import ApiUser, UserChange, UserConfirm
from application.models.Responses import User as RespUser
from application.models.Responses import Message
from application.models.User import User
from application.infra.DB.database import Users, Confirm
import datetime

router = APIRouter(
    tags=["User"],
    prefix='/user'
)
def handle_code_gen(email):
    randstring = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))
    Confirm.create({"user_email": email, "Code": randstring, "expire_at" : datetime.datetime.now() + datetime.timedelta(hours = 1)})
    return randstring

@router.post('/create', responses={400: {"model": Message, "description": "Bad Request"}})
def create_user(user_request: ApiUser):
    user_exists = Users.read({"user_email":user_request.user_email})
    if not user_exists:
        new_user = User(user_request.user_name, user_request.user_email, user_request.user_password)
        transaction = Users.create(new_user.orm())
        rand = handle_code_gen(user_request.user_email)
        if transaction == 0:
            requests.post('http://localhost:8001/sendmail', json.dumps({"addrs": user_request.user_email, "code": rand}))
            return JSONResponse(status_code=201)
    else:
        return JSONResponse(status_code=400, content={"Message": "This user alredy exists"})
    return user_exists 

@router.get('/{email}', response_model=RespUser, responses={404: {"model": Message, "description": "Resource not found"}})
def read_user(email):
    user_exists = Users.read({"user_email": email}, {'_id': 0})
    if user_exists:
        return user_exists
    else:
        return JSONResponse(status_code=404, content={"Message": "User not found"})

@router.put('/{email}/edit', responses={
    404: {"model": Message, "description": "Resource not found"}, 
    500: {"model": Message, "description": "Internal Server error"}
})
def update_user(email, u: UserChange):
    user_exists = Users.read({"user_email" : email}, {'_id' : 0})
    if user_exists:
        transaction = Users.update({'user_email': email}, {u.field:u.value})
        if transaction >= 1:
            return JSONResponse(status_code=201)
        else:
            return JSONResponse(status_code=500, content={"Message": "Something went wrong, please contact the server administrator"})
    else:
        return JSONResponse(status_code = 404, content={"Message": "User not found"})

@router.get('/{email}/delete', responses={
    404: {"model": Message, "description": "Resource not found"}, 
    500: {"model": Message, "description": "Internal Server error"}
})
def delete_user(email):
    user_exists = Users.read({"user_email" : email}, {'_id' : 0})
    if user_exists:
        transaction = Users.delete({"user_email": email})
        if transaction >= 1:
            return JSONResponse(status_code=201)
        else:
            return JSONResponse(status_code=500, content={"Message": "Something went wrong, please contact the server administrator"})
    else:
        return JSONResponse(status_code = 404, content={"Message": "User not found"})

@router.get('/{email}/confirm', responses={
    404: {"model": Message, "description": "Resource not found"}, 
    500: {"model": Message, "description": "Internal Server error"}
})
def request_confirm(email):
    usr = Users.read({"user_email": email}, {'_id': 0})
    if usr:
        if usr['verified'] == False:
            code = Confirm.read({"user_email": email}, {'_id': 0})
            if code:
                return JSONResponse(status_code=200, content={"Message": "You already has a code"})
            else:
                handle_code_gen(email)
                return JSONResponse(status_code=201, content={"Message": "Code generated"})
        else:
            return JSONResponse(status_code=200, content={"Message": "You already are verified"})
    else:
        return JSONResponse(status_code=404, content={"Message": "User not found"})
        
    
@router.post('/{email}/confirm', responses={
    404: {"model": Message, "description": "Resource not found"}, 
    500: {"model": Message, "description": "Internal Server error"}
})
async def confirm_user(email, user_input: UserConfirm):
    code = Confirm.read({"user_email": email}, {'_id': 0})
    if code:
        if user_input.randstring == code['Code']:
            Users.update({"user_email": email}, {"verified": True})
            Confirm.delete({"user_email": email})           
            return JSONResponse(status_code=200)
        else:
            return JSONResponse(status_code=400)
    else:
        return JSONResponse(status_code=404, content={"Message": "There's no code for this user"})    