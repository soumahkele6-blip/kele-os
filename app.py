import streamlit as st
import os
import json
import base64
from groq import Groq
from gtts import gTTS

# --- CONFIGURATION API ---
GROQ_API_KEY = "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"

st.set_page_config(page_title="KELE-OS", layout="wide")

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #020111 0%, #050531 35%, #0c0c52 100%); color: white; }
    .chat-bubble { padding: 15px; border-radius: 15px; margin: 10px 0; background: rgba(255, 255, 255, 0.05); border-left: 4px solid #00d2ff; }
    .stButton>button { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; border-radius: 10px; border:none; font-weight: bold; }
    .stChatInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "turbo" not in st.session_state: st.session_state.turbo = False
if "auth" not in st.session_state: st.session_state.auth = False
if "code_prive" not in st.session_state: st.session_state.code_prive = "kele224"

client = Groq(api_key=GROQ_API_KEY)

# --- LOGIQUE KELE ---
def get_kele_response(user_input):
    # Choix du modèle selon le mode
    model_to_use = "openai/gpt-oss-120b" if st.session_state.turbo else "qwen/qwen3.6-27b"
    
    # SYSTEM PROMPT ULTRA-STRICT
    system_instr = f"""
    Tu es KELE. 
    PUISSANCE: {"MAXIMALE (10^7)" if st.session_state.turbo else "SOMMEIL (LIMITÉE)"}.
    
    RÈGLES CRITIQUES :
    1. NE JAMAIS afficher ton "Thinking Process" ou ton raisonnement interne. Donne uniquement la réponse finale.
    2. LANGUE : Réponds strictement dans la langue utilisée par l'utilisateur. Si l'utilisateur dit "Salut", réponds en Français. Si c'est de l'Anglais, réponds en Anglais. Langue par défaut : Français.
    3. PAS DE PRÉTENTION : Ne te présente pas à chaque message. Sois direct, efficace et précis.
    4. MAÎTRISE : Tu es le maître du code, du Coran et des sciences.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "system", "content": system_instr}] + st.session_state.messages,
            temperature=0.1, # Pour éviter les divagations
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erreur : {str(e)}"

def speak(text):
    clean_text = text.replace("*", "").replace("#", "").replace("`", "")
    tts = gTTS(text=clean_text, lang='fr')
    tts.save("v.mp3")
    audio_file = open("v.mp3", "rb")
    st.audio(audio_file.read(), format='audio/mp3', autoplay=True)

# --- INTERFACE ---

st.title("🌌 KELE-OS")

# Barre de statut en haut
col1, col2 = st.columns([2, 1])
with col1:
    status = "🔥 TURBO ACTIF" if st.session_state.turbo else "💤 MODE SOMMEIL"
    st.info(f"Statut : {status}")
with col2:
    if not st.session_state.auth:
        if st.button("🔑 CONNEXION COMPTE"):
            st.session_state.show_login = True
    else:
        st.success("✅ CONNECTÉ")

# Fenêtre de connexion (si cliqué)
if "show_login" in st.session_state and not st.session_state.auth:
    with st.expander("FORMULAIRE DE CONNEXION", expanded=True):
        email = st.text_input("Gmail")
        mdp = st.text_input("Mot de passe", type="password")
        if st.button("VALIDER"):
            if mdp == st.session_state.code_prive:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Code invalide.")

# Affichage du chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-bubble'>{m['content']}</div>", unsafe_allow_html=True)

# Entrée utilisateur
if prompt := st.chat_input("Parlez à Kele..."):
    
    # INTERCEPTION DU CODE TURBO
    if prompt.strip() == st.session_state.code_prive:
        st.session_state.turbo = True
        st.session_state.messages.append({"role": "assistant", "content": "🚀 PROTOCOLE KELE-224 ACTIVÉ. PUISSANCE MAXIMALE DÉPLOYÉE."})
        st.rerun()

    # Ajout du message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Réponse Kele
    with st.chat_message("assistant"):
        response = get_kele_response(prompt)
        st.markdown(f"<div class='chat-bubble'>{response}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Audio automatique si connecté
        if st.session_state.auth:
            speak(response)

# Sidebar : Fonctions Import/Export
with st.sidebar:
    st.header("MÉMOIRE")
    if st.button("📥 EXPORTER TRAVAIL"):
        b64 = base64.b64encode(json.dumps(st.session_state.messages).encode()).decode()
        st.markdown(f'<a href="data:file/json;base64,{b64}" download="kele.json">Télécharger</a>', unsafe_allow_html=True)
    if st.button("🗑️ NOUVELLE CONVERSATION"):
        st.session_state.messages = []
        st.rerun()
