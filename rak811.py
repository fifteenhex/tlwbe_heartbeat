class Rak811:
    __slots__ = ['port']

    def __init__(self, port):
        self.port = port

    @staticmethod
    def __encode_command(command: str, params=[]):
        line = 'at+%s' % command
        if len(params) > 0:
            line += "=%s" % ','.join(params)
        print(line)
        line += '\r\n'
        return line.encode('ascii')

    def get_version(self):
        line = self.__encode_command('version')
        self.port.write(line)
        line = self.port.readline()
        print(line)

    def join(self, otaa=True):
        line = self.__encode_command('join', (['otaa'] if otaa else ['abp']))
        self.port.write(line)
        line = self.port.readline()
        print(line)
        line = self.port.readline()
        print(line)

    def send(self, port, data: bytearray, confirmed=False):
        assert (1 <= port <= 223)
        line = self.__encode_command('send', [str(1 if confirmed else 0), str(port), data.hex()])
        self.port.write(line)
        line = self.port.readline()
        print(line)
        line = self.port.readline()
        print(line)
