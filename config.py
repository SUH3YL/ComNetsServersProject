from enum import Enum, auto

# Protokol Sabitleri
HEADER_SIZE = 12
BUFFER_SIZE = 1024
PORT_A = 5000
PORT_B = 5001

class PacketType(Enum):
   
    SYN = auto()
    ACK = auto()
    DATA = auto()
    FIN = auto()
    ERROR = auto()
