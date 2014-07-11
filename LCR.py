import math

class Container(object):
    
    DEFAULTS = {}

    def __init__(self, **kwargs):
        for (k,v) in self.DEFAULTS.iteritems():
            setattr(self, k, v)

        for (k,v) in kwargs.iteritems():
            setattr(self, k, v)

class Component(object):
    '''
    Component class. All component types (R, C, L, etc) are subclassed from this.
    '''

    SUFFIX = ''
    SUFFIXES = ['', 'V', 'v', 'F', 'f', 'h', 'H', 'Hz', 'hz']
    TYPES = {
            'T' : 1000000000000.0, 
            'G' : 1000000000.0, 
            'M' : 1000000.0, 
            'K' : 1000.0, 
            'k' : 1000.0,
            ''  : 1.0,
            'm' : .001, 
            'u' : .000001, 
            'n' : .000000001, 
            'p' : .000000000001,
    }
    ALLOWED_TYPES = TYPES
    MIN_VALUE = 1.0
    MAX_VALUE = 10000.0

    def __init__(self, value=0, parasitics=None):
        '''
        Class constructor.

        @value      - A int, float or string value (e.g., .000000000001 or '1pf').
        @parasitics - An instance of the Parasitics class.

        Returns None.
        '''
        self.value = self._value2float(value)
        self.parasitics = parasitics
        self._init()

    def _init(self):
        return None

    def __float__(self):
        return self.value

    def __str__(self):
        display_key = ''
        display_value = "%.2f" % self.value
         
        for key in sorted(self.TYPES, key=self.TYPES.get):
            if key not in self.ALLOWED_TYPES:
                continue
            value = self.value / self.TYPES[key]
            if value >= self.MIN_VALUE and value < self.MAX_VALUE:
                display_key = key
                display_value = "%.2f" % value
                break

        display_value = display_value.strip('0')
        if display_value.endswith('.'):
            display_value = display_value[:-1]

        return "%s%s%s" % (display_value, display_key, self.SUFFIX)

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

                    if metric and value.endswith(metric):
                        try:
                            return (float(value.replace(metric, '')) * conversion)
                        except ValueError:
                            continue
        else:
            raise Exception("Invalid suffix '%s'!" % str(self.SUFFIX))

        raise Exception("Invalid value!")

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

    def series2parallel(self, *args, **kwargs):
        return None

    def parallel2series(self, *args, **kwargs):
        return None

class V(Component):
    SUFFIX = 'V'
    MAX_VALUE = 1000.0

class F(Component):
    '''
    Wrapper class for frequency values.
    '''
    SUFFIX = 'Hz'

    def _init(self):
        self.w = 2*math.pi*self.value

class Crystal(Component):
    SUFFIX = 'Hz'

class R(Component):
    '''
    Wrapper class for resistor values.
    '''
    SUFFIX = ''
    ALLOWED_TYPES = ['M', 'k', 'K']

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
        return R(1 / (Fo.w * self.value))
    
    def series(self, components):
        return C(self._inverse_sum(components))

    def parallel(self, components):
        return C(self._sum(components))

    def series2parallel(self, Rs, Fo):
        Q = 1 / (Fo.w * float(Rs) * self.value)
        Rp = R(float(Rs) * (1 + (Q**2)))
        Cp = C(self.value * (Q**2 / (1 + Q**2)))
        return (Rp, Cp)

    def parallel2series(self, Rp, Fo):
        Q = Fo.w * self.value * float(Rp)
        Rs = R(float(Rp) * (1 / (1 + Q**2)))
        Cs = C(self.value * ((1 + Q**2) / Q**2))
        return (Rs, Cs)

class L(Component):
    '''
    Wrapper class for inductance values.
    '''
    SUFFIX = 'H'

    def Q(self, Fo):
        Xl = self.reactance(Fo)
        return (Xl.value / self.parasitics.Rs.value)

    def reactance(self, Fo):
        return R(Fo.w * self.value)
    
    def series(self, components):
        return L(self._sum(components))

    def parallel(self, components):
        return L(self._inverse_sum(components))

    def series2parallel(self, Rs, Fo):
        Q = self.reactance(Fo).value / float(Rs)
        Rp = R(((Q**2) + 1) * float(Rs))
        Xp = Rp.value / Q
        Lp = L(Xp / Fo.w)
        return (Rp, Lp)

    def parallel2series(self, Rp, Fo):
        Xp = self.value * Fo.w
        Q = float(Rp) / Xp
        Rs = R(float(Rp) / ((Q**2) + 1))
        Ls = L((Q * float(Rs)) / Fo.w)
        return (Rs, Ls)

class Parasitics(Container):
    '''
    Class container describing parasitic elements of a component.
    '''
    DEFAULTS = {
            'Rs' : R(0),
            'Rp' : R(0),
            'Ls' : L(0),
            'Lp' : L(0),
            'Cs' : C(0),    
            'Cp' : C(0),    
    }

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
    def divider(R1, R2, Vcc):
        return V(Vcc.value * (R2.value / (R1.value + R2.value)))

    @staticmethod
    def series2parallel(Rs, Xs, Fo):
        return Xs.series2parallel(Rs, Fo)

    @staticmethod
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

class Amidon(L):

    def _init(self):
        uH = self.value / .000001
        self.N = 100 * math.sqrt((uH / self.AL))
        self.AWG = 0

    def turns(self):
        return (self.N, self.AWG)

class T506(Amidon):

    AL = 40
    DIAMETER = .3
