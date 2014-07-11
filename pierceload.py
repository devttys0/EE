#!/usr/bin/env python

from LCR import *

Fo = F('15MHz')

Co = C('5pf')
C2 = C('1000pf')
C1 = C('1000pf')

R1 = R(100)
Rx = R(10000)
Ri = R(5200)
Ro = Circuits.series(R1, Rx)

(R1s, C1s) = Circuits.parallel2series(Ri, C1, Fo)
(R2s, C2s) = Circuits.parallel2series(Ro, C2, Fo)

Cs = Circuits.parallel(Circuits.series(C1s, C2s), Co)
Rs = Circuits.series(R1s, R2s)

print "Cs:", Cs
print "Rs:", Rs

