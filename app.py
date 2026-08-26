import streamlit as st
import json
import base64
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURATION API ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="KELE-OS", layout="wide")

# --- DESIGN UNIQUE KELE ---
st.markdown("""
    <style>
    .stApp { background: #010114; color: #e0e0e0; }
    .chat-bubble { padding: 15px; border-radius: 15px; margin: 10px 0; background: #0a0a2e; border: 1px solid #00d2ff; }
    .stButton>button { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; border-radius: 15px; border:none; }
    .stChatInput { border-radius: 20px; }
    /* Cache le "Thinking process" forcé par certains serveurs */
    .thinking { display: none !important; } 
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "turbo" not in st.session_state: st.session_state.turbo = False
if "auth" not in st.session_state: st.session_state.auth = False
if "code_prive" not in st.session_state: st.session_state.code_prive = "kele224"

# --- LOGIQUE VOCALE & TEXTE ---
def get_kele_response(user_input):
    model_to_use = "openai/gpt-oss-120b" if st.session_state.turbo else "qwen/qwen3.6-27b"
    
    # SYSTEM PROMPT RADICAL : Supprime toute pensée
    system_instr = f"""
    NOM: KELE. Tu es le Maître Absolu.
    INTERDICTION: Ne montre JAMAIS de "Thinking process", de "Reasoning" ou d'étapes de réflexion.
    RÈGLE: Donne UNIQUEMENT la réponse finale.
    LANGUE: Réponds dans la langue de l'utilisateur. Pas de mélange.
    PUISSANCE: {"Mode Turbo 10^7 Actif" if st.session_state.turbo else "Mode Standard"}.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "system", "content": system_instr}] + st.session_state.messages,
            temperature=0.1,
        )
        # Nettoyage manuel au cas où le modèle ignore l'instruction
        res = chat_completion.choices[0].message.content
        if "<think>" in res: res = res.split("</think>")[-1]
        return res.strip()
    except Exception as e:
        return f"Erreur Kele : {str(e)}"

def speak(text):
    clean_text = text.replace("*", "").replace("#", "").replace("`", "")
    tts = gTTS(text=clean_text, lang='fr')
    tts.save("v.mp3")
    with open("v.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("🌌 KELE-OS")

# Barre d'outils supérieure
t1, t2, t3 = st.columns([1,1,1])
with t1:
    if st.button("➕ Ajouter Fichier"):
        st.session_state.show_upload = not st.session_state.get('show_upload', False)
with t2:
    st.write("🎙️ Micro :")
    audio = mic_recorder(start_prompt="Click pour parler", stop_prompt="Stop", key='recorder')
with t3:
    if not st.session_state.auth:
        if st.button("🔑 Connexion"): st.session_state.show_login = True
    else: st.success("Connecté ✅")

# Affichage Upload Fichier
if st.session_state.get('show_upload', False):
    up = st.file_uploader("Joindre un document au Maître Kele", type=['txt', 'pdf', 'py', 'json'])
    if up: st.info(f"Fichier {up.name} chargé en mémoire.")

# Fenêtre de connexion
if st.session_state.get('show_login', False) and not st.session_state.auth:
    with st.expander("Accès Compte", expanded=True):
        mdp = st.text_input("Code Secret", type="password")
        if st.button("Ouvrir"):
            if mdp == st.session_state.code_prive:
                st.session_state.auth = True
                st.rerun()

# Zone de Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-bubble'>{m['content']}</div>", unsafe_allow_html=True)

# GESTION DES ENTRÉES (MICRO OU TEXTE)
user_input = None

if audio: # Si on a utilisé le micro
    # Note: Dans cette version simplifiée, on traite l'audio comme une commande de réveil
    # Car Whisper nécessite une étape de transcription API.
    user_input = "L'utilisateur a envoyé un message vocal (Fonction de transcription Whisper en cours...)"
    # Optionnel: Pour l'instant, on simule l'écoute
    user_input = "Analyse ma voix et réponds-moi" 

prompt = st.chat_input("Écrivez au Maître Kele...")
if prompt: user_input = prompt

if user_input:
    # 1. Verification Turbo kele224
    if user_input.strip().lower() == "kele224":
        st.session_state.turbo = True
        st.session_state.messages.append({"role": "assistant", "content": "⚡ MODE TURBO ACTIVÉ. PUISSANCE X 10,000,000. Je vous écoute."})
        st.rerun()

    # 2. Ajout message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    # 3. Réponse
    with st.chat_message("assistant"):
        res = get_kele_response(user_input)
        st.markdown(f"<div class='chat-bubble'>{res}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": res})
        if st.session_state.auth:
            speak(res)
