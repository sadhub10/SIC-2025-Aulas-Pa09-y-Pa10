import easyocr
import os
from typing import List

reader = easyocr.Reader(['es', 'en'])

def extract_text_from_image(image_path: str) -> List[str]:
    """
    Extrae texto de una imagen y retorna una lista de tokens.

    Args:
        image_path: Ruta de la imagen a procesar

    Returns:
        Lista de tokens extraídos de la imagen
    """
    if not os.path.exists(image_path):
        print(f"Error: La imagen {image_path} no existe")
        return []

    try:
        result = reader.readtext(image_path, detail=0)
        tokens = []
        for text in result:
            tokens.extend(text.lower().split())

        print(f"Tokens extraídos de imagen: {len(tokens)}")
        return tokens
    except Exception as e:
        print(f"Error al procesar imagen: {e}")
        return []

