#!/usr/bin/env python
from usbtmc import Instrument
from time import sleep


class DG1022(Instrument):
    """
    Control the Rigol DM3058E Digital Multimeter from python
    """
    def __init__(self, dev):
        super(DG1022, self).__init__(dev)
        self.channels = [DG1022Channel(ch + 1, self) for ch in range(2)]

    def ask(self, message, num=-1, encoding='utf-8'):
        """ override Instrument ask since ask is broken on the DG1022, it needs a little sleep :( """
        self.write(message, encoding=encoding)
        sleep(0.1)
        return self.read(num=num, encoding=encoding)

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
        return self.parent.ask(message, num=num, encoding=encoding)

    def write(self, message, encoding='utf-8'):
        """ pass though for ch1, else append CH otherwise """
        if self.ch != 1: 
            msg = message.split(' ')
            msg.insert(-1, ':CH{} '.format(self.ch))
            message = ''.join(msg)
        return self.parent.write(message, encoding=encoding)

    def __repr__(self):
        return '{} CHANNEL 1'.format(self.parent)

    def apply(self, function='DEFAULT', amplitude='DEFAULT', offset='DEFAULT'):
        return self.write('APPLY:{} {},{},{}'.format(function, frequency, amplitude, offset))

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

