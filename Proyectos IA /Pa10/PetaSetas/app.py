import streamlit as st
import pickle as pk
import numpy as np
from PIL import Image
from keras.preprocessing import image
from keras.models import load_model
import io

st.set_page_config(page_title="Clasificador de Imágenes", page_icon="")

st.title("Clasificador de hongos")
st.write("Sube una imagen del hongo que quieres identificar")

@st.cache_resource
def cargar_modelo_y_encoder():
    try:
        modelo = load_model('model.h5')
        with open('label_encoder.pkl', 'rb') as f:
            label_encoder = pk.load(f)
        return modelo, label_encoder
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
        return None, None

modelo, Le = cargar_modelo_y_encoder()

def predecir_imagen(img_pil, modelo, label_encoder):

    img_resized = img_pil.resize((64, 64))
    
    x = image.img_to_array(img_resized)
    
    x = x.astype('float32') / 255.0
    
    x = np.expand_dims(x, axis=0)
    
    predicciones = modelo.predict(x, verbose=0)
    clase_predicha = predicciones.argmax(axis=1)
    
    etiqueta_predicha = label_encoder.inverse_transform(clase_predicha)
    probabilidad = predicciones[0][clase_predicha[0]]
    
    return etiqueta_predicha[0], probabilidad, predicciones[0]

uploaded_file = st.file_uploader(
    "Selecciona una imagen",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    st.success("¡Imagen cargada exitosamente!")
    
    st.image(img, caption=uploaded_file.name, use_container_width=True, width=300)
    
    if st.button("Clasificar hongo", type="primary"):
        if modelo is not None and Le is not None:
            with st.spinner("Clasificando..."):
                try:
        
                    etiqueta, prob, todas_probs = predecir_imagen(img, modelo, Le)
                    
                    st.markdown("---")
                    st.subheader("Resultado de la Clasificación")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Clase Predicha", etiqueta)
                    with col_b:
                        st.metric("Confianza", f"{prob:.2%}")
                    
                    st.markdown("### Probabilidades por Clase")
                    
                    resultados = {clase: float(todas_probs[i]) 
                                for i, clase in enumerate(Le.classes_)}
                    
                    resultados_ordenados = dict(sorted(resultados.items(), 
                                                      key=lambda x: x[1], 
                                                      reverse=True))
                    
                    for i, (clase, probabilidad) in enumerate(resultados_ordenados.items()):
                        if i >= 3:
                            break
                        st.write(f"**{clase}**")
                        st.progress(probabilidad)
                        st.write(f"{probabilidad:.2%}")
                        st.write("")

                except Exception as e:
                    st.error(f"Error al clasificar: {e}")
        else:
            st.error("Modelo no cargado. Verifica que los archivos existan.")
else:
    st.info("Sube una imagen")