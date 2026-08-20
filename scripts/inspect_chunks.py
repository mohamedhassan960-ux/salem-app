"""Read Background chunk and a few others to understand actual text structure."""
import json, sys, re

with open('outputs/retrieval_records_v2.json', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, dict):
    records = data.get('records', data.values() if not isinstance(list(data.values())[0], str) else [data])
elif isinstance(data, list):
    records = data
else:
    records = []

chunks_to_inspect = [
    'chunk_node_L2_background',
    'chunk_sec_3_3_1',
    'chunk_sec_3_1_1',
    'chunk_sec_4_4_p03',
]

if isinstance(data, dict) and 'records' not in data:
    for k, r in data.items():
        if isinstance(r, dict) and r.get('chunk_id') in chunks_to_inspect:
            print(f"\n=== {r.get('chunk_id')} ===")
            print(f"section_number: {r.get('section_number')}")
            print(f"section_title:  {r.get('section_title')}")
            print(f"content_type:   {r.get('content_type')}")
            text = r.get('verbatim_text', r.get('text', ''))
            print(f"text ({len(text)} chars):\n{text[:500]}\n")
            nums = re.findall(r'\b\d[\d,\.]*\b', text)
            pcts = re.findall(r'\d[\d\.]*\s*%', text)
            print(f"Numbers found: {nums[:10]}")
            print(f"Percentages found: {pcts[:5]}")
else:
    for r in records:
        if isinstance(r, dict) and r.get('chunk_id') in chunks_to_inspect:
            print(f"\n=== {r.get('chunk_id')} ===")
            print(f"section_number: {r.get('section_number')}")
            print(f"section_title:  {r.get('section_title')}")
            print(f"content_type:   {r.get('content_type')}")
            text = r.get('verbatim_text', r.get('text', ''))
            print(f"text ({len(text)} chars):\n{text[:500]}\n")
            nums = re.findall(r'\b\d[\d,\.]*\b', text)
            pcts = re.findall(r'\d[\d\.]*\s*%', text)
            print(f"Numbers found: {nums[:10]}")
            print(f"Percentages found: {pcts[:5]}")
