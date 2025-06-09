import streamlit as st
import folium
from streamlit_folium import st_folium
from google_sheets import leer_restaurantes, guardar_restaurantes
import pandas as pd
import requests

st.set_page_config(page_title="Añadir nuevo restaurante", layout="wide")

# ========================
# 🔐 API Key de Google Maps
# ========================
if "google_maps_api_key" not in st.secrets:
    st.error("❌ No se encontró la clave 'google_maps_api_key' en los secrets.")
    st.stop()

API_KEY = st.secrets["google_maps_api_key"]


# ========================
# 🧠 Función de geocodificación
# ========================
def geocodificar_direccion(direccion, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": direccion, "key": api_key}
    response = requests.get(url, params=params)
    data = response.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None, None

# ========================
# 👤 Comprobar usuario
# ========================
if "usuario" not in st.session_state or st.session_state["usuario"] is None:
    st.warning("Primero selecciona un usuario en la página principal.")
    st.stop()

usuario = st.session_state["usuario"]
col_voto = f"votos_{usuario}"
col_reseña = f"reseña_{usuario}"

st.title("🗺️ Añadir o editar restaurante")

# ========================
# 🔍 Sidebar: Buscar restaurante
# ========================
st.sidebar.subheader("🔍 Buscar restaurante")

direccion = st.sidebar.text_input("Introduce nombre o dirección")

if st.sidebar.button("Buscar"):
    lat, lon = geocodificar_direccion(direccion, API_KEY)
    if lat and lon:
        st.session_state["ultimo_click"] = {"lat": lat, "lng": lon}
        st.sidebar.success(f"📍 Coordenadas: {lat:.5f}, {lon:.5f}")
    else:
        st.sidebar.error("Dirección no encontrada")

# ========================
# 🧭 Layout principal
# ========================
st.subheader("➕ Añadir nuevo restaurante")

with st.container():
    col_mapa, col_form = st.columns([3, 2])

    with col_mapa:
        m = folium.Map(location=[28.4636, -16.2518], zoom_start=11)

        # Mostrar marcador si hay coordenadas seleccionadas
        if st.session_state.get("ultimo_click"):
            lat = st.session_state["ultimo_click"]["lat"]
            lng = st.session_state["ultimo_click"]["lng"]
            folium.Marker([lat, lng], tooltip="Ubicación seleccionada").add_to(m)

        map_click = st_folium(m, width=700, height=500)

        if map_click.get("last_clicked"):
            st.session_state["ultimo_click"] = map_click["last_clicked"]

        # =============================
        # ✏️ Editar restaurante existente
        # =============================
        st.subheader("✏️ Editar restaurante existente")

        restaurantes = leer_restaurantes()

        if restaurantes.empty:
            st.info("No hay restaurantes aún.")
        else:
            nombres = restaurantes["nombre"].dropna().tolist()
            restaurante_seleccionado = st.selectbox("Selecciona un restaurante existente", nombres)

            if restaurante_seleccionado:
                r = restaurantes[restaurantes["nombre"] == restaurante_seleccionado].iloc[0]

                try:
                    lat = float(r["lat"])
                    lon = float(r["lon"])
                except:
                    lat = lon = 0.0

                st.markdown(f"**Tipo**: {r['tipo'].title()}")
                st.markdown(f"**Ubicación**: {lat:.5f}, {lon:.5f}")

                puntuacion_actual = float(r.get(col_voto, 3.0) or 3.0)
                reseña_actual = r.get(col_reseña, "")

                nueva_puntuacion = st.slider("Tu puntuación", 0.0, 5.0, puntuacion_actual, 0.25, key="editar_puntuacion")
                nueva_reseña = st.text_area("Tu reseña", value=reseña_actual, key="editar_reseña")

                if st.button("Guardar cambios", key="guardar_edicion"):
                    restaurantes.loc[restaurantes["nombre"] == restaurante_seleccionado, col_voto] = nueva_puntuacion
                    restaurantes.loc[restaurantes["nombre"] == restaurante_seleccionado, col_reseña] = nueva_reseña
                    guardar_restaurantes(restaurantes)
                    st.success("✅ Cambios guardados correctamente.")

    with col_form:
        if st.session_state.get("ultimo_click"):
            coords = st.session_state["ultimo_click"]
            lat = coords["lat"]
            lng = coords["lng"]

            st.success(f"📍 Coordenadas seleccionadas: {lat:.5f}, {lng:.5f}")

            nombre = st.text_input("Nombre del restaurante")
            tipo = st.text_input("Tipo de restaurante")
            puntuacion = st.slider("Tu puntuación", 0.0, 5.0, 3.0, 0.25, key="nueva_puntuacion")
            reseña = st.text_area("Tu reseña", key="nueva_reseña")

            if st.button("Guardar restaurante"):
                if not nombre or not tipo:
                    st.error("Por favor, completa el nombre y el tipo del restaurante.")
                else:
                    nuevo_restaurante = {
                        "nombre": nombre,
                        "tipo": tipo,
                        "lat": lat,
                        "lon": lng,
                        col_voto: puntuacion,
                        col_reseña: reseña
                    }

                    restaurantes = leer_restaurantes()
                    nuevo_df = pd.DataFrame([nuevo_restaurante])
                    restaurantes = pd.concat([restaurantes, nuevo_df], ignore_index=True)

                    guardar_restaurantes(restaurantes)
                    st.success("✅ Restaurante guardado correctamente.")
                    st.session_state["ultimo_click"] = None
        else:
            st.info("Haz clic en el mapa o busca un restaurante para seleccionarlo.")
