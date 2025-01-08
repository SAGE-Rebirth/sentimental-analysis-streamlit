import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.embedding_model = SentenceTransformer(model_name)
        self.index = None

    def generate_embeddings(self, documents):
        embeddings = self.embedding_model.encode(documents, convert_to_tensor=True)
        embeddings = embeddings.cpu().numpy()
        faiss.normalize_L2(embeddings)
        return embeddings

    def create_faiss_index(self, embeddings):
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        self.index = index

    def search_similar_documents(self, query_embedding, k=5):
        if self.index is None:
            raise ValueError("FAISS index not initialized.")
        query_embedding = np.array(query_embedding).reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices