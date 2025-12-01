import json
import os

class Base_db:
    def __init__(self):
        self.base_path = 'data'
        self.file_path = '/'.join((self.base_path, self.file_name))

    def read(self):
        if not os.path.exists(self.file_path):
            print(f"{self.file_path} not exists")
            return False
        
        with open(self.file_path, 'r') as file:
            raw = file.readline()
    
            if len(raw) > 0:
                data = json.loads(raw)
            else:
                data = []

        return data
    
    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item

        with open(self.file_path, 'w') as file:
            file.write(json.dumps(data))


class Blockchain_db(Base_db):
    def __init__(self):
        self.file_name = 'blockchain'
        super().__init__()

    def last_block(self):
        data = self.read()
        if data:
            return data[-1]
