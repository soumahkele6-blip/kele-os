import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Chargement de la clé API (via .env en local ou Secrets sur GitHub)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuration du client OpenAI pour utiliser Groq
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

st.set_page_config(page_title="AI Quran & Reciters", page_icon="🌙")

st.title("🌙 Coran AI avec Modèles Spécialisés")

# --- SIDEBAR : SÉLECTION DU RÉCITATEUR ---
st.sidebar.header("Configuration")
edition_choice = st.sidebar.selectbox("Choisir un récitateur", [
    ("Mishary Rashid Alafasy", "ar.alafasy"),
    ("Abdul Basit Murattal", "ar.abdulsamad"),
    ("Abdurrahmaan As-Sudais", "ar.asudais"),
    ("Ahmed Al-Ajmy", "ar.ahmedajamy")
])

# --- SÉLECTION DES MODÈLES ---
ai_model = st.sidebar.selectbox("Modèle d'IA pour le Tafsir", [
    "openai/gpt-oss-120b",
    "qwen/qwen3.6-27b",
    "allam-2-7b",
    "groq/compound"
])

# --- CONTENU PRINCIPAL ---
surah = st.number_input("Numéro de la Sourate (1-114)", min_value=1, max_value=114, value=1)
ayah = st.number_input("Numéro du Verset", min_value=1, max_value=286, value=1)

if st.button("Afficher le Verset et l'Audio"):
    # Appel à l'API AlQuran.cloud
    res = requests.get(f"http://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{edition_choice[1]}")
    if res.status_code == 200:
        data = res.json()['data']
        
        st.subheader(f"Sourate {data['surah']['name']} - Verset {ayah}")
        st.write(f"### {data['text']}")
        st.audio(data['audio'])
        
        # --- ANALYSE PAR L'IA ---
        with st.spinner(f"Analyse avec {ai_model}..."):
            # Sécurité (Prompt Guard)
            guard_check = client.chat.completions.create(
                model="meta-llama/llama-prompt-guard-2-86m",
                messages=[{"role": "user", "content": data['text']}]
            )
            
            # Tafsir / Explication
            response = client.chat.completions.create(
                model=ai_model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en exégèse coranique utilisant le modèle Allam pour le contexte arabe et les modèles Orpheus pour la précision linguistique."},
                    {"role": "user", "content": f"Donne-moi le Tafsir (explication) et les leçons à tirer de ce verset : {data['text']}"}
                ]
            )
            
            st.markdown("---")
            st.markdown("### 📖 Explication de l'IA")
            st.write(response.choices[0].message.content)
    else:
        st.error("Verset non trouvé ou erreur de l'API.")

# --- TRANSCRIPTION AUDIO (Whisper) ---
st.markdown("---")
st.subheader("🎤 Pratiquer la récitation")
audio_file = st.file_uploader("Enregistrez votre récitation (mp3/wav)", type=['mp3', 'wav'])

if audio_file:
    with st.spinner("Transcription par Whisper-turbo..."):
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file
        )
        st.write("Vous avez dit :")
        st.info(transcription.text)
