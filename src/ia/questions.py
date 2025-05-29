import streamlit as st
from openai import OpenAI
import json
from pathlib import Path

from streamlit import session_state, columns

# Configuración de directorios
CONFIG_DIR = Path(__file__).parent / "config"

class StateManager:
    def __init__(self):
        self.required_state = {
            'current_page': 11,
            'respuestas': {},
            'history': [],
            'relato_accidente': "",
            'preguntas_generadas': {},
            'qa_pairs': {},
            'qap_procesada': "",
            'hechos': "",
            'arbol': {},
            'relatof': ""
        }

    def initialize_session_state(self):
        """Inicializa y valida el estado de la sesión"""
        for key, default_value in self.required_state.items():
            if key not in session_state:
                session_state[key] = default_value
            self._validate_type(key, type(default_value))

    def _validate_type(self, key, expected_type):
        """Valida el tipo de los valores en el estado"""
        value = session_state[key]
        if not isinstance(value, expected_type):
            try:
                session_state[key] = expected_type()
            except Exception:
                st.error(f"Error de tipo en {key}. Reiniciando estado...")
                session_state[key] = self.required_state[key]
                st.rerun()

    def safe_history_append(self, page):
        """Manejo seguro del historial de navegación"""
        if isinstance(session_state.history, list):
            session_state.history.append(page)
        else:
            session_state.history = [page]

class ConfigLoader:
    @staticmethod
    def load_config(file_name):
        try:
            with open(CONFIG_DIR / file_name, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error cargando {file_name}: {e}")
            st.stop()

class QuestionManager:
    def __init__(self, secrets):
        self.clients = {
            'openai': OpenAI(
                api_key=secrets['OPENAI_API_KEY']),
            'deepseek': OpenAI(
                api_key=secrets['DEEPSEEK_API_KEY'],
                base_url="https://api.deepseek.com/v1"
            )
        }
        self.prompts = ConfigLoader.load_config("prompts.json")["prompts"]

    def _select_client(self, config):
        """Selecciona el cliente basado en la configuración"""
        provider = config.get("provider",
                      "deepseek" if "deepseek" in config["model"].lower() else "openai")
        return self.clients[provider]


    @st.cache_data(show_spinner=False)
    def generar_pregunta(_self, prompt_key: str, contexto: str):
        try:
            config = _self.prompts[prompt_key]
            client = _self._select_client(config)

            messages = [
                {"role": "system", "content": config["instruction"]},
                {"role": "user", "content": contexto}
            ]

            params = {
                "model": config["model"],
                "messages": messages,
                **{k: v for k, v in config.items() if k in [
                    "temperature", "top_p", "max_tokens",
                    "frequency_penalty", "presence_penalty", "response_format"
                ]}
            }

            completion = client.chat.completions.create(**params)

            # Debug mejorado
            if st.secrets.get("DEBUG", False):
                debug_info = {
                    "model": config["model"],
                    "provider": "deepseek" if "deepseek" in config["model"].lower() else "openai",
                    "prompt": config["instruction"],
                    "contexto": contexto[:500] + "..." if len(contexto) > 500 else contexto,
                    "respuesta": completion.choices[0].message.content.strip()[:1000] + "..."
                }
                st.write(f"```json\n{json.dumps(debug_info, indent=2)}\n```")

            return completion.choices[0].message.content.strip()

        except Exception as e:
            st.error(f"Error generando '{prompt_key}': {str(e)}")
            return ""

class PageManager:
    def __init__(self):
        pages_config = ConfigLoader.load_config("pages.json")
        self.pages = pages_config.get("pages", [])

    def get_page_config(self, page_id):
        """Obtiene la configuración de página comparando IDs como strings para mayor robustez."""
        pid = str(page_id)
        return next((p for p in self.pages if str(p.get("id")) == pid), None)

class NavigationHandler:
    @staticmethod
    def render():
        col1, col2 = st.columns([5, 1])
        nav_action = False

        with col2:
            if st.button("◀ Regresar", use_container_width=True):
                if session_state.history:
                    session_state.current_page = session_state.history.pop()
                    st.rerun()
        with col1:
            if st.button("Continuar ▶", type="primary", use_container_width=True):
                nav_action = True
        return nav_action

class InvestigationApp:
    def __init__(self, secrets):
        self.state_manager = StateManager()
        self.state_manager.initialize_session_state()
        self.question_manager = QuestionManager(secrets)
        self.page_manager = PageManager()
        self.nav_handler = NavigationHandler()
        self.page_handlers = {
            'input': self.render_input_page,
            'question': self.render_question_page,
            'final': self.render_final_page
        }

    def run(self):
        """Ejecuta la página según session_state.current_page"""
        cfg = self.page_manager.get_page_config(session_state.current_page)
        if not cfg:
            st.error("Configuración de página no encontrada")
            return
        handler = self.page_handlers.get(cfg.get("type", "question"))
        handler(cfg)

    def render_input_page(self, cfg):
        st.header("Inicio de Investigación")
        processed = self.question_manager.generar_pregunta("relato_inicial", session_state.initial_story)
        respuesta = st.text_area(
            "Revisa el relato inicial:",
            value=session_state.respuestas.get(cfg.get("key", ""), processed),
            key=cfg.get("key", "input_response"),
            height=250
        )
        if self.nav_handler.render() and respuesta.strip():
            self.process_initial_response(cfg, respuesta)

    def process_initial_response(self, cfg, respuesta):
        session_state.respuestas[cfg.get("key")] = respuesta
        contexto = f"{respuesta} {session_state.initial_story}"
        session_state.relato_accidente = self.question_manager.generar_pregunta("relato_inicial", contexto)
        self.navigate_to(cfg.get("next_page"))

    def render_question_page(self, cfg):
        st.subheader("Profundización")
        prompt_key = cfg.get("prompt_key", "")
        if prompt_key and prompt_key not in session_state.preguntas_generadas:
            session_state.preguntas_generadas[prompt_key] = self.question_manager.generar_pregunta(
                prompt_key, session_state.relato_accidente
            )
        pregunta = session_state.preguntas_generadas.get(prompt_key, "")
        respuesta = st.text_area(
            label=pregunta,
            value=session_state.respuestas.get(cfg.get("key", ""), ''),
            key=cfg.get("key", "question_response"),
            height=150
        )
        if self.nav_handler.render() and respuesta.strip():
            self.process_question_response(cfg, respuesta)

    def process_question_response(self, cfg, respuesta):
        # DEBUG: inicio
        print(f"DEBUG: process_question_response key={cfg.get('key')}")
        session_state.respuestas[cfg.get("key")] = respuesta
        prompt_key = cfg.get("prompt_key", "")
        pregunta = session_state.preguntas_generadas.get(prompt_key, "")
        session_state.qa_pairs[cfg.get("key")] = {"pregunta": pregunta, "respuesta": respuesta}
        contexto_fraseado = f"Pregunta: {pregunta}\nRespuesta: {respuesta}"
        print("DEBUG: contexto para frasear=", contexto_fraseado)
        redac = self.question_manager.generar_pregunta("frasear_preguntas", contexto_fraseado)
        print("DEBUG: redac=", redac)
        prev = session_state.get('qap_procesada', "")
        session_state.qap_procesada = f"{prev}\n{redac}" if prev else redac
        print("DEBUG: qap_procesada=", session_state.qap_procesada)
        session_state.relato_accidente += f"\n{redac}"
        print("DEBUG: relato_accidente=", session_state.relato_accidente)
        self.navigate_to(cfg.get("next_page"))

    def render_final_page(self, cfg):
        st.header("Informe Final")
        with st.spinner("Generando..."):
            session_state.relatof = self.question_manager.generar_pregunta(
                "reporte_final", session_state.relato_accidente
            )
            print(session_state.relatof)
        st.expander("Relato Completo", expanded=True).write(session_state.relatof)

        col1, col2 = columns(2)

        #with col1:
        #    if st.button("Seguir completando relato"):
        #        session_state.relato_accidente = session_state.relatof
        #        session_state.current_page = 11
        #        st.rerun()

        with col2:
            if st.button("Continuar con identificación de hechos"):
                st.session_state['_page'] = 6
                st.rerun()

    def navigate_to(self, next_page):
        self.state_manager.safe_history_append(session_state.current_page)
        session_state.current_page = next_page
        print(f"DEBUG: navegando a {next_page}")
        st.rerun()
