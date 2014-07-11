from Components import *

class BJT(object):

    B = 0
    Ft = F(0)

    def __init__(self, Fo):
        self.Beta = self.Ft.value / Fo.value

    def bias(self, Vcc, Ve, Ie):
        Vb = V(float(Ve) + .7)
        Re = R(float(Ve) / float(Ie))
        Rb = R((self.Beta * float(Re)) / 5)
        Rb2 = R(.83*((float(Vcc)/float(Vb))*float(Rb)))
        Rb1 = R(((1/float(Rb)) - (1/float(Rb2)))**-1)
        return (Rb1, Rb2, Re)

class PN2222A(BJT):
    B = 100
    Ft = F('300MHz')

#(Rb1, Rb2, Re) = PN2222A(F('28.8MHz')).bias(V(9), V(2), I('2mA'))

#print Rb1
#print Rb2
#print Re
