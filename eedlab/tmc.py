#!/usr/bin/env python

class USBTMC(object):
    """
    API to /dev/usbtmc devices
    """
    def __init__(self, dev):
        self.usbtmc = open(dev, "r+")

    def write(self, cmd):
        # usbtmc requires null terms
        if cmd[-1] != '\n':
            cmd +='\n'
        self.usbtmc.write(cmd)

    def ask(self, cmd):
        self.write(cmd)
        return self.usbtmc.readline().strip('\n')


