import math
from Components import *

def parallel(*components):
    if len(set([x.SUFFIX for x in components])) != 1:
        raise Exception("All components must be of the same type!")
    return components[0].parallel(components)

def series(*components):
    if len(set([x.SUFFIX for x in components])) != 1:
        raise Exception("All components must be of the same type!")
    return components[0].series(components)

def divider(R1, R2, Vcc):
    return V(Vcc.value * (R2.value / (R1.value + R2.value)))

def series2parallel(Rs, Xs, Fo):
    return Xs.series2parallel(Rs, Fo)

def parallel2series(Rp, Xp, Fo):
    return Xp.parallel2series(Rp, Fo)


class TunedCircuit(object):

    @staticmethod
    def Q(Rs, Rl, C, L, Fo):
        '''
        Calculates the Q of a parallel tuned circuit with source and load impedances.

        @Rs - Source impedance.
        @Rl - Load impedance.
        @Ct - Capacitor.
        @Lt - Inductor.
        @Fo - Frequency.

        Returns the calculated Q.
        '''
        Rp = Circuit.parallel(Rs, Rl)
        Xp = Circuit.parallel(C.reactance(Fo), L.reactance(Fo))
        return (Rp/Xp)

    @staticmethod
    def resonance(L, C):
        '''
        Calculate the resonant frequency of L and C.

        @L - Inductor.
        @C - Capacitor.

        Returns an F object.
        '''
        return F(1 / (2*math.pi*math.sqrt(L.value*C.value)))

    @staticmethod
    def LC(Rs, Rl, Fo, F3db):
        '''
        Calculate the required L and C values for a tuned circuit of a given Q.

        @Rs   - Source impedance
        @Rl   - Load impedance
        @Fo   - Tuned circuit center frequency
        @F3db - Desired 3db bandwidth

        Returns a tuple of (L, C).
        '''
        Q = Fo.value / F3db.value
        Rp = Circuit.parallel(Rs, Rl).value
        Xp = (Rp / Q)
        Lt = L(Xp / Fo.w)
        Ct = C((1/Fo.w) / Xp)
        return (Lt, Ct)

