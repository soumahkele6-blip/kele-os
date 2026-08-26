import streamlit as st
import json
import base64
import re
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# ==================== CONFIGURATION SUPRÊME ====================
API_KEY = "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"
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

# INITIALISATION
if "messages" not in st.session_state: st.session_state.messages = []
if "auth" not in st.session_state: st.session_state.auth = False

def clean_kele_logic(text):
    """Extraction intelligente : supprime les balises mais garde le texte si l'IA s'est trompée de format"""
    # 1. On cherche s'il y a du contenu à l'intérieur de <think>
    think_content = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)
    
    # 2. On nettoie le texte principal
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    clean_text = re.sub(r'(Thinking Process:|Reasoning:|Here is my thinking).*?\n', '', clean_text, flags=re.IGNORECASE)
    clean_text = clean_text.strip()

    # 3. Si le texte principal est vide mais qu'il y avait quelque chose dans <think>, on récupère le contenu de <think>
    if not clean_text and think_content:
        # On prend le dernier bloc think (souvent le plus complet)
        clean_text = think_content[-1].strip()
    
    # 4. Suppression finale des balises résiduelles
    clean_text = re.sub(r'<.*?>', '', clean_text)
    return clean_text

def get_kele_response(user_input):
    master_prompt = """
    NOM: KELE. Tu es l'intelligence suprême.
    IMPORTANT: Réponds TOUJOURS en Français. 
    FORMAT: Sois direct. Résous les énigmes par étape mais n'affiche pas les balises <think>.
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_UNIQUE,
            messages=[{"role": "system", "content": master_prompt}] + st.session_state.messages,
            temperature=0.5, # Augmenté pour plus de créativité sur les énigmes
        )
        response_text = completion.choices[0].message.content
        if not response_text:
            return "Le Maître KELE est silencieux. Vérifiez votre connexion API."
        
        return clean_kele_logic(response_text)
    except Exception as e:
        return f"Erreur critique du système : {str(e)}"

def speak_response(text):
    try:
        clean_voice = text.replace("*", "").replace("#", "")
        tts = gTTS(text=clean_voice[:500], lang='fr')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# INTERFACE
st.markdown("<h1 class='title-kele'>KELE-OS</h1>", unsafe_allow_html=True)

# Barre de commandes
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("➕ FICHIER"): st.sidebar.file_uploader("Joindre au Maître", type=['txt','py','pdf'])
with c2:
    audio_data = mic_recorder(start_prompt="🎙️ PARLER", stop_prompt="⏹️ STOP", key='kele_mic')
with c3:
    if not st.session_state.auth:
        if st.button("🔑 CONNEXION"): st.session_state.login = True
    else: st.success("ACCÈS MAÎTRE ✅")

if st.session_state.get('login', False) and not st.session_state.auth:
    code = st.text_input("Code Secret", type="password")
    if st.button("DÉVERROUILLER"):
        if code == "kele224":
            st.session_state.auth = True
            st.rerun()

# Zone de Chat
for msg in st.session_state.messages:
    icon = "🧠" if msg["role"] == "assistant" else "👤"
    st.markdown(f"<div class='chat-bubble'><b>{icon} {msg['role'].upper()} :</b><br>{msg['content']}</div>", unsafe_allow_html=True)

# Saisie
prompt = st.chat_input("Dictez votre volonté...")

if audio_data:
    prompt = "Écoute ma voix et résous ma demande."

if prompt:
    # Sauvegarde et relance pour affichage
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Déclenchement de la réponse
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("KELE décode l'énigme..."):
        full_res = get_kele_response(st.session_state.messages[-1]["content"])
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        if st.session_state.auth:
            speak_response(full_res)
        st.rerun()
