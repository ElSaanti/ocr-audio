import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

def translate_and_audio(text, in_lang, out_lang, tld):
    translator = Translator()
    translation = translator.translate(text, src=in_lang, dest=out_lang)
    trans_text = translation.text
    
    tts = gTTS(trans_text, lang=out_lang, tld=tld, slow=False)
    if not os.path.exists("temp"):
        os.mkdir("temp")
    
    fname = f"temp/audio_{int(time.time())}.mp3"
    tts.save(fname)
    return trans_text, fname

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    now = time.time()
    for f in mp3_files:
        if os.stat(f).st_mtime < now - (n * 86400):
            try: os.remove(f)
            except: pass

remove_files(7)

# --- INTERFAZ ---
st.title("🔍 OCR Audio")

# --- EXPANDER DE AYUDA ---
with st.expander("📖 Cómo usar este OCR", expanded=True):
    with col_t:
        st.markdown("""
        1. **Sube tu imagen** o usa la **cámara**.
        2. El texto aparecerá automáticamente en la sección **"Texto Original"**.
        3. Configura los idiomas en la **barra lateral**.
        4. Presiona **"Traducir y Procesar"** para ver la traducción y generar el audio.
        """)
    with col_i:
        try:
            st.image(Image.open('traductor.jpg'), use_container_width=True)
        except:
            st.write("🖼️")

st.divider()

# --- ENTRADA DE IMAGEN ---
cam_ = st.checkbox("📷 Activar Cámara")
img_file = None

if cam_:
    img_file = st.camera_input("Toma una foto al texto")
else:
    img_file = st.file_uploader("Sube una imagen (JPG/PNG)", type=["png", "jpg"])

# --- PROCESAMIENTO VISUAL ---
if img_file is not None:
    # Leer imagen
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # OCR
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    extracted_text = pytesseract.image_to_string(img_rgb)
    
    if extracted_text.strip():
        # MOSTRAR TEXTO ORIGINAL EN PANTALLA
        st.markdown('<div class="label">📄 Texto Original Detectado</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="text-box">{extracted_text}</div>', unsafe_allow_html=True)
        
        # --- CONFIGURACIÓN (SIDEBAR) ---
        with st.sidebar:
            st.header("⚙️ Configuración")
            langs = {"Inglés": "en", "Español": "es", "Francés": "fr", "Alemán": "de", "Italiano": "it", "Portugués": "pt"}
            
            in_lang = st.selectbox("Idioma del texto original", list(langs.keys()), index=1)
            out_lang = st.selectbox("Idioma a traducir", list(langs.keys()), index=0)
            
            accent_map = {"EE.UU (Default)": "com", "Reino Unido": "co.uk", "España": "es", "México": "com.mx"}
            accent = st.selectbox("Acento de voz", list(accent_map.keys()))
            
            btn_process = st.button("✨ Traducir y Procesar", use_container_width=True)

        # --- RESULTADO DE TRADUCCIÓN ---
        if btn_process:
            with st.spinner("Traduciendo texto..."):
                txt_traducido, audio_path = translate_and_audio(
                    extracted_text, 
                    langs[in_lang], 
                    langs[out_lang], 
                    accent_map[accent]
                )
                
                # MOSTRAR TRADUCCIÓN EN PANTALLA
                st.markdown('<div class="label">🌍 Traducción Visual</div>', unsafe_allow_html=True)
                st.success(txt_traducido)
                
                # REPRODUCTOR DE AUDIO
                st.markdown('<div class="label">🔊 Reproductor de voz</div>', unsafe_allow_html=True)
                with open(audio_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
    else:
        st.warning("No se pudo extraer texto claro de la imagen. Intenta con otra toma.")
