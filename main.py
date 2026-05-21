from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import math
import base64
import sqlite3
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = "app_data.db"

# 1. CREAR LA APLICACIÓN (Esto debe ir antes de cualquier @app)
app = FastAPI()

# 2. CONFIGURAR EL PERMISO (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. BASE DE DATOS

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entrada TEXT NOT NULL,
            algoritmo TEXT NOT NULL,
            resultado TEXT NOT NULL,
            fecha_hora TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def guardar_registro(entrada, algoritmo, resultado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO solicitudes (entrada, algoritmo, resultado, fecha_hora) VALUES (?, ?, ?, ?)",
        (entrada, algoritmo, resultado, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


init_database()

# 4. CARGAR EL MODELO
try:
    model = joblib.load("modelo_entrenado.pkl")
    print("✅ IA cargada correctamente")
except Exception as e:
    print(f"❌ Error cargando el modelo: {e}")

class Entrada(BaseModel):
    texto: str

# 4. FUNCIÓN DEL MOTOR
def extraer_17_caracteristicas(texto):
    n = len(texto)
    if n == 0: return np.zeros((1, 17))
    
    f1 = float(n)
    probs = [texto.count(c) / n for c in set(texto)]
    f2 = -sum(p * math.log2(p) for p in probs) if probs else 0
    f3 = sum(1 for c in texto if c.isupper()) / n
    f4 = sum(1 for c in texto if c.islower()) / n
    f5 = texto.count(' ') / n
    f6 = sum(1 for c in texto if c.isdigit()) / n
    f7 = (n - sum(1 for c in texto if c.isalnum())) / n 
    
    ascii_vals = [ord(c) for c in texto]
    f8 = float(min(ascii_vals)) if ascii_vals else 0
    f9 = float(max(ascii_vals)) if ascii_vals else 0
    f10 = sum(ascii_vals) / n
    f11 = sum((x - f10)**2 for x in ascii_vals) / n
    f12 = f4 / f3 if f3 > 0 else 0
    f13 = f5 / f1 if f1 > 0 else 0
    f14 = 1.0 if any(c.isdigit() for c in texto) else 0.0
    f15 = f2 / 8
    f16 = float(len(set(texto)))
    f17 = f16 / n
    
    return np.array([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16, f17]).reshape(1, -1)

def descifrar_mensaje(texto, algo_id):
    try:
        if algo_id == 3: # Base64
            return base64.b64decode(texto).decode('utf-8')
        if algo_id == 4: # Binario
            t_limpio = texto.replace(" ", "")
            return "".join([chr(int(t_limpio[i:i+8], 2)) for i in range(0, len(t_limpio), 8)])
        return texto 
    except:
        return "⚠️ Formato no compatible para descifrado automático."


@app.post("/procesar")
async def procesar(entrada: Entrada):
    datos = extraer_17_caracteristicas(entrada.texto)
    id_detectado = int(model.predict(datos)[0])
    
    nombres = {0: "Texto Plano", 1: "Sustitución", 2: "César", 3: "Base64", 4: "Binario"}
    
    resultado_descifrado = descifrar_mensaje(entrada.texto, id_detectado)
    respuesta = {
        "algoritmo": nombres.get(id_detectado, "Desconocido"),
        "original": resultado_descifrado
    }

    guardar_registro(entrada.texto, respuesta["algoritmo"], respuesta["original"])
    return respuesta


@app.get("/historial")
async def historial(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, entrada, algoritmo, resultado, fecha_hora FROM solicitudes ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    filas = cursor.fetchall()
    conn.close()
    return [
        {
            "id": fila[0],
            "entrada": fila[1],
            "algoritmo": fila[2],
            "resultado": fila[3],
            "fecha_hora": fila[4],
        }
        for fila in filas
    ]