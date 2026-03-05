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

# --- CONFIGURACIÓN DE PÁGINA ESTILO NOTION ---
st.set_page_config(page_title="OCR & Traductor Shiny", page_icon="📄", layout="centered")

# CSS para mantener la estética Notion
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #37352f; }
    .stAlert { border-radius: 10px; border: 1px solid #edeef0; background-color: #f7f6f3; }
    .stButton>button { border-radius: 6px; border: 1px solid #e0e0e0; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
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

# --- INTERFAZ PRINCIPAL ---
st.title("📄 Reconocimiento Óptico (OCR)")
st.caption("Extrae texto de imágenes y tradúcelo automáticamente.")

# --- EXPANDER: CÓMO USAR ---
with st.expander("📖 Guía de uso rápido", expanded=True):
    col_text, col_img = st.columns([2, 1])
    with col_text:
        st.markdown("""
        **Sigue estos pasos:**
        1. **Elige la fuente**: Activa la cámara o sube un archivo (JPG/PNG).
        2. **Procesamiento**: El sistema extraerá el texto de la imagen automáticamente.
        3. **Traducción**: En la barra lateral, elige los idiomas y acentos.
        4. **Audio**: Haz clic en **Convert** para escuchar la traducción.
        """)
    with col_img:
        try:
            # Aquí se intenta cargar tu imagen previa
            image = Image.open('traductor.jpg')
            st.image(image, use_container_width=True)
        except:
            st.write("🖼️") # Icono de respaldo

st.write("---")

# --- LÓGICA DE CAPTURA ---
text = "" # Inicializar variable de texto

cam_ = st.checkbox("Usar Cámara")
if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.header("⚙️ Ajustes")
    st.subheader("Cámara")
    filtro = st.radio("Filtro para imagen", ('No', 'Sí'))

bg_image = st.file_uploader("O carga una imagen desde tu equipo:", type=["png", "jpg"])

# Procesamiento de imagen cargada
if bg_image is not None:
    st.image(bg_image, caption='Imagen cargada.', use_container_width=True)
    with open(bg_image.name, 'wb') as f:
        f.write(bg_image.read())
    
    img_cv = cv2.imread(bg_image.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Procesamiento de cámara
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
        
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

# Mostrar texto extraído
if text:
    st.markdown("##### 📝 Texto extraído:")
    st.info(text)

# --- BARRA LATERAL: TRADUCCIÓN ---
with st.sidebar:
    st.divider()
    st.subheader("Parámetros de traducción")
    
    in_lang = st.selectbox("Idioma de entrada", ("Español", "Ingles", "Bengali", "koreano", "Mandarin", "Japones"))
    out_lang = st.selectbox("Idioma de salida", ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"))
    
    langs = {"Ingles": "en", "Español": "es", "Bengali": "bn", "koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}
    
    english_accent = st.selectbox("Seleccione el acento", 
        ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"))
    
    tlds = {"Default": "com", "India": "co.in", "United Kingdom": "co.uk", "United States": "com", 
            "Canada": "ca", "Australia": "com.au", "Ireland": "ie", "South Africa": "co.za"}
    
    display_output_text = st.checkbox("Mostrar texto traducido", value=True)

    if st.button("Convertir a Audio ✨"):
        if text.strip():
            result, output_text = text_to_speech(langs[in_lang], langs[out_lang], text, tlds[english_accent])
            
            st.audio(f"temp/{result}.mp3", format="audio/mp3")
            if display_output_text:
                st.markdown("**Traducción:**")
                st.write(output_text)
        else:
            st.error("No se detectó texto para traducir.")
