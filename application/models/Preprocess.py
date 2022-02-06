import inspect
import json

class Preprocess:
    def __init__(self) -> None:
        ...
        
    def orm(self):
        attr = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        useds = [a for a in attr if not(a[0].startswith('__') and a[0].endswith('__'))]
        usr_obj = {}
        for used in useds:
            usr_obj[f"{used[0]}"] = used[1]
    
        return usr_obj