# src/forms/data_form.py

import streamlit as st
import pandas as pd
from datetime import date, datetime


@st.cache_data
def load_locales(path: str = 'EBCO-CT.xlsx') -> pd.DataFrame:
#def load_locales(path: str = 'SMU-CT.xlsx') -> pd.DataFrame:
#def load_locales(path: str = 'UM-CT.xlsx') -> pd.DataFrame:

    """
    Lee y cachea el archivo de locales SMU-CT.xlsx, limpiando espacios en los nombres de columnas.
    """
    df = pd.read_excel(path)
    df.columns = [col.strip() for col in df.columns]
    return df


def init_session_fields():
    """
    Inicializa todos los campos en session_state con valores por defecto,
    asegurando que siempre existan antes de acceder a ellos.
    """
    # Valores por defecto para numéricos
    numeric = {'edad': 18}
    # Fechas por defecto
    dates = {
        'fecha_nacimiento': date(2008, 12, 31),
        'fecha_accidente': date.today(),
        'fecha_informe': date.today()
    }
    # Horas por defecto
    times = {'hora_accidente': datetime.now().time()}
    # Campos de texto
    texts = [
        'empresa','rut_empresa','actividad','direccion_empresa','telefono', 'representante_legal',
        'region','comuna','nombre_local','direccion_centro','nombre_trabajador',
        'rut_trabajador','nacionalidad','estado_civil','contrato','antiguedad_empresa'
        'cargo_trabajador','antiguedad_cargo','domicilio','lugar_accidente',
        'tipo_accidente','naturaleza_lesion','parte_afectada','tarea','operacion',
        'daños_personas','daños_propiedad','perdidas_proceso','declaracion_accidentado',
        'decl1_nombre','decl1_cargo','decl1_rut','decl1_texto',
        'decl2_nombre','decl2_cargo','decl2_rut','decl2_texto',
        'informe_numero','investigador','contexto','circunstancias','initial_story'
    ]

    # Asigna defaults si no existen
    for k, v in {**numeric, **dates, **times}.items():
        st.session_state.setdefault(k, v)
    for field in texts:
        st.session_state.setdefault(field, "")

    # Estados para IA

    st.session_state.setdefault('analisis_antecedentes', None)
    st.session_state.setdefault('preguntas_entrevista', None)
    st.session_state.setdefault('relatof', None)
    st.session_state.setdefault('hechos', None)
    st.session_state.setdefault('arbol', None)
    st.session_state.setdefault('resumen', None)

    # Flags para reseteos dinámicos
    st.session_state.setdefault('prev_empresa', None)
    st.session_state.setdefault('prev_region', None)
    st.session_state.setdefault('prev_comuna', None)

def get_qm():
    """
    Devuelve una instancia de QuestionManager usando los secrets completos
    """
    from src.ia.questions import QuestionManager
    return QuestionManager(st.secrets)



def medidas_app_wrapper():
    """
    Wrapper para llamar a la función de medidas correctivas.
    """
    from src.ia.questions import QuestionManager
    qm = QuestionManager(st.secrets)
    from src.actions.corrective import medidas_app
    status = medidas_app()
    return status


def export_docx_wrapper():
    """
    Wrapper para exportar el informe a DOCX.
    """
    from src.ia.questions import QuestionManager
    qm = QuestionManager(st.secrets)
    from src.report.generator import export_to_docx
    export_to_docx()
