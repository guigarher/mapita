import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from google_sheets import leer_restaurantes

st.set_page_config(page_title="Guía Gastronómica", layout="wide")

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# Selección de usuario
if st.session_state["usuario"] is None:
    st.title("🍽️ Nuestro Letterboxd de Restaurantes")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👩 Claudia", use_container_width=True):
            st.session_state["usuario"] = "Claudia"
            st.rerun()
    with col2:
        if st.button("🧑 Guillermo", use_container_width=True):
            st.session_state["usuario"] = "Guillermo"
            st.rerun()

else:
    usuario = st.session_state["usuario"]
    st.sidebar.title(f"Usuario: {usuario}")

    df = leer_restaurantes()

    tipos = sorted(df["tipo"].dropna().unique())
    tipo_seleccionado = st.sidebar.selectbox("Tipo de restaurante", ["Todo"] + tipos)

    if tipo_seleccionado != "Todo":
        df = df[df["tipo"] == tipo_seleccionado]

    # Agrupamos mapa y top 10 en un contenedor
    col_mapa, col_info = st.columns([2, 1])

    with col_mapa:
            # Comparación completa 
            st.markdown(f"## 📊 Comparación de puntuaciones y reseñas de {tipo_seleccionado}")
            comparacion_data = []
            for _, row in df.iterrows():
                comparacion_data.append({
                    "Restaurante": row.get("nombre"),
                    "Tipo": row.get("tipo"),
                    "Claudia ⭐": row.get("votos_Claudia", "—"),
                    "Guillermo ⭐": row.get("votos_Guillermo", "—"),
                    "Claudia 📝": row.get("reseña_Claudia", "—"),
                    "Guillermo 📝": row.get("reseña_Guillermo", "—")
                })

            comparacion_df = pd.DataFrame(comparacion_data)
            st.dataframe(comparacion_df, use_container_width=True) 

            st.markdown(f"## Mapa mostrando: {tipo_seleccionado}")
            m = folium.Map(location=[28.4636, -16.2518], zoom_start=11)

            for _, r in df.iterrows():
                try:
                    lat = float(r["lat"])
                    lon = float(r["lon"])
                    nombre = r["nombre"]
                    tipo = r["tipo"]

                    puntuacion_claudia = r.get("votos_Claudia", "—")
                    puntuacion_guillermo = r.get("votos_Guillermo", "—")
                    reseña_claudia = r.get("reseña_Claudia", "")
                    reseña_guillermo = r.get("reseña_Guillermo", "")

                    popup_html = f"""
                    <strong>{nombre}</strong><br>
                    Tipo: {tipo}<br>
                    Claudia: ⭐ {puntuacion_claudia} <br>
                    Guillermo: ⭐ {puntuacion_guillermo} <br>
                    <hr style='margin:4px 0'>
                    <small><em>Claudia:</em> {reseña_claudia}</small><br>
                    <small><em>Guillermo:</em> {reseña_guillermo}</small>
                    """
                    popup = folium.Popup(popup_html, max_width=300)
                    folium.Marker(
                        location=[lat, lon],
                        popup=popup,
                        tooltip=f"{nombre} ({tipo})"
                    ).add_to(m)

                except (ValueError, TypeError, KeyError):
                    continue

            st_folium(m, width=700, height=500)   

    with col_info:
            st.markdown(f"## 🔝 Nuestro Top 10 de {tipo_seleccionado} 🔝")

            top_claudia = df[pd.to_numeric(df["votos_Claudia"], errors="coerce") > 0].copy()
            top_guillermo = df[pd.to_numeric(df["votos_Guillermo"], errors="coerce") > 0].copy()

            top_claudia["votos_Claudia"] = pd.to_numeric(top_claudia["votos_Claudia"], errors="coerce")
            top_guillermo["votos_Guillermo"] = pd.to_numeric(top_guillermo["votos_Guillermo"], errors="coerce")

            top_claudia = top_claudia.sort_values(by="votos_Claudia", ascending=False).head(10)
            top_guillermo = top_guillermo.sort_values(by="votos_Guillermo", ascending=False).head(10)

            top_data = []
            for i in range(10):
                fila = {
                    "Claudia (⭐)": f'{top_claudia.iloc[i]["nombre"]} ({top_claudia.iloc[i]["votos_Claudia"]})' if i < len(top_claudia) else "",
                    "Guillermo (⭐)": f'{top_guillermo.iloc[i]["nombre"]} ({top_guillermo.iloc[i]["votos_Guillermo"]})' if i < len(top_guillermo) else ""
                }
                top_data.append(fila)

            top_df = pd.DataFrame(top_data)
            st.dataframe(top_df, use_container_width=True)

    
