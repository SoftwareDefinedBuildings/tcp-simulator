import random

# Probability that a frame is lost
a = 0.1

# Average number of segments that each ACK acknowledges
d = 2.0

# Capacity of the first frame for TCP segment text
cf = 70

# Capacity of each of the remaining frames for TCP segment text
cr = 100

# Sanity check constants
assert(1 <= d and d <= 2)

def set_cf(newcf):
    global cf
    cf = newcf

def set_cr(newcr):
    global cr
    cr = newcr

def set_loss_rate(lossrate):
    global a
    a = lossrate

frame_tries = 0
def reset_frame_tries():
    global frame_tries
    frame_tries = 0

def get_frame_tries():
    return frame_tries

def frame_transmit_once():
    """ Simulates transmission of a single 802.15.4 frame. Returns
        True if the retransmission succeeds, or False if it fails.
    """
    global frame_tries
    frame_tries += 1
    return random.random() >= a

def mac_transmit_once():
    """ Simulates the transmission of an 802.15.4 frame and the ACK
        sent in response. Returns two booleans. The first indicates
        if the frame was received by the other side. The second indicates
        whether the ACK was received by the sender.
    """
    frm_received = frame_transmit_once()
    if frm_received:
        ack_received = frame_transmit_once()
    else:
        ack_received = False
    return frm_received, ack_received

def mac_transmit_full(l):
    """ Simulates the transmission of an 802.15.4 frame with retries.
        Returns two booleans. The first indicates if the frame was received
        by the other side. The second indicates whether the sender knows
        that the other side received it.
        l is the number of MAC-layer retries.
    """
    success = False
    for xmit in xrange(l):
        rcvd, acked = mac_transmit_once()
        if acked:
            return True, True
        success = (success or rcvd)
    return success, False

def ip_transmit_one_hop(l, r):
    """ Simulates the transmission of an IP packet that is r frames long,
        over a single hop.
    """
    for fragment in xrange(r):
        rcvd, acked = mac_transmit_full(l)
        if not acked:
            if fragment == r - 1:
                # If it is the last fragment, it may go through anyway
                return rcvd
            return False
    return True

def ip_transmit_multi_hop(l, r, h):
    """ Simulates the transmission of an IP packet that is r frames long,
        over h hops.
    """
    for hop in xrange(h):
        hopped = ip_transmit_one_hop(l, r)
        if not hopped:
            return False
    return True

def tcp_transmit(l, r, h, b, w, D, f):
    """ Simulates the transmission of b bytes over a TCP stream over h hops,
        where r is the maximum segment size in frames.
        w is the window size in bytes, or 0 if you want to assume exactly one outstanding segment.
    """
    assert r >= 1
    segcap = cf + (r - 1) * cr
    numsegs = int(float(b) / segcap + 0.5)
    
    delackthresh = float(D) / float(f)
    
    winsize = int(w / float(b) + 0.5)
    if winsize == 0:
        winsize = 1
    del w # avoid confusion
    
    wacked = []
    wrcved = []
    
    numacked = 0
    
    while numacked < numsegs:
        # If we have extra space in the window, transmit another segment
        assert len(wacked) == len(wrcved)
        if len(wacked) + numacked < numsegs:
            wrcved.append(ip_transmit_multi_hop(l, r, h))
            if wrcved[-1]:
                wacked.append(ip_transmit_multi_hop(l, 1, h))
                if wacked[-1]:
                    for j in xrange(len(wacked)):
                        if wrcved[j] and not wacked[j]:
                            wacked[j] = True
            else:
                wacked.append(False)
        # If the first thing in the window is ACKed, then remove it from the window
        elif wacked[0]:
            wacked.pop(0)
            wrcved.pop(0)
            numacked += 1
        # If the window is full and the first thing isn't ACKed, then we need to retransmit
        else:
            # Snapshot the current state and retransmit everything that isn't ACKed (snapshot it so we can process the ACKs immediately)
            notacked = [i for i, isacked in enumerate(wacked) if not isacked]
            for i in notacked:
                # Retransmit segment i
                received = ip_transmit_multi_hop(l, r, h)
                if received:
                    wrcved[i] = True
                    acked = ip_transmit_multi_hop(l, 1, h)
                    if acked:
                        for j in xrange(len(wacked)):
                            if wrcved[j] and not wacked[j]:
                                wacked[j] = True
    
def extra():
    # Skip at most one packet due to DELACK
    skippedlast = False

    for segid in xrange(numsegs):
        success = False
        start = get_frame_tries()
        while not success:
            success = ip_transmit_multi_hop(l, r, h)
            #if success:
            #    success = ip_transmit_multi_hop(l, 1, h)
        end = get_frame_tries()
        if skippedlast and end - start > delackthresh:
            # We missed the delack threshold!
            # Pay for the previous packet's ACK.
            #ip_transmit_multi_hop(l, 1, h)
            skippedlast = True
        elif skippedlast:
            # We already skipped the ACK on the previous segment, so we need to pay for it this time.
            #ip_transmit_multi_hop(l, 1, h)
            skippedlast = False
        elif not skippedlast:
            skippedlast = True
    numacks = int(float(numsegs) / d + 0.5)
    for ackid in xrange(numacks):
        ip_transmit_multi_hop(l, 1, h)
        
def tcp_transmit_cwnd_one(l, r, h, b):
    """ Simulates the transmission of b bytes over a TCP stream over h hops,
        where r is the maximum segment size in frames.
    """
    assert r >= 1
    segcap = cf + (r - 1) * cr
    numsegs = int(float(b) / segcap + 0.5)

    for segid in xrange(numsegs):
        success = False
        while not success:
            success = ip_transmit_multi_hop(l, r, h)
            if success:
                success = ip_transmit_multi_hop(l, 1, h)
        
def tcp_transmit_cwnd_inf(l, r, h, b):
    """ Simulates the transmission of b bytes over a TCP stream over h hops,
        where r is the maximum segment size in frames.
    """
    assert r >= 1
    segcap = cf + (r - 1) * cr
    numsegs = int(float(b) / segcap + 0.5)

    for segid in xrange(numsegs):
        success = False
        while not success:
            success = ip_transmit_multi_hop(l, r, h)
    numacks = int(float(numsegs) / d + 0.5)
    for ackid in xrange(numacks):
        ip_transmit_multi_hop(l, 1, h)
