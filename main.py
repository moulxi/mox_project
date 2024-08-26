import mox
import threading
import time



buf1 = mox.Buffer(pack_num = 100, capacity = 150)
buf2 = mox.Buffer(pack_num = 100, capacity = 300)



mox.Buffer.move_all_packet(mox.black_hole, buf2)