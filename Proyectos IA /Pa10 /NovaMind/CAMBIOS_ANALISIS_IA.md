# Correcciones en el Análisis con IA (Transformers)

## Problema Identificado

El sistema de análisis de comentarios con IA tenía los siguientes problemas:

1. **Modelos configurados para INGLÉS**: Los modelos de Transformers estaban usando versiones en inglés que no funcionaban correctamente con texto en español.


## Solución Implementada

### 1. Modelos cambiados a ESPAÑOL

Se actualizaron los modelos en `backend/ia/configIA.py`:

| Tarea | Modelo Anterior (Inglés) | Modelo Nuevo (Español) |
|-------|-------------------------|------------------------|
| Análisis de Sentimiento | `cardiffnlp/twitter-roberta-base-sentiment-latest` | `pysentimiento/robertuito-sentiment-analysis` |
| Detección de Emociones | `j-hartmann/emotion-english-distilroberta-base` | `finiteautomata/beto-emotion-analysis` |
| Clasificación Zero-shot | `facebook/bart-large-mnli` | `joeddav/xlm-roberta-large-xnli` |
| Resumen de Texto | `sshleifer/distilbart-cnn-12-6` | `ELiRF/NASE` |

### 2. Mejoras en el procesamiento

**Archivo**: `backend/ia/iaCore.py`

- Mejorado el manejo de etiquetas en español para el análisis de sentimiento
- Ahora reconoce etiquetas como "positivo", "negativo", "neutral" además de las versiones en inglés


## Campos que se Guardan en la Base de Datos

El sistema SIEMPRE guarda los siguientes campos en la tabla `analisis_comentarios`:

1. **comentario** (TEXT): El comentario original
2. **emotion_label** (VARCHAR): La emoción detectada (ej: "joy", "sadness", "anger")
3. **emotion_score** (FLOAT): Score de confianza de la emoción (0.0 a 1.0)
4. **stress_level** (VARCHAR): Nivel de estrés ("bajo", "medio", "alto")
5. **sent_pos** (FLOAT): Score de sentimiento positivo
6. **sent_neu** (FLOAT): Score de sentimiento neutral
7. **sent_neg** (FLOAT): Score de sentimiento negativo
8. **categories** (JSON): Categorías detectadas con sus scores
9. **summary** (TEXT): Resumen del comentario
10. **suggestion** (TEXT): Sugerencia para RRHH
11. **departamento** (VARCHAR): Departamento del empleado
12. **equipo** (VARCHAR): Equipo del empleado
13. **fecha** (VARCHAR): Fecha del comentario
14. **created_at** (DATETIME): Timestamp de creación

## Cómo Probar el Sistema

### Opción 1: Script de prueba directo

```bash
python test_analisis.py
```

Este script probará el análisis con 3 comentarios de ejemplo en español y mostrará todos los resultados.

### Opción 2: A través de la API

1.  el backend tiene que estar corriendo:
```bash
cd backend
uvicorn main:app --reload
```

## Notas Importantes

1. **Primera carga de modelos**: La primera vez que se ejecute el análisis, descargará los modelos de HuggingFace. Esto puede tardar varios minutos dependiendo de la conexión a internet.

2. **Cache de modelos**: Los modelos se cachean localmente en `~/.cache/huggingface/`, por lo que las ejecuciones posteriores serán mucho más rápidas.

3. **Dependencias**: Asegúrate de tener instaladas todas las dependencias del `requirements.txt`.

## Troubleshooting

### Si los modelos no se descargan:

```bash
pip install --upgrade transformers torch sentencepiece
```


### Si los resultados no se guardan:

1. Verifica que la base de datos esté corriendo
2. Verifica que la tabla `analisis_comentarios` exista con la estructura correcta
