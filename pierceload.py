#!/usr/bin/env python

from LCR import *

Fo = F('15MHz')

Co = C('5pf')
C2 = C('1000pf')
C1 = C('1000pf')

R1 = R(100)
Rx = R(10000)
Ri = R(5200)
Ro = Circuit.series(R1, Rx)

(R1s, C1s) = Circuit.parallel2series(Ri, C1, Fo)
(R2s, C2s) = Circuit.parallel2series(Ro, C2, Fo)

Cs = Circuit.parallel(Circuit.series(C1s, C2s), Co)
Rs = Circuit.series(R1s, R2s)

print "Cs:", Cs
print "Rs:", Rs

