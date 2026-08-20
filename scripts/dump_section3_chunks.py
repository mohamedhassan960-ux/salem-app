import json

with open('outputs/retrieval_records_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx in range(35, 126):
    r = data['records'][idx]
    cid = r['chunk_id']
    sec_num = r['hierarchy'].get('section_number')
    sec_title = r['hierarchy'].get('section_title')
    page = r['provenance'].get('physical_page_start')
    preview = r['content']['verbatim_text'][:90].replace('\n', ' ')
    print(f"[{idx+1:03d}] {cid:32} | Sec {str(sec_num):10} | p.{page} | {sec_title} | {preview}")
