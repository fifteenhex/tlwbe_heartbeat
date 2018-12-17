MHDR_MTYPE_SHIFT = 5
MHDR_MTYPE_MASK = 0b111
MHDR_MTYPE_JOINREQ = 0b000
MHDR_MTYPE_JOINACK = 0b001
MHDR_MTYPE_UNCNFUP = 0b010
MHDR_MTYPE_UNCNFDN = 0b011
MHDR_MTYPE_CNFUP = 0b100
MHDR_MTYPE_CNFDN = 0b101


def get_packet_type(raw_packet: bytearray):
    mhdr = raw_packet[0]
    return (mhdr >> MHDR_MTYPE_SHIFT) & MHDR_MTYPE_MASK


class Packet:
    __slots__ = ['type']

    def __init__(self, raw_packet: bytearray):
        self.type = get_packet_type(raw_packet)


class Join(Packet):
    __slots__ = ['deveui']

    def __init__(self, raw_packet: bytearray):
        super(Join, self).__init__(raw_packet)


class Uplink(Packet):
    __slots__ = ['devaddr']

    def __init__(self, raw_packet: bytearray):
        super(Uplink, self).__init__(raw_packet)
