import mox
import threading
import time

# sender   |    s1    |   consumer
#---------------------------------
#  ap1 ----| s1_buf1  | --- a1_buf
#  ap2 ----| s1_buf2  | --- a2_buf

mox.SIMULATE_DURATION = 5000

# switch1 with two buffers inside
s1_buf1 = mox.Buffer(pack_num = 1, capacity = 80, name = "s1_buf1")
s1_buf2 = mox.Buffer(pack_num = 1, capacity = 100, name = "s1_buf2")
s1 = mox.Switch(buf_list = [s1_buf1, s1_buf2], pkt_loc = 2, time_loc = 20)

# the application which put packet into switch1
ap1 = mox.Application(buf = s1_buf1, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)
ap2 = mox.Application(buf = s1_buf2, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)


# application1 and its buffer 
a1_buf = mox.Buffer(pack_num = 70, capacity = 100, name = "a1_buf")
a1 = mox.Application(buf = a1_buf, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)


# application2 and its buffer
a2_buf = mox.Buffer(pack_num = 50, capacity = 100, name = "a2_buf")
a2 = mox.Application(buf = a2_buf, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)

s1_buf1.set_downstream(a1_buf)
s1_buf2.set_downstream(a2_buf)

thread_ap1 = threading.Thread(target=ap1.ready, args=("generate", 500, mox.SIMULATE_DURATION))
thread_ap2 = threading.Thread(target=ap2.ready, args=("generate", 500, mox.SIMULATE_DURATION))
thread_s1 = threading.Thread(target=s1.ready, args=("fifo",1000))
thread_a1 = threading.Thread(target=a1.ready, args=("consume", 0, 5000))
thread_a2 = threading.Thread(target=a2.ready, args=("consume", 0, 5000))

# orange, purple, brown, pink ,gray ,olive ,navy ,lime, blue, yellow, magenta, red, green, cyan, black, white
mox.Buffer.set_buf_chain_color([s1_buf1, a1_buf], "olive")
mox.Buffer.set_buf_chain_color([s1_buf2, a2_buf], "orange")


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

