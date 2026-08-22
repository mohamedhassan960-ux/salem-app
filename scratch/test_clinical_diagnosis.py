import os
import sys

_ROOT = r"c:\Users\moham\OneDrive\Apps\اوكسجين"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
scripts_path = os.path.join(_ROOT, "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from llm_generation_pipeline import get_pipeline

pipe = get_pipeline()
query = "أنا بشرب علبة سجاير في اليوم (20 سيجارة)، وأول ما بصحى من النوم في أول 5 دقائق لازم أولع سيجارة قبل ما أقوم.. عايزك تشخص حالتي وتعملي خطة علاجية حقيقية أمشي عليها عشان أبطل"

print("Running Diagnostic & Treatment Plan Query...")
res = pipe.process(query)

print("\n" + "="*50)
print("ANSWER FROM DR. SALEM:")
print("="*50)
print(res.get("answer"))
print("\n" + "="*50)
print("CITATIONS:")
for c in res.get("citations", []):
    print(f"- Source {c.get('source_id')}: {c.get('title')} (Section: {c.get('section_number')}, Page: {c.get('physical_page_start')})")
print("="*50)
