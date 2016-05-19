#!/usr/bin/env python

from tcp import *

SAMPLE_SIZE = 10000

print "Testing E[F]..."

a = 0.23
q = (2 * a) - (a ** 2)
l = 6
EF = (2 - a) * (1 - (q ** l)) / (1 - q)

print "E[F] =", EF

set_loss_rate(a)
s = 0
for _ in xrange(SAMPLE_SIZE):
    reset_frame_tries()
    mac_transmit_full(l)
    s += get_frame_tries()

print "Experimental Fbar =", s / float(SAMPLE_SIZE)

print "Testing E[Y]..."

r = 140

p = q ** l
EY = EF * (1 - ((1 - p) ** r)) / p

print "E[Y] =", EY

s = 0
for _ in xrange(SAMPLE_SIZE):
    reset_frame_tries()
    ip_transmit_one_hop(l, r)
    s += get_frame_tries()

print "Experimental Ybar =", s / float(SAMPLE_SIZE)

print "Testing E[Z]..."

h = 5

v = 1 - ((1 - p) ** (r - 1)) * (1 - (a ** l))

EZ = EY * (1 - ((1 - v) ** h)) / v

print "E[Z] =", EZ

s = 0
for _ in xrange(SAMPLE_SIZE):
    reset_frame_tries()
    ip_transmit_multi_hop(l, r, h)
    s += get_frame_tries()
    
print "Experimental Zbar =", s / float(SAMPLE_SIZE)
