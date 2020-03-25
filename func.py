from copy import deepcopy

from util import compute as COMPUTE
from util import check_scalar_func

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
        self.wb = -1
        self.temp_wb = []

    def request(self, inst_class):
        inst = None
        if inst_class != None:
            inst = inst_class.inst
        if self.left == 1:
            self.left = 0
            if len(self.temp_wb) > 0:
                self.wb = self.temp_wb.pop(0)
                #print("VVV LET'S GO --> ", self.wb)
            else:
                self.wb = -1
            return True
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            self.wb = -1
            return False
        elif self.left != 0:
            self.left -= 1
            self.wb = -1
            return False
        elif inst[0] == 'VLOAD' or inst[0][1:] == 'VSTORE':
            size = int(inst[2])
            s_w = size / self.width 
            self.left = max(1, int(s_w * self.d_cycle))
            self.trans = True
            if inst[0] == 'VLOAD':
                temp_index = int(inst_class.org_inst[1][1:])
                self.temp_wb.append(temp_index)
                #print("VVV DEBUG --> ", temp_index)
            self.wb = -1
            return False
        else: # computation 
            size = int(inst[2])
            s_n = size / self.num
            self.left = max(int(s_n * self.c_cycle), 1)
            self.trans = False
            temp_index = int(inst_class.org_inst[1][1:])
            self.temp_wb.append(temp_index)
            #print("VVV DEBUG --> ", temp_index, " ", self.left)
            self.wb = -1
            return False
    
    def left_cycle(self):
        return self.left, self.trans, self.wb



class MatrixFunc:
    def __init__(self, num=32, c_cycle=1, d_cycle=1, width=32):
        self.num = num
        self.c_cycle = c_cycle
        self.d_cycle = d_cycle
        self.width = width
        self.left = 0
        self.trans = True
        self.wb = -1
        self.temp_wb = []

    def request(self, inst_class):
        inst = None
        if inst_class != None:
            inst = inst_class.inst
        # print("MATRIX ", inst)
        if self.left == 1:
            self.left = 0
            if len(self.temp_wb) > 0:
                self.wb = self.temp_wb.pop(0)
                #print("MMM LET'S GO --> ", self.wb)
            else:
                self.wb = -1
            return True
        if inst == None or inst == []:
            if self.left != 0:
                self.left -= 1
            self.wb = -1
            return False     
        elif self.left != 0:
            self.left -= 1
            self.wb = -1
            return False
        elif inst[0] == 'MLOAD' or inst[0] == 'MSTORE':
            size = int(inst[2])
            s_w = size / self.width
            self.left = max( 1, int(s_w * self.d_cycle))
            self.trans = True
            if inst[0] == 'MLOAD':
                temp_index = int(inst_class.org_inst[1][1:])
                self.temp_wb.append(temp_index)
                #print("MMM DEBUG --> ", temp_index)
            self.wb = -1
            #print(f"Matrix Data Inst: {inst}, Cycle: {self.left}")
            return False
        else: # computation
            size = int(inst[2])
            s_n = size / self.num
            self.left = max(1, int(s_n * self.c_cycle))
            self.trans = False
            temp_index = int(inst_class.org_inst[1][1:])
            self.temp_wb.append(temp_index)
            #print("MMM DEBUG --> ", temp_index)
            self.wb = -1
            return False

    def left_cycle(self):
        return self.left, self.trans, self.wb
