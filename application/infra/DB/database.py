from .DB import DB

#Users collection
Users = DB("NLP-Users", "NU")
#Confirm users collection
Confirm = DB("NLP-Users", "Confirm")
Confirm.collection.create_index("expire_at", expireAfterSeconds=0)
#Apis collection
Apis = DB("Nlp-Users", "APIs")
#Dialogs collection
Dialogs = DB("Nlp-Users", "Dialogs")