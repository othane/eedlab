#!/usr/bin/env python
from vxi11 import Instrument


class DP832(Instrument):
    """
    Control the Rigol DP832 Digital Multimeter from python
    """

    def __init__(self, dev):
        super(DP832, self).__init__(dev)
        self.write(':measure AUTO')
        self.channels = [Channel(self, ch) for ch in range(3)]

    def __repr__(self):
        return self.idn()

    def idn(self):
        return self.ask('*IDN?')


class Channel(object):
    CH_MAP = {
        0: 'CH1',
        1: 'CH2',
        2: 'CH3',
    }

    def __init__(self, parent, ch):
        super(Channel, self).__init__()
        self.parent = parent
        self.ch = ch

    def ask(self, *args, **kwargs):
        return self.parent.ask(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.parent.write(*args, **kwargs)

    def __repr__(self):
        return str(self.CH_MAP[self.ch])

    @property
    def mode(self):
        return self.ask(':output:mode? {}'.format(self.CH_MAP[self.ch]))

    @property
    def all(self):
        res = self.ask(':measure:all:DC? {}'.format(self.CH_MAP[self.ch]))
        return {k: float(v) for k,v in zip(('voltage', 'current', 'power'), res.split(','))}

    @property
    def power(self):
        return float(self.ask(':measure:power:DC? {}'.format(self.CH_MAP[self.ch])))

    @property
    def vdc(self):
        vact = float(self.ask(':measure:voltage:DC? {}'.format(self.CH_MAP[self.ch])))
        vset = float(self.ask(':source{}:voltage?'.format(self.ch + 1)))
        vmin = float(self.ask(':source{}:voltage? min'.format(self.ch + 1)))
        vmax = float(self.ask(':source{}:voltage? max'.format(self.ch + 1)))
        return { 'act': vact, 'set': vset, 'min': vmin, 'max': vmax}

    @vdc.setter
    def vdc(self, vset):
        self.write(':source{}:volt {}'.format(self.ch + 1, vset))
        self.ask(':source{}:volt?'.format(self.ch + 1))  # this seems to change the value

    @property
    def idc(self):
        iact = float(self.ask(':measure:current:DC? {}'.format(self.CH_MAP[self.ch])))
        iset = float(self.ask(':source{}:current?'.format(self.ch + 1)))
        imin = float(self.ask(':source{}:current? min'.format(self.ch + 1)))
        imax = float(self.ask(':source{}:current? max'.format(self.ch + 1)))
        return { 'act': iact, 'set': iset, 'min': imin, 'max': imax}

    @idc.setter
    def idc(self, iset):
        self.write(':source{}:current {}'.format(self.ch + 1, iset))
        self.ask(':source{}:current?'.format(self.ch + 1))    # this seems to change the value

    @property
    def state(self):
        return self.ask(':output:state? {}'.format(self.CH_MAP[self.ch]))

    @state.setter
    def state(self, state):
        self.write(':output:state {},{}'.format(self.CH_MAP[self.ch], state))
        self.state  # this seems to turn it on/off ?

    def on(self):
        self.state = 'ON'

    def off(self):
        self.state = 'OFF'

