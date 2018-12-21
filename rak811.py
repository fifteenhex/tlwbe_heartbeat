import logging
import serial
import time
import re


class CommandException(Exception):
    pass


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

    def __read_line(self):
        return self.port.readline().decode('ascii')

    def __read_command_result(self, line=None):
        if line is None:
            line = self.__read_line()
        self.__logger.debug('result: %s' % line)
        matches = re.search('OK', line)
        if matches is None:
            matches = re.search('ERROR', line)
            assert matches is not None
            self.__logger.debug('command resulted in an error')
            raise CommandException()

    def __read_recv(self, line=None):
        if line is None:
            line = self.__read_line()
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

    def get_band(self):
        line = self.__encode_command('band')
        self.port.write(line)
        self.__read_command_result()

    def get_channel_list(self):
        line = self.__encode_command('get_config', ['ch_list'])
        self.port.write(line)
        self.__read_command_result()

    def get_signal(self):
        line = self.__encode_command('signal')
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

        # there seems to be a firmware bug that causes
        # the OK to come after the at+recv sometimes
        # so read both lines and reorder them if needed
        lines = [self.__read_line(), self.__read_line()]
        if lines[0].startswith("at+recv"):
            recvline = lines.pop(0)
            lines.append(recvline)

        self.__read_command_result(lines[0])
        self.__read_recv(lines[1])
