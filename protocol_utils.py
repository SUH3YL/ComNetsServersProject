import struct
import zlib
from config import PacketType

# Paket Formatı (Network byte order - Big Endian):
# ! - Big Endian
# B - Packet Type (1 byte, unsigned char)
# I - Sequence Number (4 bytes, unsigned int)
# I - Checksum (4 bytes, unsigned int)
# H - Payload Length (2 bytes, unsigned short)
# Toplam Header Boyutu: 1 + 4 + 4 + 2 = 11 byte. 
# Not: Kullanıcı config.py'de HEADER_SIZE=12 istemişti, bu yüzden 1 byte padding veya 
# doğrudan 11 byte üzerinden devam edilebilir. İstek doğrultusunda 11 byte header + payload kullanacağız.
PACKET_FORMAT = "!BIIH"
HEADER_SIZE_STRUCT = struct.calcsize(PACKET_FORMAT)

def calculate_checksum(data: bytes) -> int:
    """
    Verilen bayt verisi için CRC32 checksum hesaplar.
    """
    return zlib.crc32(data) & 0xFFFFFFFF

def pack_packet(packet_type: PacketType, seq_num: int, payload: bytes) -> bytes:
    """
    Verileri belirtilen formata göre paketler.
    """
    payload_len = len(payload)
    # Checksum hesaplanırken paket tipi, sıra numarası ve payload dahil edilir.
    # Önce geçici bir checksumsız paket oluşturup checksum hesaplıyoruz.
    temp_header = struct.pack("!B I H", packet_type.value, seq_num, payload_len)
    checksum = calculate_checksum(temp_header + payload)
    
    # Gerçek paketleme
    return struct.pack(PACKET_FORMAT, packet_type.value, seq_num, checksum, payload_len) + payload

def unpack_packet(data: bytes):
    """
    Alınan bayt verisini ayrıştırır ve checksum kontrolü yapar.
    """
    if len(data) < HEADER_SIZE_STRUCT:
        raise ValueError("Paket boyutu header için yetersiz.")
    
    header_data = data[:HEADER_SIZE_STRUCT]
    payload = data[HEADER_SIZE_STRUCT:]
    
    packet_type_val, seq_num, received_checksum, payload_len = struct.unpack(PACKET_FORMAT, header_data)
    
    # Checksum doğrulaması
    # Doğrulama için header'ın checksumsız kısmını ve payload'u kullanıyoruz.
    check_header = struct.pack("!B I H", packet_type_val, seq_num, payload_len)
    calculated_checksum = calculate_checksum(check_header + payload)
    
    if received_checksum != calculated_checksum:
        raise ValueError(f"Checksum hatası! Beklenen: {calculated_checksum}, Alınan: {received_checksum}")
    
    return PacketType(packet_type_val), seq_num, payload
