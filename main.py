import mox
import threading
import time



buf1 = mox.Buffer(pack_num = 1000, capacity = 2000, name = "buf1")
buf2 = mox.Buffer(pack_num = 200, capacity = 2000, name = "buf2")
app1 = mox.Application(buf1, 10, 2, 5, 1)
app2 = mox.Application(buf2, 10, 2, 5, 1)
buf_list = [buf1, buf2]
end_time:int = 10000


def prioer(downstream:list[mox.Buffer]):
    list_len:int = len(downstream)
    highest:mox.Buffer = min(downstream, key=lambda x: x.pack_num)
    return highest

def prioer2(downstream:list[mox.Buffer]):
    list_len:int = len(downstream)
    highest:mox.Buffer = min(downstream, key=lambda x: x.pack_num)
    return highest

def sender_thread():
    while(mox.now_ms() < end_time):
        mox.Buffer.move_packet(mox.BLACK_HOLE, prioer(buf_list), 10, buf_limit = False)
        mox.sleep_ms(5)
        

t1 = threading.Thread(target=app1.ready, args=(500, end_time))
t2 = threading.Thread(target=app2.ready, args=(500, end_time))
ts = threading.Thread(target=sender_thread, args=())

t1.start()
t2.start()
ts.start()

t1.join()
t2.join()
ts.join()

buf1.gen_log()
buf2.gen_log() 

