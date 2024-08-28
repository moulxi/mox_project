import numpy as np
import time
import math
import threading
import matplotlib.pyplot as plt
from queue import Queue

# exception definition
class MoxError(Exception):
    def __init__(self, message="There is an error from illegal use of Mox"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    
class BufferError(Exception):
    def __init__(self, message="Buffer overflow or there is negative number of packet"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    
class BlackHoleError(Exception):
    def __init__(self, message="form_buf in move_all_packet() can not be black hole"):
        self.message = message
        super().__init__(self.message)


SIMULATE_START_TIME:int = int(time.time() * 1000)
SIMULATE_DURATION:int = 5000

    
# sleep control
def sleep_ms(duration:int):
    time.sleep(duration / 1000)

# clock
def now_ms(basetime:int = SIMULATE_START_TIME):
    return int(time.time() * 1000) - basetime

def sleep_until_ms(wake_up_time:int, basetime:int = SIMULATE_START_TIME):
    #print(f"wake_up_time : {wake_up_time}, now_ms(basetime) = {now_ms(basetime)}")
    if(wake_up_time > now_ms(basetime)):
        sleep_ms(wake_up_time - now_ms(basetime))    


class PacketError(Exception):
    def __init__(self, message="Packet belong to unknown app"):
        self.message = message
        super().__init__(self.message)

class Packet:

    def __init__(self, app:str = None, ack:bool = False, rwnd:int = 0):
        self.ack:bool = ack
        if(app == None):
            raise PacketError(message = "Packet belong to unknown app")
        self.app:str = app
        self.rwnd = rwnd
        
    

class Buffer:
    
    
    @staticmethod
    def move_all_packet(from_buf:"Buffer", to_buf:"Buffer", buf_limit:bool = True):
        if(from_buf.buf_type == "black_hole"):
            raise BlackHoleError()
        if(to_buf.pack_num + from_buf.pack_num > to_buf.capacity and to_buf.buf_type != "black_hole" and buf_limit):
            raise BufferError(f"From {from_buf.name} to {to_buf.name}, {to_buf.name} overflow.")
        pack_num:int = from_buf.pack_num
        from_buf.remove_all()
        to_buf.add(pack_num)
 
    
    @staticmethod
    def move_packet(from_buf:"Buffer", to_buf:"Buffer", pack_num:int, buf_limit:bool = True):
        if(from_buf.pack_num < pack_num and from_buf.buf_type != "black_hole" and buf_limit):
            raise BufferError(f"From {from_buf.name} to {to_buf.name}, {from_buf.name} has negative amount of packet.")
        if(to_buf.pack_num + pack_num > to_buf.capacity and to_buf.buf_type != "black_hole" and buf_limit):
            raise BufferError(f"From {from_buf.name} to {to_buf.name}, {to_buf.name} overflow.")
        from_buf.remove(pack_num)
        to_buf.add(pack_num)

        
    @staticmethod
    def draw_plt(buf_list:"list[Buffer]"):
        plt.figure(figsize=(10, 6))
        plt.xlabel('time(ms)')
        plt.ylabel('#packet')
        plt.xlim(0, 5000)
        for buf in buf_list:
            plt.plot(np.array(buf.time_list), np.array(buf.pack_num_list), drawstyle="steps-post",label = buf.name)
        plt.grid(True)
        plt.title(f"packets in buffers")
        plt.show()
    
        
    def __init__(self,capacity:int = 100, pack_num:int = 0, name:str = "unknown", buf_type:str = "normal"):
        
        # basic init
        self.name:str = name
        self.capacity = capacity
        self.buf_type:str = buf_type
        self.pack_num:int = pack_num
        
        # for log 
        self.time_list = [0]
        self.pack_num_list = [pack_num]
        self.buf_op_lock = threading.Lock()

        # packet box
        self.pkt_box = Queue()
        
    def set_downstream(self, downstream_buf:"Buffer"):
        self.downstream_buf:Buffer = downstream_buf
        
        

    def add(self, num:int):
        with self.buf_op_lock:
            self.pack_num = self.pack_num + num
            self.record_one()


    def remove(self, num:int):
        with self.buf_op_lock:
            self.pack_num = self.pack_num - num
            self.record_one()
    
    def remove_all(self):
        with self.buf_op_lock:
            self.pack_num = 0
            self.record_one()

    
    def get_pack_num(self):
        return self.pack_num
    
    def record_one(self):
            self.pack_num_list.append(self.pack_num)
            self.time_list.append(now_ms())
            print(f"{self.name} --- time:{self.time_list[-1]} --- pack:{self.pack_num_list[-1]}")

    def gen_log(self):
        plt.figure(figsize=(10, 6))
        plt.xlabel('time(ms)')
        plt.ylabel('#packet')
        plt.plot(np.array(self.time_list), np.array(self.pack_num_list), label='number of packets in the buffer')
        plt.grid(True)
        plt.title(f"packets in buffer {self.name}")
        plt.show()
        
class BlackHoleBuffer(Buffer):
        
    def __init__(self):
        super().__init__()
        self.buf_type = "black_hole"
        self.name = "BLACK_HOLE"
    
    def add(self, place_holder):
        pass
    
    def remove(self, place_holder):
        pass
    
    def remove_all():
        pass
    
    def record_one(place_holder):
        pass

BLACK_HOLE = BlackHoleBuffer()
        
        
class Switch:
    
    def __init__(self, buf_list:list[Buffer], pkt_loc:int, time_loc:int):
        self.buf_list = buf_list
        self.pkt_loc = pkt_loc
        self.time_loc = time_loc
        
    def schedule(self, policy:str):
        selected_buf:Buffer = self.buf_list[0]
        if(policy == "local_max_buf_first"):
            for i in range(len(self.buf_list)):
                if(self.buf_list[i].pack_num > selected_buf.pack_num):
                    selected_buf = self.buf_list[i]
        return selected_buf
        
    def ready(self, policy:str):
        while(now_ms() < SIMULATE_DURATION): # for whole simulation
            sleep_ms(self.time_loc)
            selected_buf:Buffer = self.schedule(policy = policy)
            Buffer.move_packet(selected_buf, selected_buf.downstream_buf, self.pkt_loc)

            
        
# Application : generating or comsuming packets to the specific buffer (not switch scale) 
class Application:
    
    def __init__(self ,app_buf:Buffer, time_loc:int, time_scale:int, pkt_loc:int, pkt_scale:int, name:str = "unknown_app"):
        self.name = name
        self.app_buf:Buffer = app_buf
        self.time_loc:int = time_loc
        self.time_scale:int = time_scale
        self.pkt_loc:int  = pkt_loc
        self.pkt_scale:int = pkt_scale
        
        
    def ready(self, action:str, start_time:int, end_time:int, basetime:int = SIMULATE_START_TIME):
        now:int = 0
        next_wait = []
        next_pkt_change = []
        sleep_until_ms(wake_up_time = start_time, basetime = basetime)
        if(action == "consume"):
            while(now_ms() < end_time):
                next_wait = int(np.random.normal(self.time_loc, self.time_scale, 1)[0])
                next_pkt_change = int(np.round(np.random.normal(self.pkt_loc, self.pkt_scale, 1)[0]))
                sleep_ms(next_wait)
                now = now + next_wait
                Buffer.move_packet(self.app_buf, BLACK_HOLE, next_pkt_change, False)
        elif(action == "generate"):
            while(now_ms() < end_time):
                next_wait = int(np.random.normal(self.time_loc, self.time_scale, 1)[0])
                next_pkt_change = int(np.round(np.random.normal(self.pkt_loc, self.pkt_scale, 1)[0]))
                sleep_ms(next_wait)
                now = now + next_wait
                Buffer.move_packet(BLACK_HOLE, self.app_buf, next_pkt_change, False)
            
            
        





            
            
            
            
            
            
        
        

    
    