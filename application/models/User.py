try:
    from Preprocess import Preprocess
    from security.SecurityUtils import encrypt
except (ModuleNotFoundError, ImportError):
    from .Preprocess import Preprocess
    from .security.SecurityUtils import encrypt


from datetime import timezone, timedelta, datetime

class User(Preprocess):
    def __init__(self, user_name, user_email, user_password) -> None:
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = encrypt(user_password).decode('utf-8')
        self.tier = 'Free'
        
        self.verified = False
        self.is_active = True
        
        fuso_horario = timezone(timedelta(hours=-3))
        date = datetime.now().astimezone(fuso_horario).strftime('%Y/%m/%d')
        
        self.created_at = date
        self.modified_at = date
        
if __name__ == '__main__':
    u1 = User('Elias', 'Elias@a.com', '123')
    print(u1.orm())