import json

with open('outputs/retrieval_records_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for r in data['records']:
    sec_num = r['hierarchy'].get('section_number')
    sec_title = r['hierarchy'].get('section_title')
    cid = r['chunk_id']
    page = r['provenance'].get('physical_page_start')
    if sec_num or any(term in str(sec_title).lower() for term in ['pharmacological', 'behavioural', 'advice', 'counselling', 'digital', 'combination', 'telephone', 'special', 'group', 'varenicline', 'nrt', 'traditional', 'system']):
        print(f"ID: {cid:45} | Sec: {str(sec_num):10} | p.{str(page):3} | Title: {sec_title}")
