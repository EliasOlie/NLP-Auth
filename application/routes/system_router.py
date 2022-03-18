import os
import json
import requests
from decouple import config
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from application.models.SystemApiSchema import ValidReq
from application.infra.DB.database import Users
from application.routes.auth_router import auth_handler

try:
    PSW = os.environ["INTERNAL_PASSWORD"]
    CORE_URL = os.environ["CORE_API"]
except KeyError:
    ENV = config("ENV")
    CORE_URL = config("CORE_API")

router = APIRouter(
    prefix='/api/v1/system',
    tags=['System']
)

def handle_user_calls(api_key):
    user = Users.read({"api_key": api_key}, {"_id": 0})
    transaction = Users.update({"user_email": user['user_email']}, {"$set": {"daily_calls": str(int(user['daily_calls'])-1)}})
    if transaction >= 1:
        return True
    else:
        return False

def restore_user_limits(payload):
    transaction = Users.update({"api_key": payload}, {"$set":{"daily_calls": 1000}})
    if transaction >= 1:
        return True
    else:
        return False
        
@router.post('/is_req_valid')
def valid_req(req: ValidReq, user=Depends(auth_handler.auth_wrapper)):
    if user:
        if user['daily_calls'] >= 1:
            payload = {"usr_api": user['api_key'], "data": req.data}
            r = requests.post(url=f"{CORE_URL}{req.callback_url}", data=json.dumps(payload))
            try:
                if r.json()['process_output']:
                   if handle_user_calls(user['api_key']):
                        return JSONResponse(status_code=200, content=r.json())   
            except KeyError:
                return JSONResponse(status_code=500)
        else:
            return JSONResponse(status_code = 403, content={"Message": "You're running out of fuel boy! Consider upgrade your plan ;)"})
    else:
        return JSONResponse(status_code=404, content={"Message": "User not found"})