import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from google_sheets import leer_restaurantes
from folium import Icon

st.set_page_config(page_title="Guía Gastronómica", layout="wide")
st.markdown("""
    <style>
    @media screen and (max-width: 768px) {
        iframe {
            height: 400px !important;
            max-height: 400px !important;
        }
        .element-container:has(iframe) {
            margin-bottom: -30px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

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

    # 🔹 Mapa + Top 10 en columnas
    with st.container():
        col_mapa, col_info = st.columns([3, 2])

        with col_mapa:
            titulo_tipo = tipo_seleccionado if tipo_seleccionado != "Todo" else "todos los restaurantes"
            st.markdown(f"## Mapa mostrando: {titulo_tipo}")
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
                        tooltip=f"{nombre} ({tipo})",
                        icon=Icon(icon='glyphicon glyphicon-map-marker', prefix='glyphicon')
                    ).add_to(m)

                except (ValueError, TypeError, KeyError):
                    continue

            st_folium(m, width="100%", height=400, returned_objects=[])

        with col_info:
            titulo_tipo_top = tipo_seleccionado if tipo_seleccionado != "Todo" else "todos los tipos"
            st.markdown(f"## 🔝 Nuestro Top 10 de {titulo_tipo_top} 🔝")

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
    # 🔸 Restaurantes deseados (nuevo)
    with st.expander("📍 Restaurantes que queremos visitar"):
        deseados = df[df.get("deseado", False).fillna(False) == True]

        if deseados.empty:
            st.info("No hay restaurantes marcados como deseados todavía.")
        else:
            st.dataframe(
                deseados[["nombre", "tipo", "lat", "lon"]],
                use_container_width=True
            )

    
    # 🔸 Comparación de reseñas (desplegable)
    titulo_tipo = f"de {tipo_seleccionado}" if tipo_seleccionado != "Todo" else ""
    with st.expander(f"📊 Comparación de puntuaciones y reseñas {titulo_tipo}"):

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
