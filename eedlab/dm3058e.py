#!/usr/bin/env python
from universal_usbtmc import import_backend, UsbtmcError
from sys import platform


class DM3058E(object):
    """
    Control the Rigol DM3058E Digital Multimeter from python
    """
    def __init__(self, dev):
        super(DM3058E, self).__init__(dev)
    def __init__(self, dev, backends=None):
        if backends is None:
            backends = ['python_usbtmc']
            if "linux" in platform:
                # this is a way better api to use than python_usbtmc, but but it only works on linux
                backends.insert(0, 'linux_kernel')
        elif not isinstance(backends, Iterable) or isinstance(backends, StringTypes):
            backends = [backends]
        self.__backends__ = backends

        for be_name in backends:
            try:
                be = import_backend(be_name)
                instr = be.Instrument(dev)
                idn = instr.query('*IDN?')
                self.instr = instr
                self.backend = be
                self.backend_name = be_name
                break
            except Exception:
                # I hate this generic error handling too, but the many backends
                # can throw so many different exception types its just easier
                # to try and if anything goes wrong then try the next backend
                pass
        else:
            raise UsbtmcError('no matching backends in {} connected using {}'.format(','.join(backends), dev))
        self.write(':measure AUTO')


    FUNC_LUT = {
        'VDC': 'function:voltage:DC',
        'VAC': 'function:voltage:AC',
        'IDC': 'function:current:DC',
        'IAC': 'function:current:AC',
        'RESISTANCE': 'function:resistance',
        'FRESISTANCE': 'function:fresistance',
        'FREQUENCY': 'function:frequency',
        'PERIOD': 'function:period',
        'CONTINUITY': 'function:continuity',
        'DIODE': 'function:diode',
        'CAPACITANCE': 'function:capacitance',
    }

    def ask(self, *args, **kwargs):
        res = self.instr.query(*args, **kwargs).split()
        if res[0][0] == '#':
            return ' '.join(res[1::])
        return ' '.join(res)

    def write(self, *args, **kwargs):
        return self.instr.write(*args, **kwargs)

    def __repr__(self):
        return self.idn()

    def idn(self):
        return self.ask('*IDN?')

    @property
    def function(self):
        return {'set':self.ask(':function?'), 'options': self.FUNC_LUT.keys()}

    @function.setter
    def function(self, func):
        try:
            self.write(self.FUNC_LUT[func.upper()])
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
            except (ValueError,TypeError):
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


