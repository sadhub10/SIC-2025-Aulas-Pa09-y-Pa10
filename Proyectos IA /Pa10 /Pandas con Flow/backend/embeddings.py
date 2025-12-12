from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def generate(self, text: str) -> np.ndarray:
        """
        Genera un vector de embedding para el texto dado.
        """
        return self.model.encode([text])[0]

if __name__ == "__main__":
    e = EmbeddingGenerator()
    vec = e.generate("This is a document.")
    print(vec.shape)
