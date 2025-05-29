import io
import streamlit as st
from graphviz import Source
from src.forms.data_form import get_qm
from src.models import causaltree as cst
from src.report.generator import InformeGenerator
from src.models.causaltree import getvalues
from src.forms.data_form import init_session_fields
from statsmodels.sandbox.regression.try_treewalker import data2

ig = InformeGenerator()

def run():
    qm = get_qm()
    st.header("Árbol de Causas")

    relatof = st.session_state.get('relatof')
    hechos  = st.session_state.get('hechos')

    if not st.session_state.get('arbol'):
        if st.button('Generar Árbol', use_container_width=True):
            with st.spinner("Generando arbol con IA.."):
                prompt = f"Relato: {relatof}\nHechos: {hechos}"
                st.session_state.arbol         = qm.generar_pregunta('arbol_causas', prompt)
                st.session_state.arbol_from_5q = st.session_state.arbol
                st.rerun()
    else:
        cst.main()

    if st.session_state.get('arbol') and st.button('Guardar Árbol', use_container_width=True):
        if st.session_state.nodes:
            # 1) Generar DOT y guardar el source
            cst.generate_dot()
            dot_code = st.session_state.arbol_dot

            dot_code = dot_code.replace('{', '{\n    graph [dpi=300];', 1)

            graph     = Source(dot_code)
            png_bytes = graph.pipe(format='png')
            img_buf   = io.BytesIO(png_bytes)
            img_buf.seek(0)

            st.session_state['cause_tree_img'] = img_buf
            st.image(img_buf, caption="Árbol de Causas", use_column_width=True)
            st.success("¡Árbol exportado y guardado en memoria!")
            st.session_state.selected_tool = "Ficha"
        else:
            st.warning("¡El árbol está vacío!")
        st.rerun()

    if st.session_state.get('cause_tree_img'):
        st.image(
            st.session_state['cause_tree_img'],
            caption="Árbol previo",
            use_column_width=True
        )
