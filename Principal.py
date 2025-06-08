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

# Página principal con mapa + comparaciones
else:
    usuario = st.session_state["usuario"]
    st.sidebar.title(f"Usuario: {usuario}")

    from google_sheets import leer_restaurantes

    df = leer_restaurantes()

    tipos = sorted(df["tipo"].unique())
    tipo_seleccionado = st.sidebar.selectbox("Tipo de restaurante", ["Todo"] + tipos)

    if tipo_seleccionado != "Todo":
        df = df[df["tipo"] == tipo_seleccionado]

    # Columnas para mapa y comparaciones
    col_mapa, col_info = st.columns([1, 1])

    with col_mapa:
        st.markdown(f"## Mapa mostrando: {tipo_seleccionado}")
        m = folium.Map(location=[28.4636, -16.2518], zoom_start=11)

        for r in df.itertuples():
            claudia_score = r.votos.get("Claudia", "—")
            guillermo_score = r.votos.get("Guillermo", "—")
            tipo = r.tipo.title()

            popup = f"""
            <b>{r.nombre}</b><br>
            Tipo: {tipo}<br>
            Claudia ⭐: {claudia_score}<br>
            Guillermo ⭐: {guillermo_score}
            """
            folium.Marker(
                location=[r.lat, r.lon],
                popup=popup,
                tooltip=f"{r.nombre} ({r.tipo})"
            ).add_to(m)

        st_folium(m, width=700, height=500)

    with col_info:
        st.markdown(f"## 🔝 Nuestro Top 10 de {tipo_seleccionado} 🔝")

        top_claudia = sorted(
            [r for r in df.to_dict(orient="records") if r.get("votos", {}).get("Claudia", 0) > 0],
            key=lambda x: -x["votos"]["Claudia"]
        )[:10]

        top_guillermo = sorted(
            [r for r in df.to_dict(orient="records") if r.get("votos", {}).get("Guillermo", 0) > 0],
            key=lambda x: -x["votos"]["Guillermo"]
        )[:10]


        top_data = []
        for i in range(10):
            fila = {
                "Claudia (⭐)": f'{top_claudia[i]["nombre"]} ({top_claudia[i]["votos"].get("Claudia", "—")})' if i < len(top_claudia) else "",
                "Guillermo (⭐)": f'{top_guillermo[i]["nombre"]} ({top_guillermo[i]["votos"].get("Guillermo", "—")})' if i < len(top_guillermo) else ""
            }
            top_data.append(fila)

        top_df = pd.DataFrame(top_data)
        st.dataframe(top_df, use_container_width=True)

    # Comparación completa debajo
    st.markdown(f"## 📊 Comparación de puntuaciones y reseñas de {tipo_seleccionado}")
    comparacion_data = []
    for r in df.to_dict(orient="records"):
        comparacion_data.append({
            "Restaurante": r["nombre"],
            "Tipo": r["tipo"],
            "Claudia ⭐": r["votos"].get("Claudia", "—"),
            "Guillermo ⭐": r["votos"].get("Guillermo", "—"),
            "Claudia 📝": r["reseñas"].get("Claudia", "—"),
            "Guillermo 📝": r["reseñas"].get("Guillermo", "—")
        })

    comparacion_df = pd.DataFrame(comparacion_data)
    st.dataframe(comparacion_df, use_container_width=True)
