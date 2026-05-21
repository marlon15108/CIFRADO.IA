import streamlit as st
import joblib
import numpy as np
import math
import base64

st.set_page_config(page_title="Detector de Cifrado IA", layout="centered")

st.title("🔐 Detector de Cifrado con IA")
st.write("Introduce un texto para que la IA identifique el algoritmo y lo intente descifrar.")

@st.cache_resource
def cargar_modelo():
    try:
        return joblib.load("modelo_entrenado.pkl")
    except Exception as e:
        st.error(f"Error cargando el modelo: {e}")
        return None


def extraer_17_caracteristicas(texto):
    n = len(texto)
    if n == 0:
        return np.zeros((1, 17))

    f1 = float(n)
    probs = [texto.count(c) / n for c in set(texto)]
    f2 = -sum(p * math.log2(p) for p in probs) if probs else 0
    f3 = sum(1 for c in texto if c.isupper()) / n
    f4 = sum(1 for c in texto if c.islower()) / n
    f5 = texto.count(" ") / n
    f6 = sum(1 for c in texto if c.isdigit()) / n
    f7 = (n - sum(1 for c in texto if c.isalnum())) / n

    ascii_vals = [ord(c) for c in texto]
    f8 = float(min(ascii_vals)) if ascii_vals else 0
    f9 = float(max(ascii_vals)) if ascii_vals else 0
    f10 = sum(ascii_vals) / n
    f11 = sum((x - f10) ** 2 for x in ascii_vals) / n
    f12 = f4 / f3 if f3 > 0 else 0
    f13 = f5 / f1 if f1 > 0 else 0
    f14 = 1.0 if any(c.isdigit() for c in texto) else 0.0
    f15 = f2 / 8
    f16 = float(len(set(texto)))
    f17 = f16 / n

    return np.array([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17]).reshape(1, -1)


def descifrar_mensaje(texto, algo_id):
    try:
        if algo_id == 3:  # Base64
            return base64.b64decode(texto).decode("utf-8")
        if algo_id == 4:  # Binario
            t_limpio = texto.replace(" ", "")
            return "".join([chr(int(t_limpio[i:i+8], 2)) for i in range(0, len(t_limpio), 8)])
        return texto
    except Exception:
        return "⚠️ Formato no compatible para descifrado automático."


def detectar_algoritmo(texto, model):
    datos = extraer_17_caracteristicas(texto)
    id_detectado = int(model.predict(datos)[0])
    nombres = {0: "Texto Plano", 1: "Sustitución", 2: "César", 3: "Base64", 4: "Binario"}
    algoritmo = nombres.get(id_detectado, "Desconocido")
    mensaje = descifrar_mensaje(texto, id_detectado)
    return algoritmo, mensaje


modelo = cargar_modelo()
texto_usuario = st.text_area("Texto a analizar:", "SGVsbG8gV29ybGQ=")

if st.button("Analizar con IA"):
    if not modelo:
        st.error("No se pudo cargar el modelo. Revisa el archivo modelo_entrenado.pkl.")
    elif len(texto_usuario.strip()) == 0:
        st.warning("Escribe un texto antes de analizar.")
    else:
        algoritmo, original = detectar_algoritmo(texto_usuario, modelo)
        st.success(f"🤖 Algoritmo detectado: **{algoritmo}**")
        st.info(f"🔓 Intento de descifrado: {original}")
