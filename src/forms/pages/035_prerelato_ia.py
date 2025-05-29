#035_prerelato_ia.py
import streamlit as st
from src.forms.data_form import get_qm
from src.ia.questions import InvestigationApp
import json
from datetime import datetime


def run():
    qm = get_qm()

    #with st.expander("Debug Técnico"):
    #    st.json({
    #        "session_state": dict(st.session_state),
    #        "secrets_keys": list(st.secrets.keys()),
    #        "active_model": qm.current_model if hasattr(qm, "current_model") else "n/d"
    #    })

    # Flags que usaremos
    st.session_state.setdefault("prerelato_form_guardado", False)

    st.header("Evaluación de antecedentes")

    qm = get_qm()

    if st.button("Evaluar antecedentes con IA y generar preguntas guía"):
        # Construir prompt inicial estructurado
        if not st.session_state.get("initial_story"):
            # Convertir fechas/horas a strings serializables
            fecha_accidente = st.session_state.fecha_accidente.isoformat() if hasattr(
                st.session_state.fecha_accidente, 'isoformat') else str(st.session_state.fecha_accidente)
            hora_accidente = st.session_state.hora_accidente.isoformat() if hasattr(st.session_state.hora_accidente,
                                                                                    'isoformat') else str(
                st.session_state.hora_accidente)

            preinitial_data = {
                "datos_generales": {
                    "nombre_accidentado": st.session_state.nombre_trabajador,
                    "fecha": fecha_accidente,
                    "hora": hora_accidente,
                    "actividad": st.session_state.actividad,
                    "local": st.session_state.nombre_local,
                    "lugar_accidente": st.session_state.lugar_accidente,
                    "lesion": st.session_state.naturaleza_lesion
                },
                "operaciones": {
                    "tarea": st.session_state.tarea,
                    "operacion": st.session_state.operacion
                },
                "contexto": {
                    "general": st.session_state.contexto,
                    "circunstancias": st.session_state.circunstancias
                }
            }

            st.session_state.preinitial_story = json.dumps(preinitial_data, ensure_ascii=False, indent=2)

            prompt = (
                f"Antecedentes: {st.session_state.preinitial_story}\n"
            )

            # Generar relato inicial con manejo de modelo
            with st.spinner(f"Generando preguntas e identificando documentos claves..."):
                st.session_state.preguntas_entrevista = qm.generar_pregunta(
                    "preguntas_entrevista",
                    prompt
                )

    if st.session_state.preguntas_entrevista:
        st.write(st.session_state.preguntas_entrevista)
