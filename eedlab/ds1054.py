from vxi11 import Instrument
from universal_usbtmc import import_backend, UsbtmcError
from sys import platform
try:
    from types import StringTypes
except ImportError:
    StringTypes = (str,)
from collections import Iterable
import logging


class DS1054(Instrument):

    def __init__(self, dev, backends=None):
        if backends is None:
            backends = ['python_vxi11', 'python_usbtmc']
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
                pass
        else:
            raise UsbtmcError('no matching backends in {} connected using {}'.format(','.join(backends), dev))

        self.channels = [DS1054Channel(ch + 1, self) for ch in range(4)]

    @property
    def dev(self):
        return self._dev_

    def ask(self, *args, **kwargs):
        return self.instr.query(*args, **kwargs).replace('\n', '')

    def ask_raw(self, *args, **kwargs):
        return self.instr.query_raw(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.instr.write(*args, **kwargs)

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
        return self.write('TRIGGER:MODE {}'.format(ttype))

    @property
    def trigger_edge_slope(self):
        return {
            'set': self.ask('TRIGGER:EDGE:SLOPE?'),
            'options': ['POSitive', 'NEGative', 'rising', 'falling']
        }

    @trigger_edge_slope.setter
    def trigger_edge_slope(self, slope):
        if slope == 'rising':
            slope = 'positive'
        elif slope == 'falling':
            slope = 'negative'
        return self.write('TRIGGER:EDGE:SLOPE {}'.format(slope))

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

    @property
    def measure_threshold_low(self):
        return float(self.ask('measure:setup:min?'))

    @measure_threshold_low.setter
    def measure_threshold_low(self, low):
        return self.write('measure:setup:min {}'.format(low))

    @property
    def measure_threshold_mid(self):
        return float(self.ask('measure:setup:mid?'))

    @measure_threshold_mid.setter
    def measure_threshold_mid(self, mid):
        return self.write('measure:setup:mid {}'.format(mid))

    @property
    def measure_threshold_high(self):
        return float(self.ask('measure:setup:max?'))

    @measure_threshold_high.setter
    def measure_threshold_high(self, high):
        return self.write('measure:setup:max {}'.format(high))

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
    def stats_mode(self):
        return self.ask(':measure:statistic:mode?')

    @stats_mode.setter
    def stats_mode(self, mode):
        return self.write(':measure:statistic:mode {}'.format(mode))

    def stat_on(self, item, ch=None):
        if ch is None:
            ch = ''
        elif isinstance(ch, list) or isinstance(ch, tuple):
            ch = ','.join(ch)
        self.write(':measure:statistic:item {},{}'.format(item, ch))

    def stat(self, item, type='averages', ch=None):
        return self.ask(':measure:statistic:item? {},{}'.format(type, item))

    def stats_reset(self):
        self.write(':measure:statistic:reset')

    @property
    def sample_rate(self):
        return float(self.ask(':waveform:xincrement?'))

    @property
    def timebase(self):
        return float(self.ask(':timebase:main:scale?'))

    @timebase.setter
    def timebase(self, scale):
        self.write(':timebase:main:scale {}'.format(scale))

    @property
    def timebase_offset(self):
        return float(self.ask(':timebase:main:offset?'))

    @timebase_offset.setter
    def timebase_offset(self, offset):
        self.write(':timebase:main:offset {}'.format(offset))

    @property
    def averages(self):
        return float(self.ask(':acquire:averages?'))

    @averages.setter
    def averages(self, avgs):
        self.write(':acquire:averages {}'.format(avgs))

    @property
    def acquire_type(self):
        return {
            'set':self.ask(':acquire:type?'),
            'options': ['NORMal', 'AVERages', 'PEAK', 'HRESolution'],
        }

    @acquire_type.setter
    def acquire_type(self, atype):
        self.write(':acquire:type {}'.format(atype))

    @property
    def mem_depth(self):
        return int(self.ask(':acquire:mdepth?'))

    @mem_depth.setter
    def mem_depth(self, mdepth):
        return self.write(':acquire:mdepth {}'.format(int(mdepth)))

    @property
    def x_origin(self):
        return float(self.ask(':wav:xorigin?'))

    @property
    def x_reference(self):
        return float(self.ask(':wav:xreference?'))

    @property
    def x_increment(self):
        return float(self.ask(':wav:xincrement?'))

    @property
    def y_origin(self):
        return float(self.ask(':wav:yorigin?'))

    @property
    def y_reference(self):
        return float(self.ask(':wav:yreference?'))

    @property
    def y_increment(self):
        return float(self.ask(':wav:yincrement?'))

    def get_trace(self, chan=None, batch=False):
        # ensure we are in ascii mode as we only support this mode need this mode
        if chan:
             self.write('WAV:SOURCE CHAN{}'.format(chan))

        if not batch:
            self.write('WAV:MODE NORMAL')
            self.write('WAV:FORMAT ASCII')
            trace = self.ask('WAV:DATA?').split(',')[1:]  # the manual is not clear what the first value is 
            return [float(t) for t in trace], scope.sample_rate
        else:
            self.write('WAV:MODE MAX')
            self.write('WAV:FORMAT BYTE')
            y_origin = self.y_origin
            max_pts = 250000
            self.stop()
            mem_depth = self.mem_depth
            trace = []
            for m in range(1, mem_depth, max_pts):
                self.write('WAV:START {}'.format(m))
                remaining = mem_depth - len(trace)
                if remaining < max_pts:
                    self.write('WAV:STOP {}'.format(m + remaining - 1))
                else:
                    self.write('WAV:STOP {}'.format(m + max_pts - 1))
                data = self.ask_raw('WAV:DATA?', num=max_pts + 256)
                y_origin = self.y_origin
                y_reference = self.y_reference
                y_increment = self.y_increment
                trace += [(y - y_origin - y_reference) * y_increment
                            for y in bytearray(data)[12:]]
                remaining -= len(data[12:])
            ts = self.sample_rate
            self.run()
            return trace, ts

    def auto(self, wait=True):
        self.write(':AUTOSCALE')
        if wait:
            while not self.opc:
                sleep(0.1)

    def vauto(self):
        """ auto the vertical scale """
        # save our horizontal and trigger settings to restore later
        timebase = self.timebase
        trigger_type = self.trigger_type
        trigger_mode = self.trigger_mode
        # auto scale the whole scope
        self.auto()
        # restore the timebase and triggers so just the vertical is auto
        # scaled
        self.timebase = timebase
        self.trigger_type = trigger_type
        self.trigger_mode = trigger_mode


class DS1054Channel(object):

    def __init__(self, ch, parent):
        self.ch = ch
        self.parent = parent

    @property
    def scale(self):
        return float(self.parent.ask(':channel{}:scale?'.format(self.ch)))

    @scale.setter
    def scale(self, s):
        return self.parent.write(':channel{}:scale {}'.format(self.ch, s))

    @property
    def bandwidth(self):
        return {
            'set': self.parent.ask(':channel{}:bwlimit?'.format(self.ch)),
            'options': ['OFF', '20M'],
        }

    @bandwidth.setter
    def bandwidth(self, bw):
        return self.parent.write(':channel{}:bwlimit {}'.format(self.ch, bw))

    def measure(self, item):
        return self.parent.measure(item, 'CHAN{}'.format(self.ch))

