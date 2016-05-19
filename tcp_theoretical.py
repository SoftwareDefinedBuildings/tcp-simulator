#!/usr/bin/python

import math
import matplotlib.pyplot
import numpy
# import scipy.optimize

Q_LOW = 0.01
Q_HIGH = 0.50
NUM_BYTES = 100000
VIRTUAL_INF = 100
GRAPH_NUM_VALS = 50
A_VALS = (0.05, 0.10, 0.15, 0.20, 0.25)#, 0.40, 0.45, 0.50)
colormap = {0.05: "b", 0.10: "g", 0.15: "r", 0.20: "c", 0.25: "m", 0.40: "y", 0.45: "dimgray", 0.50 : "k"}
R_VALS = tuple(xrange(1, 16))

D = 100
f = 12

# THIS FUNCTION ASSUMES THAT 6LOWPAN STOPS TRANSMITTING FRAGMENTS ONCE ONE IS LOST
FRAG_LABEL_STOP = "Assuming 6LoWPAN stops sending\nfragments once one is lost"

def construct_f(cf, cr, l, h, a, D, f):
    b = float(NUM_BYTES)
    a = float(a) # just in case
    q = (2 * a) - (a * a)
    p = q ** l
    def EX(r):
        omv = ((1 - p) ** (r - 1)) * (1 - (a ** l))
        v = 1 - omv
        
        v1 = a ** l
        
        u = 1 - (omv ** h)
        u1 = 1 - ((1 - v1) ** h)
        
        coeff = (b / (cf + ((r - 1) * cr)))
        ql = q ** l
        omql = 1 - ql
        omqlrh = omql ** (r * h)
        EF = (2 - a) * (1 - (q ** l)) / (1 - q)
        EY = EF * (1 - ((1 - p) ** r)) / p
        EY1 = EF
        
        EZ = EY * (1 - ((1 - v) ** h)) / v
        EZ1 = EY1 * (1 - ((1 - v1) ** h)) / v1
        
        d = 1 if True or (EZ >= float(D) / f) else 2
        
        ES = (EZ + (1 - u) / d * EZ1) / (1 - u - (1 - u) * u1)
        
        return b / (cf + (r - 1) * cr) * ES
    return EX
    
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
    print "Generating plot..."
    """
    qvals = numpy.linspace(Q_LOW, Q_HIGH, GRAPH_NUM_VALS)
    rvals = []
    fvals = []
    for q in qvals:
        f = construct_f(cf, cr, l, h, q)
        optval = scipy.optimize.minimize_scalar(f, bounds=(1, VIRTUAL_INF), method='bounded')
        rvals.append(optval.x)
        fvals.append(optval.fun)
 
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title("Optimum TCP Segment Size vs. Loss Rate [cf = {0}, cr = {1}, l = {2}, h = {3}]".format(cf, cr, l, h))
    matplotlib.pyplot.xlabel("q (Frame Loss Rate)")
    matplotlib.pyplot.ylabel("r (Optimum Segment Length, Measured in Frames)")
    matplotlib.pyplot.axis(ymin = 0, ymax = 16)
    matplotlib.pyplot.plot(qvals, rvals, label = FRAG_LABEL_STOP)
#    matplotlib.pyplot.plot(qvals, rnvals, label = FRAG_LABEL_CONT)
#    matplotlib.pyplot.legend(loc = "upper right")
    
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title("Number of Frames Sent vs. Loss Rate [cf = {0}, cr = {1}, l = {2}, h = {3}]".format(cf, cr, l, h))
    matplotlib.pyplot.xlabel("q (Frame Loss Rate)")
    matplotlib.pyplot.yscale('log')
    matplotlib.pyplot.ylabel("f (Optimum Exp. Number of Frames to Send {0} Bytes)".format(NUM_BYTES))
    matplotlib.pyplot.plot(qvals, fvals, label = FRAG_LABEL_STOP)
#    matplotlib.pyplot.plot(qvals, fnvals, label = FRAG_LABEL_CONT)
#    matplotlib.pyplot.legend(loc = "lower right")
    """
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title("Frames Sent vs. Segment Size [cf = {0}, cr = {1}, l = {2}, h = {3}]".format(cf, cr, l, h))
    matplotlib.pyplot.xlabel("r (TCP Segment Size in Frames)")
    matplotlib.pyplot.ylabel("E[X] (Number of Frames to Send {0} Bytes)".format(NUM_BYTES))
    curves = []
    for a in A_VALS:
        print "a = {0}".format(a)
        EX = construct_f(cf, cr, l, h, a, D, f)
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
