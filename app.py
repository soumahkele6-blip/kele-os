import streamlit as st
import json
import os
import base64
import re
from datetime import datetime
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import pandas as pd

# ==================== CONFIGURATION & API ====================
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="KELE - Intelligence Suprême",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== DESIGN CSS (VIOLET DÉGRADÉ) ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    .main { background: rgba(0, 0, 0, 0.3); border-radius: 20px; padding: 2rem; }
    h1, h2, h3 { color: #00d2ff !important; font-weight: 800 !important; }
    
    .chat-bubble {
        padding: 1.2rem; border-radius: 15px; margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        background: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #764ba2;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important; border-radius: 12px !important;
        border: none !important; font-weight: 600 !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important; color: white !important;
        border-radius: 12px !important; border: 1px solid #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GESTION MÉMOIRE ====================
if "messages" not in st.session_state: st.session_state.messages = []
if "turbo" not in st.session_state: st.session_state.turbo = False
if "auth" not in st.session_state: st.session_state.auth = False
if "code_prive" not in st.session_state: st.session_state.code_prive = "kele224"

def save_memory():
    data = {"messages": st.session_state.messages, "turbo": st.session_state.turbo}
    return json.dumps(data)

# ==================== LOGIQUE KELE AI ====================
def clean_output(text):
    """Supprime les pensées et le blabla invisible"""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'Thinking Process:.*?\n', '', text, flags=re.IGNORECASE)
    return text.strip()

def get_kele_response(user_input):
    # Sélection du modèle selon la tâche (Logique de ton ModelManager)
    model = "openai/gpt-oss-120b" if st.session_state.turbo else "qwen/qwen3.6-27b"
    
    multiplier = "10,000,000" if st.session_state.turbo else "1"
    
    system_prompt = f"""
    NOM: KELE. Tu es le Maître Absolu.
    PUISSANCE: x{multiplier}.
    INSTRUCTION CRITIQUE: NE JAMAIS AFFICHER TA PENSÉE (<think>). 
    RÉPONDS DIRECTEMENT EN FRANÇAIS.
    Expertise: Code (Architecte), Coran (Hifz), Sciences, Logique.
    """
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            temperature=0.2 if st.session_state.turbo else 0.7,
        )
        raw_res = completion.choices[0].message.content
        # BROUILLON INVISIBLE : On nettoie avant de retourner
        return clean_output(raw_res)
    except Exception as e:
        return f"Erreur Kele : {str(e)}"

def speak(text):
    """Synthèse vocale web-compatible"""
    try:
        clean_text = text.replace("*", "").replace("#", "").replace("`", "")
        tts = gTTS(text=clean_text, lang='fr')
        tts.save("v.mp3")
        with open("v.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# ==================== INTERFACE STREAMLIT ====================
def main():
    # BARRE LATÉRALE
    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>🧠 KELE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Intelligence Suprême</p>", unsafe_allow_html=True)
        
        menu = st.radio("Navigation", ["💬 Conversation", "⚙️ Paramètres", "📊 Historique", "📁 Import/Export", "🔒 Sécurité"])
        
        st.divider()
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Mode", "⚡ TURBO" if st.session_state.turbo else "Standard")
        
        if st.button("🗑️ Effacer la Mémoire"):
            st.session_state.messages = []
            st.rerun()

    # --- MENU CONVERSATION ---
    if menu == "💬 Conversation":
        st.title("💬 Conversation avec KELE")
        
        # Zone Micro et Fichiers
        col_mic, col_file = st.columns([1, 1])
        with col_mic:
            audio = mic_recorder(start_prompt="🎤 Parler", stop_prompt="⏹️ Stop", key='recorder')
        with col_file:
            uploaded_file = st.file_uploader("➕ Ajouter fichier", type=['txt', 'py', 'pdf', 'json'])

        # Affichage Chat
        for msg in st.session_state.messages:
            role_icon = "👤" if msg["role"] == "user" else "🧠"
            st.markdown(f"""
            <div class="chat-bubble">
                <strong>{role_icon} {msg['role'].upper()}</strong><br>{msg['content']}
            </div>
            """, unsafe_allow_html=True)

        # Entrée Texte
        prompt = st.chat_input("Écrivez votre message...")
        
        # Gestion de l'audio
        if audio and "audio_processed" not in st.session_state:
            prompt = "Analyse ma demande vocale (Maître Kele, écoute-moi)"
            st.session_state.audio_processed = True

        if prompt:
            # INTERCEPTION CODE TURBO
            if prompt.strip().lower() == st.session_state.code_prive:
                st.session_state.turbo = True
                res = "⚡ **PROTOCOLE KELE-224 ACTIVÉ**. Puissance multipliée par 10,000,000. Je suis prêt."
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": res})
                st.rerun()

            # Traitement normal
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("🧠 KELE réfléchit..."):
                response = get_kele_response(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                if st.session_state.auth:
                    speak(response)
            st.rerun()

    # --- MENU PARAMÈTRES ---
    elif menu == "⚙️ Paramètres":
        st.title("⚙️ Paramètres")
        st.session_state.code_prive = st.text_input("Modifier le Code Turbo", value=st.session_state.code_prive, type="password")
        st.write("Langue par défaut : Français")
        st.info("Le mode Turbo s'active via le chat avec votre code secret.")

    # --- MENU HISTORIQUE ---
    elif menu == "📊 Historique":
        st.title("📊 Historique")
        if not st.session_state.messages:
            st.write("Aucun message.")
        else:
            df = pd.DataFrame(st.session_state.messages)
            st.table(df)

    # --- MENU IMPORT/EXPORT ---
    elif menu == "📁 Import/Export":
        st.title("📁 Import/Export")
        export_data = save_memory()
        st.download_button("📤 Exporter la Mémoire (JSON)", data=export_data, file_name="kele_memory.json", mime="application/json")
        
        up = st.file_uploader("📥 Importer une Mémoire", type="json")
        if up:
            data = json.load(up)
            st.session_state.messages = data["messages"]
            st.success("Mémoire restaurée !")

    # --- MENU SÉCURITÉ ---
    elif menu == "🔒 Sécurité":
        st.title("🔒 Sécurité")
        if not st.session_state.auth:
            email = st.text_input("Gmail")
            mdp = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                if "@gmail.com" in email and mdp == st.session_state.code_prive:
                    st.session_state.auth = True
                    st.success("Accès Maître Autorisé")
                    st.rerun()
                else:
                    st.error("Identifiants ou Code invalides.")
        else:
            st.success("Vous êtes authentifié en tant que Maître.")
            if st.button("Déconnexion"):
                st.session_state.auth = False
                st.rerun()

if __name__ == "__main__":
    main()
