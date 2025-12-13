import streamlit as st
import requests
import os
import time
import pdfplumber
from PIL import Image

# URL de API Backend
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Análisis Multimodal de Archivos",
    page_icon="🧠",
    layout="wide"
)

# CSS Personalizado para apariencia premium
st.markdown("""
<style>
    /* Modo Oscuro Global */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .main {
        background-color: #0e1117;
    }
    /* Botones */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #00D4FF; /* Neon Cyan for contrast */
        color: black;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00a3cc;
        color: white;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
    }
    /* Tarjetas */
    .card {
        padding: 20px;
        background-color: #262730; /* Streamlit Dark Gray */
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        color: #ffffff; /* Explicit White Text */
        border: 1px solid #41424C;
    }
    h3 {
        color: #00D4FF !important;
    }
    strong {
        color: #E0E0E0;
    }
    /* Ajustes de Título */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    h1 {
        margin-bottom: 2rem;
    }
    
    /* Animación del Botón de Carga de Archivos */
    [data-testid="stFileUploader"] button {
        transition: all 0.3s ease;
        border: 1px solid #41424C;
    }
    [data-testid="stFileUploader"] button:hover {
        transform: scale(1.05);
        border-color: #00D4FF !important;
        color: #00D4FF !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='display: flex; align-items: center; gap: 0px; margin-top: 20px;'>
        <div style='font-size: 1.2em; margin-right: 8px; margin-left: -5px;'>🧠</div> Análisis Multimodal de Archivos
    </h1>
""", unsafe_allow_html=True)
st.markdown("Sube **PDFs, Imágenes o Fotos** para que la IA los analice, clasifique y extraiga su información.")

# Barra lateral para Búsqueda e Historial
with st.sidebar:
    st.header("🔍 Búsqueda & Razonamiento")
    st.markdown("Haz preguntas complejas sobre tus archivos. La IA entiende el contexto visual y textual.")
    search_query = st.text_input("", placeholder="Ej: ¿Qué coche es rojo? o Busca facturas de >$100")
    st.caption("💡 Truco: Puedes buscar por conceptos visuales, valores numéricos o texto específico.")
    
    if st.button("Buscar"):
        if search_query:
            with st.spinner("Buscando..."):
                try:
                    res = requests.get(f"{API_URL}/search", params={"query": search_query})
                    if res.status_code == 200:
                        results = res.json()
                        st.session_state['search_results'] = results
                    else:
                        st.error("Error en la búsqueda")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # Mostrar Resultados de Búsqueda
    if 'search_results' in st.session_state:
        st.subheader("Resultados")
        results = st.session_state['search_results']
        if not results:
            st.info("No se encontraron coincidencias.")
        for item in results:
            meta = item['metadata']
            
            # Verificar Datos de Reranking IA
            if 'ai_score' in item:
                # Modo Rerank con Gemini
                score = item['ai_score']
                reasoning = item.get('ai_reasoning', '')
                
                quality = "Alta" if score > 0.8 else "Media" if score > 0.5 else "Baja"
                color = "green" if score > 0.8 else "orange" if score > 0.5 else "red"
                
                with st.expander(f"{meta['filename']} ({int(score*100)}%)"):
                    st.markdown(f"**Relevancia:** :{color}[{quality}]")
                    if reasoning:
                        st.info(f"💡 **Análisis:** {reasoning}")
                    st.caption(f"Categoría: {meta.get('category', 'N/A')}")
                    st.write(f"**Resumen:** {meta.get('summary', '')[:150]}...")
            
            else:
                # Modo Legado (Distancia L2)
                score = item['distance']
                # Interpretar puntuación (menor es mejor para L2)
                quality = "Alta" if score < 1.0 else "Media" if score < 1.4 else "Baja"
                color = "green" if score < 1.0 else "orange" if score < 1.4 else "red"
                
                with st.expander(f"{meta['filename']}"):
                    st.markdown(f"**Coincidencia Vectorial:** :{color}[{quality} ({int((2-min(score, 2))*50)}%)]")
                    st.caption(f"Categoría: {meta.get('category', 'N/A')}")
                    st.write(f"**Resumen:** {meta.get('summary', '')[:150]}...")

    st.markdown("---")
    st.header("📂 Historial")
    
    # Callback para Borrar Todo
    def delete_all_callback():
        try:
            res = requests.delete(f"{API_URL}/documents")
            if res.status_code == 200:
                 if 'search_results' in st.session_state:
                     del st.session_state['search_results']
                 st.toast("Historial borrado correctamente")
                 # No se necesita sleep para callback, toast usualmente sobrevive o aparece en la siguiente ejecución
            else:
                 st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    # Dialogo de confirmación usando st.dialog (Popup Modal)
    @st.dialog("⚠️ Confirmar Borrado")
    def open_delete_dialog():
        # CSS Hack para forzar el centrado vertical estricto del modal
        st.markdown(
            """
            <style>
            div[data-testid="stDialog"] > div:first-child {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0 !important;
            }
            div[data-testid="stDialog"] > div:first-child > div {
                margin-top: 0 !important;
                max-height: 80vh;
                overflow-y: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.write("¿Estás seguro de que quieres borrar **TODO** el historial?")
        st.write("Esta acción no se puede deshacer.")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("Sí, borrar todo", type="primary", use_container_width=True):
                delete_all_callback()
                st.rerun()
        with col_d2:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()

    cols_container = st.container()
    with cols_container:
        if st.button("🗑️ Borrar Todo", type="primary", use_container_width=True):
            open_delete_dialog()
    
    # Esperar el siguiente ciclo de ejecución para actualizar UI (implícito en callback)

    # Obtener documentos
    try:
        res_docs = requests.get(f"{API_URL}/documents")
        if res_docs.status_code == 200:
            docs = res_docs.json()
            st.caption(f"Total: {len(docs)} documentos")
            
            if docs:
                # Mapa Nombre -> ID
                name_to_id = {d['filename']: d['id'] for d in docs}
                file_options = list(name_to_id.keys())
                
                # Lógica para limpiar selección después de borrar
                if 'deleted_files' not in st.session_state:
                    st.session_state['deleted_files'] = []

                # Filtrar opciones para excluir los conocidos como eliminados localmente (feedback visual)
                # Pero típicamente st.rerun() volverá a comprobar el backend.
                
                selected_filenames = st.multiselect(
                    "Seleccionar documentos para borrar:", 
                    file_options,
                    key="delete_multiselect"
                )
                
                if st.button("Borrar Seleccionados"):
                    if selected_filenames:
                        progress_bar = st.progress(0)
                        for i, name in enumerate(selected_filenames):
                           doc_id = name_to_id.get(name)
                           if doc_id:
                               try:
                                   res = requests.delete(f"{API_URL}/documents/{doc_id}")
                                   if res.status_code == 200:
                                       pass
                                   else:
                                       st.error(f"Error borrando {name}")
                               except Exception as e:
                                   st.error(f"Error de conexión: {e}")
                           
                           progress_bar.progress((i + 1) / len(selected_filenames))
                        
                        st.success(f"Proceso finalizado.")
                        time.sleep(1)
                        # Forzar reinicio del widget multiselect
                        if "delete_multiselect" in st.session_state:
                            del st.session_state["delete_multiselect"]
                        st.rerun()
                    else:
                        st.warning("Por favor, selecciona al menos un archivo.")
                
                # List details below
                with st.expander("Ver detalles de todos"):
                    for i, doc in enumerate(docs):
                        st.markdown(f"""
                        <div style="margin-bottom: 2px; font-weight: 600; display: flex; align-items: flex-start; gap: 6px;">
                            <span style="min-width: 1.2em;">📄</span>
                            <span style="word-break: break-word; line-height: 1.2;">{doc['filename']}</span>
                        </div>
                        <div style="font-size: 0.85em; color: #aaa; margin-bottom: 5px; display: flex; align-items: center; gap: 4px;">
                            <span style="position: relative; top: -2px;">📂</span> <span>{doc.get('category', 'N/A')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info(doc.get('summary', 'Sin resumen disponible.'))
                        
                        # Only show separator if it's not the last item
                        if i < len(docs) - 1:
                            st.markdown("<hr style='margin: 5px 0; border-color: #41424C; opacity: 0.6;'>", unsafe_allow_html=True)
            else:
                st.info("El historial está vacío.")

        else:
            st.warning("No se pudo cargar el historial.")
    except Exception as e:
        st.warning(f"Error de conexión: {e}")

# Área Principal - Lado a Lado optimizado con gran espacio
col1, col2 = st.columns([1, 1], gap="large")

# Callback para limpiar resultados cuando cambia el archivo
def reset_analysis():
    if 'analysis_result' in st.session_state:
        del st.session_state['analysis_result']

with col1:
    st.markdown("""
        <h3 style='display: flex; align-items: center; gap: 8px; margin-bottom: 5px;'>
            <div style='margin-left: -5px;'>📤</div> Cargar Documento
        </h3>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Elige un archivo (PDF o Imagen)", type=["pdf", "png", "jpg", "jpeg", "webp"], on_change=reset_analysis, key="main_file_uploader")

    if uploaded_file is not None:
        # --- Pre-validación de Duplicados ---
        try:
             # Obtener docs existentes para verificar sin golpear el análisis del backend
             doc_res = requests.get(f"{API_URL}/documents")
             if doc_res.status_code == 200:
                 existing_docs = doc_res.json()
                 existing_filenames = [d.get('filename') for d in existing_docs]
                 
                 if uploaded_file.name in existing_filenames:
                     # ARREGLO CRÍTICO:
                     # Solo bloquear si este archivo NO es el que acabamos de analizar con éxito y estamos mostrando.
                     # Esto previene el bucle "Éxito -> Refrescar -> Error".
                     current_result = st.session_state.get('analysis_result', {})
                     is_current_result = current_result.get('filename') == uploaded_file.name
                     
                     if not is_current_result:
                         st.error(f"⚠️ El archivo '{uploaded_file.name}' ya existe en el sistema. Por favor, elimínalo primero o sube uno diferente.")
                         # Detener ejecución aquí (no mostrar botón Analizar)
                         st.stop()
        except:
            pass # Fallar abierto si el backend es inalcanzable, dejar que el análisis principal lo maneje

        # Asegurar stream al inicio
        uploaded_file.seek(0)
        
        # Estandarizar Tamaño de Vista Previa: Siempre usar 1/3 del ancho del contenedor
        preview_cols = st.columns(3)
        
        # Detectar Tipo Robustamente
        file_type = uploaded_file.type
        file_name = uploaded_file.name.lower()
        
        # Mostrar Vista Previa si es imagen
        if "image" in file_type or any(file_name.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
             with preview_cols[0]:
                 st.image(uploaded_file, caption="Vista Previa de Imagen", use_container_width=True)
        
        elif "pdf" in file_type or file_name.endswith('.pdf'):
             try:
                 with pdfplumber.open(uploaded_file) as pdf:
                     total_pages = len(pdf.pages)
                     if total_pages > 0:
                         # Mostrar hasta 3 páginas
                         preview_count = min(3, total_pages)
                         if total_pages > 1:
                             st.caption(f"📑 Vista Previa (Primeras {preview_count} de {total_pages} páginas)")
                         else:
                             st.caption("📑 Vista Previa (Portada)")
                             
                         for i in range(preview_count):
                             page = pdf.pages[i]
                             # Alta Res 300 DPI
                             im = page.to_image(resolution=300).original
                             with preview_cols[i]:
                                 st.image(im, caption=f"Pág {i+1}", use_container_width=True)
             except Exception:
                 st.caption("Vista previa no disponible")

        # Verificar si ya tenemos resultados para ESTE archivo específico
        current_result = st.session_state.get('analysis_result', {})
        is_analyzed = current_result.get('filename') == uploaded_file.name

        if is_analyzed:
            st.markdown("""
            <div style="
                background-color: rgba(46, 160, 67, 0.15); 
                color: #3fb950; 
                border: 1px solid rgba(46, 160, 67, 0.4); 
                padding: 10px 15px; 
                border-radius: 6px; 
                display: inline-block;
                font-weight: 500;
            ">
                ✅ Documento procesado correctamente
            </div>
            """, unsafe_allow_html=True)

        elif st.button("Analizar Documento"):
            data = None
            with st.spinner("Procesando documento (Extrayendo, Clasificando, Resumiendo)..."):
                try:
                    # Reset pointer because pdfplumber might have read it
                    uploaded_file.seek(0)
                    # Dynamically pass the MIME type from Streamlit's detection
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/analyze", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state['analysis_result'] = data
                    elif response.status_code == 400:
                         # Handle duplicate file error gracefully
                         st.warning(f"⚠️ {response.json().get('detail')}")
                    else:
                        st.error(f"Falló el análisis: {response.text}")
                except Exception as e:
                    st.error(f"Error conectando al backend: {e}")

            # Fuera del Spinner
            if data:
                 # Asegurar que solo mostramos éxito si los datos se cargaron realmente en esta ejecución
                 st.session_state['just_analyzed'] = True # Bandera opcional si queremos mostrar un toast luego
                 st.rerun()

with col2:
    st.subheader("📊 Resultados del Análisis")
    if 'analysis_result' in st.session_state:
        res = st.session_state['analysis_result']
        
        if 'error' in res:
            st.error(f"Error: {res['error']}")
        else:
            category_score = res.get('category_score', 0)
            category_name = res.get('category', 'Desconocido').upper()
            

            with st.expander("Clasificación", expanded=True):
                 st.info(f"Categoría: **{res.get('category')}** (Confianza: {res.get('category_score', 0)*100:.1f}%)")
            
            st.success("Resumen Generado:")
            st.write(res.get('summary'))
            
            with st.expander("Ver texto extraído completo"):
                full_text = res.get('full_text') or res.get('text_preview', '')
                
                tab1, tab2 = st.tabs(["👀 Vista Renderizada", "📝 Código Markdown"])
                
                with tab1:
                    st.markdown(full_text)
                    
                with tab2:
                    st.text_area("Copiar Texto:", value=full_text, height=300)

    else:
        st.info("Sube y analiza un documento para ver los resultados aquí.")
