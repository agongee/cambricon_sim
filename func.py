from copy import deepcopy

from utill import compute as COMPUTE

class ScalarFunc:
    def __init__(self, cycle=1):
        self.cycle = cycle
        self.left = 0
        self.current_inst = []

    def compute(self, inst):
        if self.left == 1:
            self.left = 0
            v, r = COMPUTE(self.current_inst[0], self.current_inst[1:])
            return v, r
        elif self.left == 0:
            self.left = self.cycle
            self.current_inst = deepcopy(inst)
            return None, None
        else:
            self.left -= 1
            return None, None

class VectorFunc:
    def __init__(self, num=32, c_cycle=1, d_cycle=1, width=512, capacity=64):
        self.num = num
        self.c_cycle = c_cycle
        self.d_cycle = d_cycle
        self.width = width
        self.capacity = capacity
        self.left = 0

    def request(self, inst):
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            return False
        if self.left == 1:
            self.left = 0
            return True
        elif self.left != 0:
            self.left -= 1
            return False
        elif inst[0][1:] == 'LOAD' or inst[0][1:] == 'STORE':
            size = int(inst[2])
            s_w = size / self.width * 32
            self.left = s_w * self.d_cycle
            return False
        else: # computation 
            size = int(inst[2])
            s_n = size / self.num
            self.left = s_n * self.c_cycle
            return False
    
    def left_cycle(self):
        return self.left



class MatrixFunc:
    def __init__(self, num=32, c_cycle=1, d_cycle=1, width=512, capacity=768):
        self.num = num
        self.c_cycle = c_cycle
        self.d_cycle = d_cycle
        self.width = width
        self.capacity = capacity
        self.left = 0

    def request(self, inst):
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            return False
        if self.left == 1:
            self.left = 0
            return True
        elif self.left != 0:
            self.left -= 1
            return False
        elif inst[0][1:] == 'LOAD' or inst[0][1:] == 'STORE':
            size = int(inst[2])
            s_w = size / self.width * 32
            self.left = s_w * self.d_cycle
            return False
        else: # computation 
            size = int(inst[2])
            s_n = size / self.num
            self.left = s_n * self.c_cycle
            return False

    def left_cycle(self):
        return self.left