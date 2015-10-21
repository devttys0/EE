#!/usr/bin/env python
# Plots JFET intercept curves for common JFETs, given the gate voltage and source resistance.

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

class JFET(object):
    # Min/max Idss, in mA
    IDSS_MIN = 2
    IDSS_MAX = 20

    # Min/max pinchoff voltages, in V
    VP_MAX = -8
    VP_MIN = -2

    def shockley(self, Vgs, Idss, Vp):
        return (Idss * (1 - (Vgs/float(Vp)))**2)

    def id_min_points(self):
        x = range(self.VP_MIN, 1)
        y = []

        for Vgs in x:
            y.append(self.shockley(Vgs, self.IDSS_MIN, self.VP_MIN))

        return (x, y)

    def id_max_points(self):
        x = range(self.VP_MAX, 1)
        y = []

        for Vgs in x:
            y.append(self.shockley(Vgs, self.IDSS_MAX, self.VP_MAX))

        return (x, y)

    def vg_intercept(self, Rs, Vg=0):
        x = []
        y = [0, self.IDSS_MAX]

        for Id in y:
            x.append(Vg - (Rs * (Id*.001)))

        return (x, y)

    def plot(self, Rs=None, Vg=0):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # Generate plot
        plt = pg.plot(title=self.__class__.__name__, clear=True)
        plt.setYRange(0, self.IDSS_MAX)
        plt.setXRange(self.VP_MAX, 0)
        plt.showGrid(True, True, 1.0)
        plt.setLabel('left', "Id (mA)")
        plt.setLabel('bottom', "Vgs (V)")

        (x, y) = self.id_max_points()
        plt.plot(x, y, pen=pg.mkPen('g', width=3))

        (x, y) = self.id_min_points()
        plt.plot(x, y, pen=pg.mkPen('b', width=3))

        if Rs is not None:
            (x, y) = self.vg_intercept(Rs, Vg)
            plt.plot(x, y, pen=pg.mkPen('r', width=3))

        # Display plot
        QtGui.QApplication.instance().exec_()
        pg.exit()

class MPF102(JFET):
    IDSS_MIN = 2
    IDSS_MAX = 20
    VP_MAX = -8
    VP_MIN = -2

class J310(JFET):
    IDSS_MIN = 24
    IDSS_MAX = 60
    VP_MAX = -6
    VP_MIN = -2


if __name__ == '__main__':
    import sys
    import inspect

    def enumerate_jfet_classes():
        for (name, cls) in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, JFET) and cls is not JFET:
                yield (name, cls)

    try:
        jfet_type = sys.argv[1].strip('-').upper()
    except IndexError:
        jfet_opts = []
        for (name, cls) in enumerate_jfet_classes():
            jfet_opts.append("--%s" % name.lower())
        print "Usage: %s <%s> <Rs> [Vg]" % (sys.argv[0], " | ".join(jfet_opts))
        sys.exit(1)

    try:
        Rs = float(sys.argv[2])
    except IndexError:
        Rs = None

    try:
        Vg = float(sys.argv[3])
    except IndexError:
        Vg = 0

    for (name, cls) in enumerate_jfet_classes():
        if name.upper() == jfet_type:
            cls().plot(Rs, Vg)
            sys.exit(0)

    print "Sorry, '%s' is not a currently supported JFET!" % jfet_type


