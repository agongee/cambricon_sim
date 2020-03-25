from copy import deepcopy

class Inst:
    def __init__(self, inst, pc, decoded=False):
        self.inst = deepcopy(inst)
        self.pc = pc
        self.issue = False
        if decoded:
            self.org_inst = deepcopy(inst)
        else:
            self.org_inst = []

    def __str__(self):
        return f"PC: {self.pc}, INST: {self.inst}"

def compute(type, operands):
    # logical
    if type == 'SAND':
        return operands[1] & operands[2], operands[0]

    elif type == 'SOR':
        return operands[1] | operands[2], operands[0]

    elif type == 'SNOT':
        return ~operands[1], operands[0]
    
    # compare
    elif type == 'SGT':
        return int(operands[1] > operands[2]), operands[0]

    elif type == 'SGEQ':
        return int(operands[1] >= operands[2]), operands[0]

    # arithmetic
    elif type == 'SADD':
        return operands[1] + operands[2], operands[0]

    elif type == 'SSUB':
        return operands[1] - operands[2], operands[0]

    elif type == 'SMUL':
        return operands[1] * operands[2], operands[0]

    elif type == 'SDIV':
        return operands[1] * operands[2], operands[0]

    elif type == 'SLSH':
        return operands[1] << operands[2], operands[0]

    elif type == 'SRSH':
        return operands[1] >> operands[2], operands[0]

    elif type == 'SLOAD':
        return operands[1], operands[0]

    elif type == 'SMOVE':
        return operands[1], operands[0]

    # transcendental
    # NEED

    else:
        return None, None

def check_scalar_func(inst):
    if len(inst) == 0:
        return False

    # scalar_func_type = ['AND', 'OR', 'NOT', 'LT', 'LEQ', 'GT', 'GEQ', 'ADD', 'SUB', 'MUL', 'DIV', 'LSH', 'RSH']
    if isinstance(inst, str):
        return inst[0] == 'S'
    else:
        return inst[0][0] == 'S'


def check_vector_func(inst):
    if len(inst) == 0:
        return False

    if isinstance(inst, str):
        return inst[0] == 'V'
    else:
        return inst[0][0] == 'V'

def check_matrix_func(inst):
    if len(inst) == 0:
        return False

    if isinstance(inst, str):
        return inst[0] == 'M'
    else:
        return inst[0][0] == 'M'

def check_control_func(inst):
    if len(inst) == 0:
        return False
    
    return inst[0] == 'JUMP' or inst[0] == 'CB'


def check_func_type(inst):
    
    if check_scalar_func(inst):
        return 0 # scalar

    elif check_vector_func(inst):
        return 1 # vector

    elif check_matrix_func(inst):
        return 2 # matrix

    else:
        return 3 # others (e.g. branch)

def check_transfer(inst):
    if len(inst) == 0:
        return False

    if isinstance(inst, str):
        return inst[1:] == 'LOAD' or inst[1:] == 'STORE'
    else:
        return inst[0][1:] == 'LOAD' or inst[0][1:] == 'STORE'