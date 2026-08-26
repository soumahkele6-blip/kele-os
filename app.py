import streamlit as st
import json
import base64
import re
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# ==================== CONFIGURATION SUPRÊME ====================
API_KEY = "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"
# Modèle 120B : Puissance maximale
MODEL_UNIQUE = "openai/gpt-oss-120b" 
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="KELE-OS", page_icon="🧠", layout="wide")

# STYLE CSS (CONSERVÉ)
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top, #05051a 0%, #010105 100%); color: #e0e0e0; }
    .chat-bubble {
        padding: 20px; border-radius: 15px; margin: 15px 0;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 210, 255, 0.3);
    }
    .title-kele {
        font-size: 3rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: 5px;
    }
    .stButton>button { background: linear-gradient(45deg, #00d2ff, #3a7bd5); color: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "auth" not in st.session_state: st.session_state.auth = False

def clean_kele_output(text):
    """Extrait la réponse finale ou le raisonnement si nécessaire"""
    if not text: return ""
    
    # On cherche le contenu des balises <think>
    think_match = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)
    # On enlève les balises pour voir ce qu'il reste
    final_output = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    # Si le texte hors balise est vide, on prend le dernier raisonnement (souvent la réponse)
    if not final_output and think_match:
        final_output = think_match[-1].strip()
    
    # Nettoyage final des résidus de balises
    final_output = re.sub(r'<.*?>', '', final_output)
    return final_output

def get_kele_response(user_input):
    system_prompt = "Tu es KELE. Réponds directement et uniquement en Français. Ne montre pas de balises."
    try:
        completion = client.chat.completions.create(
            model=MODEL_UNIQUE,
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            temperature=0.5,
            max_tokens=2048 # Augmenté pour les énigmes longues
        )
        raw_text = completion.choices[0].message.content
        return clean_kele_output(raw_text)
    except Exception as e:
        return f"Erreur Système : {str(e)}"

def speak_response(text):
    try:
        tts = gTTS(text=text[:400], lang='fr')
        tts.save("r.mp3")
        with open("r.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# --- INTERFACE ---
st.markdown("<h1 class='title-kele'>KELE-OS</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c2: audio_data = mic_recorder(start_prompt="🎙️ PARLER", stop_prompt="⏹️ STOP", key='kele_mic')
with c3:
    if not st.session_state.auth:
        if st.button("🔑 CONNEXION"): st.session_state.login = True
    else: st.success("MAÎTRE CONNECTÉ")

if st.session_state.get('login', False) and not st.session_state.auth:
    code = st.text_input("Code Secret", type="password")
    if st.button("OK"):
        if code == "kele224":
            st.session_state.auth = True
            st.rerun()

# Zone de Chat
for msg in st.session_state.messages:
    icon = "🧠" if msg["role"] == "assistant" else "👤"
    st.markdown(f"<div class='chat-bubble'><b>{icon} {msg['role'].upper()} :</b><br>{msg['content']}</div>", unsafe_allow_html=True)

# Saisie
prompt = st.chat_input("Dictez votre volonté...")
if audio_data: prompt = "Analyse ma demande vocale."

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("KELE calcule..."):
        res = get_kele_response(st.session_state.messages[-1]["content"])
        if not res: res = "Le modèle n'a pas renvoyé de texte. Essayez de raccourcir la question."
        st.session_state.messages.append({"role": "assistant", "content": res})
        if st.session_state.auth: speak_response(res)
        st.rerun()
