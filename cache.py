

class Cache:
    def __init__(self, hit=4, miss=10, size=32):
        self.hit = hit
        self.miss = miss
        self.size = size
        self.addr_list = []
        self.left = 0

    def request(self, inst):
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            return False
        if self.left != 0:
            self.left -= 1
            return False
        elif self.left == 1:
            self.left = 0
            return True
        elif int(inst[2]) in self.addr_list:
            self.left = self.hit
            return False
        elif int(inst[2]) in self.addr_list:
            self.left = self.miss
            if len(self.addr_list) < self.size:
                self.addr_list.append(int(inst[2]))
            else:
                self.addr_list.pop(0)
                self.addr_list.append(int(inst[2]))
            return False
        else:
            return False
        

    def left_cycle(self):
        return self.left
