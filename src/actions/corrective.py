# corrective.py
import streamlit as st
from openai import OpenAI
import json
from typing import List

# Configuración de modelo y API
GPT_MODEL = "gpt-4.1-mini-2025-04-14"
API_KEY = "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"
client = OpenAI(api_key=API_KEY)

# Estado de la sesión
st.session_state.setdefault('edited_measures', [])

# Función para llamar a la API de OpenAI
def call_ai(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {'role': 'system', 'content': 'Eres un especialista en seguridad laboral con 20 años de experiencia.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.error(f"Error en la API de OpenAI: {e}")
        return ''

# Función para generar medidas correctivas
def generate_measures():
    relato_parts: List[str] = []
    for key in ('relatof', 'hechos', 'arbol'):
        val = st.session_state.get(key)
        if val:
            if key == 'arbol':
                relato_parts.append(json.dumps(val, indent=2, ensure_ascii=False))
            else:
                relato_parts.append(str(val))
    relato = "\n".join(relato_parts)

    prompt = f"""
Analiza el siguiente accidente y genera medidas correctivas profesionales.

RELATO:
{relato}

Instrucciones:
1. Genera entre 3 y 5 medidas correctivas en español.
2. Usa EXCLUSIVAMENTE el siguiente formato JSON válido:
{{
  "medidas": [
    {{
      "id": "uuid-único",
      "tipo": "<Tipo>",
      "prioridad": "<Prioridad>",
      "descripcion": "<Descripción>",
      "plazo": "<Plazo>",
      "responsable": "<Responsable>"
    }}
  ]
}}
3. Para cada campo utiliza **exactamente** uno de estos valores:
   - tipo: Ingenieril, Administrativa, EPP
   - prioridad: Alta, Media, Baja
   - plazo: Corto, Mediano, Largo

4. Son medidas administrativas las capacitaciones, procedimientos y otras.
5. El campo descripción debe ser un texto completo en español.
6. El campo responsable debe ser el área o departamento responsable.

"""
    ai_response = call_ai(prompt)

    try:
        json_block = ai_response.split('```json')[1].split('```')[0].strip()
    except Exception:
        st.error('No se encontró JSON en la respuesta de IA.')
        st.write(ai_response)
        return

    try:
        result = json.loads(json_block)
        st.session_state.edited_measures = result.get('medidas', [])
        st.success('Medidas generadas y formateadas correctamente.')
    except Exception as e:
        st.error(f"Error procesando JSON: {e}")
        st.write(json_block)

# Función para mostrar y permitir editar y eliminar medidas
def show_measures_editor():
    st.markdown('### Medidas Propuestas')
    tipo_opts = ["Ingenieril", "Administrativa", "EPP"]
    prioridad_opts = ["Alta", "Media", "Baja"]
    plazo_opts = ["Corto", "Mediano", "Largo"]
    #costo_opts = ["Bajo", "Medio", "Alto"]

    for idx, m in enumerate(st.session_state.edited_measures.copy()):
        with st.expander(f"Medida {idx+1}: {m.get('descripcion','')[:40]}..."):

            col1, col2 = st.columns(2)
            with col1:
                default_tipo = m.get('tipo', tipo_opts[0])
                idx_tipo = tipo_opts.index(default_tipo) if default_tipo in tipo_opts else 0
                tipo = st.selectbox("Tipo", tipo_opts, index=idx_tipo, key=f"tipo_{idx}")

                default_plazo = m.get('plazo', '')
                if default_plazo in plazo_opts:
                    idx_plazo = plazo_opts.index(default_plazo)
                elif 'Corto' in default_plazo:
                    idx_plazo = 0
                elif 'Mediano' in default_plazo:
                    idx_plazo = 1
                elif 'Largo' in default_plazo:
                    idx_plazo = 2
                else:
                    idx_plazo = 0
                plazo = st.selectbox("Plazo", plazo_opts, index=idx_plazo, key=f"plazo_{idx}")

            with col2:
                responsable = st.text_input("Responsable", value=m.get('responsable',''), key=f"resp_{idx}")

                default_prio = m.get('prioridad', prioridad_opts[1])
                idx_prio = prioridad_opts.index(default_prio) if default_prio in prioridad_opts else 1
                prioridad = st.selectbox("Prioridad", prioridad_opts, index=idx_prio, key=f"prio_{idx}")

                #default_costo = m.get('costo_estimado', '')
                #idx_costo = costo_opts.index(default_costo) if default_costo in costo_opts else 1
                #costo = st.selectbox("Costo estimado", costo_opts, index=idx_costo, key=f"costo_{idx}")

            descripcion = st.text_area("Descripción", value=m.get('descripcion',''), key=f"desc_{idx}", height=120)

            cols = st.columns(2)
            with cols[0]:
                if st.button('Guardar cambios', key=f'save_{idx}'):
                    st.session_state.edited_measures[idx].update({
                        'tipo': tipo,
                        'prioridad': prioridad,
                        'plazo': plazo,
                        'responsable': '', #responsable,
                        #'costo_estimado': costo,
                        'descripcion': descripcion
                    })
                    st.success(f"Medida {idx+1} actualizada.")
            with cols[1]:
                if st.button('Eliminar', key=f'del_{idx}'):
                    st.session_state.edited_measures.pop(idx)
                    st.rerun()

# Función principal para integrar en botón
def medidas_app():
    status = False
    if not st.session_state.edited_measures:
        st.session_state.edited_measures = []

    if st.button('Generar medidas correctivas con IA'):
        with st.spinner("Analizando hechos y generando medidas correctivas con IA..."):
            if not any(st.session_state.get(k) for k in ('relatof','hechos','arbol')):
                print("Faltan datos")
                st.warning('Faltan datos: asegúrate de tener relato, hechos y arbol guardados.')
                status = False
            else:
                status = True
                print("Antes de generate_measures")
                generate_measures()

    if st.session_state.edited_measures:
        show_measures_editor()
    else:
        st.session_state.edited_measures = []
    return status