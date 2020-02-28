
class Reg:
    def __init__(self, num=64):
        self.reg_num = num
        self.reg_file = [0]*num
        self.to_wb = [0]*num
        
    def get(self, param):
        if param[0] == '$':
            index = int(param[1:])
            if self.to_wb[index] == 1:
                return param
            return self.reg_file[index]
        else:
            return param
    
    def will_wb(self, index):
        self.to_wb[index] = 1

    def writeback(self, index, value):
        if self.to_wb[index] == 1:
            self.to_wb[index] = 0
            self.reg_file[index] = value
