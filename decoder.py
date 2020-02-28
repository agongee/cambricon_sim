import re


class Decoder:
    def __init__(self):
        self.to_decode = None
        self.decoded = None
        self.to_pass = None

    def recv(self, inst):
        self.to_decode = inst

    def send(self):
        self.to_pass = self.decoded
        
        
    def decode(self):
        pattern = '\s+,?\s*|\s?,?\s+'
        self.decoded = re.split(pattern, self.to_decode)
        

        


