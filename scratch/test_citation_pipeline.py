import os
import sys
import json

_ROOT = r"c:\Users\moham\OneDrive\Apps\اوكسجين"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
scripts_path = os.path.join(_ROOT, "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from llm_generation_pipeline import get_pipeline

pipe = get_pipeline()
res = pipe.process("أنا بقالى أسبوعين مبطل، بس بعد الأكل بحس برغبة شديدة في السيجارة. أعمل إيه؟")

print("Answer preview:", res.get("answer")[:200])
print("Citations count:", len(res.get("citations", [])))

for i, cit in enumerate(res.get("citations", []), 1):
    print(f"\n--- Citation #{i} ---")
    print("Citation ID:", cit.get("citation_id"))
    print("Chunk ID:", cit.get("chunk_id"))
    print("Source:", cit.get("source"))
    print("Original Text Length:", len(cit.get("evidence", {}).get("original_text", "")))
    print("Verified Highlight:", cit.get("evidence", {}).get("highlight_text"))
    orig = cit.get("evidence", {}).get("original_text", "")
    high = cit.get("evidence", {}).get("highlight_text")
    if high:
        print("Highlight verified in original text:", high in orig)
