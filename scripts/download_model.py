import sys
import time
from sentence_transformers import SentenceTransformer

model_name = "intfloat/multilingual-e5-small"
print(f"Starting download and loading of {model_name}...", flush=True)
t0 = time.time()
try:
    model = SentenceTransformer(model_name)
    print(f"SUCCESS: Loaded {model_name} in {time.time()-t0:.2f}s! Dim = {model.get_sentence_embedding_dimension()}", flush=True)
except Exception as e:
    print(f"FAILED: {e}", flush=True)
    # Fallback to paraphrase-multilingual-MiniLM-L12-v2
    fallback = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    print(f"Trying fallback {fallback}...", flush=True)
    try:
        model = SentenceTransformer(fallback)
        print(f"SUCCESS: Loaded fallback {fallback} in {time.time()-t0:.2f}s! Dim = {model.get_sentence_embedding_dimension()}", flush=True)
    except Exception as e2:
        print(f"Fallback FAILED: {e2}", flush=True)
