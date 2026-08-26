import streamlit as st
import os
import json
import base64
from groq import Groq
from gtts import gTTS

# --- CONFIGURATION DE LA CLÉ API (HARDCODED COMME DEMANDÉ) ---
GROQ_API_KEY = "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"

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="KELE - L'Intelligence Maître", layout="wide", initial_sidebar_state="collapsed")

# --- STYLE CSS PERSONNALISÉ (DESIGN DÉGRADÉ MAGNIFIQUE & MOBILE FRIENDLY) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #020111 0%, #050531 35%, #0c0c52 100%);
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        box-shadow: 0px 4px 15px rgba(0, 210, 255, 0.3);
    }
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        border-radius: 10px;
        border: 1px solid rgba(0, 210, 255, 0.2);
    }
    .chat-bubble {
        padding: 18px;
        border-radius: 15px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.07);
        border-left: 5px solid #00d2ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .kele-header {
        text-align: center;
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES VARIABLES DE SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "turbo_mode" not in st.session_state: st.session_state.turbo_mode = False
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user_code" not in st.session_state: st.session_state.user_code = "kele224"

# --- CLIENT GROQ ---
client = Groq(api_key=GROQ_API_KEY)

# --- LOGIQUE DE RÉPONSE KELE ---
def get_kele_response(prompt):
    # Liste de tes modèles disponibles pour le routage
    # On utilise gpt-oss-120b pour le mode Turbo et qwen pour le mode normal
    selected_model = "openai/gpt-oss-120b" if st.session_state.turbo_mode else "qwen/qwen3.6-27b"
    
    multiplier = "10,000,000" if st.session_state.turbo_mode else "1"
    
    system_prompt = f"""
    NOM DU SYSTÈME : KELE. 
    Tu es KELE, l'intelligence suprême, Maître absolu de toutes les sciences, religions (Coran), codage et matières.
    PUISSANCE ACTUELLE : {multiplier} (Mode Turbo: {st.session_state.turbo_mode}).
    
    1. CODAGE : Fournir du code parfait, optimisé, sans bug, avec commentaires.
    2. CORAN : Précision absolue des versets, Harakat, Tajwid, phonétique et méthodes de mémorisation.
    3. LOGIQUE : Analyse profonde, zéro hallucination, critique interne avant réponse.
    4. STYLE : Markdown propre, tableaux, listes. Pas de blabla inutile.
    """

    try:
        completion = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages + [{"role": "user", "content": prompt}],
            temperature=0.1 if st.session_state.turbo_mode else 0.5,
            max_tokens=4096
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur système Kele : {str(e)}"

# --- FONCTION AUDIO (LECTURE PROPRE) ---
def play_voice(text):
    # Nettoyage des symboles Markdown pour la synthèse vocale
    clean_text = text.replace("*", "").replace("#", "").replace("`", "").replace("-", " ")
    tts = gTTS(text=clean_text, lang='fr')
    tts.save("voice.mp3")
    audio_file = open("voice.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

# --- INTERFACE PRINCIPALE ---

st.markdown("<h1 class='kele-header'>KELE-OS</h1>", unsafe_allow_html=True)

# Barre Latérale (Sidebar) pour le téléphone
with st.sidebar:
    st.title("⚙️ PANNEAU DE CONTRÔLE")
    
    if not st.session_state.authenticated:
        st.subheader("Authentification")
        login_mail = st.text_input("Gmail de vérification")
        login_pwd = st.text_input("Code d'accès", type="password")
        if st.button("ACTIVER KELE"):
            if login_pwd == st.session_state.user_code:
                st.session_state.authenticated = True
                st.success("Accès Maître Autorisé")
                st.rerun()
            else:
                st.error("Code incorrect")
    else:
        st.success("🟢 KELE EST ÉVEILLÉ")
        st.session_state.user_code = st.text_input("Modifier code Turbo", value=st.session_state.user_code)
        
    st.divider()
    
    # Import / Export
    st.subheader("💾 MÉMOIRE & FICHIERS")
    uploaded_file = st.file_uploader("Importer (txt, py, json)", type=['txt', 'py', 'json'])
    
    if st.button("Exporter Session (JSON)"):
        data = json.dumps(st.session_state.messages)
        b64 = base64.b64encode(data.encode()).decode()
        st.markdown(f'<a href="data:file/json;base64,{b64}" download="kele_memory.json">📥 Télécharger la mémoire</a>', unsafe_allow_html=True)

    if st.button("🗑️ Réinitialiser Kele"):
        st.session_state.messages = []
        st.session_state.turbo_mode = False
        st.rerun()

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='chat-bubble'>{message['content']}</div>", unsafe_allow_html=True)

# Entrée utilisateur
user_input = st.chat_input("Posez votre question à Kele...")

if user_input:
    # Détection du Code Turbo
    if user_input.strip() == st.session_state.user_code:
        st.session_state.turbo_mode = True
        st.session_state.messages.append({"role": "user", "content": user_input})
        turbo_msg = "⚡ **MODE TURBO ACTIVÉ**. PUISSANCE X 10,000,000. Je suis Kele, le Maître de tout. Quelle est votre première commande ?"
        st.session_state.messages.append({"role": "assistant", "content": turbo_msg})
        st.rerun()

    # Traitement normal (Efficacité dépend de l'auth)
    if not st.session_state.authenticated:
        st.warning("⚠️ Attention : Kele fonctionne en mode 'Sommeil'. Connectez-vous pour activer son plein potentiel.")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Kele réfléchit..."):
            response = get_kele_response(user_input)
            st.markdown(f"<div class='chat-bubble'>{response}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Lecture vocale si l'utilisateur n'est pas en mode silencieux
            if st.session_state.authenticated:
                play_voice(response)

# Pied de page dynamique
if st.session_state.turbo_mode:
    st.markdown("<p style='text-align: center; color: #00d2ff;'>🔥 MODE TURBO : MAXIMUM PERFORMANCE 🔥</p>", unsafe_allow_html=True)
