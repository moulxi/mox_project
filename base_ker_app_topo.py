import mox
import threading
import time

# sender   |    s1    |   kernel buffer  |  app buffer  |
#-------------------------------------------------------------
#  ap1 ----| s1_buf1  | ---- k1_buf ---- | -- a1_buf -- |
#  ap2 ----| s1_buf2  | ---- k2_buf ---- | -- a2_buf -- |

mox.SIMULATE_DURATION = 5000


# application1 in the host
k1_buf = mox.Buffer(pack_num = 0, capacity = 100, name = "k1_buf")
a1_buf = mox.Buffer(pack_num = 0, capacity = 100, name = "a1_buf")
recv1 = mox.Application(buf = k1_buf , time_loc = 200, time_scale = 20, pkt_loc = 0, pkt_scale = 0, to_buf = a1_buf)
a1 = mox.Application(buf = a1_buf, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)

# applicatino2 in the host
k2_buf = mox.Buffer(pack_num = 0, capacity = 100, name = "k2_buf")
a2_buf = mox.Buffer(pack_num = 0, capacity = 100, name = "a2_buf")
recv2 = mox.Application(buf = k2_buf ,time_loc = 200, time_scale = 20, pkt_loc = 0, pkt_scale = 0, to_buf = a2_buf)
a2 = mox.Application(buf = a2_buf, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)

# switch with two buffers inside
s1_buf1 = mox.Buffer(pack_num = 0, capacity = 80, name = "s1_buf1")
s1_buf1.set_downstream(k1_buf)
s1_buf2 = mox.Buffer(pack_num = 0, capacity = 100, name = "s1_buf2")
s1_buf2.set_downstream(k2_buf)
s1 = mox.Switch(buf_list = [s1_buf1, s1_buf2], pkt_loc = 2, time_loc = 20)

# the application which put packet into switch1
ap1 = mox.Application(buf = s1_buf1, time_loc = 20, time_scale = 0, pkt_loc = 2, pkt_scale = 0)
ap2 = mox.Application(buf = s1_buf2, time_loc = 20, time_scale = 0, pkt_loc = 1, pkt_scale = 0)


thread_ap1 = threading.Thread(target=ap1.ready, args=("generate", 0, mox.SIMULATE_DURATION))
thread_ap2 = threading.Thread(target=ap2.ready, args=("generate", 0, mox.SIMULATE_DURATION))
thread_s1 = threading.Thread(target=s1.ready, args=("local_max_buf_first",500))
thread_recv1 = threading.Thread(target=recv1.ready, args=("move_all", 500, mox.SIMULATE_DURATION))
thread_recv2 = threading.Thread(target=recv2.ready, args=("move_all", 500, mox.SIMULATE_DURATION))
thread_a1 = threading.Thread(target=a1.ready, args=("consume", 700, 5000))
thread_a2 = threading.Thread(target=a2.ready, args=("consume", 700, 5000))

# orange, purple, brown, pink ,gray ,olive ,navy ,lime, blue, yellow, magenta, red, green, cyan, black, white
mox.Buffer.set_buf_chain_color([s1_buf1, k1_buf, a1_buf], "olive")
mox.Buffer.set_buf_chain_color([s1_buf2, k2_buf, a2_buf], "orange")


thread_ap1.start()
thread_ap2.start()
thread_s1.start()
thread_a1.start()
thread_a2.start()
thread_recv1.start()
thread_recv2.start()

thread_ap1.join()
thread_ap2.join()
thread_s1.join()
thread_a1.join()
thread_a2.join()
thread_recv1.join()
thread_recv2.join()

mox.Buffer.draw_plt([s1_buf1, s1_buf2])
mox.Buffer.draw_plt([k1_buf, k2_buf])
mox.Buffer.draw_plt([a1_buf, a2_buf])

