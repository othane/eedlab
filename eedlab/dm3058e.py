#!/usr/bin/env python
from tmc import USBTMC


class DM3058E(USBTMC):
    """
    Control the Rigol DM3058E Digital Multimeter from python
    """
    def __init__(self, dev):
        super(DM3058E, self).__init__(dev)
        self.write(':measure AUTO')

    @property
    def function(self):
        return self.ask(':function?')

    @function.setter
    def function(self, func):
        func_lut = {
            'DCV': 'function:voltage:DC',
            'ACV': 'function:voltage:AC',
            'DCI': 'function:current:DC',
            'ACI': 'function:current:AC',
            'RESISTANCE': 'function:resistance',
            'FRESISTANCE': 'function:fresistance',
            'FREQUENCY': 'function:frequency',
            'PERIOD': 'function:period',
            'CONTINUITY': 'function:continuity',
            'DIODE': 'function:diode',
            'CAPACITANCE': 'function:capacitance',
        }
        try:
            self.write(func_lut[func.upper()])
        except KeyError:
            raise KeyError('Unknown function type')
        return self.ask(':function?')

    @property
    def vdc(self):
        return float(self.ask(':measure:voltage:DC?'))

    @vdc.setter
    def vdc(self, cmd):
        cmd_lut = {
            'SLOW': ':rate:voltage:DC slow',
            'MEDIUM': ':rate:voltage:DC medium',
            'FAST': ':rate:voltage:DC fast',
            'MIN': ':measure:voltage:DC MIN',
            'MAX': ':measure:voltage:DC MAX',
            'DEF': ':measure:voltage:DC DEF',
            '0': ':measure:voltage:DC 0',
            '1': ':measure:voltage:DC 1',
            '2': ':measure:voltage:DC 2',
            '3': ':measure:voltage:DC 3',
            '4': ':measure:voltage:DC 4',
            round(0.2): ':measure:voltage:DC 0',
            round(2.0): ':measure:voltage:DC 1',
            round(20.0): ':measure:voltage:DC 2',
            round(200.0): ':measure:voltage:DC 3',
            round(1000.0): ':measure:voltage:DC 4',
        }
        try:
            try:
                cmd = round(cmd)
            except ValueError:
                pass
            self.write(cmd_lut[cmd])
        except KeyError:
            raise KeyError('Unknown voltage command')

    @property
    def vac(self):
        return float(self.ask(':measure:voltage:AC?'))

    @property
    def idc(self):
        return float(self.ask(':measure:current:DC?'))

    @property
    def iac(self):
        return float(self.ask(':measure:current:AC?'))

    @property
    def resistance(self):
        return float(self.ask(':measure:resistance?'))

    @property
    def resistance4(self):
        return float(self.ask(':measure:fresistance?'))

    @property
    def frequency(self):
        return float(self.ask(':measure:frequency?'))

    @property
    def period(self):
        return float(self.ask(':measure:period?'))

    @property
    def continuity(self):
        return float(self.ask(':measure:continuity?'))

    @property
    def diode(self):
        return float(self.ask(':measure:diode?'))

    @property
    def capacitance(self):
        return float(self.ask(':measure:capacitance?'))


