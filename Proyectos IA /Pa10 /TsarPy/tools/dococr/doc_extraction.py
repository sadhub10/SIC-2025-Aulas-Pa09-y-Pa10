from pdf2image import convert_from_path
import pytesseract
from typing import List
import os

def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extrae texto de un PDF y retorna una lista de tokens.

    Args:
        pdf_path: Ruta del archivo PDF a procesar

    Returns:
        Lista de tokens extraídos del PDF
    """
    full_text_list = []

    if not os.path.exists(pdf_path):
        print(f"Error: El archivo {pdf_path} no existe")
        return []

    try:
        print(f"Convirtiendo páginas de {pdf_path}...")
        images = convert_from_path(pdf_path, dpi=300)
    except Exception as e:
        print("Error: No se pudo convertir el PDF. Asegúrese de que Poppler esté instalado.")
        print(f"Error subyacente: {e}")
        return []

    for i, image in enumerate(images):
        print(f"Procesando Página {i+1}...")
        page_text = pytesseract.image_to_string(image)
        full_text_list.extend(page_text.lower().split())

    print(f"OCR Completo. Total de tokens: {len(full_text_list)}")
    return full_text_list

