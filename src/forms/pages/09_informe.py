import streamlit as st
from src.forms.data_form import export_docx_wrapper
from src.forms.data_form import init_session_fields
from src.forms.data_form import get_qm
import datetime

def run():
    st.header("Informe investigación")
    qm = get_qm()

    # Datos básicos del informe (sin formulario)
    st.session_state.informe_numero = st.text_input(
        'Informe N°*',
        st.session_state.get('informe_numero', ''),
        help="Ej: INF-2024-001"
    )

    st.session_state.investigador = st.text_input(
        'Investigador*',
        st.session_state.get('investigador', ''),
        help="Nombre completo del investigador responsable"
    )

    st.session_state.fecha_informe = st.date_input(
        'Fecha Informe',
        st.session_state.get('fecha_informe', datetime.date.today())
    )

    if st.button("Generar informe"):
        try:
            with st.spinner("Generando informe..."):
                st.session_state.setdefault('resumen', None)
                if not st.session_state.resumen:
                        st.session_state.resumen = qm.generar_pregunta(
                            "resumen",
                            st.session_state.relatof
                        )
                    # Llamada al wrapper que genera y despliega el documento
                export_docx_wrapper()
                st.success('Informe generado correctamente')
        except Exception as e:
            st.error(f'Error al generar informe: {e}')





