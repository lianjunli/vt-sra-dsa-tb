import numpy as np

class env:
    def __init__(self):
        # self.slot_counter = -1
        self.state_width = 3
        self.state = '{0:0{width}}'.format(0,width=self.state_width) #string. state is previous sensing result, 0: channel busy 1:channel available
        # self.PU_pattern=[0,0,1,1,1] #1=busy 0=idle
        self.n_actions = 2
    def reset(self):
        self.state = '{0:0{width}}'.format(0,width=self.state_width)
        return self.state
    def step(self, s, a, sensing_result):
        # self.slot_counter+=1
        # slot_number = self.slot_counter%self.state_width
        # print 'slot: ', slot_number
        if a == 0: r = 0
        else: # SU access a==1
            if sensing_result == 0: r = -1 #PU busy, conflict
            else: r = 1
        s_=s[1:] + str(sensing_result)
        return r, s_
