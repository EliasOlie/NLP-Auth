from fastapi.testclient import TestClient
import json
from app import app

"""
TODO:
• Confirmar email automaticamente
• Fail tests
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
    
def test_create_user_fail():
    payload = {
        "user_name": "TestUssr",
        "user_email": "test@test.com",
        "user_password": "123"
    }
    r = client.post('/user/create', json.dumps(payload))
    assert r.status_code == 400
    
def test_read_user():
    email = "test@test.com"
    r = client.get(f'/user/{email}')
    attrs = r.json()
    attrs_list = ['user_name', 'user_email', 'created_at', 'is_active', 'verified']
    control = 0
    for key in attrs.keys():
        if key in attrs_list:
            control += 1
        else:
            control -= 1
    
    assert control == len(attrs_list) and r.status_code == 200
    
def test_read_user_fail():
    email = "foobar@baarfoor.coms.a"
    r = client.get(f'/user/{email}')
    
    assert r.status_code == 404

def test_update_user():
    email = "test@test.com"
    payload = json.dumps({
        "field": "user_name",
        "value": "TestUser"
    })
    
    r = client.put(f'/user/{email}/edit', payload)
    rs = client.get(f'/user/{email}').json()
    
    
    assert r.status_code == 201 and rs['user_name'] == "TestUser"
    
def test_update_user_fail():
    email = "foobar@baarfoor.coms.a"
    payload = json.dumps({
        "field": "user_name",
        "value": "TestUser"
    })
    
    r = client.put(f'/user/{email}/edit', payload)    
    
    assert r.status_code == 404
    
def test_delete_user():
    email = "test@test.com"
    r = client.get(f'/user/{email}/delete')
    assert r.status_code == 201

def test_delete_user_fail():
    email = "foobar@baarfoor.coms.a"
    r = client.get(f'/user/{email}/delete')
    assert r.status_code == 404
    
    
if __name__ == '__main__':
    test_create_user()
    test_create_user_fail()
    test_read_user()
    test_read_user_fail()
    test_update_user()
    test_update_user_fail()
    test_delete_user()
    test_delete_user_fail()