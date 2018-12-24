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
        line = self.port.read_until(b'\r\n').decode('ascii')
        if len(line) == 0:
            return None
        line = line[:-2]
        self.__logger.debug('read line: %s' % line)
        return line

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

    def __write_line_read_result(self, out_line):
        self.port.write(out_line)
        return self.__read_command_result()

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
        self.__write_line_read_result(line)

    def get_band(self):
        line = self.__encode_command('band')
        self.__write_line_read_result(line)

    def get_class(self):
        line = self.__encode_command('class')
        self.__write_line_read_result(line)

    def get_channel_list(self):
        line = self.__encode_command('get_config', ['ch_list'])
        self.__write_line_read_result(line)

    def get_signal(self):
        line = self.__encode_command('signal')
        self.__write_line_read_result(line)

    def join(self, otaa=True):
        line = self.__encode_command('join', (['otaa'] if otaa else ['abp']))
        self.port.write(line)
        self.__read_command_result()
        self.__read_recv()

    def send(self, port, data: bytearray, confirmed=False):
        assert (1 <= port <= 223)
        line = self.__encode_command('send', [str(1 if confirmed else 0), str(port), data.hex()])
        self.port.write(line)

        # We should get 2 or 3 lines back here
        lines = []
        while len(lines) < 3:
            in_line = self.__read_line()
            if in_line is None:
                break
            lines.append(in_line)

        self.__logger.debug(",".join(lines))

        self.__read_command_result(lines[0])
        for recv_line in lines[1:]:
            self.__read_recv(recv_line)
