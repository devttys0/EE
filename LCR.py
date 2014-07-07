import math

class Container(object):
    
    def __init__(self, **kwargs):
        for (k,v) in kwargs.iteritems():
            setattr(self, k, v)

class Component(object):
    '''
    Component class. All component types (R, C, L, etc) are subclassed from this.
    '''

    SUFFIX = ''
    SUFFIXES = ['', 'F', 'f', 'h', 'H', 'Hz', 'hz']
    TYPES = {
            'T' : 1000000000000.0, 
            'G' : 1000000000.0, 
            'M' : 1000000.0, 
            'K' : 1000.0, 
            'k' : 1000.0,
            'm' : .001, 
            'u' : .000001, 
            'n' : .000000001, 
            'p' : .000000000001,
    }

    def __init__(self, value):
        '''
        Class constructor.

        @value - A int, float or string value (e.g., .000000000001 or '1pf').

        Returns None.
        '''
        self.value = self._value2float(value)
        
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

    def _value2float(self, value):
        '''
        Converts a user-specified value to a float.

        @value - A int, float or string value (e.g., .000000000001 or '1pf').

        Returns a float value.
        '''
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

    def w(self, Fo):
        '''
        Omega function.

        @Fo - The frequency at which to calculate omega.
              May be a literal value, or an F object.

        Returns 2*math.pi*Fo.
        '''
        if isinstance(Fo, Component):
            freq = Fo.value
        else:
            freq = Fo

        return (2*math.pi*freq)

    def _sum(self, components):
        '''
        Returns a sum of the specified components (e.g., resistors in series).

        @components - A list of component objects.

        Returns a float sum of the component values.
        '''
        summ = 0.0
        for c in components:
            summ += c.value
        return summ

    def _inverse_sum(self, components):
        '''
        Returns the inverse sum of the specified components 
        (e.g., resistors in parallel).

        @components - A list of component objects.

        Returns a float sum of the component values.
        '''
        summ = 0.0
        for c in components:
            summ += (1/c.value)
        return (1/summ)

    def reactance(self, Fo):
        '''
        Calculates the reactance at the specified frequency.
        Should be overridden by the subclass.

        @Fo - The frequency at which to calculate omega.
              May be a literal value, or an F object.
        
        Returns an R object.
        '''
        return R(0)

    def series(self, components):
        '''
        Calculates the series impedance of the specified components.
        Should be overridden by the subclass.

        @components - A list of component objects.

        Returns an R object.
        '''
        return R(0)

    def parallel(self, components):
        '''
        Calculates the parallel impedance of the specified components.
        Should be overridden by the subclass.

        @components - A list of component objects.

        Returns an R object.
        '''
        return R(0)

class F(Component):
    '''
    Wrapper class for frequency values.
    Only purpose is to simplify specifying frequencies (e.g., in MHz, mHz, GHz, etc).
    '''
    SUFFIX = 'Hz'
     
class R(Component):
    '''
    Wrapper class for resistor values.
    '''
    SUFFIX = ''

    def series(self, components):
        return R(self._sum(components))

    def parallel(self, components):
        return R(self._inverse_sum(components))

class C(Component):
    '''
    Wrapper class for capacitance values.
    '''
    SUFFIX = 'F'

    def reactance(self, Fo):
        return R(1 / (self.w(Fo) * self.value))
    
    def series(self, components):
        return C(self._inverse_sum(components))

    def parallel(self, components):
        return C(self._sum(components))

class L(Component):
    '''
    Wrapper class for inductance values.
    '''
    SUFFIX = 'L'

    def reactance(self, Fo):
        return R(self.w(Fo) * self.value)
    
    def series(self, components):
        return L(self._sum(components))

    def parallel(self, components):
        return L(self._inverse_sum(components))

class Circuit(object):
    '''
    Class for calculating component values in circuits.
    '''

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
    def series2parallel(Rs, Cs, Fo):
        Q = 1 / (Cs.w(Fo) * float(Rs) * float(Cs))
        Rp = R(float(Rs) * (1 + (Q**2)))
        Cp = C(float(Cs) * (Q**2 / (1 + Q**2)))
        return (Rp, Cp)

    @staticmethod 
    def parallel2series(Rp, Cp, Fo):
        Q = Cp.w(Fo) * float(Cp.value) * float(Rp.value)
        Rs = R(float(Rp) * (1 / (1 + Q**2)))
        Cs = C(float(Cp) * ((1 + Q**2) / Q**2))
        return (Rs, Cs)

