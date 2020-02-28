from utill import compute as COMPUTE

class ScalarFunc:
    def __init__(self, cycle=1):
        self.cycle = cycle
        self.left = 0
        self.current_inst = []

    def compute(self, inst):
        if self.left == 1:
            self.left = 0
            return COMPUTE(self.current_inst[0], self.current_inst[1:])
        elif self.left == 0:
            self.left = self.cycle
            self.current_inst = inst
        else:
            pass

        return None      

class VectorFunc:
    def __init__(self):
        pass



class MatrixFunc:
    def __init__(self):
        pass