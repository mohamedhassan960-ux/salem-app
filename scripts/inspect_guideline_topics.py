import json

with open('outputs/retrieval_records_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data['records']
print(f"Total chunks: {len(records)}")

sections = {}
for r in records:
    h = r['hierarchy']
    sec_num = h.get('section_number') or "Other"
    sec_title = h.get('section_title') or "Untitled"
    key = f"{sec_num}: {sec_title}"
    if key not in sections:
        sections[key] = []
    sections[key].append({
        'chunk_id': r['chunk_id'],
        'page': r['provenance'].get('physical_page_start'),
        'text_sample': r['content']['verbatim_text'][:120].replace('\n', ' ')
    })

print("\n--- Available Sections in WHO 2024 Guideline ---")
for k, v in sorted(sections.items()):
    print(f"\n[{k}] ({len(v)} chunks):")
    for item in v[:2]:
        print(f"   - {item['chunk_id']} (p.{item['page']}): {item['text_sample']}...")
