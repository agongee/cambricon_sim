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

def delete_enter_comment(lines):
    new_line = []
    for i in lines:
        if i == '\n':
            pass
        elif i[0:2] == '//':
            pass
        else:
            try:
                index = i.index('\n')
                new_line.append(i[:index])
            except ValueError:
                new_line.append(i)
    
    return new_line

# parse cmdline and return cfg, src file path
def cmd_parse():
    parser = argparse.ArgumentParser(description='Cambricon ISA Timing Simulator')
    
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
        parser = configparser.ConfigParser()
        parser.read(cfg)

        cache_hit_latency = parser.getint('cache', 'hit_latency')
        cache_miss_latency = parser.getint('cache', 'miss_latency')
        cache_size = parser.getint('cache', 'size')

        vector_compute_cycle = parser.getint('vector', 'compute_cycle')
        vector_data_cycle = parser.getint('vector', 'data_cycle')

        matrix_compute_cycle = parser.getint('matrix', 'compute_cycle')
        matrix_data_cycle = parser.getint('matrix', 'data_cycle')

    else:
        cache_hit_latency = 4
        cache_miss_latency = 10
        cache_size = 32

        vector_compute_cycle = 2
        vector_data_cycle = 10

        matrix_compute_cycle = 4
        matrix_data_cycle = 10
    
    # microarch setup
    fetcher = Fetcher()
    decoder = Decoder()
    memoryqueue = MemoryQueue()
    reg = Reg()
    scalarfunc = ScalarFunc()
    vectorfunc = VectorFunc(c_cycle=vector_compute_cycle, d_cycle=vector_data_cycle)
    matrixfunc = MatrixFunc(c_cycle=matrix_compute_cycle, d_cycle=matrix_data_cycle)
    issuequeue = IssueQueue(reg)
    cache = Cache(hit=cache_hit_latency, miss=cache_miss_latency, size=cache_size)
    
    # src 
    source = open(src, 'r')
    insts = source.readlines() # list of instructions
    insts = delete_enter_comment(insts)
    
    # processor variables
    # commits = [0] * len(insts) # instruction commit 
    cycle = 0 # total cycle
    pc = 0 # pc, program counter
    data_transfer = 0
    matrix_compute = 0
    vector_compute = 0
    
    next_scalar_agu = [] # next to_scalar_agu
    to_scalar_agu = [] # reg -> scalar func unit and agu

    next_memory_queue = []
    to_memory_queue = []

    branch_block = False # block when branching
    
    val_scalar = [] # scalar value to write back
    reg_scalar = [] # scalar register to write back on
    
    print(f'  Cambricon ISA Simulation')
    print(f'  Source file: {src}')
    print(f'  Source length: {len(insts)}\n')
    
    # src instruction simulation
    while True:
        #if pc % 20 == 0:
        #debug(f'CYCLE:{cycle}, PC:{pc}')

        # if issue queue is not full, i.e. can fetch and decode
        if not issuequeue.full() and not branch_block and pc < len(insts):
            # fetch
            fetcher.send()
            pc, branch_block = fetcher.get(pc, insts)
            #if branch_block:
                #print("BRANCH BLOCKED!")
        else:
            fetcher.send()
           
        # decode
        decoder.send()
        decoder.decode()
        decoder.recv(fetcher.to_decoder())

        # issue queue
        issuequeue.enqueue(decoder.to_issuequeue())      

        # issue queue  
        to_reg = issuequeue.dequeue()
        
        # register
        if len(next_scalar_agu) == 0:
            to_scalar_agu = []
        else:
            to_scalar_agu = deepcopy(next_scalar_agu)

        for i in to_reg:
            # print("DEBUG: ", i)
            if check_scalar_func(i) and i[1][0] == '$':
                reg_num = int(i[1][1:])
                i[1] = reg_num
                for j in range(2, len(i)):
                    # print("DEBUG!!: ", i[j])
                    if len(i[j]) != 0:
                        i[j] = reg.get(i[j])
                if i[0] != 'SSTORE':
                    # print("DEBUG: ", i)
                    reg.will_wb(reg_num)

            else:
                for j in range(1, len(i)):
                    if len(i[j]) != 0:
                        i[j] = reg.get(i[j])
                        
        next_scalar_agu = deepcopy(to_reg)
        
        # scalar
        v, r = scalarfunc.passing()
        if v != [] and r != []:
            val_scalar.extend(v)
            reg_scalar.extend(r)
        reg.writeback(val_scalar, reg_scalar)
        val_scalar = []
        reg_scalar = []

        for i in to_scalar_agu:
            #print("TO_SCALAR_AGU ", i)
            if check_scalar_func(i) and i[0] != 'SSTORE':
                #print("SCALAR: ", i)
                scalarfunc.compute(i)
            elif check_control_func(i):
                #print("CONTROL: ", i)
                branch_block = False
                if i[0] == 'JUMP':  # branch
                    pc += i[1]      
                elif i[2] > 0:     # control branch
                    pc += i[1]
                    #print(f'CB!!! i = {i[2]}, pc = {pc}')
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
        v_l, v_t = vectorfunc.left_cycle()
        ma_l, ma_t = matrixfunc.left_cycle()
        i_l = issuequeue.left()
        me_l = memoryqueue.left()
        d_l = decoder.left() 
        f_l = fetcher.left()
        r_l = reg.left()

        transfer_counted = False

        if c_l > 0:
            data_transfer += 1
            transfer_counted = True
        
        if v_t and not transfer_counted:
            data_transfer += 1
            transfer_counted = True
        elif not v_t:
            vector_compute += 1

        if ma_t and not transfer_counted:
            data_transfer += 1
            transfer_counted = True
        elif ma_t:
            matrix_compute += 1

        # print(f'CACHE:{c_l}, VECTOR:{v_l}, MATRIX:{ma_l}, ISSUE:{i_l}, MEMORY:{me_l}, DECODER:{d_l}, FETCHER:{f_l}, REG:{r_l}')

        left = c_l + v_l + ma_l + i_l + me_l  + d_l + f_l + r_l
        #print("LEFT ", left)
        if pc >= len(insts) and left == 0 and not branch_block:
            break
         
        
        
        cycle += 1
    
    data_ratio = round(data_transfer/cycle*100, 2)
    matrix_ratio = round(matrix_compute/cycle*100, 2)
    vector_ratio = round(vector_compute/cycle*100, 2)
    
    print('  == Simulation Complete ==')
    print(f'  Computation cycle:\t\t{cycle}')
    print(f'  Data transfer cycle:\t\t{data_transfer}, {data_ratio}%')
    print(f'  Matrix computation cycle:\t{matrix_compute}, {matrix_ratio}%')
    print(f'  Vector computation cycle:\t{vector_compute}, {vector_ratio}%')