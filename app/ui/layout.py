import streamlit as st
import json


def render_layout():
    st.set_page_config(page_title="Google Lighthouse Assistant", layout="wide")

    st.title("Asistente :blue[Google Lighthouse]")

    with st.sidebar:
        st.subheader("⚙️ Configuración del Modelo")

        # Control de temperatura
        temperature = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controla la creatividad del modelo. Valores bajos (0.1-0.3) son más precisos y determinísticos. Valores altos (0.8-1.5) son más creativos y variados."
        )

        # Guardar en session_state
        st.session_state.temperature = temperature

        # Indicador visual de temperatura actual
        if temperature <= 0.3:
            temp_label = "🎯 Preciso y determinístico"
        elif temperature <= 0.7:
            temp_label = "⚖️ Balanceado"
        else:
            temp_label = "🎨 Creativo y variado"

        st.caption(f"Temperatura actual: **{temperature}** - {temp_label}")

        st.divider()

        st.subheader("📄 Reportes Lighthouse")

        uploaded_files = st.file_uploader(
            "Carga tus reportes JSON", type="json", accept_multiple_files=True
        )

        # Procesar archivos subidos
        if uploaded_files:
            if "lighthouse_reports" not in st.session_state:
                st.session_state.lighthouse_reports = {}

            # Cargar nuevos reportes
            for uploaded_file in uploaded_files:
                try:
                    report_data = json.load(uploaded_file)
                    file_name = uploaded_file.name

                    # Solo agregar si es nuevo o diferente
                    if file_name not in st.session_state.lighthouse_reports:
                        st.session_state.lighthouse_reports[file_name] = report_data
                        st.session_state.report_loaded = True

                except json.JSONDecodeError:
                    st.error(f"Error al leer {uploaded_file.name}: no es un JSON válido")

        # Mostrar reportes cargados
        if "lighthouse_reports" in st.session_state and st.session_state.lighthouse_reports:
            st.success(f"✅ {len(st.session_state.lighthouse_reports)} reporte(s) cargado(s)")

            # Listar reportes con opción de eliminar
            for file_name in list(st.session_state.lighthouse_reports.keys()):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"📄 {file_name}")
                with col2:
                    if st.button("🗑️", key=f"delete_{file_name}"):
                        del st.session_state.lighthouse_reports[file_name]
                        st.session_state.report_removed = True
                        st.rerun()
        else:
            st.info("No hay reportes cargados")
