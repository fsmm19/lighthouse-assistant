import streamlit as st
from core.model import get_model_response


def render_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Agregar mensaje al historial cuando se carga un nuevo reporte
    if st.session_state.get("report_loaded", False):
        num_reports = len(st.session_state.get("lighthouse_reports", {}))
        report_names = list(st.session_state.get("lighthouse_reports", {}).keys())

        if num_reports == 1:
            msg = f"📊 Reporte cargado: **{report_names[0]}**. Ahora puedes preguntarme sobre el análisis."
        else:
            msg = f"📊 {num_reports} reportes cargados. Puedo analizar cualquiera de ellos."

        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.report_loaded = False

    # Agregar mensaje al historial cuando se elimina un reporte
    if st.session_state.get("report_removed", False):
        remaining = len(st.session_state.get("lighthouse_reports", {}))
        if remaining > 0:
            msg = f"🗑️ Reporte eliminado. Quedan {remaining} reporte(s) cargado(s)."
        else:
            msg = "🗑️ Reporte eliminado. No hay reportes cargados actualmente."

        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.report_removed = False

    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                # Obtener reportes cargados si existen
                lighthouse_reports = st.session_state.get("lighthouse_reports", {})

                # Obtener temperatura del slider (default 0.7)
                temperature = st.session_state.get("temperature", 0.7)
                print(f"[DEBUG] Temperatura obtenida del session_state: {temperature}")

                response = get_model_response(
                    st.session_state.messages, lighthouse_reports, temperature
                )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
