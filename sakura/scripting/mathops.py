from __future__ import division
from math import hypot

def vector_towards(sx, sy, tx, ty, ln):
    vdif = tx - sx, ty - sy
    vlen = hypot(*vdif)
    if vlen == 0: return    # Cannot accelerate nowhere!
    return vdif[0]*ln/vlen, vdif[1]*ln/vlen    
