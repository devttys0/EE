#!/usr/bin/env python

from LCR import *

Fo = F('20MHz')

Co = C('5pf')
C2 = C('1000pf')
C1 = C('1000pf')

R1 = R(30)
Rx = R(5)
Ri = R(780)
Ro = Circuit.series(R1, Rx)

(R2s, C2s) = Circuit.parallel2series(Ro, C2, Fo)
(R1s, C1s) = Circuit.parallel2series(Ri, C1, Fo)

Cs = Circuit.parallel(Circuit.series(C1s, C2s), Co)
Rs = Circuit.series(R1s, R2s)

print "Cs:", Cs
print "Rs:", Rs

