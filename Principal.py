import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

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

    from google_sheets import leer_restaurantes
    df = leer_restaurantes()

    tipos = sorted(df["tipo"].dropna().unique())
    tipo_seleccionado = st.sidebar.selectbox("Tipo de restaurante", ["Todo"] + tipos)

    if tipo_seleccionado != "Todo":
        df = df[df["tipo"] == tipo_seleccionado]

    # Mapa
    col_mapa, col_info = st.columns([1, 1])

    with col_mapa:
        st.markdown(f"## Mapa mostrando: {tipo_seleccionado}")
        m = folium.Map(location=[28.4636, -16.2518], zoom_start=11)

        for _, row in df.iterrows():
            claudia_score = row.get("votos_Claudia", "—")
            guillermo_score = row.get("votos_Guillermo", "—")
            tipo = str(row.get("tipo", "")).title()
            nombre = row.get("nombre", "¿?")
            lat = row.get("lat")
            lon = row.get("lon")

            popup = f"""
            <b>{nombre}</b><br>
            Tipo: {tipo}<br>
            Claudia ⭐: {claudia_score}<br>
            Guillermo ⭐: {guillermo_score}
            """
            folium.Marker(
                location=[lat, lon],
                popup=popup,
                tooltip=f"{nombre} ({tipo})"
            ).add_to(m)

        st_folium(m, width=700, height=500)

    # Top 10
    with col_info:
        st.markdown(f"## 🔝 Nuestro Top 10 de {tipo_seleccionado} 🔝")

        top_claudia = df[df["votos_Claudia"] > 0].sort_values(by="votos_Claudia", ascending=False).head(10)
        top_guillermo = df[df["votos_Guillermo"] > 0].sort_values(by="votos_Guillermo", ascending=False).head(10)

        top_data = []
        for i in range(10):
            fila = {
                "Claudia (⭐)": f'{top_claudia.iloc[i]["nombre"]} ({top_claudia.iloc[i]["votos_Claudia"]})' if i < len(top_claudia) else "",
                "Guillermo (⭐)": f'{top_guillermo.iloc[i]["nombre"]} ({top_guillermo.iloc[i]["votos_Guillermo"]})' if i < len(top_guillermo) else ""
            }
            top_data.append(fila)

        top_df = pd.DataFrame(top_data)
        st.dataframe(top_df, use_container_width=True)

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
