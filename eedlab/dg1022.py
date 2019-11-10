#!/usr/bin/env python
from universal_usbtmc import import_backend, UsbtmcError
from sys import platform
try:
    from types import StringTypes
except ImportError:
    StringTypes = (str,)
from collections import Iterable

from time import sleep


class DG1022(object):
    """
    Control the Rigol DM3058E Digital Multimeter from python
    """
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
            except Exception as e:
                # I hate this generic error handling too, but the many backends
                # can throw so many different exception types its just easier
                # to try and if anything goes wrong then try the next backend
                print('Exceptional {}'.format(e))
                pass
        else:
            raise UsbtmcError('no matching backends in {} connected using {}'.format(','.join(backends), dev))

        self.channels = [DG1022Channel(ch + 1, self) for ch in range(2)]

    def ask(self, *args, **kwargs):
        ret = self.instr.query(*args, **kwargs)
        return ret

    def write(self, *args, **kwargs):
        return self.instr.write(*args, **kwargs)

    def __repr__(self):
        return self.idn()

    def idn(self):
        return self.ask('*IDN?')

    @property
    def unit(self):
        return self.ask('VOLTAGE:UNIT?')

    @unit.setter
    def unit(self, unit):
        return self.write('VOLTAGE:UNIT {}'.format(unit))

    def phase_align(self):
        self.write('PHASE:ALIGN')

    def trigger(self, trig_type=None):
        """ from manual trig_type can be {IMMediate|EXTernal|BUS} """
        trig_type = trig_type or 'BUS'
        self.write('TRIGGER:SOURCE {}'.format(trig_type))

    @property
    def burst_mode(self):
        return self.ask('BURST:MODE?')

    @burst_mode.setter
    def burst_mode(self, trig_type):
        self.write('BURST:MODE {}'.format(trig_type))

    @property
    def burst_cycles(self):
        res = self.ask('BURST:NCYCLES?')
        if res == 'Infinite':
            return float('inf')
        else:
            return float(res)

    @burst_cycles.setter
    def burst_cycles(self, cycles):
        self.write('BURST:NCYCLES {}'.format(cycles))

    @property
    def burst_period(self):
        return float(self.ask('BURST:INTERNAL:PERIOD?'))

    @burst_period.setter
    def burst_period(self, period):
        self.write('BURST:INTERNAL:PERIOD{}'.format(period))

    @property
    def burst_phase(self):
        return float(self.ask('BURST:PHASE?'))

    @burst_phase.setter
    def burst_phase(self, phase):
        self.write('BURST:PHASE{}'.format(phase))

    @property
    def burst(self):
        res = self.ask('BURST:STATE?')
        return 'ON' in res.upper()

    @burst.setter
    def burst(self, state):
        if type(state) == bool:
            state = 'ON' if state else 'OFF'
        self.write('BURST:STATE {}'.format(state))


class DG1022Channel(object):

    def __init__(self, ch, parent):
        self.ch = ch
        self.parent = parent

    def ask(self, message, num=-1, encoding='utf-8'):
        """ pass though for ch1, else append CH otherwise """
        if self.ch != 1: 
            msg = message.split('?')
            msg.insert(-1, ':CH{}?'.format(self.ch))
            message = ''.join(msg)
        res = self.parent.ask(message, num=num, encoding=encoding)
        if self.ch != 1:
            res = res.replace('CH{}:'.format(self.ch), '')
        return res

    def write(self, message, encoding='utf-8'):
        """ pass though for ch1, else append CH otherwise """
        if self.ch != 1: 
            msg = message.split(' ')
            msg.insert(-1, ':CH{} '.format(self.ch))
            message = ''.join(msg)
        return self.parent.write(message, encoding=encoding)

    def __repr__(self):
        return '{} CHANNEL {}'.format(self.parent, self.ch)

    def apply(self, function=None, frequency=None, amplitude=None, offset=None):
        return self.write('APPLY:{} {},{},{}'.format(function or '', frequency or '', amplitude or '', offset or ''))

    @property
    def phase(self):
        return float(self.ask('PHASE?'))

    @phase.setter
    def phase(self, phs):
        self.write('PHASE {}'.format(phs))

    @property
    def function(self):
        return self.ask('FUNCTION?')

    @function.setter
    def function(self, function):
        return self.write('FUNCTION {}'.format(function))

    @property
    def duty(self):
        """ return the duty cycle of the square wave function """
        return float(self.ask('FUNCTION:SQUARE:DCYCLE?'))

    @duty.setter
    def duty(self, percent):
        """ set the duty cycle of the square wave function """
        self.write('FUNCTION:SQUARE:DCYCLE {}'.format(percent))

    @property
    def sym(self):
        """ return the symmetry of the ramp function """
        return float(self.ask('FUNCTION:RAMP:SYMM?'))

    @sym.setter
    def sym(self, percent):
        """ set the symmetry of the ramp function """
        self.write('FUNCTION:RAMP:SYMM {}'.format(percent))

    @property
    def frequency(self):
        return float(self.ask('FREQUENCY?'))

    @frequency.setter
    def frequency(self, freq):
        self.write('FREQUENCY {}'.format(freq))

    @property
    def amplitude(self):
        return float(self.ask('VOLTAGE?'))

    @amplitude.setter
    def amplitude(self, amp):
        self.write('VOLTAGE {}'.format(amp))

    @property
    def vdc(self):
        return self.ask('VOLTAGE:OFFSET?')

    @vdc.setter
    def vdc(self, vdc):
        self.write('VOLTAGE:OFFSET {}'.format(vdc))

    @property
    def vhigh(self):
        return self.ask('VOLTAGE:HIGH?')

    @vhigh.setter
    def vhigh(self, vhigh):
        self.write('VOLTAGE:HIGH {}'.format(vhigh))

    @property
    def vlow(self):
        return self.ask('VOLTAGE:LOW?')

    @vlow.setter
    def vlow(self, vlow):
        self.write('VOLTAGE:LOW {}'.format(vlow))

    @property
    def output(self):
        state = self.ask('OUTPUT?')
        if state.lower() == 'off':
            return False
        else:
            return True

    @output.setter
    def output(self, state):
        if type(state) != str:
            state = 'ON' if state else 'OFF'
        self.write('OUTPUT {}'.format(state))

    def on(self):
        self.output = True

    def off(self):
        self.output = False

    @property
    def load(self):
        return self.ask('OUTPUT:LOAD?')

    @load.setter
    def load(self, load):
        return self.write('OUTPUT:LOAD {}'.format(load))


class DG1022Channel2(object):

    def __init__(self, parent):
        self.parent = parent

    def __repr__(self):
        return '{} CHANNEL 2'.format(self.parent)

    def apply(self, function='DEFAULT', amplitude='DEFAULT', offset='DEFAULT'):
        return self.write('APPLY:{}:CH2 {},{},{}'.format(function, frequency, amplitude, offset))

    @property
    def phase(self):
        return float(self.ask('PHASE:CH2?'))

    @phase.setter
    def phase(self, phs):
        self.write('PHASE:CH2 {}'.format(phs))

    @property
    def function(self):
        return self.ask('FUNCTION:CH2?')

    @function.setter
    def function(self, function):
        self.write('FUNCTION:CH2 {}'.format(function))

    @property
    def duty(self):
        """ return the duty cycle of the square wave function """
        return float(self.ask('FUNCTION:SQUARE:DCYCLE:CH2?'))

    @duty.setter
    def duty(self, percent):
        """ set the duty cycle of the square wave function """
        self.write('FUNCTION:SQUARE:DCYCLE:CH2 {}'.format(percent))

    @property
    def sym(self):
        """ return the symmetry of the ramp function """
        return float(self.ask('FUNCTION:RAMP:SYMM:CH2?'))

    @sym.setter
    def sym(self, percent):
        """ set the symmetry of the ramp function """
        self.write('FUNCTION:RAMP:SYMM:CH2 {}'.format(percent))

    @property
    def frequency(self):
        return float(self.ask('FREQUENCY:CH2?'))

    @frequency.setter
    def frequency(self, freq):
        self.write('FREQUENCY:CH2 {}'.format(freq))

    @property
    def amplitude(self):
        return float(self.ask('VOLTAGE:CH2?'))

    @amplitude.setter
    def amplitude(self, freq):
        self.write('VOLTAGE:CH2 {}'.format(freq))

    @property
    def output(self):
        state = self.ask('OUTPUT:CH2?')
        if state.lower() == 'off':
            return False
        else:
            return True

    @output.setter
    def output(self, state):
        if type(state) != str:
            state = 'ON' if state else 'OFF'
        self.write('OUTPUT:CH2 {}'.format(state))

    def on(self):
        self.output = True

    def off(self):
        self.output = False

    @property
    def load(self):
        return self.ask('OUTPUT:LOAD:CH2?')

    @load.setter
    def load(self, load):
        return self.write('OUTPUT:LOAD:CH2 {}'.format(load))

