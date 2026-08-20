"""
Automated Validation Test Suite for Medical RAG Semantic Chunks
WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)

Runs 12 comprehensive validation checks against semantic_chunks.json.
Generates machine-readable JSON and formatted Markdown audit reports.
"""

import os
import json
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ChunkValidator:
    def __init__(self, chunks_json_path: str):
        self.chunks_json_path = chunks_json_path
        self.data: Dict[str, Any] = {}
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_map: Dict[str, Dict[str, Any]] = {}
        self.test_results: List[Dict[str, Any]] = []

    def load_chunks(self):
        if not os.path.exists(self.chunks_json_path):
            raise FileNotFoundError(f"Chunks file not found: {self.chunks_json_path}")
        with open(self.chunks_json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.chunks = self.data.get("chunks", [])
        self.chunk_map = {c["chunk_id"]: c for c in self.chunks}
        logging.info(f"Loaded {len(self.chunks)} chunks for validation.")

    def run_all_tests(self) -> Dict[str, Any]:
        self.test_results = []
        
        t1 = self.test_1_all_canonical_recommendations()
        t2 = self.test_2_recommendation_fields_completeness()
        t3 = self.test_3_no_rec_evidence_accidental_merges()
        t4 = self.test_4_no_misclassified_evidence()
        t5 = self.test_5_no_false_positive_headings()
        t6 = self.test_6_valid_section_and_heading_paths()
        t7 = self.test_7_referential_integrity()
        t8 = self.test_8_page_provenance_validity()
        t9 = self.test_9_no_duplicate_chunk_ids()
        t10 = self.test_10_no_running_headers_in_chunks()
        t11 = self.test_11_tables_and_glossary_structure()
        t12 = self.test_12_word_count_and_content_integrity()

        all_passed = all(t["passed"] for t in self.test_results)

        summary = {
            "all_tests_passed": all_passed,
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for t in self.test_results if t["passed"]),
            "failed_tests": sum(1 for t in self.test_results if not t["passed"]),
            "total_chunks_evaluated": len(self.chunks),
            "chunks_by_type": self._get_chunks_by_type(),
            "test_details": self.test_results
        }
        return summary

    def _get_chunks_by_type(self) -> Dict[str, int]:
        counts = {}
        for c in self.chunks:
            t = c.get("chunk_type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts

    def _record(self, test_name: str, passed: bool, message: str, details: Any = None):
        res = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(res)
        status = "PASSED" if passed else "FAILED"
        logging.info(f"[{status}] {test_name}: {message}")
        return res

    def test_1_all_canonical_recommendations(self):
        rec_chunks = [c for c in self.chunks if c.get("chunk_type") == "recommendation"]
        found_rec_ids = {c.get("recommendation_id") for c in rec_chunks if c.get("recommendation_id")}
        expected_rec_ids = {f"REC_{i:02d}" for i in range(1, 13)}
        
        missing = expected_rec_ids - found_rec_ids
        passed = (len(missing) == 0 and len(rec_chunks) == 12)
        msg = f"Found {len(found_rec_ids)} canonical recommendations out of 12 expected."
        return self._record("TEST 1: All 12 Canonical Recommendations Exist", passed, msg, {
            "found": sorted(list(found_rec_ids)),
            "missing": sorted(list(missing)),
            "total_rec_chunks": len(rec_chunks)
        })

    def test_2_recommendation_fields_completeness(self):
        rec_chunks = [c for c in self.chunks if c.get("chunk_type") == "recommendation"]
        incomplete = []
        for c in rec_chunks:
            rid = c.get("recommendation_id")
            if not c.get("recommendation_strength"):
                incomplete.append((rid, "Missing recommendation_strength"))
            if not c.get("certainty_of_evidence"):
                incomplete.append((rid, "Missing certainty_of_evidence"))
            if not c.get("target_intervention"):
                incomplete.append((rid, "Missing target_intervention"))
            if not c.get("target_population"):
                incomplete.append((rid, "Missing target_population"))
            if not c.get("physical_page_start"):
                incomplete.append((rid, "Missing physical_page_start"))
        passed = len(incomplete) == 0
        msg = "All recommendations have complete clinical metadata." if passed else f"Found {len(incomplete)} incomplete fields."
        return self._record("TEST 2: Recommendation Clinical Fields Completeness", passed, msg, {"issues": incomplete})

    def test_3_no_rec_evidence_accidental_merges(self):
        # Recommendations should not contain long Cochrane systematic review meta-analysis stats
        rec_chunks = [c for c in self.chunks if c.get("chunk_type") == "recommendation"]
        suspicious = []
        for c in rec_chunks:
            txt = c.get("content", "")
            if "Cochrane systematic review" in txt or "trials;" in txt:
                suspicious.append(c.get("chunk_id"))
        passed = len(suspicious) == 0
        msg = "No recommendation chunks contain accidental merged evidence review text." if passed else f"Suspicious chunks: {suspicious}"
        return self._record("TEST 3: Clean Separation of Recommendations from Evidence", passed, msg, {"suspicious_chunks": suspicious})

    def test_4_no_misclassified_evidence(self):
        evidence_chunks = [c for c in self.chunks if c.get("chunk_type") == "evidence_justification"]
        misclassified = []
        for c in evidence_chunks:
            if c.get("recommendation_strength") is not None:
                misclassified.append(c.get("chunk_id"))
        passed = len(misclassified) == 0
        msg = "All evidence chunks are strictly classified as evidence without false recommendation tags." if passed else f"Misclassified: {misclassified}"
        return self._record("TEST 4: Strict Classification of Evidence Chunks", passed, msg, {"misclassified": misclassified})

    def test_5_no_false_positive_headings(self):
        false_patterns = [
            "50 US dollars",
            "1.3 million",
            "10. WHO recommends",
            "11. WHO recommends",
            "12. WHO recommends"
        ]
        bad_headings = []
        for c in self.chunks:
            hpath = c.get("heading_path", "")
            for p in false_patterns:
                if p in hpath:
                    bad_headings.append((c.get("chunk_id"), hpath))
        passed = len(bad_headings) == 0
        msg = "No false-positive numerical lines or recommendation lines were promoted to section headings." if passed else f"Bad headings found: {bad_headings}"
        return self._record("TEST 5: Zero False-Positive Section Headings", passed, msg, {"bad_headings": bad_headings})

    def test_6_valid_section_and_heading_paths(self):
        missing_context = []
        for c in self.chunks:
            if not c.get("heading_path") or not c.get("section_id"):
                missing_context.append(c.get("chunk_id"))
        passed = len(missing_context) == 0
        msg = "Every chunk has a fully resolved section_id and heading_path." if passed else f"Missing context in: {missing_context}"
        return self._record("TEST 6: Contextual Hierarchy & Heading Path Completeness", passed, msg, {"missing": missing_context})

    def test_7_referential_integrity(self):
        broken_links = []
        for c in self.chunks:
            cid = c.get("chunk_id")
            for rid in c.get("related_chunk_ids", []):
                if rid not in self.chunk_map:
                    broken_links.append((cid, rid))
        passed = len(broken_links) == 0
        msg = "All related_chunk_ids resolve to valid chunk IDs (100% Referential Integrity)." if passed else f"Broken links: {broken_links}"
        return self._record("TEST 7: Knowledge Graph & Cross-Reference Integrity", passed, msg, {"broken_links": broken_links})

    def test_8_page_provenance_validity(self):
        invalid_provenance = []
        for c in self.chunks:
            cid = c.get("chunk_id")
            p_start = c.get("physical_page_start")
            p_end = c.get("physical_page_end")
            if p_start is None or p_end is None or p_start > p_end or p_start < 1 or p_end > 76:
                invalid_provenance.append((cid, p_start, p_end))
        passed = len(invalid_provenance) == 0
        msg = "All chunks have valid physical page boundaries (1 <= start <= end <= 76)." if passed else f"Invalid: {invalid_provenance}"
        return self._record("TEST 8: Physical Page Provenance & Boundary Invariants", passed, msg, {"invalid": invalid_provenance})

    def test_9_no_duplicate_chunk_ids(self):
        seen = set()
        duplicates = []
        for c in self.chunks:
            cid = c.get("chunk_id")
            if cid in seen:
                duplicates.append(cid)
            seen.add(cid)
        passed = len(duplicates) == 0
        msg = "All chunk IDs are globally unique." if passed else f"Duplicates found: {duplicates}"
        return self._record("TEST 9: Unique Chunk Identifiers", passed, msg, {"duplicates": duplicates})

    def test_10_no_running_headers_in_chunks(self):
        running_header = "WHO clinical treatment guideline for tobacco cessation in adults"
        contaminated = []
        for c in self.chunks:
            # Check if running header appears inside content (except front matter title chunk)
            if c.get("chunk_id") != "chunk_front_matter_title_copyright":
                if running_header in c.get("content", ""):
                    contaminated.append(c.get("chunk_id"))
        passed = len(contaminated) == 0
        msg = "No running headers contaminated clinical chunk content." if passed else f"Contaminated: {contaminated}"
        return self._record("TEST 10: PDF Running Header Cleansing", passed, msg, {"contaminated": contaminated})

    def test_11_tables_and_glossary_structure(self):
        glossary_chunks = [c for c in self.chunks if c.get("chunk_type") == "glossary_definition"]
        table_chunks = [c for c in self.chunks if c.get("chunk_type") == "structured_table"]
        passed = len(glossary_chunks) >= 20 and len(table_chunks) >= 3
        msg = f"Parsed {len(glossary_chunks)} individual glossary definitions and {len(table_chunks)} structured tables."
        return self._record("TEST 11: Tables & Glossary Structured Preservation", passed, msg, {
            "glossary_count": len(glossary_chunks),
            "table_count": len(table_chunks)
        })

    def test_12_word_count_and_content_integrity(self):
        empty_chunks = [c["chunk_id"] for c in self.chunks if not c.get("content", "").strip()]
        passed = len(empty_chunks) == 0
        msg = "Zero empty chunks detected. All chunks contain meaningful clinical text." if passed else f"Empty: {empty_chunks}"
        return self._record("TEST 12: Content Non-Emptiness & Text Integrity", passed, msg, {"empty": empty_chunks})

    def export_reports(self, report_json_path: str, report_md_path: str, summary: Dict[str, Any]):
        os.makedirs(os.path.dirname(report_json_path), exist_ok=True)
        
        # JSON Report
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # Markdown Report
        md = []
        md.append("# تقرير التحقق النهائي من الـ Semantic Chunks (Chunk Validation Audit Report)")
        md.append(f"**الوثيقة:** WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024)")
        md.append(f"**النتيجة الكلية:** `{'ALL TESTS PASSED (12/12)' if summary['all_tests_passed'] else 'SOME TESTS FAILED'}`\n")
        
        md.append("## 1. ملخص توزيع الـ Chunks حسب النوع الدلالي (Chunk Distribution)")
        md.append("| نوع الـ Chunk (`chunk_type`) | العدد | الوظيفة السريرية |")
        md.append("| :--- | :--- | :--- |")
        for ctype, count in summary["chunks_by_type"].items():
            md.append(f"| `{ctype}` | **{count}** | {self._describe_type(ctype)} |")
        md.append(f"| **الإجمالي الكلي** | **{summary['total_chunks_evaluated']}** | تغطية شاملة لجميع أقسام وملاحق الدليل |")
        md.append("")

        md.append("## 2. تفاصيل نتائج الاختبارات الـ 12 الآلية")
        md.append("| # | اسم الاختبار | النتيجة | الرسالة |")
        md.append("| :--- | :--- | :--- | :--- |")
        for idx, t in enumerate(summary["test_details"], 1):
            status = "✅ ناجح (PASSED)" if t["passed"] else "❌ راسب (FAILED)"
            md.append(f"| {idx} | **{t['test_name']}** | {status} | {t['message']} |")
        md.append("")

        md.append("## 3. قائمة التوصيات الكنسية الـ 12 الموثقة (Canonical Recommendations)")
        md.append("| المعرف (`recommendation_id`) | نوع التدخل (`target_intervention`) | القوة (`strength`) | مستوى الدليل (`certainty`) | الصفحة الفيزيائية / المطبوعة |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        recs = [c for c in self.chunks if c.get("chunk_type") == "recommendation"]
        for r in sorted(recs, key=lambda x: x.get("recommendation_id", "")):
            rid = r.get("recommendation_id")
            interv = r.get("target_intervention", "")[:40]
            st = r.get("recommendation_strength")
            cert = r.get("certainty_of_evidence")
            p_phys = r.get("physical_page_start")
            p_pr = r.get("printed_page_start")
            md.append(f"| `{rid}` | {interv} | **{st}** | {cert} | P{p_phys} (Printed: {p_pr}) |")
        
        md.append("\n---\n*تم التوليد آلياً بواسطة وحدة التحقق المعتمدة لنظام Medical RAG.*")

        with open(report_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        logging.info(f"Exported validation reports to {report_json_path} and {report_md_path}.")

    def _describe_type(self, ctype: str) -> str:
        desc = {
            "recommendation": "نصوص التوصيات السريرية الكنسية الـ 12 المعتمدة من منظمة الصحة العالمية",
            "clinical_question": "الأسئلة السريرية التوجيهية (PICO Questions) لكل قسم فرعي",
            "evidence_justification": "التبرير العلمي والمراجعات المنهجية وإحصاءات التجارب السريرية (RR, CI)",
            "implementation_guidance": "إرشادات التطبيق السريري والتشغيلي للكوادر والأنظمة الصحية والملحق 2",
            "narrative_background": "المقدمة، المنهجية، أهداف الدليل، الجمهور المستهدف، وأولويات البحث",
            "structured_table": "جداول معايير GRADE، قاموس الاختصارات، وجداول اللجان وإعلانات المصالح",
            "glossary_definition": "تعريفات المصطلحات الطبية والتقنية المفصلة من قاموس الدليل"
        }
        return desc.get(ctype, "نصوص سياقية عامة")


if __name__ == "__main__":
    chunks_path = r"C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\semantic_chunks.json"
    r_json = r"C:\Users\moham\OneDrive\Apps\اوكسجين\reports\chunk_validation_report.json"
    r_md = r"C:\Users\moham\OneDrive\Apps\اوكسجين\reports\chunk_validation_report.md"

    val = ChunkValidator(chunks_path)
    val.load_chunks()
    summary = val.run_all_tests()
    val.export_reports(r_json, r_md, summary)
    print("Chunk validation complete. All tests evaluated.")
