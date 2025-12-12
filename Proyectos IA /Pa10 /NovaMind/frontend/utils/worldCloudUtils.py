from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import List
import streamlit as st

def generarWordCloud(textos: List[str], max_words: int = 100, width: int = 800, height: int = 400):
    if not textos:
        return None

    texto_completo = " ".join(textos)

    if not texto_completo.strip():
        return None

    stopwords_es = {
        'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para',
        'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya',
        'o', 'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre',
        'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante',
        'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos',
        'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras',
        'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos',
        'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros', 'mi',
        'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras',
        'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo',
        'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro',
        'vuestra', 'vuestros', 'vuestras', 'esos', 'esas',

        # Conjugaciones de "estar"
        'estoy', 'estás', 'está', 'estamos', 'estáis', 'están',
        'esté', 'estés', 'estemos', 'estéis', 'estén',
        'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán',
        'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían',
        'estaba', 'estabas', 'estábamos', 'estabais', 'estaban',
        'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron'
    }

    wc = WordCloud(
        width=width,
        height=height,
        background_color='white',
        stopwords=stopwords_es,
        max_words=max_words,
        colormap='viridis',
        relative_scaling=0.5,
        min_font_size=10
    ).generate(texto_completo)

    return wc


def mostrarWordCloud(textos: List[str], titulo: str = "WordCloud de Comentarios"):
    wc = generarWordCloud(textos)

    if wc is None:
        st.warning("No hay suficientes datos para generar el WordCloud")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.set_title(titulo, fontsize=16, fontweight='bold')
    ax.axis('off')

    st.pyplot(fig)
    plt.close()


def generarWordCloudPorCategoria(comentarios: List[dict], categoria: str, max_words: int = 80):
    textos_filtrados = []

    for comentario in comentarios:
        cats = comentario.get("categories", [])
        if isinstance(cats, list):
            for cat in cats:
                if isinstance(cat, dict) and cat.get("label") == categoria:
                    textos_filtrados.append(comentario.get("comentario", ""))
                    break

    return generarWordCloud(textos_filtrados, max_words=max_words)


def generarWordCloudPorStress(comentarios: List[dict], nivel_stress: str, max_words: int = 80):
    textos_filtrados = [
        c.get("comentario", "")
        for c in comentarios
        if c.get("stress_level") == nivel_stress
    ]

    return generarWordCloud(textos_filtrados, max_words=max_words)
