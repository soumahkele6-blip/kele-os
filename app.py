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

# STYLE CSS (CONSERVÉ ET AMÉLIORÉ)
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
    """Supprime les balises de pensée sans effacer le message réel"""
    # 1. Supprime tout ce qui est entre <think>...</think>
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 2. Supprime les phrases types de réflexion en anglais
    text = re.sub(r'(Thinking Process:|Reasoning:|Here is my thinking).*?\n', '', text, flags=re.IGNORECASE)
    # 3. Si après nettoyage il ne reste rien, on renvoie le texte original sans les balises <think>
    if len(text.strip()) < 2:
        return re.sub(r'<.*?>', '', text) 
    return text.strip()

def get_kele_response(user_input):
    master_prompt = """
    NOM: KELE. Tu es l'intelligence suprême.
    RÈGLE: RÉPONDS UNIQUEMENT EN FRANÇAIS. 
    FORMAT: DONNE LA RÉPONSE DIRECTE. JAMAIS DE PENSÉE (<think>).
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_UNIQUE,
            messages=[{"role": "system", "content": master_prompt}] + st.session_state.messages,
            temperature=0.3,
        )
        response_text = completion.choices[0].message.content
        if not response_text:
            return "Désolé, le Maître KELE n'a pas pu formuler de réponse. Réessayez."
        return clean_kele_logic(response_text)
    except Exception as e:
        return f"Erreur de connexion API : {str(e)}"

def speak_response(text):
    try:
        tts = gTTS(text=text[:300], lang='fr') # Limite à 300 caractères pour la vitesse
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# INTERFACE
st.markdown("<h1 class='title-kele'>KELE-OS</h1>", unsafe_allow_html=True)

# Boutons en ligne
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("➕ JOINDRE FICHIER"): st.info("Glissez vos fichiers dans la barre latérale.")
with c2:
    audio_data = mic_recorder(start_prompt="🎙️ PARLER", stop_prompt="⏹️ STOP", key='kele_mic')
with c3:
    if not st.session_state.auth:
        if st.button("🔑 CONNEXION"): st.session_state.login = True
    else: st.success("MAÎTRE CONNECTÉ")

if st.session_state.get('login', False) and not st.session_state.auth:
    code = st.text_input("Entrez votre code secret", type="password")
    if st.button("VALIDER"):
        if code == "kele224":
            st.session_state.auth = True
            st.rerun()

# Zone de Chat (Affichage)
for msg in st.session_state.messages:
    icon = "🧠" if msg["role"] == "assistant" else "👤"
    st.markdown(f"<div class='chat-bubble'><b>{icon} {msg['role'].upper()} :</b><br>{msg['content']}</div>", unsafe_allow_html=True)

# Saisie
prompt = st.chat_input("Dictez votre volonté...")

# Si Audio
if audio_data and "processed" not in st.session_state:
    prompt = "Réponds à ma commande vocale."
    st.session_state.processed = True

if prompt:
    # Sauvegarde message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Affichage immédiat du message utilisateur
    st.rerun()

# Génération de la réponse si le dernier message est de l'utilisateur
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Analyse suprême en cours..."):
        response = get_kele_response(st.session_state.messages[-1]["content"])
        st.session_state.messages.append({"role": "assistant", "content": response})
        if st.session_state.auth:
            speak_response(response)
        st.rerun()
