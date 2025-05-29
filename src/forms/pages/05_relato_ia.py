#05_relato_ia.py
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
    st.session_state.setdefault("relato_form_guardado", False)
    st.session_state.setdefault("relatof", "")
    st.session_state.setdefault("contexto", "")
    st.session_state.setdefault("circunstancias", "")

    st.header("Construcción del relato")

    qm = get_qm()

    if st.button("Asistente para mejorar relatos con IA"):
        try:
            # Construir prompt inicial estructurado
            if not st.session_state.get("initial_story"):
                # Convertir fechas/horas a strings serializables
                fecha_accidente = st.session_state.fecha_accidente.isoformat() if hasattr(
                    st.session_state.fecha_accidente, 'isoformat') else str(st.session_state.fecha_accidente)
                hora_accidente = st.session_state.hora_accidente.isoformat() if hasattr(st.session_state.hora_accidente,
                                                                                        'isoformat') else str(
                    st.session_state.hora_accidente)

                initial_data = {
                    "metadata": {
                        "versión": "1.2",
                        "modelo": st.secrets.get("DEFAULT_MODEL", "deepseek-reasoner"),
                        "timestamp": datetime.now().isoformat(),
                        "source": "SMU-CT v2.3"
                    },
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
                    "declaraciones": {
                        "accidentado": st.session_state.declaracion_accidentado,
                        "testigos": [
                            {
                                "nombre": st.session_state.decl1_nombre,
                                "declaracion": st.session_state.decl1_texto
                            },
                            {
                                "nombre": st.session_state.decl2_nombre,
                                "declaracion": st.session_state.decl2_texto
                            }
                        ]
                    },
                    "contexto": {
                        "general": st.session_state.contexto,
                        "circunstancias": st.session_state.circunstancias
                    }
                }

                st.session_state.initial_story = json.dumps(initial_data, ensure_ascii=False, indent=2)

            # Generar relato inicial con manejo de modelo
            with st.spinner(f"Generando relato con {st.secrets.get('DEFAULT_MODEL', 'deepseek-reasoner')}..."):
                st.session_state.relatof = qm.generar_pregunta(
                    "relato_inicial",
                    st.session_state.initial_story
                )

            # Manejo del estado de la aplicación
            st.session_state['invest_active'] = True
            st.session_state.relato_form_guardado = False

            # Forzar actualización de UI
            st.rerun()

        except json.JSONDecodeError as je:
            st.error("Error en formato de datos. Verifica los campos ingresados.")
            if st.secrets.get("DEBUG"):
                st.error(f"Detalle técnico: {str(je)}")
                st.json(st.session_state.initial_story)

        except Exception as e:
            st.error("🚨 Error crítico durante la generación del relato")
            st.markdown("""
                **Pasos para solucionar:**
                1. Verifica tu conexión a internet
                2. Confirma que las claves API sean válidas
                3. Intenta reducir la longitud de los textos
                4. Contacta al equipo técnico si persiste el error
            """)

            if st.secrets.get("DEBUG"):
                st.divider()
                st.exception(e)
                st.json({
                    "session_state": dict(st.session_state),
                    "last_prompt": st.session_state.initial_story,
                    "secrets_config": {
                        "model": st.secrets.get("DEFAULT_MODEL"),
                        "api_available": "DEEPSEEK_API_KEY" in st.secrets
                    }
                })


    # Si ya existe relato, pasamos a la app de investigación
    if st.session_state.get("relatof") and st.session_state.get("invest_active"):
        app = InvestigationApp(st.secrets)  # Pasar todos los secrets
        app.run()
