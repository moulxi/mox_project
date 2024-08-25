import mox
import threading
import time
import config

def worker():
    for i in range(10):
        print("hello world")
        time.sleep(1)

my_buf = mox.Buffer(pack_num = 100, capacity = 1000)
my_app = mox.Application(my_buf, 1000, 100, 10, 5)



t = threading.Thread(target=my_app.start(10000));
t.start()
t.join()
my_buf.gen_log()
