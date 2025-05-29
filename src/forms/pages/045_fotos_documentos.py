import streamlit as st
from src.forms.data_form import init_session_fields


def run():
    st.header("Fotos y documentos investigación")

    #with st.expander("Debug"):
    #    st.write(st.session_state)

    # Inicializar session_state para etiquetas y análisis
    if 'file_labels' not in st.session_state:
        st.session_state.file_labels = {}
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = {}

    # Widget para subir archivos
    uploaded_files = st.file_uploader(
        '📁 Fotos y documentos recopilados',
        type=['png', 'jpg', 'jpeg', 'pdf'],
        accept_multiple_files=True,
        key='fotos_accidente'
    )

    # Etiquetado manual de archivos
    if uploaded_files:
        st.subheader("🔖 Etiquetado de evidencias")
        for idx, file in enumerate(uploaded_files):
            unique_key = f"file_label_{idx}_{file.name}"

            # Etiqueta sugerida por IA
            suggested_label = ""

            # Widget para editar etiqueta
            label = st.text_input(
                f"Etiqueta para {file.name}",
                value=suggested_label,
                key=unique_key
            )

            # Almacenar en session_state
            st.session_state.file_labels[file.name] = {
                'label': label,
                'file_obj': file,
                'type': file.type
            }

    # Visualización de etiquetas
    if st.session_state.file_labels:
        st.divider()
        st.subheader("📚 Archivos etiquetados")

        for file_data in st.session_state.file_labels.values():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{file_data['label']}**")
            with col2:
                st.caption(f"Tipo: {file_data['type'].split('/')[-1].upper()} | "
                           f"Nombre: {file_data['file_obj'].name}")

    # Botón Siguiente
    if st.button('Guardar etiquetas y documentos'):
        st.success("Sección Declaraciones guardada")
        st.rerun()
