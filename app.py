import streamlit as st
import json
import base64
import re
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
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "turbo" not in st.session_state: st.session_state.turbo = False
if "auth" not in st.session_state: st.session_state.auth = False
if "code_prive" not in st.session_state: st.session_state.code_prive = "kele224"

# --- LOGIQUE DE NETTOYAGE RADICAL ---
def clean_kele_output(text):
    # Supprime tout ce qui est entre les balises <think> ou les blocs de raisonnement
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'Thinking Process:.*?\n', '', text, flags=re.IGNORECASE)
    # Supprime les introductions de raisonnement en anglais
    if "Here's a thinking process" in text:
        text = text.split("Final Output:")[-1] if "Final Output:" in text else text.split("\n\n")[-1]
    return text.strip()

def get_kele_response(user_input):
    model_to_use = "openai/gpt-oss-120b" if st.session_state.turbo else "qwen/qwen3.6-27b"
    
    system_instr = f"""
    NOM: KELE. Tu es le Maître Absolu.
    INTERDICTION STRICTE: Ne parle JAMAIS anglais. Ne montre JAMAIS de pensée.
    RÈGLE: Réponds UNIQUEMENT en Français, de manière directe et chirurgicale.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "system", "content": system_instr}] + st.session_state.messages,
            temperature=0.1,
        )
        raw_res = chat_completion.choices[0].message.content
        return clean_kele_output(raw_res) # Nettoyage avant affichage
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

# Barre d'outils
t1, t2, t3 = st.columns([1,1,1])
with t1:
    if st.button("➕ Fichier"): st.session_state.show_up = not st.session_state.get('show_up', False)
with t2:
    audio = mic_recorder(start_prompt="🎙️ Parler", stop_prompt="⏹️ Stop", key='recorder')
with t3:
    if not st.session_state.auth:
        if st.button("🔑 Connexion"): st.session_state.show_login = True
    else: st.success("Maître Connecté")

if st.session_state.get('show_up', False):
    st.file_uploader("Joindre un document", type=['txt', 'pdf', 'py'])

if st.session_state.get('show_login', False) and not st.session_state.auth:
    mdp = st.text_input("Code Secret", type="password")
    if st.button("Ouvrir"):
        if mdp == st.session_state.code_prive:
            st.session_state.auth = True
            st.rerun()

# Zone de Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-bubble'>{m['content']}</div>", unsafe_allow_html=True)

# Entrée
prompt = st.chat_input("Écrivez au Maître Kele...")
if prompt:
    if prompt.strip().lower() == st.session_state.code_prive:
        st.session_state.turbo = True
        st.session_state.messages.append({"role": "assistant", "content": "🚀 MODE TURBO ACTIVÉ."})
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        res = get_kele_response(prompt)
        st.markdown(f"<div class='chat-bubble'>{res}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": res})
        if st.session_state.auth:
            speak(res)
