"""
Vector Store Builder (Production ChromaDB)
Medical RAG Project: أوكسجين (Oxygen)

Generates dense embeddings using sentence-transformers/all-MiniLM-L6-v2
and indexes all 145 semantic chunks into a local, persistent ChromaDB vector store.

Input:
- outputs/semantic_chunks_v1.json

Output:
- Local Persistent ChromaDB: data/chroma_db
- Collection: medical_knowledge
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
import chromadb
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class VectorStoreBuilder:
    """Builds and populates local ChromaDB collection with semantic chunks and embeddings."""

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_COLLECTION_NAME = "medical_knowledge"

    def __init__(
        self,
        chunks_json_path: str,
        persist_directory: str,
        model_name: str = DEFAULT_MODEL_NAME,
        collection_name: str = DEFAULT_COLLECTION_NAME
    ):
        self.chunks_json_path = chunks_json_path
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.collection_name = collection_name
        self.model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.ClientAPI] = None

    def load_model(self):
        """Loads the embedding model locally."""
        logging.info(f"Loading embedding model '{self.model_name}'...")
        self.model = SentenceTransformer(self.model_name)
        logging.info("Embedding model loaded successfully.")

    def sanitize_metadata(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all metadata values conform to ChromaDB supported types (str, int, float, bool)."""
        clean_meta = {}
        for k, v in meta.items():
            if v is None:
                clean_meta[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v)
        return clean_meta

    def build_store(self) -> int:
        """Reads semantic_chunks_v1.json, generates embeddings, and populates ChromaDB."""
        if not os.path.exists(self.chunks_json_path):
            raise FileNotFoundError(f"Missing semantic chunks file: {self.chunks_json_path}")

        if self.model is None:
            self.load_model()

        with open(self.chunks_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract all chunk items
        all_chunks = []
        for node_item in data.get("nodes", []):
            all_chunks.extend(node_item.get("chunks", []))

        total_chunks = len(all_chunks)
        logging.info(f"Loaded {total_chunks} semantic chunks from {self.chunks_json_path}.")

        ids = []
        documents = []
        metadatas = []

        for ch in all_chunks:
            ids.append(ch["chunk_id"])
            documents.append(ch["text"])
            metadatas.append(self.sanitize_metadata(ch.get("metadata", {})))

        logging.info(f"Generating dense embeddings for {total_chunks} chunks...")
        embeddings = self.model.encode(documents, show_progress_bar=True, batch_size=32)
        embeddings_list = [emb.tolist() for emb in embeddings]
        logging.info(f"Generated {len(embeddings_list)} embeddings (dimension: {len(embeddings_list[0])}).")

        # Initialize Persistent ChromaDB Client
        os.makedirs(self.persist_directory, exist_ok=True)
        logging.info(f"Connecting to ChromaDB at '{self.persist_directory}'...")
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Delete existing collection if present to guarantee clean rebuild
        try:
            self.client.delete_collection(self.collection_name)
            logging.info(f"Reset existing collection '{self.collection_name}'.")
        except Exception:
            pass

        # Create collection with cosine similarity
        collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine", "embedding_model": self.model_name}
        )

        logging.info(f"Adding {total_chunks} records to collection '{self.collection_name}'...")
        # Add records in batches
        batch_size = 50
        for i in range(0, total_chunks, batch_size):
            end_idx = min(i + batch_size, total_chunks)
            collection.add(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx],
                embeddings=embeddings_list[i:end_idx]
            )

        count = collection.count()
        logging.info(f"Successfully populated ChromaDB collection '{self.collection_name}' with {count} chunks.")
        return count

if __name__ == '__main__':
    chunks_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks_v1.json'
    db_path = r'C:\Users\moham\OneDrive\Apps\اوكسجين\data\chroma_db'

    builder = VectorStoreBuilder(chunks_path, db_path)
    total_stored = builder.build_store()
    print(f"Vector Store built successfully with {total_stored} records.")
