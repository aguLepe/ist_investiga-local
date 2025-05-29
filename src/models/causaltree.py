# causaltree.py
import streamlit as st
from graphviz import Digraph
import html
import json

def getvalues(data1,data2):
    relatof = data1
    hechos = data2

    return relatof, hechos

def get_parent_key(key_str):
    parts = list(map(int, key_str.split('.')))
    for i in reversed(range(len(parts))):
        if parts[i] != 0:
            parent_parts = parts.copy()
            parent_parts[i] = 0
            return '.'.join(map(str, parent_parts))
    return None


def import_from_5q():
    if 'arbol_from_5q' not in st.session_state:
        st.error("No hay datos para importar")
        return

    try:
        # Recuperar los datos crudos
        data = json.loads(st.session_state.arbol_from_5q)
        # ——————————————————————————————
        # DEBUG: mostrar contenido y claves de data
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: contenido de arbol_from_5q:", data)
        #print("DEBUG_IMPORT_FROM_5Q: contenido de arbol_from_5q:", data)
        keys = list(data.keys())
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: claves encontradas:", keys)
        #print("DEBUG_IMPORT_FROM_5Q: claves encontradas:", keys)
        # ——————————————————————————————

        # Comprobar existencia de la clave raíz esperada
        root_key = "0.0.0.0.0.0.0.0.0"
        if root_key not in data:
        #    st.write(f"🔍 DEBUG_IMPORT_FROM_5Q: ¡Clave raíz faltante! Esperada '{root_key}' no encontrada.")
            print(f"DEBUG_IMPORT_FROM_5Q: clave raíz faltante: '{root_key}' no en {keys}")
            raise ValueError("Formato de árbol inválido: falta nodo raíz")

        # Limpiar la entrada para no re-importar
        del st.session_state.arbol_from_5q

        # ——————————————————————————————
        # DEBUG: inicio de limpieza de estado
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: limpiando estado nodes/edges/current")
        print("DEBUG_IMPORT_FROM_5Q: limpiando state nodes/edges/current")
        # ——————————————————————————————

        # Limpiar datos actuales
        st.session_state.nodes = {}
        st.session_state.edges = []
        st.session_state.current = None

        # Mapeo de claves originales a IDs
        key_to_id = {root_key: 'root'}
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: asignada root ID 'root'")
        print("DEBUG_IMPORT_FROM_5Q: key_to_id inicial:", key_to_id)
        node_counter = 1

        # Determinar orden jerárquico
        def get_level(key):
            parts = list(map(int, key.split('.')))
            for i in reversed(range(len(parts))):
                if parts[i] != 0:
                    return i + 1
            return 0

        # Ordenar las claves
        sorted_keys = sorted(data.keys(), key=lambda x: get_level(x))
        sorted_keys.remove(root_key)
        sorted_keys.insert(0, root_key)
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: sorted_keys =", sorted_keys)
        print("DEBUG_IMPORT_FROM_5Q: sorted_keys =", sorted_keys)

        # Asignar IDs a cada clave (excepto la raíz)
        for key in sorted_keys[1:]:
            key_to_id[key] = f'node_{node_counter}'
            node_counter += 1
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: key_to_id completo:", key_to_id)
        print("DEBUG_IMPORT_FROM_5Q: key_to_id completo:", key_to_id)

        # Crear nodos y aristas
        for key in sorted_keys:
            node_id = key_to_id[key]
            parent_key = get_parent_key(key)
            parent_id = key_to_id.get(parent_key) if parent_key else None

            st.session_state.nodes[node_id] = {
                'label': data[key],
                'parent': parent_id,
                'children': []
            }
            if parent_id:
                st.session_state.nodes[parent_id]['children'].append(node_id)
                st.session_state.edges.append({'from': parent_id, 'to': node_id})

        # DEBUG: mostrar nodos y edges finales
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: nodes =", st.session_state.nodes)
        #st.write("🔍 DEBUG_IMPORT_FROM_5Q: edges =", st.session_state.edges)
        print("DEBUG_IMPORT_FROM_5Q: nodes =", st.session_state.nodes)
        print("DEBUG_IMPORT_FROM_5Q: edges =", st.session_state.edges)

        # Inicializar el nodo actual en la raíz y refrescar
        st.session_state.current = 'root'
        st.rerun()

    except Exception as e:
        st.error(f"Error importando árbol: {str(e)}")
        print("ERROR import_from_5q:", e)


def main():
    # DEBUG: inicio de main en Model_Marquis2
    #st.write("🌳 DEBUG_ARBOL_MAIN_START")
    print("DEBUG_ARBOL_MAIN_START")

    #st.header("🌳 Árbol de Causas Interactivo")

    if 'arbol_from_5q' in st.session_state:
    #    st.write("🌳 DEBUG_ARBOL_MAIN: arbol_from_5q encontrado, llamando import_from_5q()")
        print("DEBUG_ARBOL_MAIN: calling import_from_5q()")
        print("🔍 DEBUG-STAT relatof hechos antes de import_from_5q:", {
            'relatof': bool(st.session_state.get('relatof')),
            'hechos': bool(st.session_state.get('hechos'))
        })


        import_from_5q()
        return  # import_from_5q incluye rerun()



    # Inicialización del estado
    if 'nodes' not in st.session_state:
    #    st.write("🌳 DEBUG_ARBOL_MAIN: inicializando nodes/edges/current")
        print("DEBUG_ARBOL_MAIN: init nodes")
        st.session_state.nodes = {}
        st.session_state.edges = []
        st.session_state.current = None

    # Sincronizar selector de nodo antes de renderizar la barra lateral
    if 'node_selector' not in st.session_state:
        st.session_state.node_selector = st.session_state.current if 'current' in st.session_state else None
    elif st.session_state.current != st.session_state.node_selector:
        st.session_state.node_selector = st.session_state.current

    # Área de visualización principal
    with st.container():
    #    st.write("🌳 DEBUG_ARBOL_MAIN: antes de render_graph(), nodes:", len(st.session_state.nodes))
        print("DEBUG_ARBOL_MAIN: before render_graph, nodes count=", len(st.session_state.nodes))

        render_graph()

    #    st.write("🌳 DEBUG_ARBOL_MAIN_END")
        print("DEBUG_ARBOL_MAIN_END")


    # Columnas principales: contenedor de controles y contenedor de navegación/editor
    col1, col2 = st.columns([2, 1])

    with col1:
        # 🎮 Controles del Árbol
        with st.expander("🎮 Controles del Árbol", expanded=True):
            new_label = st.text_input(
                "📝 Texto del nodo:",
                key=f"node_label_{st.session_state.current}",
                help="Ingrese la descripción de la causa"
            )

            # Nivel 2: dos columnas para botones de control (raíz, hijo, hermano, eliminar)
            ctrl_left, ctrl_right = st.columns([1, 1])
            with ctrl_left:
                st.button(
                    "🌱 Raíz",
                    on_click=lambda: navigate_to_root(),
                    disabled=(not st.session_state.current or st.session_state.current == "root"),
                    help="Ir al nodo raíz",
                    use_container_width=True
                )
                st.button(
                    "➕ Crear Hijo",
                    on_click=lambda: add_child_node(new_label),
                    help="Añadir nuevo nodo hijo",
                    use_container_width=True
                )
            with ctrl_right:
                st.button(
                    "🔗 Hermano",
                    on_click=lambda: add_sibling_node(new_label),
                    help="Añadir nodo hermano",
                    use_container_width=True
                )
                st.button(
                    "🗑️ Eliminar",
                    on_click=confirm_delete,
                    help="Eliminar nodo actual",
                    use_container_width=True
                )

        # Usamos un container() para “resetear” el contexto antes de crear nuevas columnas
        nav_container = st.container()
        nav_left, nav_center, nav_right = nav_container.columns([1, 2, 1])

        with nav_left:
            st.button(
                "← Anterior",
                on_click=navigate_previous_cousin,
                use_container_width=True
            )

        with nav_center:
            st.button(
                "⬆️ Arriba",
                on_click=navigate_to_parent,
                disabled=(
                        not st.session_state.current or
                        not st.session_state.nodes[st.session_state.current]["parent"]
                ),
                help="Navegar al nodo padre",
                use_container_width=True
            )
            st.button(
                "⬇️ Abajo",
                on_click=navigate_to_first_child,
                disabled=(
                        not st.session_state.current or
                        not st.session_state.nodes[st.session_state.current]["children"]
                ),
                help="Navegar al primer hijo",
                use_container_width=True
            )

        with nav_right:
            st.button(
                "→ Próximo",
                on_click=navigate_next_cousin,
                use_container_width=True
            )

    with col2:


        # ✏️ Editor de Nodo
        if st.session_state.current:
            with st.expander("✏️ Editor de Nodo", expanded=True):
                render_node_editor()

def create_root_node(label: str):
    """Crea un nuevo nodo raíz (solo uno permitido)"""
    # Verificar si ya existe una raíz
    existing_root = next((node_id for node_id, node in st.session_state.nodes.items()
                          if node['parent'] is None), None)

    if existing_root:
        st.error("❌ Ya existe un nodo raíz. Elimine el actual para crear uno nuevo.")
        return

    root_id = "root"  # ID fijo para la raíz
    st.session_state.nodes = {
        root_id: {
            'label': label,
            'parent': None,
            'children': []
        }
    }
    st.session_state.edges = []
    st.session_state.current = root_id
    st.rerun()


def add_child_node(label: str):
    """Añade un nodo hijo al actual"""
    parent_id = st.session_state.current
    new_id = f"node_{len(st.session_state.nodes)}"

    st.session_state.nodes[new_id] = {
        'label': label,
        'parent': parent_id,
        'children': []
    }

    st.session_state.nodes[parent_id]['children'].append(new_id)
    st.session_state.current = new_id
    st.session_state.edges.append({'from': parent_id, 'to': new_id})
    #st.rerun()  # Actualización inmediata del gráfico

def add_sibling_node(label: str):
    """Añade un nodo hermano al actual"""
    current_id = st.session_state.current
    parent_id = st.session_state.nodes[current_id]['parent']

    if parent_id:
        new_id = f"node_{len(st.session_state.nodes)}"

        st.session_state.nodes[new_id] = {
            'label': label,
            'parent': parent_id,
            'children': []
        }

        st.session_state.nodes[parent_id]['children'].append(new_id)
        st.session_state.edges.append({'from': parent_id, 'to': new_id})
        st.session_state.current = new_id
        st.rerun()  # Actualización inmediata del gráfico


def delete_current_node():
    """Elimina el nodo actual y sus dependencias"""
    if not st.session_state.current:
        return

    current_id = st.session_state.current
    node_data = st.session_state.nodes.get(current_id)

    if node_data:
        # Eliminar hijos recursivamente
        for child_id in node_data['children']:
            delete_node(child_id)

        # Eliminar referencias del padre
        if node_data['parent']:
            parent_id = node_data['parent']
            st.session_state.nodes[parent_id]['children'].remove(current_id)

        # Eliminar el nodo
        del st.session_state.nodes[current_id]
        st.session_state.edges = [e for e in st.session_state.edges if e['to'] != current_id]

        # Actualizar selección
        st.session_state.current = node_data['parent'] if node_data['parent'] else None

    #st.rerun()  # Actualización inmediata del gráfico

def delete_node(node_id: str):
    """Función recursiva para eliminar nodos"""
    if node_id in st.session_state.nodes:
        for child_id in st.session_state.nodes[node_id]['children']:
            delete_node(child_id)
        del st.session_state.nodes[node_id]


# Nuevas funciones de navegación
def navigate_to_parent():
    current_id = st.session_state.current
    if current_id and st.session_state.nodes[current_id]['parent']:
        st.session_state.current = st.session_state.nodes[current_id]['parent']
        #st.rerun()


def navigate_to_first_child():
    current_id = st.session_state.current
    if current_id and st.session_state.nodes[current_id]['children']:
        st.session_state.current = st.session_state.nodes[current_id]['children'][0]
        #st.rerun()


def navigate_to_root():
    if 'root' in st.session_state.nodes:
        st.session_state.current = 'root'
        #st.rerun()


# Nueva función de confirmación de eliminación
def confirm_delete():
    if st.session_state.current and st.session_state.current != 'root':
        with st.sidebar:
            delete_current_node()
            st.success("Nodo eliminado")
            #if st.warning("¿Eliminar este nodo y todos sus hijos?", icon="⚠️"):
    else:
        st.error("No se puede eliminar la raíz")


# Nueva función para breadcrumbs
def render_breadcrumbs():
    current_id = st.session_state.current
    path = []
    while current_id:
        node = st.session_state.nodes[current_id]
        path.append(node['label'])
        current_id = node['parent']

    breadcrumbs = " > ".join(reversed(path))
    st.markdown(f"`{breadcrumbs[:50]}...`" if len(breadcrumbs) > 50 else f"`{breadcrumbs}`")


def get_cousins(node_id: str) -> list:
    """Versión corregida de la función de primos"""
    if not node_id or node_id not in st.session_state.nodes:
        return []

    current_node = st.session_state.nodes[node_id]
    parent_id = current_node['parent']

    if not parent_id:
        return []  # Raíz no tiene primos

    # Obtener todos los nodos del mismo nivel
    siblings = st.session_state.nodes[parent_id]['children']
    return [c for c in st.session_state.nodes.keys()
            if st.session_state.nodes[c]['parent'] == parent_id
            and c != node_id]


def navigate_previous_cousin():
    current_id = st.session_state.current
    if not current_id:
        return

    # Obtener el nodo actual y su padre
    current_node = st.session_state.nodes[current_id]
    parent_id = current_node.get('parent')
    if not parent_id:
        return  # Si es raíz, no hay hermanos

    # Lista de hermanos (incluye al nodo actual)
    siblings = st.session_state.nodes[parent_id]['children']
    if not siblings:
        return

    current_index = siblings.index(current_id)
    new_index = (current_index - 1) % len(siblings)  # Navegación circular
    st.session_state.current = siblings[new_index]
    #st.rerun()


def navigate_next_cousin():
    current_id = st.session_state.current
    if not current_id:
        return

    # Obtener el nodo actual y su padre
    current_node = st.session_state.nodes[current_id]
    parent_id = current_node.get('parent')
    if not parent_id:
        return  # Si es raíz, no hay hermanos

    # Lista de hermanos (incluye al nodo actual)
    siblings = st.session_state.nodes[parent_id]['children']
    if not siblings:
        return

    current_index = siblings.index(current_id)
    new_index = (current_index + 1) % len(siblings)  # Navegación circular
    st.session_state.current = siblings[new_index]
    #st.rerun()



def generate_dot() -> str:
    """Genera el código DOT para visualización con texto envuelto"""
    dot = Digraph()
    dot.attr(rankdir='TB',
             ranksep='0.4',
             nodesep='0.3',
             newrank='true',
             compound='true',
             bgcolor='#f5f5f5',
             dir='back'
             )

    # Configuración mejorada de nodos
    dot.attr('node',
             shape='Mrecord',
             style='filled,rounded',
             fillcolor='#E1F5FE',
             gradientangle='270',
             color='#0277BD',
             fontname="Helvetica",
             fontsize="10pt",
             penwidth='1.5',
             width='2.0',
             height='1.0',
             margin='0.2,0.1',
             dir='back'
             )

    dot.attr('edge', color='#606060', penwidth='1.5')

    def wrap_text(text: str, max_width: int = 25) -> list:
        """Versión mejorada que mantiene palabras completas"""
        if not text:
            return []

        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    # Procesar todos los nodos
    for node_id, node_data in st.session_state.nodes.items():
        # 1. Aplicar wrap al texto
        raw_text = node_data['label']
        wrapped_lines = wrap_text(raw_text, 20)  # 20 caracteres por línea

        # 2. Formatear como HTML para Graphviz
        escaped_lines = [f"<FONT>{html.escape(line)}</FONT>" for line in wrapped_lines]
        html_label = f"<{'<BR/>'.join(escaped_lines)}>"

        # 3. Configurar atributos especiales para nodo seleccionado
        node_attrs = {}
        if node_id == st.session_state.current:
            node_attrs = {
                'fillcolor': '#FF6666',
                'color': '#CC0000',
                'penwidth': '3',
                'fontname': 'Helvetica-Bold'
            }

        # Crear nodo con label formateado
        dot.node(name=node_id, label=html_label, **node_attrs)

    # Añadir todas las conexiones
    for edge in st.session_state.edges:
        edge_attrs = {'arrowhead':'inv', 'dir':'back'}
        dot.edge(edge['from'], edge['to'],**edge_attrs )

    st.session_state.arbol_dot = dot.source
    return dot.source


def render_graph():
    """Renderiza el gráfico interactivo usando DOT nativo"""
    dot_code = generate_dot()

    # Sección de visualización principal
    with st.container():
        if st.session_state.nodes:
            st.graphviz_chart(dot_code, use_container_width=True)
        else:
            st.info("⭐ Comience creando un nodo raíz usando los controles inferiores")

        # Selector de nodo integrado
        if st.session_state.nodes:
            # Sincronizar selector con nodo actual
            if st.session_state.get("node_selector") != st.session_state.current:
                st.session_state.node_selector = st.session_state.current

def render_node_editor():
    """Editor de propiedades del nodo actual"""
    current_id = st.session_state.current
    node_data = st.session_state.nodes.get(current_id)

    with st.form("node_editor"):
        new_label = st.text_area(
            "📝 Editar descripción:",
            value=node_data['label'],
            height=70,
            key=f"node_editor_{current_id}"  # Clave única por nodo
        )

        if st.form_submit_button("💾 Guardar cambios"):
            node_data['label'] = new_label.strip()
            st.rerun()


if __name__ == "__main__":
    main()