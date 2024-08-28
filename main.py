import mox
import threading
import time


# switch1 with two buffers inside
s1_buf1 = mox.Buffer(pack_num = 800, capacity = 2000, name = "s1_buf1")
s1_buf2 = mox.Buffer(pack_num = 400, capacity = 2000, name = "s1_buf2")
s1 = mox.Switch(buf_list = [s1_buf1, s1_buf2], pkt_loc = 20, time_loc = 50)

# the application which put packet into switch1
ap1 = mox.Application(app_buf = s1_buf1, time_loc = 50, time_scale = 0, pkt_loc = 10, pkt_scale = 0)
ap2 = mox.Application(app_buf = s1_buf2, time_loc = 50, time_scale = 0, pkt_loc = 10, pkt_scale = 0)


# application1 and its buffer 
a1_buf = mox.Buffer(pack_num = 1000, capacity = 2000, name = "a1_buf")
a1 = mox.Application(app_buf = a1_buf, time_loc = 50, time_scale = 0, pkt_loc = 10, pkt_scale = 0)


# application2 and its buffer
a2_buf = mox.Buffer(pack_num = 1000, capacity = 2000, name = "a2_buf")
a2 = mox.Application(app_buf = a2_buf, time_loc = 50, time_scale = 0, pkt_loc = 10, pkt_scale = 0)

s1_buf1.set_downstream(a1_buf)
s1_buf2.set_downstream(a2_buf)

thread_ap1 = threading.Thread(target=ap1.ready, args=("generate", 500, mox.SIMULATE_DURATION))
thread_ap2 = threading.Thread(target=ap2.ready, args=("generate", 500, mox.SIMULATE_DURATION))
thread_s1 = threading.Thread(target=s1.ready, args=("local_max_buf_first",))
thread_a1 = threading.Thread(target=a1.ready, args=("consume", 0, 5000))
thread_a2 = threading.Thread(target=a2.ready, args=("consume", 0, 5000))


thread_ap1.start()
thread_ap2.start()
thread_s1.start()
thread_a1.start()
thread_a2.start()

thread_ap1.join()
thread_ap2.join()
thread_s1.join()
thread_a1.join()
thread_a2.join()

mox.Buffer.draw_plt([s1_buf1, s1_buf2])
mox.Buffer.draw_plt([a1_buf, a2_buf])

