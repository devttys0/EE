#!/usr/bin/env python
# Caculates approximate Pierce oscillator operating parameters.

import sys
import math

class PierceXtal(object):

    def __init__(self, f, Co, C1, C2, R1=60):
        self.Co = self.pf2f(Co)
        self.C1 = self.pf2f(C1)
        self.C2 = self.pf2f(C2)
        self.CL = (self.C1 * self.C2) / (self.C1 + self.C2)
        self.R1 = float(R1)
        self.w = 2*math.pi*f*1000000

    def parallel2series(self, Rp, Cp):
        Q2 = (self.w*Cp*Rp)**2
        Rs = Rp * (1 / (1 + Q2))
        Cs = Cp * ((1 + Q2) / Q2)
        print Rs, Cs
        return (Rs, Cs)

    def xtaload(self, Rin, Rout):
        (Rs1, Cs1) = self.parallel2series(Rout, self.C1)
        (Rs2, Cs2) = self.parallel2series(Rin, self.C2)

        Rs = Rs1 + Rs2
        Cs = (1 / ((1/Cs1) + (1/Cs2))) + self.Co

        return (Rs, Cs)

    def gm_crit(self):
        return (4*self.R1) * self.w**2 * (self.Co + (self.C1/2))**2

    def drive_level(self, Vpp):
        Vx = Vpp * .3535
        print self.f2pf(self.CL)
        P = ((self.w * (self.Co + self.CL) * Vx)**2) * self.R1
        return (P * 1000000)

    def f2pf(self, C):
        return (C * 1000000000000)

    def pf2f(self, C):
        return (C / 1000000000000)

if __name__ == '__main__':
    try:
        f = float(sys.argv[1])
        Rin = float(sys.argv[2])
        Rout = float(sys.argv[3])
        C1 = float(sys.argv[4])
        C2 = float(sys.argv[5])
        try:
            Co = float(sys.argv[6])
        except:
            Co = 5.0
        try:
            Vpp = float(sys.argv[7])
        except:
            Vpp = None
    except:
        print "Usage: %s <freq> <Rin> <Rout> <Cc> <Cb> [Co]" % sys.argv[0]
        print "All values should be entered in MHz, pF, and ohms."
        sys.exit(1)

    osc = PierceXtal(f, Co, C1, C2)
    (Rs, Cs) = osc.xtaload(Rin, Rout)

    print "Xtal Load: %.2f ohms, %.2f pf" % (Rs, osc.f2pf(Cs))
    if Vpp is not None:
        print "Drive Level: %.2f uW" % osc.drive_level(Vpp)
    print "gm(crit):", osc.gm_crit()

