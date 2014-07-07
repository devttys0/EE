import math

class Component(object):
    SUFFIX = ''
    SUFFIXES = ['', 'F', 'f', 'h', 'H', 'Hz', 'hz']
    TYPES = {
            'M' : 1000000.0, 
            'K' : 1000.0, 
            'k' : 1000.0,
            'm' : .001, 
            'u' : .000001, 
            'n' : .000000001, 
            'p' : .000000000001,
    }

    def __init__(self, value):
        if isinstance(value, str):
            self.value = self._str2float(value)
        else:
            self.value = float(value)
        
    def __float__(self):
        return self.value

    def __str__(self):
        display_key = ''
        display_value = "%.2f" % self.value
        
        for key in sorted(self.TYPES, key=self.TYPES.get):
            if isinstance(self, R) and self.TYPES[key] not in ['M', 'K', 'k']:
                continue
            value = self.value / self.TYPES[key]
            if value >= 1.0 and value < 10000.0:
                display_key = key
                display_value = "%.2f" % value
                break

        return "%s%s%s" % (display_value.strip('0'), display_key, self.SUFFIX)

    def _str2float(self, value):
        try:
            return float(value)
        except ValueError:
            pass

        if self.SUFFIX in self.SUFFIXES:
            for (mtype, conversion) in self.TYPES.iteritems():
                for suffix in self.SUFFIXES:
                    metric = mtype + suffix

                    if value.endswith(metric):
                        return (float(value.replace(metric, '')) * conversion)
        else:
            raise Exception("Invalid suffix '%s'!" % str(self.SUFFIX))

        raise Exception("Invalid value!")

    def w(self, F):
        if isinstance(F, Component):
            freq = F.value
        else:
            freq = F

        return (2*math.pi*freq)

    def _sum(self, components):
        summ = 0.0
        for c in components:
            summ += c.value
        return summ

    def _inverse_sum(self, components):
        summ = 0.0
        for c in components:
            summ += (1/c.value)
        return (1/summ)

    def reactance(self, F):
       return R(0)

class F(Component):
    SUFFIX = 'Hz'
     
class R(Component):
    SUFFIX = ''

    def series(self, components):
        return R(self._sum(components))

    def parallel(self, components):
        return R(self._inverse_sum(components))

class C(Component):
    SUFFIX = 'F'

    def reactance(self, F):
        return R(1 / (self.w(F) * self.value))
    
    def series(self, components):
        return C(self._inverse_sum(components))

    def parallel(self, components):
        return C(self._sum(components))

class L(Component):
    SUFFIX = 'L'

    def reactance(self, F):
        return R(self.w(F) * self.value)
    
    def series(self, components):
        return L(self._sum(components))

    def parallel(self, components):
        return L(self._inverse_sum(components))

class Circuit(object):
   
    @staticmethod 
    def parallel(*components):
        if len(set([x.SUFFIX for x in components])) != 1:
            raise Exception("All components must be of the same type!")
        
        return components[0].parallel(components)

    @staticmethod 
    def series(*components):
        if len(set([x.SUFFIX for x in components])) != 1:
            raise Exception("All components must be of the same type!")
        
        return components[0].series(components)

    @staticmethod 
    def series2parallel(Rs, Cs, F):
        Q = 1 / (S.w(F) * float(Rs) * float(Cs))
        Rp = R(float(Rs) * (1 + (Q**2)))
        Cp = C(float(Cs) * (Q**2 / (1 + Q**2)))
        return (Rp, Cp)

    @staticmethod 
    def parallel2series(Rp, Cp, F):
        Q = Cp.w(F) * float(Cp.value) * float(Rp.value)
        Rs = R(float(Rp) * (1 / (1 + Q**2)))
        Cs = C(float(Cp) * ((1 + Q**2) / Q**2))
        return (Rs, Cs)

