import logging
import serial
import time


class Rak811:
    __slots__ = ['port', '__logger']

    def __init__(self, port: serial.Serial):
        self.port = port
        self.__logger = logging.getLogger('rak811')

    def __encode_command(self, command: str, params=[]):
        line = 'at+%s' % command
        if len(params) > 0:
            line += "=%s" % ','.join(params)
        self.__logger.debug('sending command: %s' % line)
        line += '\r\n'
        return line.encode('ascii')

    def __read_command_result(self):
        line = self.port.readline()
        self.__logger.debug('result: %s' % line)

    def __read_recv(self):
        line = self.port.readline()
        self.__logger.debug('recv: %s' % line)

    def reset(self):
        self.__logger.debug('doing reset...')
        self.port.setDTR(1)
        time.sleep(1)
        self.port.setDTR(0)
        time.sleep(1)
        self.port.flushInput()

    def get_version(self):
        line = self.__encode_command('version')
        self.port.write(line)
        self.__read_command_result()

    def join(self, otaa=True):
        line = self.__encode_command('join', (['otaa'] if otaa else ['abp']))
        self.port.write(line)
        self.__read_command_result()
        self.__read_recv()

    def send(self, port, data: bytearray, confirmed=False):
        assert (1 <= port <= 223)
        line = self.__encode_command('send', [str(1 if confirmed else 0), str(port), data.hex()])
        self.port.write(line)
        self.__read_command_result()
        self.__read_recv()
