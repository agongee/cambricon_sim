import argparse
import configparser

from copy import deepcopy

from decoder import Decoder
from queue import IssueQueue, MemoryQueue
from reg import Reg
from func import ScalarFunc, VectorFunc, MatrixFunc
from utill import check_scalar_func

# parse cmdline and return cfg, src file path
def cmd_parse():
    parser = argparse.ArgumentParser(description='Simulation Arguments')
    
    parser.add_argument('--cfg', required=True, help='microarchitecture and latency config file')
    parser.add_argument('--src', required=True, help='nn cambricon code file')
    
    args = parser.parse_args()
    
    return args.cfg, args.src



if __name__ == '__main__':
    
    # parse cmdline
    cfg, src = cmd_parse()
    
    # config
    config = configparser.ConfigParser()
    config.read(cfg)
    
    # microarch setup
    fetcher = {'pre' : None, 'post' : None, 'dec' : None}
    decoder = Decoder()
    issuequeue = IssueQueue()
    memoryqueue
    reg = Reg()
    scalarfunc = ScalarFunc()
    vectorfunc = VectorFunc()
    matrixfunc = MatrixFunc()

    
     
    
    # src 
    source = open(src, 'r')
    insts = source.readlines()
    
    # processor variables
    # commits = [0] * len(insts) # instruction commit 
    cycle = 0 # total cycle
    pc = 0 # pc, program counter
    
    next_scalar_agu = [] # next to_scalar_agu
    to_scalar_agu = [] # reg -> scalar func unit and agu

    next_memory_queue = []
    to_memory_queue = []

    branch_block = False # block when branching
    
    val_scalar = 0 # scalar value to write back
    reg_scalar = 0 # scalar register to write back on
    
    
    # src instruction simulation
    while True:
        # write back
        reg.writeback(reg_scalar, val_scalar)

        # if issue queue is not full, i.e. can fetch and decode
        if not issuequeue.full():
            # fetch
            pc += 1 # pc update
            fetcher['dec'] = fetcher['post']
            fetcher['post'] = fetcher['pre']
            fetcher['pre'] = insts[pc]
            
            # decode
            decoder.send()
            decoder.decode()
            decoder.recv(fetcher['dec'])

            # issue queue
            issuequeue.enqueue(decoder.to_decode)

        # issue queue   
        to_reg = issuequeue.dequeue()

        # register
        to_scalar_agu = deepcopy(next_scalar_agu)

        reg_stall = False
        for i in range(len(to_reg)):
            to_reg[i] = reg.get(to_reg[i])
            if to_reg[i][0] == '$':
                issuequeue.requeue(to_reg)
                reg_stall = True
                break
        
        next_scalar_agu = []
        if not reg_stall:
            next_scalar_agu = to_reg[:]

        # scalar
        if check_scalar_func(to_scalar_agu[0]):
            val_scalar = scalarfunc.compute(to_scalar_agu)
        
        # agu
        # NEED
        to_memory_queue = next_memory_queue[:]
        next_memory_queue = to_scalar_agu[:]

        # memory queue
        
        
        

                