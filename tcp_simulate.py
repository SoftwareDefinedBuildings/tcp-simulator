#!/usr/bin/env python

import matplotlib.pyplot
from tcp import *

NUM_BYTES = 100000
A_VALS = ("packetloss/jack-3-hours-50-60-histo", "packetloss/jack-3-hours-11-21-histo", "packetloss/jack-3-hours-0-70-histo", "packetloss/far-2-hours-20-30-histo", "packetloss/far-2-hours-0-35-histo")#), 0.40, 0.45, 0.50)
colormap = {0.01: "b", 0.10: "g", 0.20: "r", 0.30: "c", 0.40: "m", 0.50: "y", 0.60: "dimgray", 0.70 : "k", "packetloss/jack-3-hours-50-60-histo": "b", "packetloss/jack-3-hours-11-21-histo": "g", "packetloss/jack-3-hours-0-70-histo": "r", "packetloss/far-2-hours-20-30-histo": "c", "packetloss/far-2-hours-0-35-histo": "m"}
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
        if isinstance(a, int) or isinstance(a, float):
            set_loss_rate(a)
        else:
            load_runs(a)
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
