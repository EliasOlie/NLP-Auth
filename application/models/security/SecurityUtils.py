import bcrypt

def encrypt(password:str):
    password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed_password

def compare_digest(password:str):
    tr = input("PSW: ")
    tr = tr.encode('utf-8')
    if bcrypt.checkpw(tr, password):
        print('SUCESS')
    else:
        print('Fail')