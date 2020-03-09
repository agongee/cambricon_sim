from copy import deepcopy

class Fetcher:
    def __init__(self, width=2):
        self.width = width
        self.to_fetch = []
        self.fetched = []

    def get(self, pc, lines):

        # print("GET ", pc, len(lines))

        if pc+self.width < len(lines):
            self.to_fetch = deepcopy(lines[pc:pc+self.width])
            return pc + self.width
        elif pc >= len(lines):
            self.to_fetch = []
            return pc
        else:
            self.to_fetch = deepcopy(lines[pc:])
            return len(lines)

    def send(self):
        if len(self.to_fetch) == 0:
            self.fetched = []
        else:
            self.fetched = deepcopy(self.to_fetch)
            self.to_fetch = []
    
    def to_decoder(self):
        if len(self.fetched) != 0:
            temp = deepcopy(self.fetched)
            self.fetched = []
            return temp
        else:
            return []

    def is_empty(self):
        return len(self.to_fetch) == 0 and len(self.fetched) == 0

    def left(self):
        return len(self.to_fetch) + len(self.fetched)