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

    def __repr__(self):
        return self.idn()

    def get_trace(self, chan=None):
        # ensure we are in ascii mode as we only support this mode need this mode
        self.write('WAV:FORMAT ASCII')
        if chan:
             self.write('WAV:SOURCE CHAN{}'.format(chan))
        trace = self.ask('WAV:DATA?').split(',')[1:]  # the manual is not clear what the first value is 
        return [float(t) for t in trace]

