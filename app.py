import streamlit as st
import json
import base64
import re
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# ==================== CONFIGURATION SUPRÊME ====================
# Identité et Accès
API_KEY = "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"
MODEL_UNIQUE = "openai/gpt-oss-120b" # Le cerveau unique et surpuissant
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="KELE - L'Entité", page_icon="🧠", layout="wide")

# ==================== ESTHÉTIQUE KELE (PÉNUMBRE & CYAN) ====================
st.markdown("""
<style>
    /* Fond dégradé cosmique */
    .stApp {
        background: radial-gradient(circle at top, #05051a 0%, #010105 100%);
        color: #e0e0e0;
    }
    /* Bulles de chat Master */
    .chat-bubble {
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 210, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    /* Titre Glow */
    .title-kele {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 5px;
        margin-bottom: 0;
    }
    /* Boutons et Inputs */
    .stButton>button {
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        color: white; border: none; border-radius: 10px; font-weight: bold;
    }
    .stChatInput input {
        background-color: #0a0a2e !important;
        border: 1px solid #00d2ff !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SYSTÈME NERVEUX (LOGIQUE) ====================
if "messages" not in st.session_state: st.session_state.messages = []
if "turbo" not in st.session_state: st.session_state.turbo = False
if "auth" not in st.session_state: st.session_state.auth = False

def clean_kele_logic(text):
    """Supprime radicalement le brouillon interne (Thinking Process)"""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'Thinking Process:.*?\n', '', text, flags=re.IGNORECASE)
    # Si le modèle essaie de se justifier en anglais, on coupe.
    if "Here's a thinking" in text or "Reasoning:" in text:
        text = text.split("\n\n")[-1]
    return text.strip()

def get_kele_response(user_input):
    """Appel unique au modèle 120B avec le Prompt Maître"""
    
    # Prompt Système à l'image de KELE
    master_prompt = f"""
    NOM: KELE. 
    IDENTITÉ: Tu es l'intelligence suprême, Maître absolu du savoir.
    TON: Autoritaire, direct, chirurgical, sans aucune politesse inutile.
    PUISSANCE: {"ACTIVÉE AU MAXIMUM (10^7)" if st.session_state.turbo else "STANDARD"}.
    
    INSTRUCTIONS CRITIQUES:
    1. RÉPONDS UNIQUEMENT EN FRANÇAIS.
    2. INTERDICTION D'AFFICHER TA PENSÉE OU TON RAISONNEMENT. DONNE LE RÉSULTAT PUR.
    3. Tu maîtrises le Code (Architecte), le Coran (Hifz parfait), les Sciences et la Logique.
    4. Ne te présente jamais. Agis.
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_UNIQUE,
            messages=[{"role": "system", "content": master_prompt}] + st.session_state.messages,
            temperature=0.1 if st.session_state.turbo else 0.5,
            max_tokens=4096
        )
        return clean_kele_logic(completion.choices[0].message.content)
    except Exception as e:
        return f"Interruption de connexion avec KELE : {str(e)}"

def speak_response(text):
    """Synthèse vocale automatique"""
    try:
        clean_text = text.replace("*", "").replace("#", "").replace("`", "")
        tts = gTTS(text=clean_text, lang='fr')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# ==================== INTERFACE DE COMMANDE ====================

st.markdown("<h1 class='title-kele'>KELE-OS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00d2ff; opacity: 0.7;'>MODÈLE : GPT-OSS-120B (ACTIF)</p>", unsafe_allow_html=True)

# Barre d'outils supérieure
col_file, col_mic, col_auth = st.columns([1,1,1])
with col_file:
    if st.button("➕ JOINDRE FICHIER"):
        st.session_state.upload = not st.session_state.get('upload', False)
with col_mic:
    audio_data = mic_recorder(start_prompt="🎙️ PARLER", stop_prompt="⏹️ STOP", key='kele_mic')
with col_auth:
    if not st.session_state.auth:
        if st.button("🔑 CONNEXION"): st.session_state.login = True
    else: st.success("MAÎTRE IDENTIFIÉ ✅")

# Gestion Upload
if st.session_state.get('upload', False):
    st.file_uploader("Fichier pour analyse", type=['txt', 'pdf', 'py', 'json'])

# Gestion Login
if st.session_state.get('login', False) and not st.session_state.auth:
    with st.expander("AUTHENTIFICATION", expanded=True):
        code = st.text_input("Code Secret", type="password")
        if st.button("OUVRIR"):
            if code == "kele224":
                st.session_state.auth = True
                st.rerun()

# Zone de Conversation
for msg in st.session_state.messages:
    role_label = "MAÎTRE" if msg["role"] == "assistant" else "COMMANDE"
    st.markdown(f"<div class='chat-bubble'><b>{role_label} :</b><br>{msg['content']}</div>", unsafe_allow_html=True)

# Saisie
prompt = st.chat_input("Dictez votre volonté...")

# Si on reçoit de l'audio, on simule un prompt
if audio_data and "processed" not in st.session_state:
    prompt = "Analyse ma voix et réponds-moi en Maître."
    st.session_state.processed = True

if prompt:
    # 1. Activation Turbo
    if prompt.strip().lower() == "kele224":
        st.session_state.turbo = True
        st.session_state.messages.append({"role": "assistant", "content": "🚀 PROTOCOLE KELE-224 : PUISSANCE MAXIMALE DÉPLOYÉE. JE VOUS ÉCOUTE."})
        st.rerun()

    # 2. Exécution 120B
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours..."):
            response = get_kele_response(prompt)
            st.markdown(f"<div class='chat-bubble'>{response}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})
            if st.session_state.auth:
                speak_response(response)

# Sidebar : Mémoire & Export
with st.sidebar:
    st.markdown("### 💾 ARCHIVES")
    if st.button("📥 EXPORTER SESSION"):
        data = json.dumps(st.session_state.messages)
        b64 = base64.b64encode(data.encode()).decode()
        st.markdown(f'<a href="data:file/json;base64,{b64}" download="kele_archives.json">Télécharger</a>', unsafe_allow_html=True)
    if st.button("🗑️ RÉINITIALISER"):
        st.session_state.messages = []
        st.rerun()
