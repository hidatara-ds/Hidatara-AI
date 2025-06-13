import streamlit as st
import streamlit.components.v1 as components
import ollama
import time
import re
from functools import lru_cache

# Konfigurasi halaman untuk performa lebih baik
st.set_page_config(layout="wide", page_title="AI Curhat", page_icon="💬")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Ollama"

# Sistem prompt yang lebih ringkas
PROMPT_SYSTEM = "Kamu adalah teman curhat virtual yang responsif dan empatik. Berikan respons pendek (1-2 kalimat)."

# Cache untuk respons ollama
@st.cache_data(ttl=300)  # Cache selama 5 menit
def cached_ollama_response(prompt, history_str):
    """Cache respons ollama untuk prompt yang sama"""
    return get_raw_ollama_response(prompt, history_str)

def clean_response(text):
    """Membersihkan respons - versi lebih sederhana"""
    # Memotong ke maksimal 2 kalimat
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) > 2:
        return ' '.join(sentences[:2])
    return text

# LRU cache untuk mengoptimalkan respons yang sering diminta
@lru_cache(maxsize=100)
def get_raw_ollama_response(user_message, history_str):
    """Generate respons mentah dari Ollama dengan caching"""
    # Konversi history_str kembali ke struktur pesan
    messages = [{"role": "system", "content": PROMPT_SYSTEM}]
    
    # Tambahkan pesan saat ini
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Tambahkan parameter untuk membatasi output
        response = ollama.chat(
            model="llama3.1", 
            messages=messages,
            options={
                "num_predict": 100,  # Batasi output untuk respons lebih cepat
                "temperature": 0.7
            }
        )
        ai_response = response["message"]["content"]
        return ai_response
    except Exception as e:
        return f"Error: {str(e)}"

def get_ollama_response(user_message, chat_history=None):
    """Mendapatkan respons cepat dari Ollama dengan optimasi"""
    if chat_history is None:
        chat_history = []
    
    # Hanya gunakan 2 pesan terakhir untuk konteks lebih ringkas
    recent_history = chat_history[-2:] if len(chat_history) > 2 else chat_history
    
    # Konversi riwayat ke string untuk caching
    history_str = ""
    if recent_history:
        history_str = str([f"{msg['role']}:{msg['content']}" for msg in recent_history])
    
    start_time = time.time()
    raw_response = cached_ollama_response(user_message, history_str)
    response_time = time.time() - start_time
    
    # Bersihkan respons
    clean_resp = clean_response(raw_response)
    
    return clean_resp, response_time

# Dialogflow CX widget yang dioptimasi
def render_dialogflow_widget():
    dialogflow_html = """
    <link rel="stylesheet" href="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/themes/df-messenger-default.css">
    <script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
    <df-messenger
      location="asia-southeast2"
      project-id="unique-hash-448408-d6"
      agent-id="1b594ea3-62dc-4670-82ca-f55d213c2e83"
      language-code="id"
      max-query-length="-1">
      <df-messenger-chat-bubble
       chat-title="AI Curhat">
      </df-messenger-chat-bubble>
    </df-messenger>
    <style>
      df-messenger {
        z-index: 999;
        position: fixed;
        --df-messenger-font-color: #000000;
        --df-messenger-font-family: Google Sans;
        --df-messenger-chat-background: #FEF8E6;
        --df-messenger-message-user-background: #FCE8B2;
        --df-messenger-message-bot-background: #fff;
        bottom: 16px;
        right: 16px;
      }
    </style>
    """
    components.html(dialogflow_html, height=500)

# UI yang dioptimasi untuk Streamlit
def main():
    # Tampilan header yang lebih simpel
    st.markdown("<h1 style='text-align: center;'>AI Curhat</h1>", unsafe_allow_html=True)
    
    # Sidebar yang lebih ramping
    with st.sidebar:
        st.session_state.selected_model = st.radio(
            "Model:",
            ["Ollama", "Dialogflow CX"]
        )
        
        # Tombol reset yang lebih jelas
        if st.button("Reset Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.experimental_rerun()
    
    # Mode Ollama yang dioptimasi untuk kecepatan
    if st.session_state.selected_model == "Ollama":
        # Tampilkan riwayat chat dengan cara yang lebih efisien
        chat_container = st.container()
        with chat_container:
            # Gunakan loop yang efisien untuk menampilkan chat
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Input pengguna
        user_message = st.chat_input("Ketik pesan...")
        
        if user_message:
            # Tampilkan pesan pengguna
            with st.chat_message("user"):
                st.write(user_message)
            
            # Tambahkan pesan pengguna ke riwayat
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            # Dapatkan respons Ollama dengan tampilan yang lebih efisien
            with st.chat_message("assistant"):
                with st.spinner(""):  # Spinner tanpa teks untuk mengurangi overhead
                    response, response_time = get_ollama_response(user_message, st.session_state.chat_history)
                    st.write(response)
                    st.caption(f"Waktu: {response_time:.2f}s")
            
            # Tambahkan respons asisten ke riwayat
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    else:  # Dialogflow CX
        render_dialogflow_widget()

if __name__ == "__main__":
    main()