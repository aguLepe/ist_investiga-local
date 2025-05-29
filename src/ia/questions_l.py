import json
from pathlib import Path

import streamlit as st
from openai import OpenAI

# Directorio de configuración (prompts.json, pages.json)
CONFIG_DIR = Path(__file__).parent / "config"


def load_json(filename: str) -> dict:
    """
    Carga y devuelve un archivo JSON desde CONFIG_DIR.
    En caso de error, muestra un mensaje de Streamlit y detiene la ejecución.
    """
    path = CONFIG_DIR / filename
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error cargando {filename}: {e}")
        st.stop()


class StateManager:
    """Maneja la inicialización y validación del estado de sesión"""
    def __init__(self):
        self.defaults = {
            'current_page': '1',
            'respuestas': {},
            'history': [],
            'relato_accidente': "",
            'preguntas_generadas': {},
            'qa_pairs': {},
            'hechos': "",
            'arbol': {},
            'relatof': "",
        }

    def initialize(self):
        for key, default in self.defaults.items():
            val = st.session_state.get(key, None)
            if not isinstance(val, type(default)):
                st.session_state[key] = default

    def append_history(self, page: str):
        history = st.session_state.get('history', [])
        if not isinstance(history, list):
            history = []
        history.append(page)
        st.session_state['history'] = history


class QuestionManager:
    """Encapsula llamadas a la API de OpenAI y cacheo de respuestas"""
    def __init__(self, api_key: str):
        prompts = load_json("prompts.json").get("prompts", {})
        self.client = OpenAI(api_key=api_key)
        self.prompts = prompts

    @st.cache_data(show_spinner=False)
    def generate(self, prompt_key: str, context: str) -> str:
        cfg = self.prompts.get(prompt_key, {})
        try:
            completion = self.client.chat.completions.create(
                model=cfg.get("model"),
                temperature=cfg.get("temperature", 0.1),
                top_p=cfg.get("top_p", 1),
                messages=[
                    {"role": "system", "content": cfg.get("instruction", "")},
                    {"role": "user", "content": context},
                ]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error generando pregunta ({prompt_key}): {e}")
            return ""


class Navigation:
    """Renderiza botones de navegación y controla avance/retroceso"""
    def render(self) -> bool:
        col_content, col_back = st.columns([5, 1])
        advance = False
        with col_back:
            if st.button("◀ Regresar", use_container_width=True):
                hist = st.session_state.get('history', [])
                if hist:
                    st.session_state.current_page = hist.pop()
                    st.rerun()
        with col_content:
            if st.button("Continuar ▶", type="primary", use_container_width=True):
                advance = True
        return advance


class BasePage:
    """Clase base para páginas de la aplicación"""
    def __init__(self, app, cfg: dict):
        self.app = app
        self.cfg = cfg

    def render(self):
        raise NotImplementedError


class InputPage(BasePage):
    """Página inicial: captura y refina el relato de accidente"""
    def render(self):
        st.markdown("##### Inicio proceso de investigación")
        st.markdown("**Relato inicial**")
        st.markdown(
            "En base a la información que me has entregado, revisa o modifica el relato antes de continuar."
        )

        inicial = st.session_state.get('initial_story', '')
        default = self.app.qm.generate('relato_inicial', inicial)

        respuesta = st.text_area(
            label=self.cfg.get('question', ''),
            value=st.session_state.respuestas.get(self.cfg['key'], default),
            key=self.cfg['key'],
            height=300,
        )

        if self.app.nav.render() and respuesta.strip():
            st.session_state.respuestas[self.cfg['key']] = respuesta
            contexto = f"{respuesta} {inicial}".strip()
            st.session_state.relatо_accidente = self.app.qm.generate('relato_inicial', contexto)
            self.navigate()

    def navigate(self):
        self.app.sm.append_history(st.session_state.current_page)
        st.session_state.current_page = self.cfg.get('next_page')
        st.rerun()


class QuestionPage(BasePage):
    """Página para preguntas de profundización"""
    def render(self):
        st.markdown("##### Preguntas de profundización")
        prompt_key = self.cfg['prompt_key']  # ahora puede ser siempre 'investiga'
        page_id = self.cfg['id']
        inst_key = f"{prompt_key}_{page_id}"

        # Generar pregunta única por página
        if inst_key not in st.session_state.preguntas_generadas:
            context = st.session_state.relatо_accidente
            st.session_state.preguntas_generadas[inst_key] = (
                self.app.qm.generate(prompt_key, context)
            )
        pregunta = st.session_state.preguntas_generadas[inst_key]

        respuesta = st.text_area(
            label=pregunta,
            value=st.session_state.respuestas.get(self.cfg['key'], ''),
            key=self.cfg['key'],
            height=100,
        )

        if self.app.nav.render() and respuesta.strip():
            # Almacenar Q&A y extender relato
            st.session_state.respuestas[self.cfg['key']] = respuesta
            st.session_state.qa_pairs[self.cfg['key']] = {
                'pregunta': pregunta,
                'respuesta': respuesta,
            }
            st.session_state.relatо_accidente += f"\n\n{pregunta}\n{respuesta}"
            self.navigate()

    def navigate(self):
        self.app.sm.append_history(st.session_state.current_page)
        st.session_state.current_page = self.cfg.get('next_page')
        st.rerun()


class FinalPage(BasePage):
    """Página final: genera el reporte completo"""
    def render(self):
        st.markdown("### Generación de relato completo")

        if not st.session_state.relatof:
            with st.spinner("Generando relato completo..."):
                contexto = "\n".join(
                    f"{k}: {v}" for k, v in st.session_state.respuestas.items()
                )
                st.session_state.relatof = self.app.qm.generate('reporte_final', contexto)

        if st.session_state.relatof:
            with st.expander("Relato detallado del accidente", expanded=True):
                st.write(st.session_state.relatof)

        if st.button("↩️ Volver a Ficha de Investigación", use_container_width=True):
            st.session_state.selected_tool = "Ficha"
            st.rerun()


class InvestigationApp:
    """Orquesta el flujo y renderizado de páginas"""
    def __init__(self, api_key: str):
        self.sm = StateManager()
        self.sm.initialize()
        self.qm = QuestionManager(api_key)
        self.nav = Navigation()

        pages_cfg = load_json("pages.json").get('pages', [])
        self.pages_map = {p['id']: p for p in pages_cfg}

        self.handlers = {
            'input': InputPage,
            'question': QuestionPage,
            'final': FinalPage,
        }

    def run(self):
        st.markdown("<meta charset='UTF-8'>", unsafe_allow_html=True)
        st.subheader("Asistente de investigación")

        current = st.session_state.current_page
        cfg = self.pages_map.get(current)
        if not cfg:
            st.error("Configuración de página no encontrada")
            return

        page_type = cfg.get('type', 'question')
        handler_cls = self.handlers.get(page_type, QuestionPage)
        handler_cls(self, cfg).render()


def main():
    InvestigationApp(api_key="sk-...").run()


if __name__ == '__main__':
    main()
