from base64 import encode
import bcrypt

def encrypt(password:str):
    password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed_password

def compare_digest(user_input ,password):
    return bcrypt.checkpw(user_input.encode('utf-8'), password.encode('utf-8'))
       
if __name__ == '__main__':
    osw = "$2b$12$zLFrUBuzNQwqtTxxF.PkyubYcSoXFSP1VUuPffb5904anpP5mbrnC"
    print(compare_digest("c", osw))
