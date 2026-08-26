import streamlit as st
import json
import base64
import re
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# ==================== MOTEUR SUPRÊME KELE ====================
API_KEY = "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"
MODEL_ID = "openai/gpt-oss-120b"
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="KELE-OS", page_icon="🧠", layout="wide")

# STYLE CSS IMMERSIF
st.markdown("""
<style>
    .stApp { background: #020205; color: #ffffff; }
    .chat-bubble {
        padding: 20px; border-radius: 15px; margin: 10px 0;
        background: #0a0a1a; border: 1px solid #00d2ff;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.1);
        font-size: 1.1rem;
    }
    .title {
        font-size: 3.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stButton>button { background: #00d2ff; color: #000; font-weight: bold; width: 100%; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# GESTION ÉTATS
if "messages" not in st.session_state: st.session_state.messages = []
if "auth" not in st.session_state: st.session_state.auth = False

def clean_output(text):
    """Extraction chirurgicale de la réponse (invisiblement)"""
    if not text: return "Erreur : Le cerveau est vide."
    # On récupère tout ce qui est HORS des balises <think>
    final = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    # Si le modèle a tout mis dans <think>, on récupère le contenu de <think>
    if not final:
        think_content = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)
        final = think_content[-1] if think_content else text
    return re.sub(r'<.*?>', '', final).strip()

def get_response(prompt):
    """Communication directe avec le 120B"""
    sys_prompt = "Tu es KELE. Maître absolu. Réponds en Français. Pas de blabla, juste la solution."
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
            temperature=0.4,
            max_tokens=3000
        )
        return clean_output(completion.choices[0].message.content)
    except Exception as e:
        return f"Échec Système : {str(e)}"

def speak(text):
    """Voix de Kele"""
    try:
        tts = gTTS(text=text[:300], lang='fr')
        tts.save("s.mp3")
        with open("s.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# INTERFACE
st.markdown("<h1 class='title'>KELE-OS</h1>", unsafe_allow_html=True)

# Barre d'outils mobile
col_mic, col_auth = st.columns(2)
with col_mic:
    audio = mic_recorder(start_prompt="🎙️ PARLER", stop_prompt="⏹️ STOP", key='mic')
with col_auth:
    if not st.session_state.auth:
        if st.button("🔑 LOGIN"): st.session_state.show_login = True
    else: st.success("MAÎTRE ✅")

if st.session_state.get('show_login') and not st.session_state.auth:
    pwd = st.text_input("Code", type="password")
    if st.button("DÉVERROUILLER"):
        if pwd == "kele224":
            st.session_state.auth = True
            st.rerun()

# Affichage des messages
for m in st.session_state.messages:
    icon = "🧠" if m["role"] == "assistant" else "👤"
    st.markdown(f"<div class='chat-bubble'><b>{icon} {m['role'].upper()}</b><br>{m['content']}</div>", unsafe_allow_html=True)

# Entrée Utilisateur
user_query = st.chat_input("Dictez votre volonté...")
if audio: user_query = "Réponds à mon message vocal."

if user_query:
    # Sauvegarde et génération
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("Analyse KELE..."):
        answer = get_response(user_query)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        if st.session_state.auth: speak(answer)
    st.rerun()
