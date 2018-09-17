from vxi11 import Instrument
import logging


class DS1054(Instrument):

    def __init__(self, ip):
        self._ip_ = ip
        self._instr_ = Instrument(self.ip)

    @property
    def ip(self):
        return self._ip_

    def ask(self, msg, n=None):
        if msg.find('?') > 0:
            logging.debug("asking {}".format(msg))
            return self._instr_.ask(msg, n)
        else:
            return self.write(msg)

    def write(self, msg):
        if msg.find('?') > 0:
            return self.ask(msg)
        else:
            logging.debug("writing {}".format(msg))
            res = self._instr_.write(msg)
            esr = int(self._instr_.ask("*ESR?"))
            if esr != 0:
                raise IOError('*ESR failed after write of "{}"'.format(msg))

    def idn(self):
        return self.ask('*IDN?')

    def opc(self):
        return self.ask('*OPC?')

    def __repr__(self):
        return self.idn()

    def clear(self):
        self.write(':CLEAR')

    def run(self):
        self.write(':RUN')

    def stop(self):
        self.write(':STOP')

    def single(self):
        self.write(':SINGLE')

    def force(self):
        self.write(':TFORCE')

    @property
    def trigger_status(self):
        return self.ask('TRIGGER:STATUS?')

    @property
    def trigger_mode(self):
        return self.ask('TRIGGER:SWEEP?')

    @trigger_mode.setter
    def trigger_mode(self, mode):
        self.write('TRIGGER:SWEEP {}'.format(mode))

    @property
    def trigger_type(self):
        return self.ask('TRIGGER:MODE?')

    @trigger_type.setter
    def trigger_type(self, ttype):
        return self.ask('TRIGGER:MODE {}'.format(ttype))

    @property
    def trigger_level(self):
        ttype = self.trigger_type
        return float(self.ask('TRIGGER:{}:LEVEL?'.format(ttype)))

    @trigger_level.setter
    def trigger_level(self, level):
        ttype = self.trigger_type
        self.write('TRIGGER:{}:LEVEL {}'.format(ttype, level))

    @property
    def measure_source(self):
        return self.ask('measure:source?')

    @measure_source.setter
    def measure_source(self, source):
        return self.write('measure:source {}'.format(source))

    def measure(self, item, srcs):
        if type(srcs) == str:
            srcs = [srcs]
        elif type(srcs) != list:
            srcs = list(srcs)
        res = self.ask('measure:item? {},{}'.format(item, ','.join(srcs)))
        try:
            return float(res)
        except (ValueError, TypeError) as e:
            return res

    @property
    def sample_rate(self):
        return float(self.ask(':waveform:xincrement?'))

    @property
    def timebase(self):
        return float(self.ask(':timebase:main:scale?'))

    @timebase.setter
    def timebase(self, scale):
        self.ask(':timebase:main:scale {}'.format(scale))

    def get_trace(self, chan=None):
        # ensure we are in ascii mode as we only support this mode need this mode
        self.write('WAV:FORMAT ASCII')
        if chan:
             self.write('WAV:SOURCE CHAN{}'.format(chan))
        trace = self.ask('WAV:DATA?').split(',')[1:]  # the manual is not clear what the first value is 
        return [float(t) for t in trace]

