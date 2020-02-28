def compute(type, operands):
    # logical
    if type == 'SAND':
        return operands[1] & operands[2], operands[0]

    elif type == 'SOR':
        return operands[1] | operands[2], operands[0]

    elif type == 'SNOT':
        return ~operands[1], operands[0]
    
    # compare
    elif type == 'SLT':
        return operands[1] < operands[2], operands[0]

    elif type == 'SLEQ':
        return operands[1] <= operands[2], operands[0]

    elif type == 'SGT':
        return operands[0] > operands[1]

    elif type == 'SGEQ':
        return operands[0] >= operands[1]

    # arithmetic
    elif type == 'SADD':
        return operands[0] + operands[1]

    elif type == 'SSUB':
        return operands[0] - operands[1]

    elif type == 'SMUL':
        return operands[0] * operands[1]

    elif type == 'SDIV':
        return operands[0] * operands[1]

    elif type == 'SLSH':
        return operands[0] << operands[1]

    elif type == 'SRSH':
        return operands[0] >> operands[1]

    # transcendental
    # NEED

    else:
        return None

def check_scalar_func(inst):
    scalar_func_type = ['AND', 'OR', 'NOT', 'LT', 'LEQ', 'GT', 'GEQ', 'ADD', 'SUB', 'MUL', 'DIV', 'LSH', 'RSH']
    if isinstance(inst, str):
        return inst in scalar_func_type
    else:
        return inst[0] in scalar_func_type
