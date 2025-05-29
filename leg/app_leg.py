import os
import sys
import streamlit as st


# Asegura que 'src' esté en el path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Definición de páginas con íconos y rutas
PAGES = {
    1: ("🏭 Empresa", "forms.pages.01_empresa"),
    2: ("👷 Datos Trabajador", "forms.pages.02_trabajador"),
    3: ("⚠️ Detalle Accidente", "forms.pages.03_accidente"),
    4: ("📝 Declaraciones y Fotos", "forms.pages.04_declaraciones_fotos"),
    5: ("🧠 Relato IA", "forms.pages.05_relato_ia"),
    6: ("🔎 Hechos IA", "forms.pages.06_hechos_ia"),
    7: ("🌳 Árbol IA", "forms.pages.07_arbol_ia"),
    8: ("🛠️ Medidas Correctivas", "forms.pages.08_medidas_correctivas"),
    9: ("📄 Generar Informe", "forms.pages.09_informe")
}

# Inicializa página por defecto si no existe en session_state
if "_page" not in st.session_state:
    st.session_state["_page"] = 1

# Obtener y asegurar tipo entero para current
data = st.session_state.get("_page", 1)
try:
    current = int(data)
except (ValueError, TypeError):
    current = 1
total = len(PAGES)

# Sidebar estilizado
st.sidebar.markdown(
    "<div style='text-align:center; padding:10px;'><h2>🚀 IST Investiga</h2></div>",
    unsafe_allow_html=True
)
#st.sidebar.markdown(f"**Paso {current} de {total}**")
#st.sidebar.progress(current / total)

# Navegación: radio con valores numéricos y etiquetas con icónos
page_keys = list(PAGES.keys())
def_index = page_keys.index(current)
selected = st.sidebar.radio(
    "Ir a sección",
    page_keys,
    format_func=lambda x: PAGES[x][0]
)
# Actualiza la página actual
st.session_state["_page"] = selected

# Import dinámico y ejecución de la página
module_path = PAGES[selected][1]
page_module = __import__(module_path, fromlist=["run"])
page_module.run()
