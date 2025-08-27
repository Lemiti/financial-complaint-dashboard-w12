import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplaintSearcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = None
        self.df = None


    def prepare_embeddings(self, df:pd.DataFrame):
        logger.info("Preparing semantic search embeddings...")
        self.df = df.copy()

        texts = self.df['consumer_complaint_narrative'].fillna('').tolist()
        

        self.embeddings = self.model.encode(texts)
        logger.info(f"Generated embeddings for {len(texts)} complaints")

    def search(self, query: str, top_k: int = 10):
        if self.embeddings is None:
            raise ValueError("Please call prepare_embeddings() first")
        
        query_embedding = self.model.encode([query])

        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            result = {
                    'similarity_score': float(similarities[idx]),
                    'company': self.df.iloc[idx]['company'],
                    'product': self.df.iloc[idx]['product'],
                    'narrative': self.df.iloc[idx]['consumer_complaint_narrative'],
                    'issue': self.df.iloc[idx].get('issue',''),
                    }
            results.append(result)

        return pd.DataFrame(results)

