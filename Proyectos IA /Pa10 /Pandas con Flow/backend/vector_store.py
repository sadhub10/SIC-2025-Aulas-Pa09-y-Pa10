import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, index_path="data/faiss_index.bin", metadata_path="data/metadata.pkl", dimension=384):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = dimension
        self.metadata = [] # List of dicts corresponding to index IDs
        
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.load()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def add_document(self, embedding: np.ndarray, doc_metadata: dict):
        """
        Agrega un embedding de documento y sus metadatos al almacén.
        """
        # Faiss espera float32
        vector = np.array([embedding]).astype('float32')
        self.index.add(vector)
        self.metadata.append(doc_metadata)
        self.save()

    def search(self, query_embedding: np.ndarray, query_text: str = None, k=5):
        """
        Busca los k vecinos más cercanos usando Búsqueda Híbrida (Vector + Palabra Clave).
        """
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, k * 2)
        
        vector_results = {}
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                vector_results[idx] = float(distances[0][i])

        keyword_matches = set()
        if query_text:
            query_lower = query_text.lower()
            for idx, meta in enumerate(self.metadata):
                # saltar eliminados
                if meta.get('deleted'): continue
                
                if query_lower in meta['filename'].lower() or \
                   (meta.get('summary') and query_lower in meta['summary'].lower()):
                    keyword_matches.add(idx)

        final_candidates = []
        all_indices = set(vector_results.keys()) | keyword_matches
        
        for idx in all_indices:
            if idx >= len(self.metadata): continue
            meta = self.metadata[idx]
            
            # Verificar bandera de eliminado O archivo faltante
            if meta.get('deleted') or not os.path.exists(meta['path']):
                continue
                
            score = vector_results.get(idx, 1.5) 
            
            if idx in keyword_matches:
                score *= 0.5
                if query_text and query_text.lower() in meta['filename'].lower():
                    score = 0.0
                    
            final_candidates.append({
                "metadata": meta,
                "distance": score
            })
            
        final_candidates.sort(key=lambda x: x['distance'])
        return final_candidates[:k]

    def list_documents(self):
        """
        Retorna una lista de todos los documentos activos.
        """
        valid_docs = []
        for meta in self.metadata:
            if not meta.get('deleted') and os.path.exists(meta['path']):
                valid_docs.append(meta)
        return valid_docs

    def delete_document(self, doc_id: str):
        """
        Deletes a document by ID.
        """
        for i, meta in enumerate(self.metadata):
            if meta.get('id') == doc_id:
                # Remove file from disk
                if os.path.exists(meta['path']):
                    try:
                        os.remove(meta['path'])
                    except Exception as e:
                        print(f"Error removing file {meta['path']}: {e}")
                
                
    def check_file_exists(self, filename: str) -> bool:
        """
        Verifica si un archivo con el nombre dado ya existe y está activo.
        """
        for meta in self.metadata:
            if not meta.get('deleted') and meta.get('filename') == filename:
                return True
        return False
        
    def delete_document(self, doc_id: str):
        """
        Elimina un documento por ID.
        Usa Borrado Suave (marcar como eliminado) para preservar la alineación del índice FAISS.
        """
        for i, meta in enumerate(self.metadata):
            if meta.get('id') == doc_id:
                # 1. Intentar eliminar archivo físico
                if os.path.exists(meta['path']):
                    try:
                        os.remove(meta['path'])
                    except Exception as e:
                        print(f"Advertencia: No se pudo eliminar el archivo {meta['path']}: {e}")
                
                # 2. Marcar como eliminado en metadatos
                meta['deleted'] = True
                
                # 3. Guardar metadatos
                self.save()
                return True
        return False

    def _rebuild_index(self):
        # Obsoleto: Ya no reconstruimos el índice para evitar perder vectores.
        # Confiamos en el filtro de la bandera 'deleted' durante la búsqueda/listado.
        pass

    def clear_all(self):
        """
        Elimina TODOS los documentos y reinicia el índice.
        """
        # 1. Eliminar todos los archivos en uploads
        upload_dir = "data/uploads"
        if os.path.exists(upload_dir):
            for f in os.listdir(upload_dir):
                os.remove(os.path.join(upload_dir, f))
        
        # 2. Reiniciar Índice y Metadatos
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self.save()
        return True

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)

if __name__ == "__main__":
    # Test logic
    pass
