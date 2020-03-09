import re

from copy import deepcopy


class Decoder:
    def __init__(self):
        self.to_decode = []
        self.decoded = []
        self.to_pass = []

    def recv(self, inst):
        if len(inst) != 0:
            self.to_decode = deepcopy(inst)
        else:
            self.to_decode = []

    def send(self):
        if len(self.decoded) != 0:
            self.to_pass = deepcopy(self.decoded)
            self.decoded = []
        else:
            self.to_pass = []
        
    def decode(self):
        if len(self.to_decode) == 0:
            self.decoded = []
            return

        pattern = '\s+,?\s*|\s?,?\s+'
        self.decoded = []
        # temp_decoded = []

        for i in self.to_decode:
            # temp_decoded.append(re.split(pattern, i))
            self.decoded.append(re.split(pattern, i))
            
        self.to_decode = []
            

    def to_issuequeue(self):
        temp = deepcopy(self.to_pass)
        self.to_pass = []
        return temp

    def is_empty(self):
        return len(self.to_decode) == 0 and \
            len(self.decoded) == 0 and len(self.to_pass) == 0

    def left(self):
        return len(self.decoded) + len(self.to_decode) + len(self.to_pass)
