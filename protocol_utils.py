import struct
import zlib
import random
from config import PacketType, DEBUG_MODE, CORRUPTION_CHANCE

# Paket Formatı (Network byte order - Big Endian):
# ... (önceki yorumlar)
PACKET_FORMAT = "!BIIH"
HEADER_SIZE_STRUCT = struct.calcsize(PACKET_FORMAT)

def corrupt_data(data: bytes) -> bytes:
    """
    Veri içindeki rastgele bir baytı değiştirerek veriyi bozar (Bit-flip simulation).
    """
    if not data:
        return data
    
    data_list = list(data)
    # Rastgele bir index seç ve değerini değiştir (0-255 arası rastgele bir değerle XOR yap)
    idx = random.randint(0, len(data_list) - 1)
    data_list[idx] = data_list[idx] ^ 0xFF 
    return bytes(data_list)

def calculate_checksum(data: bytes) -> int:
# ...
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
