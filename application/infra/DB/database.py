import datetime
try:
    from .DB import DB
except:
    from DB import DB
#Users collection
Users = DB("NLP-Users", "NU")
#Confirm users collection
Confirm = DB("NLP-Users", "Confirm")
if __name__ == '__main__':
    print(Users.read({"user_email": "b"}, {"_id": 0})['api_key'][0])