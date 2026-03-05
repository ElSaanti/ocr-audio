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

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="OCR & Traductor", layout="centered")

def text_to_speech(input_language, output_language, text, tld):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    
    if not os.path.exists("temp"):
        os.mkdir("temp")
    
    my_file_name = f"audio_{int(time.time())}"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# --- INTERFAZ ---
st.title("Reconocimiento Óptico de Caracteres")

# 1. EXPANDER DE INSTRUCCIONES
with st.expander("📖 Cómo usar este traductor", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        **Sigue estos pasos:**
        1. **Captura:** Selecciona 'Usar Cámara' o sube una imagen desde tu equipo.
        2. **Procesamiento:** El sistema leerá el texto de la imagen automáticamente.
        3. **Traducción:** En el panel izquierdo, elige los idiomas y el acento.
        4. **Audio:** Haz clic en el botón 'Convertir' para generar la voz.
        """)

st.divider()

# 2. SELECCIÓN DE FUENTE
st.subheader("Elige la fuente de la imagen")
cam_ = st.checkbox(" 📷 Usar Cámara")

text = "" # Inicializamos la variable

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
    # MENSAJE DE SUGERENCIA DEBAJO DE LA CÁMARA
    st.info("🔍 **Sugerencia:** Busca un libro, una etiqueta o un cartel con texto claro para probar el OCR.")
else:
    img_file_buffer = None

bg_image = st.file_uploader("O carga una imagen desde tu PC:", type=["png", "jpg"])

# --- LÓGICA DE PROCESAMIENTO ---
with st.sidebar:
    st.subheader("Configuración")
    filtro = st.radio("Filtro para imagen (Cámara)", ('No', 'Sí'))

# Procesar imagen cargada
if bg_image is not None:
    st.image(bg_image, caption='Imagen cargada.', use_container_width=True)
    img_cv = cv2.imdecode(np.frombuffer(bg_image.read(), np.uint8), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Procesar imagen de cámara
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Mostrar texto extraído
if text:
    st.markdown("### Texto detectado:")
    st.code(text)

# --- PANEL LATERAL: TRADUCCIÓN ---
with st.sidebar:
    st.divider()
    st.subheader("Parámetros de traducción")
    
    langs = {"Ingles": "en", "Español": "es", "Bengali": "bn", "koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}
    
    in_lang = st.selectbox("Idioma de entrada", list(langs.keys()), index=1)
    out_lang = st.selectbox("Idioma de salida", list(langs.keys()), index=0)
    
    english_accent = st.selectbox("Seleccione el acento", 
        ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"))
    
    tlds = {"Default": "com", "India": "co.in", "United Kingdom": "co.uk", "United States": "com", "Canada": "ca", "Australia": "com.au", "Ireland": "ie", "South Africa": "co.za"}

    display_output_text = st.checkbox("Mostrar texto traducido", value=True)

    if st.button("Convertir ✨"):
        if text.strip():
            with st.spinner("Traduciendo y generando audio..."):
                res_file, output_text = text_to_speech(langs[in_lang], langs[out_lang], text, tlds[english_accent])
                
                st.audio(f"temp/{res_file}.mp3", format="audio/mp3")
                if display_output_text:
                    st.markdown("**Traducción:**")
                    st.write(output_text)
        else:
            st.error("No se ha detectado ningún texto para traducir.")
