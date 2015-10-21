#!/usr/bin/env python
# Searches Digikey for crystals or crystal combinations that will achieve a
# desired frequency within the specified error range.

import sys
import urllib2

class Crystal(object):

    def __init__(self, fundamental=0.0, overtone=1):
        self.overtone = overtone
        self.fundamental = fundamental
        self.frequency = self.fundamental * self.overtone

class CrystalMatch(object):
    def __init__(self, crystals, operator=""):
        self.crystals = crystals
        self.operator = operator

class CrystalFinder(object):
    def __init__(self, desired_frequency, max_deviation):
        self.desired_frequency = desired_frequency
        self.max_deviation = max_deviation
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
                        freq = float(frequency.split('kHz')[0])
                    elif 'kHZ' in frequency:
                        freq = float(frequency.split('kHZ')[0])
                    elif 'KHz' in frequency:
                        freq = float(frequency.split('KHz')[0])
                    else:
                        raise Exception("Unknown frequency option: '%s'" % frequency)

                    frequencies.append(freq)
        except Exception as e:
            raise e

        return frequencies

    def list_available_crystals(self):
        crystals = {}

        for crystal in self.digikey_crystals() + self.mouser_crystals():
            for i in [1, 3, 5]:
                xtal = Crystal(crystal, i)
                if not crystals.has_key(xtal.frequency):
                    crystals[xtal.frequency] = xtal

        return crystals

    def deviation_ok(self, freq):
        low = self.desired_frequency - freq
        high = freq - self.desired_frequency

        return (low >= 0 and low <= self.max_deviation) or (high >= 0 and high <= self.max_deviation)

    def find_divisors(self, crystals=None):
        if not crystals:
            crystals = self.crystals

        for crystal in crystals.values():
            for i in [1, 2, 4, 8]:
                div_freq = crystal.frequency / i
                if self.deviation_ok(div_freq):
                    print "%f / %d = %f; use %f (%d overtone)" % (crystal.frequency, i, div_freq, crystal.fundamental, crystal.overtone)

    def find_sum_pairs(self, crystals=None):
        done_sum_pairs = []
        done_min_pairs = []

        if not crystals:
            crystals = self.crystals

        for crystal in crystals.keys():
            f1 = crystal
            for f2 in crystals.keys():
                f_plus = f1 + f2
                if self.deviation_ok(f_plus) and (f1, f2) not in done_sum_pairs:
                    done_sum_pairs.append((f1, f2))
                    done_sum_pairs.append((f2, f1))
                    print "%f + %f = %f; use %f (%d overtone) and %f (%d overtone)" % (f1,
                                                                                       f2,
                                                                                       f_plus,
                                                                                       self.crystals[f1].fundamental,
                                                                                       self.crystals[f1].overtone,
                                                                                       self.crystals[f2].fundamental,
                                                                                       self.crystals[f2].overtone)

                if f1 > f2:
                    f_minus = f1 - f2
                    big = f1
                    little = f2
                else:
                    f_minus = f2 - f1
                    big = f2
                    little = f1
                if self.deviation_ok(f_minus) and (big, little) not in done_min_pairs:
                    done_min_pairs.append((big, little))
                    print "%f - %f = %f; use %f (%d overtone) and %f (%d overtone)" % (big,
                                                                                       little,
                                                                                       f_minus,
                                                                                       self.crystals[big].fundamental,
                                                                                       self.crystals[big].overtone,
                                                                                       self.crystals[little].fundamental,
                                                                                       self.crystals[little].overtone)

def usage():
    print "Usage: %s <frequency, in MHz> [max deviation, in MHz]" % sys.argv[0]
    sys.exit(1)

try:
    desired_frequency = float(sys.argv[1])
except Exception:
    usage()
try:
    max_deviation = float(sys.argv[2])
except IndexError:
    max_deviation = 0.0
except Exception:
    usage()

search = CrystalFinder(desired_frequency, max_deviation)
search.find_divisors()
search.find_sum_pairs()

