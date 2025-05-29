import streamlit as st
from src.forms.data_form import init_session_fields


def run():
    st.header("Declaraciones y entrevistas")


    # Declaración del accidentado
    st.session_state.declaracion_accidentado = st.text_area(
        "Declaración Accidentado/a*",
        st.session_state.get('declaracion_accidentado', ''),
        height=150
    )
    st.divider()

    # Testigo 1
    st.write("**Testigo 1**")
    st.session_state.decl1_nombre = st.text_input(
        "Nombre Testigo 1*",
        st.session_state.get('decl1_nombre', ''),
        help="Ej: Indica el nombre con dos apellidos"
    )
    st.session_state.decl1_cargo = st.text_input(
        "Cargo Testigo 1*",
        st.session_state.get('decl1_cargo', ''),
        help="Ej: Indica el cargo del testigo"
    )
    st.session_state.decl1_rut = st.text_input(
        "RUT Testigo 1*",
        st.session_state.get('decl1_rut', ''),
        help="Ej: Indica el rut del testigo"
    )
    st.session_state.decl1_texto = st.text_area(
        "Texto Declaración 1*",
        st.session_state.get('decl1_texto', ''),
    )

    st.divider()

    # Testigo 2
    st.write("**Testigo 2**")
    st.session_state.decl2_nombre = st.text_input(
        "Nombre Testigo 2*",
        st.session_state.get('decl2_nombre', ''),
        help="Ej: Indica el nombre con dos apellidos"
    )
    st.session_state.decl2_cargo = st.text_input(
        "Cargo Testigo 2*",
        st.session_state.get('decl2_cargo', ''),
        help="Ej: Indica el cargo del testigo"
    )
    st.session_state.decl2_rut = st.text_input(
        "RUT Testigo 2*",
        st.session_state.get('decl2_rut', ''),
        help="Ej: Indica el rut del testigo"
    )
    st.session_state.decl2_texto = st.text_area(
        "Texto Declaración 2*",
        st.session_state.get('decl2_texto', ''),
    )

    # Botón Siguiente
    if st.button('Guardar declaraciones'):
        st.success("Sección Declaraciones guardada")
        #st.session_state['_page'] = 5
        st.rerun()
