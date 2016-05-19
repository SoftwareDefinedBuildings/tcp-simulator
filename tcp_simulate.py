#!/usr/bin/env python

import matplotlib.pyplot
from tcp import *

NUM_BYTES = 100000
A_VALS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.40, 0.45, 0.50)
colormap = {0.05: "b", 0.10: "g", 0.15: "r", 0.20: "c", 0.25: "m", 0.40: "y", 0.45: "dimgray", 0.50 : "k"}
R_VALS = tuple(xrange(1, 16))
D = 100
f = 12
AVG_SIZE = 30
TCP_WINDOW = 0

def prompt_int(string):
    val = None  
    while val is None:
        vals = raw_input(string)
        try:
            val = int(vals)
        except ValueError:
            pass
    return val

if __name__ == "__main__":
    cf = prompt_int("Capacity of first frame in a segment (cf): ")
    cr = prompt_int("Capacity of remaining frames in a segment (cr): ")
    l = prompt_int("Number of layer two retransmissions, including radio retries (l): ")
    h = prompt_int("Number of hops between nodes (h): ")

    set_cf(cf)
    set_cr(cr)

    print "Generating plot..."
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title("Frames Sent vs. Segment Size [cf = {0}, cr = {1}, l = {2}, h = {3}]".format(cf, cr, l, h))
    matplotlib.pyplot.xlabel("r (TCP Segment Size in Frames)")
    matplotlib.pyplot.ylabel("E[X] (Number of Frames to Send {0} Bytes)".format(NUM_BYTES))
    curves = []
    for a in A_VALS:
        print "a = {0}".format(a)
        set_loss_rate(a)
        def EXraw(r):
            reset_frame_tries()
            tcp_transmit(l, r, h, NUM_BYTES, TCP_WINDOW, D, f)
            return get_frame_tries()
        def EX(r):
            total = 0
            for _ in xrange(AVG_SIZE):
                total += EXraw(r)
            return float(total) / AVG_SIZE
        fs = tuple(map(lambda r: EX(r), R_VALS))
        for ar in fs:
            print ar
        for i in xrange(1, len(fs)):
            print (fs[i] - fs[i - 1]) / float(fs[i - 1])
        curve, = matplotlib.pyplot.plot(R_VALS, fs, label = "a = {0}".format(a), c = colormap[a])
        curves.append(curve)
    curves.reverse()
    matplotlib.pyplot.legend(handles = curves)
    print "Done."
    
    matplotlib.pyplot.show()
