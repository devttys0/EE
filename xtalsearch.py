#!/usr/bin/env python
# Searches Digikey for crystals or crystal combinations that will achieve a
# desired frequency within the specified error range.

import sys
import getopt
import urllib2

class Crystal(object):

    def __init__(self, fundamental=0.0, harmonic=1):
        self.harmonic = harmonic
        self.fundamental = fundamental
        self.frequency = self.fundamental * self.harmonic
        self.id = hash("%.5f*%d=%.5f" % (self.fundamental, self.harmonic, self.frequency))

class CrystalMatch(object):
    def __init__(self, crystals, operator=""):
        self.crystals = crystals
        self.operator = operator

class CrystalFinder(object):
    def __init__(self, desired_frequency, max_deviation, harmonics):
        self.desired_frequency = desired_frequency
        self.max_deviation = max_deviation
        self.harmonics = harmonics
        self.crystals = self.list_available_crystals()

    def wget(self, url, post=None):
        req = urllib2.Request(url, post)
        data = urllib2.urlopen(req).read()
        return data

    def digikey_crystals(self):
        frequencies = []
        # Only get crystals that are in stock and fundamental mode
        html = self.wget("http://www.digikey.com/product-search/en/crystals-and-oscillators/crystals?stock=1&pv538=2")

        try:
            select_options = html.split("<td align=center><select multiple size=10 name=pv139>")[1].split("</select>")[0].split('\n')
            for option in select_options:
                if '>' in option:
                    frequency = option.split('>')[1]
                    if frequency.endswith('MHz'):
                        freq = float(frequency.split('MHz')[0])
                    elif frequency.endswith('kHz'):
                        freq = float(frequency.split('kHz')[0]) / 1000.0
                    else:
                        raise Exception("Unknown frequency option: '%s'" % frequency)

                    frequencies.append(freq)
        except Exception as e:
            raise e

        return frequencies

    def mouser_crystals(self):
        frequencies = []

        # TODO: Mouser page parsing is broken.
        return frequencies

        html = self.wget("http://www.mouser.com/Passive-Components/Frequency-Control-Timing-Devices/Crystals/_/N-6zu9fZscv7")

        try:
            select_options = html.split('id="ctl00_ContentMain_uc5_AttributeCategoryList_ctl01_688437">')[1].split("</select")[0].split('\n')
            for option in select_options:
                if '>' in option:
                    frequency = option.split('>')[1]
                    if 'MHz' in frequency:
                        freq = float(frequency.split('MHz')[0])
                    elif 'MHZ' in frequency:
                        freq = float(frequency.split('MHZ')[0])
                    elif 'kHz' in frequency:
                        freq = float(frequency.split('kHz')[0]) / 1000.0
                    elif 'kHZ' in frequency:
                        freq = float(frequency.split('kHZ')[0]) / 1000.0
                    elif 'KHz' in frequency:
                        freq = float(frequency.split('KHz')[0]) / 1000.0
                    else:
                        raise Exception("Unknown frequency option: '%s'" % frequency)

                    frequencies.append(freq)
        except Exception as e:
            raise e

        return frequencies

    def list_available_crystals(self):
        crystals = {}

        for crystal in self.digikey_crystals() + self.mouser_crystals():
            for i in self.harmonics:
                xtal = Crystal(crystal, i)
                # Show preference to lower-order harmonics
                if not crystals.has_key(xtal.id):
                    crystals[xtal.id] = xtal

        return crystals

    def deviation_ok(self, freq):
        low = round(self.desired_frequency - freq, 6)
        high = round(freq - self.desired_frequency, 6)

        return (low >= 0 and low <= self.max_deviation) or (high >= 0 and high <= self.max_deviation)

    def find_divisors(self, crystals=None):
        if not crystals:
            crystals = self.crystals

        for crystal in crystals.values():
            for i in [1, 2, 4, 8]:
                div_freq = crystal.frequency / i
                if self.deviation_ok(div_freq):
                    print "%f / %d = %f; use %f (%d harmonic)" % (crystal.frequency, i, div_freq, crystal.fundamental, crystal.harmonic)

    def find_sum_pairs(self, crystals=None):
        done_sum_pairs = []
        done_min_pairs = []

        if not crystals:
            crystals = self.crystals

        for xtal1 in crystals.values():
            f1 = xtal1.frequency
            for xtal2 in crystals.values():
                f2 = xtal2.frequency
                f_plus = f1 + f2
                if self.deviation_ok(f_plus) and (f1, f2) not in done_sum_pairs:
                    done_sum_pairs.append((f1, f2))
                    done_sum_pairs.append((f2, f1))
                    print "%f + %f = %f; use %f (%d harmonic) and %f (%d harmonic)" % (f1,
                                                                                       f2,
                                                                                       f_plus,
                                                                                       xtal1.fundamental,
                                                                                       xtal1.harmonic,
                                                                                       xtal2.fundamental,
                                                                                       xtal2.harmonic)

                if f1 > f2:
                    f_minus = f1 - f2
                    big = xtal1
                    little = xtal2
                else:
                    f_minus = f2 - f1
                    big = xtal2
                    little = xtal1
                if self.deviation_ok(f_minus) and (big.id, little.id) not in done_min_pairs:
                    done_min_pairs.append((big.id, little.id))
                    print "%f - %f = %f; use %f (%d harmonic) and %f (%d harmonic)" % (big.frequency,
                                                                                       little.frequency,
                                                                                       f_minus,
                                                                                       big.fundamental,
                                                                                       big.harmonic,
                                                                                       little.fundamental,
                                                                                       little.harmonic)

def usage():
    print "Usage: %s -f <frequency, in MHz> -d <max deviation, in MHz> -h <comma,separated,harmonics>" % sys.argv[0]
    sys.exit(1)


if __name__ == '__main__':
    harmonics = [1, 2, 3, 4, 5]
    max_deviation = 0.0
    desired_frequency = 0.0

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "f:d:h:", ["frequency=", "deviation=", "harmonics="])
    except getopt.GetoptError as e:
        print e
        usage()

    for (opt, arg) in opts:
        if opt == "-f":
            desired_frequency = float(arg)
        elif opt == "-d":
            max_deviation = float(arg)
        elif opt == "-h":
            harmonics = []
            for h in arg.split(','):
                harmonics.append(int(h))

    if desired_frequency == 0.0:
        usage()

    search = CrystalFinder(desired_frequency, max_deviation, harmonics)
    search.find_divisors()
    search.find_sum_pairs()

