import numpy as np
import time
import math
import matplotlib.pyplot as plt
import config

# exception definition
class MoxError(Exception):
    def __init__(self, message="There is an error from illegal use of Mox"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

def move_all_packet(source, dest):
    num:int = source.getSize()
    source.clean()
    dest.add(num)
    
# sleep control
def sleep_ms(duration:int):
    time.sleep(duration / 1000)
    
# clock
def now_ms():
    return int(time.time() * 1000) - config.simulate_start_time
    

class Buffer:
        
    def __init__(self,capacity:int = 100, pack_num:int = 0, name:str = "unknown"):
        self.name:str = name
        self.capacity = capacity
        self.pack_num:int = pack_num
        self.time_list = [0]
        self.pack_num_list = [pack_num]

    def add(self, num:int):
        self.pack_num = self.pack_num + num
        self.pack_num_list.append(self.pack_num)
        self.time_list.append(now_ms())

    def remove(self, num:int):
        self.pack_num = self.pack_num - num
        self.pack_num_list.append(self.pack_num)
        self.time_list.append(now_ms())
    
    def remove_all(self):
        self.pack_num = 0
        self.pack_num_list.append(0)
        self.time_list.append(now_ms())

    def gen_log(self):
        plt.figure(figsize=(10, 6))
        plt.xlabel('time(ms)')
        plt.ylabel('#packet')
        plt.plot(np.array(self.time_list), np.array(self.pack_num_list), label='number of packets in the buffer')
        plt.grid(True)
        plt.title(f"packets in buffer {self.name}")
        plt.show()

    def getSize(self):
        return self.pack_num

class Application:
    
    def __init__(self ,buf:Buffer, time_loc:int, time_scale:int, packet_loc:int, packet_scale:int, name:str = "unknown_app"):
        self.name = name
        self.buf:Buffer = buf
        self.time_loc:int = time_loc
        self.time_scale:int = time_scale
        self.packet_loc:int  = packet_loc
        self.packet_scale:int = packet_scale
        
    def start(self, duration:int):
        self.duration:int = duration
        now:int = 0
        next_wait = []
        next_consume = []
        while(now < duration):
            next_wait = int(np.random.normal(self.time_loc, self.time_scale, 1)[0])
            next_consume = int(np.round(np.random.normal(self.packet_loc, self.packet_scale, 1)[0]))
            sleep_ms(next_wait)
            now = now + next_wait
            self.buf.remove(next_consume)
            print(f"now: {now}")
            print(f"app consume {next_consume} packets")
            print(f"there are still {self.buf.getSize()} packet in buf")


            
            
            
            
            
            
            
        
        

    
    