from copy import deepcopy

from reg import Reg
from utill import check_control_func, check_func_type, check_matrix_func, check_scalar_func, check_vector_func, check_transfer


class Inst:
    def __init__(self, inst):
        self.inst = deepcopy(inst)
        self.issue = False

class IssueQueue:
    def __init__(self, reg: Reg, depth=24, width=2):
        self.reg = reg
        self.depth = depth
        self.width = width
        self.inst_queue = []
        self.pass_inst = []

    def __str__(self):
        string = '===================\n'

        for i in self.inst_queue:
            string += str(i.inst)
            string += '\n'

        string += '===================\n'

        return string
        

    def enqueue(self, inst):
        for i in inst:
            temp = Inst(i)
            self.inst_queue.append(temp)
    
    def dequeue(self):
        self.pass_inst = []

        if len(self.inst_queue) == 0:
            return []
        
        while len(self.pass_inst) < self.width and len(self.inst_queue) != 0:
            if self.inst_queue[0].issue and self.issue_able(self.inst_queue[0].inst):
                temp = self.inst_queue.pop(0)
                self.pass_inst.append(deepcopy(temp.inst))
                # print("DEQUEUE IF", len(self.inst_queue))
            else:
                # print("DEQUEUE ELSE", len(self.inst_queue))
                break
        
        for i in self.inst_queue:
            i.issue = True

        # print(insts)
        return self.pass_inst

    def requeue(self, inst):
        self.inst_queue.insert(0, deepcopy(inst))

    def full(self):
        return len(self.inst_queue) > (self.depth - self.width)

    def issue_able(self, inst):
        temp_len = len(inst)
        going_to = []

        for i in self.pass_inst:
            if check_scalar_func(i) and i[0] != 'SSTORE':
                going_to.append(int(i[1][1:]))

        if check_scalar_func(inst):
            for i in range(2, temp_len):
                if len(inst[i]) == 0:
                    continue
                if inst[i][0] == '$':
                    reg_num = int(inst[i][1:])
                    if self.reg.check_wb(reg_num):
                        return False
                    if reg_num in going_to:
                        return False
        else:
            for i in range(1, temp_len):
                if len(inst[i]) == 0:
                    continue
                if inst[i][0] == '$':
                    reg_num = int(inst[i][1:])
                    if self.reg.check_wb(reg_num):
                        return False
                    if reg_num in going_to:
                        return False

        return True

    def left(self):
        return len(self.inst_queue)

class MemoryQueue:
    def __init__(self, depth=32):
        self.depth = depth
        self.inst_queue = []

    def enqueue(self, inst):
        temp = Inst(inst)
        self.inst_queue.append(temp)

    def dequeue(self, c_cycle, v_cycle, m_cycle):
        to_cache = None
        to_vector = None
        to_matrix = None
        
        if len(self.inst_queue) == 0:
            return to_cache, to_vector, to_matrix
        elif not self.inst_queue[0].issue:
            #print("DEQUEUE, NOT ISSUEABLE")

            for i in self.inst_queue:
                i.issue = True

            return to_cache, to_vector, to_matrix

        temp_inst = self.inst_queue[0].inst

        # print(f"DEQUEUE, {c_cycle}, {v_cycle}, {m_cycle}")

        if check_scalar_func(temp_inst) and c_cycle <= 1:
            to_cache = deepcopy(temp_inst)
            self.inst_queue.pop(0)
        elif check_vector_func(temp_inst) and v_cycle <= 1:
            to_vector = deepcopy(temp_inst)
            self.inst_queue.pop(0)
        elif check_matrix_func(temp_inst) and m_cycle <= 1:
            to_matrix = deepcopy(temp_inst)
            self.inst_queue.pop(0)
       
        for i in self.inst_queue:
            i.issue = True

        return to_cache, to_vector, to_matrix
    
    def left(self):
        return len(self.inst_queue)