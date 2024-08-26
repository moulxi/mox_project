import numpy as np
import time
import math
import matplotlib.pyplot as plt

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
    
# sleep control
def sleep_ms(duration:int):
    time.sleep(duration / 1000)

# clock
def now_ms(basetime:int = SIMULATE_START_TIME):
    return int(time.time() * 1000) - basetime

def sleep_until_ms(wake_up_time:int, basetime:int = SIMULATE_START_TIME):
    sleep_ms(wake_up_time - now_ms(basetime))    



    

class Buffer:
    
    @staticmethod
    def move_all_packet(from_buf:"Buffer", to_buf:"Buffer", buffer_limit:bool = True):
        if(from_buf.buf_type == "black_hole"):
            raise BlackHoleError()
        if(to_buf.pack_num + from_buf.pack_num > to_buf.capacity and to_buf.buf_type != "black_hole" and buffer_limit):
            raise BufferError(f"From {from_buf.name} to {to_buf.name}, {to_buf.name} overflow.")
        pack_num:int = from_buf.pack_num
        from_buf.remove_all()
        from_buf.record_one()
        to_buf.add(pack_num)
        to_buf.record_one()
        
    
    @staticmethod
    def move_packet(from_buf:"Buffer", to_buf:"Buffer", pack_num:int, buffer_limit:bool = True):
        if(from_buf.pack_num < pack_num and from_buf.buf_type != "black_hole" and buffer_limit):
            raise BufferError(f"From {from_buf.name} to {to_buf.name}, {from_buf.name} has negative amount of packet.")
        if(to_buf.pack_num + pack_num > to_buf.capacity and to_buf.buf_type != "black_hole" and buffer_limit):
            raise BufferError(f"From {from_buf.name} to {to_buf.name}, {to_buf.name} overflow.")
        from_buf.remove(pack_num)
        from_buf.record_one()
        to_buf.add(pack_num)
        to_buf.record_one()
    
        
    def __init__(self,capacity:int = 100, pack_num:int = 0, name:str = "unknown", buf_type:str = "normal"):
        self.name:str = name
        self.capacity = capacity
        self.buf_type:str = buf_type
        self.pack_num:int = pack_num
        self.time_list = [0]
        self.pack_num_list = [pack_num]

    def add(self, num:int):
        self.pack_num = self.pack_num + num
        self.pack_num_list.append(self.pack_num)
        self.time_list.append(now_ms())

    def remove(self, num:int):
        self.pack_num = self.pack_num - num

    
    def remove_all(self):
        self.pack_num = 0

    
    def get_pack_num(self):
        return self.pack_num
    
    def record_one(self):
        self.pack_num_list.append(self.pack_num)
        self.time_list.append(now_ms())
        print(f"{self.__class__.__name__} --- time:{self.time_list[-1]} --- pack:{self.pack_num_list[-1]}")

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
    
    def add(self, place_holder):
        pass
    
    def remove(self, place_holder):
        pass
    
    def remove_all():
        pass
    
    def record_one(place_holder):
        pass

BLACK_HOLE = BlackHoleBuffer()

class Application:
    
    def __init__(self ,app_buf:Buffer, time_loc:int, time_scale:int, packet_loc:int, packet_scale:int, name:str = "unknown_app"):
        self.name = name
        self.app_buf:Buffer = app_buf
        self.time_loc:int = time_loc
        self.time_scale:int = time_scale
        self.packet_loc:int  = packet_loc
        self.packet_scale:int = packet_scale
        
        
    def ready(self, start_time:int, end_time:int, basetime:int = SIMULATE_START_TIME):
        now:int = 0
        next_wait = []
        next_consume = []
        sleep_until_ms(wake_up_time = start_time, basetime = basetime)
        while(now_ms() < end_time):
            next_wait = int(np.random.normal(self.time_loc, self.time_scale, 1)[0])
            next_consume = int(np.round(np.random.normal(self.packet_loc, self.packet_scale, 1)[0]))
            sleep_ms(next_wait)
            now = now + next_wait
            Buffer.move_packet(self.app_buf, BLACK_HOLE, next_consume)
            
            
        





            
            
            
            
            
            
        
        

    
    