class IssueQueue:
    def __init__(self, capacity=24, width=2):
        self.capacity = capacity
        self.width = width
        self.inst_queue = []
        
    def enqueue(self, inst):
        if len(self.inst_queue) < self.capacity:
            self.inst_queue.append(inst)
        
    # return inst to issue.
    # if there is no possible inst to issue, return None
    def dequeue(self):
        inst = []
        index = 0

        while True:
            if issue_able(self.inst_queue[index]):
                inst.append(self.inst_queue.pop(index))
                if len(inst) == self.width:
                    break
            else:
                index += 1
            
        return inst

    def full(self):
        return len(self.inst_queue) == 2

    def requeue(self, inst):
        self.inst_queue.insert(0, inst)



class MemoryQueue:
    def __init__(self, capacity=2):
        self.capacity = capacity
        self.inst_queue = []
        
    def enqueue(self, inst):
        if len(self.inst_queue) < 2:
            self.inst_queue.append(inst)
        
    # return inst to issue.
    # if there is no possible inst to issue, return None
    def dequeue(self):
        inst = []
        index = -1

        for i in range(len(self.inst_queue)):
            if issue_able(self.inst_queue[i]): # NEED
                index = i

        if index != -1:
            inst = self.inst_queue.pop(index)

        return inst

    def full(self):
        return len(self.inst_queue) == 2

    def requeue(self, inst):
        self.inst_queue.insert(0, inst)

