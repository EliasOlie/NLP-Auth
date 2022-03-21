from fastapi.testclient import TestClient
import json

import pytest
from application.infra.DB.database import Confirm
from app import app

"""
TODO:
• Confirmar email automaticamente
• Fail tests
• Todos os cases do flow de confirmação
• fail testes de usuários cadastrados e logados
"""

client = TestClient(app)

def test_create_user():
    payload = {
        "user_name": "TestUssr",
        "user_email": "test@test.com",
        "user_password": "123"
    }
    r = client.post('/user/create', json.dumps(payload))
    assert r.status_code == 201
    
def test_user_code_generated():
    code = Confirm.read({'user_email': "test@test.com"})
    if code['Code']:
        assert True
    else:
        assert False
        
def test_confirm_user(token): #<- Error Github (TypeError expected string value)
    code = Confirm.read({'user_email': "test@test.com"})
    if code['Code']:
        payload = json.dumps({"randstring": code['Code']})
        r = client.post(f'/user/test@test.com/confirm', payload)
        usr = client.get(f'/user', headers={"Authorization": f"Bearer {token}"}).json()
        assert r.status_code == 200 and usr['verified'] == True
        
def test_create_user_fail():
    payload = {
        "user_name": "TestUssr",
        "user_email": "test@test.com",
        "user_password": "123"
    }
    r = client.post('/user/create', json.dumps(payload))
    assert r.status_code == 400


def test_login_user(): #<- Failed Github (TypeError expected string value)
    payload = json.dumps({
        "useremail": "test@test.com",
        "password": "123"
    })
    c = client.post('/security/login', payload)
    assert c.status_code == 200
    return c.json()['token']
    
def test_read_user(token): #<- Error Github (TypeError expected string value)
    r = client.get(f'/user', headers= {"Authorization": f"Bearer {token}"})
    attrs = r.json()
    attrs_list = ['user_name', 'user_email', 'created_at', 'daily_calls', 'api_key', 'is_active', 'verified']
    control = 0
    for key in attrs.keys():
        if key in attrs_list:
            control += 1
        else:
            control -= 1
    
    assert control == len(attrs_list)
    assert r.status_code == 200
    
def test_read_user_fail():
    r = client.get(f'/user')
    
    assert r.status_code == 403

def test_update_user(token): #<- Error Github (TypeError expected string value)
    payload = json.dumps({
        "field": "user_name",
        "value": "TestUser"
    })
    
    r = client.put(f'/user/edit', payload, headers={"Authorization": f"Bearer {token}"})
    rs = client.get(f'/user', headers={"Authorization": f"Bearer {token}"}).json()
    
    
    assert r.status_code == 201 
    assert rs['user_name'] == "TestUser"
    
def test_update_user_fail():
    payload = json.dumps({
        "field": "user_name",
        "value": "TestUser"
    })
    
    r = client.put(f'/user/edit', payload)    
    
    assert r.status_code == 403
    
def test_delete_user(token): #<- Error Github (TypeError expected string value)
    r = client.get("/user/delete", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201

def test_delete_user_fail():
    r = client.get(f'/user/delete')
    assert r.status_code == 403
    
    
if __name__ == '__main__':
    test_create_user()
    test_create_user_fail()
    test_login_user()
    test_user_code_generated()
    test_confirm_user(token)
    test_read_user(token)
    test_read_user_fail()
    test_update_user(token)
    test_update_user_fail()
    test_delete_user(token)
    test_delete_user_fail()