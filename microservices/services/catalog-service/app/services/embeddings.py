import numpy as np
from sentence_transformers import SentenceTransformer

# Load the model only once when this module is imported (singleton behavior)
_model = None

def _get_model():
    global _model
    if _model is None:
        # We load the model dynamically so it doesn't block app startup unless used
        # or we could load it globally. The prompt says "al iniciar la app, no por request".
        # We can load it right away.
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model

# Preload
_get_model()

def get_embedding(text: str) -> list[float]:
    """
    Returns the vector embedding for the given text.
    """
    model = _get_model()
    # encode returns a numpy array, convert to list of floats for JSON storage
    embedding = model.encode(text)
    return embedding.tolist()

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Computes cosine similarity between two vectors.
    """
    a = np.array(vec_a)
    b = np.array(vec_b)
    # Cosine similarity formula: dot(A, B) / (norm(A) * norm(B))
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
