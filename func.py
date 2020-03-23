from copy import deepcopy

from utill import compute as COMPUTE
from utill import check_scalar_func

class ScalarFunc:
    def __init__(self):
        self.next_v = []
        self.next_r = []

    def compute(self, inst):
        v, r = COMPUTE(inst[0], inst[1:])
        self.next_v.append(v)
        self.next_r.append(r)

        '''
        if self.left == 1:
            self.left = 0
            v, r = COMPUTE(self.current_inst[0], self.current_inst[1:])
            return v, r
        elif self.left == 0 and check_scalar_func(inst) and inst[0] != 'SSTORE':
            self.left = self.cycle
            self.current_inst = deepcopy(inst)
            return None, None
        else:
            self.left -= 1
            return None, None
        '''

    def passing(self):
        temp_v = deepcopy(self.next_v)
        temp_r = deepcopy(self.next_r)
        self.next_v = []
        self.next_r = []
        return temp_v, temp_r

class VectorFunc:
    def __init__(self, num=32, c_cycle=1, d_cycle=1, width=32):
        self.num = num
        self.c_cycle = c_cycle
        self.d_cycle = d_cycle
        self.width = width
        self.left = 0
        self.trans = True

    def request(self, inst):
        if self.left == 1:
            self.left = 0
            return True
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            return False
        elif self.left != 0:
            self.left -= 1
            return False
        elif inst[0] == 'VLOAD' or inst[0][1:] == 'VSTORE':
            size = int(inst[2])
            s_w = size / self.width 
            self.left = int(s_w * self.d_cycle)
            self.trans = True
            return False
        else: # computation 
            size = int(inst[2])
            s_n = size / self.num
            self.left = int(s_n * self.c_cycle)
            self.trans = False
            return False
    
    def left_cycle(self):
        return self.left, self.trans



class MatrixFunc:
    def __init__(self, num=32, c_cycle=1, d_cycle=1, width=32):
        self.num = num
        self.c_cycle = c_cycle
        self.d_cycle = d_cycle
        self.width = width
        self.left = 0
        self.trans = True

    def request(self, inst):
        # print("MATRIX ", inst)
        if self.left == 1:
            self.left = 0
            return True
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            return False     
        elif self.left != 0:
            self.left -= 1
            return False
        elif inst[0] == 'MLOAD' or inst[0] == 'MSTORE':
            size = int(inst[2])
            s_w = size / self.width
            self.left = int(s_w * self.d_cycle)
            self.trans = True
            return False
        else: # computation
            size = int(inst[2])
            s_n = size / self.num
            self.left = int(s_n * self.c_cycle)
            self.trans = False
            return False

    def left_cycle(self):
        return self.left, self.trans
