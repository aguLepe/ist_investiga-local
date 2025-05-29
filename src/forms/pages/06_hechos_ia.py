import streamlit as st
from src.ia.questions import QuestionManager
from src.forms.data_form import get_qm

def run():

    qm = get_qm()

    # Asegura la existencia de los flags que usaremos
    st.session_state.setdefault("form_hechos_guardado", False)
    st.session_state.setdefault("relatof", "")
    st.session_state.setdefault("hechos", "")

    st.header("Análisis de hechos")

    # Formulario = escribe / guarda el relato
    with st.form("form_hechos"):
        relatof_input = st.text_area(
            "Relato procesado por IA · revísalo antes de guardar",
            key="relatof_input",             # clave nueva (no pisa relatof hasta guardar)
            value=st.session_state.relatof,
            height=400
        )

        guardar = st.form_submit_button("Confirmar relato")

    # Acciones tras guardar
    if guardar:
        st.session_state.relatof = relatof_input
        st.session_state.form_hechos_guardado = True
        st.success("✅ Relato guardado. Ahora puedes identificar los hechos.")
        print(st.session_state.relatof)


    # Botón externo = identificar hechos (solo habilitado si ya se guardó)
    identificar_disabled = not st.session_state.form_hechos_guardado
    if st.button("Identificar hechos con IA", disabled=identificar_disabled, use_container_width=True):
        try:
            with st.spinner("Identificando hechos relevantes con IA..."):
                relatof = st.session_state.relatof
                st.session_state.hechos = qm.generar_pregunta(
                    "hechos",
                    relatof
                )
                st.session_state.form_hechos_guardado = False
        except Exception as e:
            if "Insufficient Balance" in str(e):
                st.warning("Usando fallback a OpenAI por saldo insuficiente en DeepSeek")
                st.session_state.hechos = qm.generar_pregunta("hechos_openai", relatof)
            else:
                raise e



    #Mostrar hechos (si existen) y botón Siguiente
    if st.session_state.hechos:
        st.text_area(
            "Hechos identificados",
            value=st.session_state.hechos,
            key="hechos_view",
            height=400
        )
        if st.button("Confirmar hechos", use_container_width=True):
            st.session_state.hechos = st.session_state.get('hechos_view', '')
            st.rerun()
