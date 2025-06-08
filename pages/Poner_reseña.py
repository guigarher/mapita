import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(page_title="Añadir nuevo restaurante", layout="wide")

if "usuario" not in st.session_state or st.session_state["usuario"] is None:
    st.warning("Primero selecciona un usuario en la página principal.")
    st.stop()

usuario = st.session_state["usuario"]

st.title("🗺️ Añadir o editar restaurante")

# ===========================
# 🔹 SECCIÓN 1: AÑADIR NUEVO
# ===========================
st.subheader("➕ Añadir nuevo restaurante (clic en el mapa)")

col_mapa, col_form = st.columns([2, 1])

with col_mapa:
    m = folium.Map(location=[28.4636, -16.2518], zoom_start=11)
    map_click = st_folium(m, width=700, height=500)

    if map_click.get("last_clicked"):
        st.session_state["ultimo_click"] = map_click["last_clicked"]

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
            nuevo_restaurante = {
                "nombre": nombre,
                "tipo": tipo,
                "lat": lat,
                "lon": lng,
                "votos": {
                    usuario: puntuacion
                },
                "reseñas": {
                    usuario: reseña
                }
            }

            try:
                with open("restaurantes.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"restaurantes": []}

            data["restaurantes"].append(nuevo_restaurante)

            with open("restaurantes.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            st.success("✅ Restaurante guardado correctamente.")
            st.session_state["ultimo_click"] = None
    else:
        st.info("Haz clic en el mapa para seleccionar la ubicación del restaurante.")


# =======================================
# 🔸 SECCIÓN 2: EDITAR EXISTENTE
# =======================================
st.subheader("✏️ Añadir o modificar tu reseña en un restaurante existente")

try:
    with open("restaurantes.json", "r", encoding="utf-8") as f:
        data = json.load(f)["restaurantes"]
except FileNotFoundError:
    data = []

nombres = [r["nombre"] for r in data]
restaurante_seleccionado = st.selectbox("Selecciona un restaurante existente", nombres)

if restaurante_seleccionado:
    restaurante = next((r for r in data if r["nombre"] == restaurante_seleccionado), None)

    if restaurante:
        st.markdown(f"**Tipo**: {restaurante['tipo'].title()}")
        st.markdown(f"**Ubicación**: {restaurante['lat']:.5f}, {restaurante['lon']:.5f}")

        puntuacion_actual = restaurante.get("votos", {}).get(usuario, 3.0)
        reseña_actual = restaurante.get("reseñas", {}).get(usuario, "")

        nueva_puntuacion = st.slider("Tu puntuación", 0.0, 5.0, puntuacion_actual, 0.25, key="editar_puntuacion")
        nueva_reseña = st.text_area("Tu reseña", value=reseña_actual, key="editar_reseña")

        if st.button("Guardar cambios", key="guardar_edicion"):
            restaurante.setdefault("votos", {})[usuario] = nueva_puntuacion
            restaurante.setdefault("reseñas", {})[usuario] = nueva_reseña

            with open("restaurantes.json", "w", encoding="utf-8") as f:
                json.dump({"restaurantes": data}, f, ensure_ascii=False, indent=4)

            st.success("✅ Cambios guardados correctamente.")
