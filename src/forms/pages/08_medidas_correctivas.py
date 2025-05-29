import streamlit as st
from src.forms.data_form import medidas_app_wrapper

def run():
    # Asegúrate de que la clave edited_measures siempre exista
    if 'edited_measures' not in st.session_state:
        st.session_state['edited_measures'] = []  # o {} según lo que uses

    st.header("Medidas Correctivas")


    # Llamada a la función de medidas correctivas
    status = medidas_app_wrapper()
    if status:
        st.success("Se generaron las medidas correctamente.")

    if st.button("Guardar medidas correctivas", disabled = not status, use_container_width=True):
        st.success("Se guardaron las medidas correctamente.")

