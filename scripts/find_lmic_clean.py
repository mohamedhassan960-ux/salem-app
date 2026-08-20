import json

with open('outputs/retrieval_records_v2.json', encoding='utf-8') as f:
    data = json.load(f)

for r in data['records']:
    t = r['content']['verbatim_text']
    t_lower = t.lower()
    if 'lmic' in t_lower or 'low- and middle' in t_lower or 'middle-income' in t_lower:
        cid = r['chunk_id']
        stitle = r['hierarchy']['section_title']
        snum = r['hierarchy']['section_number']
        page = r['provenance']['physical_page_start']
        print(f"=== Chunk: {cid} | Sec: {snum} - {stitle} | Page {page} ===")
        # clean non-ascii chars
        cleaned = t.encode('ascii', errors='replace').decode('ascii')
        print(cleaned)
        print("-" * 60)
