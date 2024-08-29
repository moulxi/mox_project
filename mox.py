import numpy as np
import time
import math
import threading
import matplotlib.pyplot as plt
from colorama import init, Fore, Back, Style

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

        
buf_op_lock = threading.Lock()


class Buffer:
    
    max_capacity:int = 0

    @staticmethod
    def move_packet(from_buf:"Buffer", to_buf:"Buffer", pack_num:int, buf_limit:bool = True):
        
        if(from_buf.buf_type != "black_hole"):
            if(from_buf.pack_num < pack_num and buf_limit):
                raise BufferError(f"{Fore.RED} From {from_buf.name} to {to_buf.name}, {from_buf.name} has negative amount of packet.{Style.RESET_ALL}")
        if(to_buf.buf_type != "black_hole"):
            if(to_buf.pack_num + pack_num > to_buf.capacity and buf_limit):
                raise BufferError(f" {Fore.RED} From {from_buf.name} to {to_buf.name}, {to_buf.name} overflow.{Style.RESET_ALL}")
        
        with buf_op_lock:
            
            action_time:int = now_ms()
            
            # remove packets from from_buf 
            from_buf.pack_num = from_buf.pack_num - pack_num
            from_buf.pack_num_list.append(from_buf.pack_num)
            from_buf.time_list.append(action_time)
            
            # add packets to to_buf
            to_buf.pack_num = to_buf.pack_num + pack_num
            to_buf.pack_num_list.append(to_buf.pack_num)
            to_buf.time_list.append(action_time)
        
        
    @staticmethod
    def move_all_packet(from_buf:"Buffer", to_buf:"Buffer", buf_limit:bool = True):
        if(from_buf.buf_type == "black_hole"):
            raise BlackHoleError()
        Buffer.move_packet(from_buf, to_buf, pack_num = from_buf.pack_num, buf_limit = buf_limit)
        

        
    @staticmethod
    def draw_plt(buf_list:"list[Buffer]", ylim:int = None):
        if(ylim == None):
            ylim = int(Buffer.max_capacity * 1.1)
        plt.figure(figsize=(10, 6))
        plt.xlabel('time(ms)')
        plt.ylabel('#packet')
        plt.xlim(0, SIMULATE_DURATION)
        plt.ylim(0,  ylim)
        for buf in buf_list:
            plt.plot(np.array(buf.time_list), np.array(buf.pack_num_list), drawstyle="steps-post", label = buf.name, color = buf.color)
            plt.axhline(y = buf.capacity, color=buf.color, linestyle='--')
        plt.grid(True)
        plt.title(f"packets in buffers")
        plt.legend(loc='best',fontsize=12)
        plt.show()
        
        
    @staticmethod
    def set_buf_chain_color(buf_list:"list[Buffer]", buf_color:str):
        for buf in buf_list:
            buf.color = buf_color
        
        
    def __init__(self,capacity:int = 100, pack_num:int = 0, name:str = "unknown", buf_type:str = "normal"):
        
        # basic init
        self.name:str = name
        self.capacity = capacity
        self.buf_type:str = buf_type
        self.pack_num:int = pack_num
        
        # for log 
        self.time_list = [0]
        self.pack_num_list = [pack_num]
        
        # for plt
        self.color:str = "gray"
        
        if(self.capacity > Buffer.max_capacity):
            Buffer.max_capacity = self.capacity
        
        
        
    def set_downstream(self, downstream_buf:"Buffer"):
        self.downstream_buf:Buffer = downstream_buf
    
        
class BlackHoleBuffer(Buffer):
        
    def __init__(self):
        super().__init__()
        self.buf_type = "black_hole"
        self.name = "BLACK_HOLE"
    

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
        elif(policy == "downstream_min_buf_first"):
            for i in range(len(self.buf_list)):
                if(self.buf_list[i].downstream_buf.pack_num < selected_buf.downstream_buf.pack_num):
                    selected_buf = self.buf_list[i]
        return selected_buf
        
    def ready(self, policy:str):
        while(now_ms() < SIMULATE_DURATION): # for whole simulation
            sleep_ms(self.time_loc)
            selected_buf:Buffer = self.schedule(policy = policy)
            pkt_num_to_foward:int = self.pkt_loc
            if(selected_buf.pack_num < pkt_num_to_foward):
                pkt_num_to_foward = selected_buf.pack_num
            Buffer.move_packet(selected_buf, selected_buf.downstream_buf, pkt_num_to_foward)

            
        
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
        if(start_time > SIMULATE_DURATION):
            start_time = SIMULATE_DURATION
            print(f"{Fore.MAGENTA} WARNING : {self.name} start_time exceeded SIMULATE_DURATION, set it to SIMULATE_DURATION {Style.RESET_ALL}")
        if(end_time > SIMULATE_DURATION):
            end_time = SIMULATE_DURATION
            print(f"{Fore.MAGENTA} WARNING : {self.name} end_time exceeded SIMULATE_DURATION, set it to SIMULATE_DURATION {Style.RESET_ALL}")
        
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
            
            
        




    