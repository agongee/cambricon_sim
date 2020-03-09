
class Reg:
    def __init__(self, num=64):
        self.reg_num = num
        self.reg_file = [0]*num
        self.to_wb = [0]*num
        
    def get(self, param):
        if param[0] == '$':
            index = int(param[1:])
            if self.to_wb[index] == 1:
               #  print("BLOCKED!")
                return param
            return self.reg_file[index]
        elif param[0] == '#':
            return int(param[1:])
        else:
            return param
    
    def will_wb(self, index):
        self.to_wb[index] = 1

    def check_wb(self, index):
        return self.to_wb[index]

    def writeback(self, value, index):
        if len(value) != len(index) or len(value) == 0:
            return
        
        temp_len = len(index)

        for i in range(temp_len):
            temp_value = value[i]
            temp_index = index[i]
            # print("WB ", temp_value, temp_index)
            if self.to_wb[temp_index] == 1:
                self.to_wb[temp_index] = 0
                self.reg_file[temp_index] = temp_value

        value = []
        index = []

    def left(self):
        return sum(self.to_wb)