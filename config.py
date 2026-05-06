from enum import Enum, auto

# Protokol Sabitleri
HEADER_SIZE = 12
BUFFER_SIZE = 1024
PORT_A = 5000
PORT_B = 5001

# Retransmission Ayarları
TIMEOUT = 2.0
MAX_RETRIES = 3

# Debug ve Hata Simülasyonu
DEBUG_MODE = False
CORRUPTION_CHANCE = 0.3 # %30 ihtimalle paket bozulacak

class PacketType(Enum):
   
    SYN = auto()
    ACK = auto()
    DATA = auto()
    FIN = auto()
    ERROR = auto()
