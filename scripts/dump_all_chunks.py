import json

with open('outputs/retrieval_records_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total Chunks: {len(data['records'])}\n")
for idx, r in enumerate(data['records']):
    cid = r['chunk_id']
    sec_num = r['hierarchy'].get('section_number')
    sec_title = r['hierarchy'].get('section_title')
    page = r['provenance'].get('physical_page_start')
    preview = r['content']['verbatim_text'][:100].replace('\n', ' ')
    print(f"[{idx+1:03d}] {cid} | Sec {sec_num} | p.{page} | {sec_title} | {preview}")
