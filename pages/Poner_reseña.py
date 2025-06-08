import streamlit as st
import folium
from streamlit_folium import st_folium
from google_sheets import leer_restaurantes, guardar_restaurantes

st.set_page_config(page_title="Añadir nuevo restaurante", layout="wide")

if "usuario" not in st.session_state or st.session_state["usuario"] is None:
    st.warning("Primero selecciona un usuario en la página principal.")
    st.stop()

usuario = st.session_state["usuario"]
col_voto = f"votos_{usuario}"
col_reseña = f"reseña_{usuario}"

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
                col_voto: puntuacion,
                col_reseña: reseña
            }

            restaurantes = leer_restaurantes()
            restaurantes = restaurantes.append(nuevo_restaurante, ignore_index=True)
            guardar_restaurantes(restaurantes)

            st.success("✅ Restaurante guardado correctamente.")
            st.session_state["ultimo_click"] = None
    else:
        st.info("Haz clic en el mapa para seleccionar la ubicación del restaurante.")

# =======================================
# 🔸 SECCIÓN 2: EDITAR EXISTENTE
# =======================================
st.subheader("✏️ Añadir o modificar tu reseña en un restaurante existente")

restaurantes = leer_restaurantes()

if restaurantes.empty:
    st.info("No hay restaurantes aún.")
    st.stop()

nombres = restaurantes["nombre"].tolist()
restaurante_seleccionado = st.selectbox("Selecciona un restaurante existente", nombres)

if restaurante_seleccionado:
    r = restaurantes[restaurantes["nombre"] == restaurante_seleccionado].iloc[0]

    st.markdown(f"**Tipo**: {r['tipo'].title()}")
    st.markdown(f"**Ubicación**: {r['lat']:.5f}, {r['lon']:.5f}")

    puntuacion_actual = r.get(col_voto, 3.0)
    reseña_actual = r.get(col_reseña, "")

    nueva_puntuacion = st.slider("Tu puntuación", 0.0, 5.0, float(puntuacion_actual), 0.25, key="editar_puntuacion")
    nueva_reseña = st.text_area("Tu reseña", value=reseña_actual, key="editar_reseña")

    if st.button("Guardar cambios", key="guardar_edicion"):
        restaurantes.loc[restaurantes["nombre"] == restaurante_seleccionado, col_voto] = nueva_puntuacion
        restaurantes.loc[restaurantes["nombre"] == restaurante_seleccionado, col_reseña] = nueva_reseña
        guardar_restaurantes(restaurantes)
        st.success("✅ Cambios guardados correctamente.")
