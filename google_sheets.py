import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd

SHEET_NAME = "restaurantes_data"

@st.cache_resource
def conectar_hoja():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_dict = json.loads(st.secrets["google_auth"]["credentials"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    cliente = gspread.authorize(creds)
    hoja = cliente.open(SHEET_NAME).sheet1
    return hoja

def leer_restaurantes():
    hoja = conectar_hoja()
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)

    # 🔧 Forzar tipo booleano en la columna 'deseado'
    if "deseado" in df.columns:
        df["deseado"] = df["deseado"].astype(str).str.lower() == "true"

    return df


def guardar_restaurantes(df):
    hoja = conectar_hoja()
    hoja.clear()
    hoja.append_row(list(df.columns))
    hoja.append_rows(df.fillna("").astype(str).values.tolist())

