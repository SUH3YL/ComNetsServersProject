import streamlit as st
import time
from node import Node, NodeState
from config import PORT_A, PORT_B, PacketType
import threading

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Custom Protocol Monitor", layout="wide")

st.title("🌐 Custom Network Protocol Monitor")

# Sidebar: Ayarlar
st.sidebar.header("Sunucu Ayarları")
my_ip = st.sidebar.text_input("Kendi IP", "127.0.0.1")
my_port = st.sidebar.number_input("Kendi Port", value=PORT_A)
target_ip = st.sidebar.text_input("Hedef IP", "127.0.0.1")
target_port = st.sidebar.number_input("Hedef Port", value=PORT_B)

is_initiator = st.sidebar.checkbox("Bağlantıyı Ben Başlatayım (SYN Gönder)", value=False)
debug_mode = st.sidebar.toggle("Hata Modu (Corrupt Packets)", value=False)

if 'node' not in st.session_state:
    st.session_state.node = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def start_node():
    try:
        node = Node(my_ip, my_port, target_ip, target_port)
        node.debug_mode = debug_mode
        st.session_state.node = node
        
        # Bağlantı kurma işlemini ayrı bir thread'de yapalım ki UI donmasın
        def connect():
            try:
                node.establish_connection(is_initiator=is_initiator)
                if node.state == NodeState.ESTABLISHED:
                    node.start_receive_thread()
            except Exception as e:
                node.log(f"Bağlantı hatası: {e}", "red")
        
        threading.Thread(target=connect, daemon=True).start()
        st.sidebar.success(f"Node başlatıldı: {my_port}")
    except Exception as e:
        st.sidebar.error(f"Başlatma hatası: {e}")

if st.sidebar.button("🔌 Bağlantıyı Başlat"):
    start_node()

if st.sidebar.button("🛑 Bağlantıyı Kes"):
    if st.session_state.node:
        st.session_state.node.close()
        st.session_state.node = None
        st.rerun()

# Ana Ekran Düzeni
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 Mesajlaşma")
    
    # Mesaj gönderme alanı
    with st.container(border=True):
        msg_input = st.text_input("Mesajınız", key="msg_input")
        if st.button("🚀 Gönder"):
            if st.session_state.node and st.session_state.node.state == NodeState.ESTABLISHED:
                st.session_state.node.send_data(msg_input.encode())
                st.session_state.chat_history.append(f"Siz: {msg_input}")
            else:
                st.error("Önce bağlantı kurulmalı!")

    # Chat geçmişi
    chat_container = st.container(height=400)
    
    # Yeni gelen mesajları kontrol et
    if st.session_state.node:
        while not st.session_state.node.received_messages.empty():
            new_msg = st.session_state.node.received_messages.get()
            st.session_state.chat_history.append(f"Karşı Taraf: {new_msg}")

    for chat in reversed(st.session_state.chat_history):
        chat_container.write(chat)

with col2:
    st.subheader("📋 Canlı Ağ Logları")
    log_container = st.empty()
    
    # Logları sürekli güncelle
    if st.session_state.node:
        st.session_state.node.debug_mode = debug_mode # Debug modunu anlık güncelle
        
        log_html = "<div style='background-color: #0e1117; padding: 10px; border-radius: 5px; height: 500px; overflow-y: auto; font-family: monospace;'>"
        for log in reversed(st.session_state.node.logs):
            color = "white"
            # Colorama renklerini HTML renklerine çevirelim (basit eşleştirme)
            raw_color = str(log['color'])
            if '32' in raw_color: color = "#00ff00" # Green
            elif '34' in raw_color: color = "#0088ff" # Blue
            elif '33' in raw_color: color = "#ffff00" # Yellow
            elif '31' in raw_color: color = "#ff4b4b" # Red
            elif '36' in raw_color: color = "#00ffff" # Cyan
            elif '35' in raw_color: color = "#ff00ff" # Magenta
            
            log_html += f"<p style='color: {color}; margin: 2px 0;'>[{log['time']}] {log['msg']}</p>"
        log_html += "</div>"
        log_container.markdown(log_html, unsafe_allow_color_allowed=True, unsafe_allow_html=True)

# Otomatik yenileme (Düşük performanslı ama basit bir çözüm)
time.sleep(0.5)
st.rerun()
