import streamlit as st
import requests

st.title("🔐 Detector de Cifrado con IA")
st.write("Introduce un texto para que la IA identifique el algoritmo.")

# Caja de texto para el usuario
texto_usuario = st.text_area("Texto a analizar:", "SGVsbG8gV29ybGQ=")

if st.button("Analizar con IA"):
    # Dirección de tu Endpoint (el que vimos en DevTools)
    url_endpoint = "http://127.0.0.1:8000/procesar"
    
    # Enlazamos con el Backend enviando el JSON
    payload = {"texto": texto_usuario}
    
    try:
        respuesta = requests.post(url_endpoint, json=payload)
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()
            st.success(f"🤖 Algoritmo detectado: **{resultado['algoritmo']}**")
            st.info(f"🔓 Intento de descifrado: {resultado['original']}")
        else:
            st.error("Error en la conexión con el servidor de IA.")
    except Exception as e:
        st.warning("Asegúrate de que el Backend (Uvicorn) esté encendido.")