import math
from Components import L

class Amidon(L):

    def _init(self):
        uH = self.value / .000001
        self.N = 100 * math.sqrt((uH / self.AL))
        self.AWG = 0

    def turns(self, N):
        return L((((N / 100.0) ** 2) * self.AL) * .000001)

class T506(Amidon):

    AL = 40
    DIAMETER = .3

