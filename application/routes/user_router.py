import string
import requests
import os
import random
import json
import datetime
from decouple import config
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from application.models.ApiUser import ApiUser, UserChange, UserConfirm
from application.routes.auth_router import auth_handler
from application.models.Responses import User as RespUser
from application.models.Responses import Message
from application.models.User import User
from application.infra.DB.database import Users, Confirm
"""
TODO

Configurar variaveis por ambiente dev/prod +/-
Link que confirme o usuário com o código como parametro de rota ✔
"""


try:
    PSW = os.environ["SECURE_KEY"]
    ENV = os.environ["ENV"]
except KeyError:
    ENV = config("ENV")
    PSW = config('SECURE_KEY')

router = APIRouter(
    tags=["User"],
    prefix='/user'
)

def handle_code_gen(email):
    randstring = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))
    Confirm.create({"user_email": email, "Code": randstring, "created_at" : datetime.datetime.now() + datetime.timedelta(hours = 2)})
    return randstring

@router.post('/create', responses={400: {"model": Message, "description": "Bad Request"}})
def create_user(user_request: ApiUser):
    user_exists = Users.read({"user_email":user_request.user_email})
    if not user_exists:
        new_user = User(user_request.user_name, user_request.user_email, user_request.user_password)
        transaction = Users.create(new_user.orm())
        rand = handle_code_gen(user_request.user_email)
        if transaction == 0:
            if ENV == 'dev':
                email_service_link = 'http://localhost:8001'
            else:
                email_service_link = ""
            
            try:
                requests.post(f'{email_service_link}/sendmail', json.dumps({"addrs": user_request.user_email, "code": rand}), headers={"internal-psw": PSW})
            except Exception as e:
                #Handling looging with no mail services
                return JSONResponse(status_code=201)
                
            return JSONResponse(status_code=201)
    else:
        return JSONResponse(status_code=400, content={"Message": "This user alredy exists"})
    return user_exists 

@router.get('/', response_model=RespUser, responses={404: {"model": Message, "description": "Resource not found"}})
def read_user(user:RespUser = Depends(auth_handler.auth_wrapper)):
    if type(user) == JSONResponse:
        return user
    user_exists = Users.read({"user_email": user['user_email']}, {'_id': 0})
    if user_exists:
        return user_exists
    else:
        return JSONResponse(status_code=404, content={"Message": "User not found"})

@router.put('/edit', responses={
    404: {"model": Message, "description": "Resource not found"}, 
    500: {"model": Message, "description": "Internal Server error"}
})
def update_user(u: UserChange, user: RespUser = Depends(auth_handler.auth_wrapper)):
    user_exists = Users.read({"user_email" : user['user_email']}, {'_id' : 0})
    if user_exists:
        transaction = Users.update({'user_email': user['user_email']}, {"$set":{u.field:u.value}})
        if transaction >= 1:
            return JSONResponse(status_code=201)
        else:
            return JSONResponse(status_code=500, content={"Message": "Something went wrong, please contact the server administrator"})
    else:
        return JSONResponse(status_code = 404, content={"Message": "User not found"})

@router.get('/delete', responses={
    404: {"model": Message, "description": "Resource not found"}, 
    500: {"model": Message, "description": "Internal Server error"}
})
def delete_user(user: RespUser = Depends(auth_handler.auth_wrapper)):
    user_exists = Users.read({"user_email" : user['user_email']}, {'_id' : 0})
    if user_exists:
        transaction = Users.delete({"user_email": user['user_email']})
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
                code = handle_code_gen(email)
                try:
                    requests.post('http://localhost:8001/sendmail', json.dumps({"addrs": email, "code": code}), headers={"internal-psw": PSW})
                except Exception as e:
                    # Informar no log que o sistema de email está indisponível
                    return JSONResponse(status_code=201, content={"Message": "Code generated"}) #CODE SMELS TEM QUE LIDAR COM O SERVIÇO DOWN
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
            Users.update({"user_email": email}, {"$set":{"verified": True}})
            Confirm.delete({"user_email": email})           
            return JSONResponse(status_code=200)
        else:
            return JSONResponse(status_code=400)
    else:
        return JSONResponse(status_code=404, content={"Message": "There's no code for this user"})
    
@router.get('/{email}/confirm/{code}')
def confirm_user_route(email, code):
    code_exists = Confirm.read({"user_email": email}, {"_id": 0})
    if code_exists:
        if code == code_exists['Code'] and Users.read({"user_email": email}, {"_id": 0})['verified'] == False:
            Users.update({"user_email": email}, {"$set": {"verified": True}})
            Confirm.delete({"user_email": email})
            return JSONResponse(status_code=200)
        else:
            return JSONResponse(status_code=403)
    else:
        return JSONResponse(status_code=400, content={"Message": "There's no code for this user"})
        

@router.get('/keys')
def get_api_key(user: RespUser = Depends(auth_handler.auth_wrapper)):
    user = Users.read({'user_email': user['user_email']}, {"_id": 0})
    if user:
        api = user['api_key']
        if not api:   
            if Users.read({'user_email': user['user_email']}):
                randstring = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))+user['user_email']
                transaction = Users.update({"user_email": user['user_email']}, {"$set":{"api_key": randstring}})
                if transaction == 0:
                    return JSONResponse(status_code=201, content={"Message": randstring})
        else:
            return JSONResponse(status_code=200, content={"Message": api})
    else:
        return JSONResponse(status_code=404, content={"Message": "User not found"})