import argparse
import configparser

from copy import deepcopy

from fetcher import Fetcher
from decoder import Decoder
from queue import IssueQueue, MemoryQueue
from reg import Reg
from func import ScalarFunc, VectorFunc, MatrixFunc
from utill import check_scalar_func, check_control_func, check_transfer
from cache import Cache

def debug(txt):
    print(txt)

# parse cmdline and return cfg, src file path
def cmd_parse():
    parser = argparse.ArgumentParser(description='Simulation Arguments')
    
    parser.add_argument('--cfg', required=False, \
        help='microarchitecture and latency config file')
    parser.add_argument('--src', required=True, \
        help='nn cambricon code file')
    
    args = parser.parse_args()
    
    return args.cfg, args.src



if __name__ == '__main__':
    
    # parse cmdline
    cfg, src = cmd_parse()
    
    # config
    if cfg != None:
        config = configparser.ConfigParser()
        config.read(cfg)
    
    # microarch setup
    fetcher = Fetcher()
    decoder = Decoder()
    memoryqueue = MemoryQueue()
    reg = Reg()
    scalarfunc = ScalarFunc()
    vectorfunc = VectorFunc()
    matrixfunc = MatrixFunc()
    issuequeue = IssueQueue(reg)
    cache = Cache()
    
     
    
    # src 
    source = open(src, 'r')
    insts = source.readlines() # list of instructions
    
    # processor variables
    # commits = [0] * len(insts) # instruction commit 
    cycle = 0 # total cycle
    pc = 0 # pc, program counter
    
    next_scalar_agu = [] # next to_scalar_agu
    to_scalar_agu = [] # reg -> scalar func unit and agu

    next_memory_queue = []
    to_memory_queue = []

    branch_block = False # block when branching
    
    val_scalar = [] # scalar value to write back
    reg_scalar = [] # scalar register to write back on
    
    
    # src instruction simulation
    while True:
        debug(f'CYCLE:{cycle}, PC:{pc}')

        # if issue queue is not full, i.e. can fetch and decode
        if not issuequeue.full() and not branch_block and pc < len(insts):
            # fetch
            fetcher.send()
            pc = fetcher.get(pc, insts)
        else:
            fetcher.send()

        # debug(fetcher.to_decoder())
        # a = input ()

        # print("FETCHER ", len(fetcher.to_fetch))
           
        # decode
        decoder.send()
        decoder.decode()
        decoder.recv(fetcher.to_decoder())

        # print("DECODER " , len(decoder.to_pass))

        # issue queue
        issuequeue.enqueue(decoder.to_issuequeue())      

        # debug(issuequeue)

        # issue queue  
        to_reg = issuequeue.dequeue()

        # debug(to_reg)
        
        # register
        if len(next_scalar_agu) == 0:
            to_scalar_agu = []
        else:
            to_scalar_agu = deepcopy(next_scalar_agu)

        for i in to_reg:
            # print("DEBUG: ", i)
            if check_scalar_func(i) and i[1][0] == '$':
                reg_num = int(i[1][1:])
                if i[0] != 'SSTORE':
                    # print("DEBUG: ", i)
                    reg.will_wb(reg_num)
                for j in range(2, len(i)):
                    # print("DEBUG!!: ", i[j])
                    if len(i[j]) != 0:
                        i[j] = reg.get(i[j])
            else:
                for j in range(1, len(i)):
                    # print("DEBUG!!: ", i[j])
                    if len(i[j]) != 0:
                        i[j] = reg.get(i[j])

        next_scalar_agu = deepcopy(to_reg)

        # debug(to_reg)


        # scalar

        reg.writeback(val_scalar, reg_scalar)

        for i in to_scalar_agu:
            # print("DEBUG: ", i)
            if check_scalar_func(i) and i[0] != 'SSTORE':
                v, r = scalarfunc.compute(i)
                if v != None and r != None:
                    val_scalar.append(v)
                    reg_scalar.append(r)
                print("DEBUG: ", i, v, r)
            elif check_control_func(i):
                if i[0] == 'JUMP':
                    pc += i[1]
                elif i[1] != 0:
                    pc += i[2]
            elif i[0] == 'NOP':
                pass
            else:
                memoryqueue.enqueue(i)                

        to_cache, to_vector, to_matrix = \
             memoryqueue.dequeue(cache.left, vectorfunc.left, matrixfunc.left)

        cache.request(to_cache)
        vectorfunc.request(to_vector)
        matrixfunc.request(to_matrix)

        # if pc >= len(insts):
        c_l = cache.left 
        v_l = vectorfunc.left 
        ma_l = matrixfunc.left
        i_l = issuequeue.left()
        me_l = memoryqueue.left()
        s_l = scalarfunc.left
        d_l = decoder.left() 
        f_l = fetcher.left()
        r_l = reg.left()

        print(f'CACHE:{c_l}, VECTOR:{v_l}, MATRIX:{ma_l}, ISSUE:{i_l}, MEMORY:{me_l}, SCALAR:{s_l}, DECODER:{d_l}, FETCHER:{f_l}, REG:{r_l}')

        left = c_l + v_l + ma_l + i_l + me_l + s_l + d_l + f_l + r_l
        print("LEFT ", left)
        if pc >= len(insts) and left == 0:
            break

        if cycle > 20:
            a = input()
        
        cycle += 1