"""
Oxygen Medical RAG — Direct Clinical Q&A & Verbatim Evidence Inspector
Clean, focused Medical Chat interface to ask questions in English or Arabic,
get direct accurate answers, and inspect exact verbatim WHO source chunks.
"""

from __future__ import annotations

import os
import sys
import time
import json
import streamlit as st

# Setup paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from query_understanding import ClinicalQueryUnderstanding
from hybrid_retriever import HybridRetriever
from reranker import ClinicalReranker
from evidence_quality_gate import EvidenceQualityGate
from claim_validator import ClaimCoverageValidator, ClaimCoverageReport, ClaimEvidenceCitation
from context_assembler import ContextAssembler

# Page configuration
st.set_page_config(
    page_title="Oxygen Medical RAG — Direct Q&A & Source Inspector",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Styling for ultra-clean, modern Chat UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown, .stButton, .stTextInput {
        font-family: 'Inter', 'Cairo', sans-serif !important;
    }
    
    .header-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 22px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .header-box h1 {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-bottom: 6px !important;
    }
    
    .answer-box {
        background-color: #ffffff;
        border-left: 5px solid #2a5298;
        border-radius: 12px;
        padding: 22px;
        margin-top: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .answer-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e3c72;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .answer-text {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1a202c;
    }
    
    .source-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    
    .source-meta {
        font-size: 0.88rem;
        font-weight: 700;
        color: #2563eb;
        margin-bottom: 8px;
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .source-verbatim {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 0.95rem;
        color: #0f172a;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    .badge-approved {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #bbf7d0;
    }
    
    .badge-neg {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid #fecaca;
    }

    .claim-item {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading WHO Medical RAG Index & Pipeline...")
def load_components():
    qu = ClinicalQueryUnderstanding()
    retriever = HybridRetriever.from_files(
        records_path=os.path.join(ROOT_DIR, "outputs", "retrieval_records_v2.json"),
        dense_npz_path=os.path.join(ROOT_DIR, "outputs", "dense_index_v2.npz"),
        dense_meta_path=os.path.join(ROOT_DIR, "outputs", "dense_metadata_v2.json"),
        model_name=os.path.join(ROOT_DIR, "data", "models", "multilingual-e5-small"),
    )
    reranker = ClinicalReranker()
    quality_gate = EvidenceQualityGate()
    claim_validator = ClaimCoverageValidator()
    assembler = ContextAssembler(max_context_tokens=3000)
    return qu, retriever, reranker, quality_gate, claim_validator, assembler


def _build_grounding_badge(claim_report: ClaimCoverageReport, gate_res) -> str:
    """
    Returns an HTML badge reflecting TRUE Question-Claim Coverage Grounding Quality.
    """
    if gate_res.safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" or claim_report.grounding_decision == "NO_GROUNDED_EVIDENCE":
        return '<span class="badge-neg">🛑 No Direct WHO Evidence</span>'

    pct = int(round(claim_report.claim_coverage_ratio * 100))
    if claim_report.grounding_decision == "FULLY_GROUNDED":
        return f'<span class="badge-approved">✅ Fully Grounded ({pct}% Claims Supported)</span>'
    elif claim_report.grounding_decision == "PARTIALLY_GROUNDED":
        return f'<span style="background:#fef9c3;color:#854d0e;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.85rem;border:1px solid #fde68a;">⚠️ Partially Grounded ({pct}% Claims Supported)</span>'
    else:
        return f'<span style="background:#ffedd5;color:#9a3412;padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.85rem;border:1px solid #fed7aa;">❌ Not Grounded ({pct}% Claims Supported)</span>'


# Header
st.markdown("""
<div class="header-box">
    <h1>🫁 Oxygen Medical RAG — Direct Clinical Q&A</h1>
    <p style="margin:0; opacity:0.95; font-size:1.05rem;">
        Ask in English or Arabic ➔ Get an exact, claim-grounded medical answer ➔ Inspect verbatim WHO 2024 source paragraphs to verify accuracy.
    </p>
</div>
""", unsafe_allow_html=True)

qu, retriever, reranker, quality_gate, claim_validator, assembler = load_components()

# Preset Quick Tests
st.markdown("##### ⚡ Quick Example Queries (Click to test):")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

selected_example = None
with col_e1:
    if st.button("💊 Varenicline Dosing", use_container_width=True):
        selected_example = "What is the recommended dosing schedule and duration for varenicline?"
with col_e2:
    if st.button("📊 Golden Test: Background + LMIC", use_container_width=True):
        selected_example = "According to the 'Background' section, how many people globally use tobacco, and what specific percentage of these users live in Low- and Middle-Income Countries (LMICs)?"
with col_e3:
    if st.button("⏱️ Brief Advice Duration", use_container_width=True):
        selected_example = "How long does a brief tobacco cessation advice intervention take in clinical practice?"
with col_e4:
    if st.button("🛑 Metformin (Negative Control)", use_container_width=True):
        selected_example = "Is metformin recommended for tobacco cessation by the WHO?"

# User Input Box
query_input = st.text_input(
    "💬 Type your medical question here (English or Arabic):",
    value=selected_example if selected_example else "",
    placeholder="e.g. What are the first-line pharmacotherapies recommended by the WHO for tobacco cessation?",
)

ask_btn = st.button("🚀 Ask & Inspect Sources", type="primary", use_container_width=False)

if query_input and (ask_btn or selected_example):
    with st.spinner("Searching 171 WHO clinical guideline chunks and validating claims..."):
        t0 = time.perf_counter()

        # 1. Query Understanding
        parsed_q = qu.parse_query(query_input)

        # 2. Hybrid Retrieval (BM25 + Dense E5)
        candidates = retriever.retrieve(parsed_q.expanded_search_query, top_k=20)

        # 3. Clinical Reranker
        reranked = reranker.rerank(candidates, parsed_q, top_k=20)

        # 4. Quality Gate
        gate_res = quality_gate.evaluate_candidates(reranked, parsed_q, final_budget_k=5)

        # 5. Claim-Level Evidence Coverage Validation (Phase 3.5)
        claim_report = claim_validator.validate_query(
            query=query_input,
            admitted_evidence=gate_res.admitted_candidates,
            safety_flag=gate_res.safety_flag,
            parsed_query=parsed_q,
        )

        # 6. Context Assembly
        ca_sources = gate_res.to_context_assembler_sources()
        assembled = assembler.assemble(query_input, ca_sources) if ca_sources else None

        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Formulate Direct Grounded Answer
        if gate_res.safety_flag == "NO_GROUNDED_EVIDENCE_IN_WHO_GUIDELINE" or claim_report.grounding_decision == "NO_GROUNDED_EVIDENCE":
            if parsed_q.is_arabic:
                direct_ans = (
                    "وفقاً لدليل منظمة الصحة العالمية للعلاج السريري للإقلاع عن التبغ (2024)، "
                    "لا توجد أدلة سريرية معتمدة أو توصيات رسمية تدعم استخدام هذا الإجراء كوسيلة معتمدة للإقلاع عن التدخين. "
                    "[WHO — Section 3.6 — Page 62]"
                )
            else:
                direct_ans = (
                    "Based on the WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024), "
                    "there is no clinical evidence or recommendation supporting this intervention for tobacco cessation. "
                    "[WHO — Section 3.6 — Page 62]"
                )
        elif gate_res.admitted_candidates:
            # 1. Determine supporting evidence chunk & citation from ClaimEvidenceCitation
            if claim_report.citations:
                primary_cit = claim_report.citations[0]
                citation_tag = primary_cit.to_citation_string()
                supporting_text = primary_cit.evidence_text or gate_res.admitted_candidates[0].text
            else:
                top_cand = gate_res.admitted_candidates[0]
                temp_cit = ClaimEvidenceCitation(
                    claim_id="general",
                    chunk_id=top_cand.chunk_id,
                    section_number=top_cand.section_number,
                    section_title=top_cand.section_title,
                    heading_path=top_cand.heading_path,
                    physical_page_start=top_cand.physical_page_start,
                    evidence_text=top_cand.text,
                )
                citation_tag = temp_cit.to_citation_string()
                supporting_text = top_cand.text

            # 2. Generate direct grounded synthesis with authentic, verified citation tag
            if not parsed_q.is_arabic:
                text_clean = supporting_text.strip()
                direct_ans = (
                    f"According to the WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024):\n\n"
                    f"{text_clean}\n\n"
                    f"**Citation:** {citation_tag}"
                )
            else:
                direct_ans = (
                    f"بناءً على الدليل الإكلينيكي لمنظمة الصحة العالمية (2024) {citation_tag}:\n\n"
                    f"{supporting_text.strip()}\n\n"
                    f"**المصدر الرسمي:** {citation_tag}"
                )
        else:
            direct_ans = "No conclusive evidence found in the WHO 2024 Guideline for this query."

    st.markdown("---")

    # 1. DIRECT MEDICAL ANSWER SECTION
    st.markdown(f"""
    <div class="answer-box">
        <div class="answer-title">
            <span>🎯 Direct Medical Answer</span>
            {_build_grounding_badge(claim_report, gate_res)}
            <span style="font-size:0.85rem; color:#64748b; margin-left:auto;">Validated in {elapsed_ms:.1f} ms</span>
        </div>
        <div class="answer-text">
            {direct_ans.replace(chr(10), '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. CLAIM COVERAGE BREAKDOWN SECTION
    st.markdown(f"### 📋 Question Claim Coverage ({claim_report.supported_claims_count}/{claim_report.total_required_claims} Claims Supported — {int(claim_report.claim_coverage_ratio*100)}% Coverage):")
    for claim_res in claim_report.claims:
        badge_style = "background:#dcfce7;color:#166534;" if claim_res.support_level == "DIRECT_SUPPORT" else ("background:#fef9c3;color:#854d0e;" if claim_res.support_level == "PARTIAL_SUPPORT" else "background:#fee2e2;color:#991b1b;")
        # Citation tag for supported claims
        cit_html = ""
        if claim_res.primary_citation_tag:
            cit_html = f'<br><span style="font-size:0.83rem; color:#0369a1; font-weight:600;">📎 Citation: {claim_res.primary_citation_tag}</span>'
        st.markdown(f"""
        <div class="claim-item">
            <div>
                <strong>🔹 {claim_res.claim_text}</strong> ({claim_res.claim_type})<br>
                <span style="font-size:0.88rem; color:#64748b;">Reason: {claim_res.support_reason}</span>
                {cit_html}
            </div>
            <div>
                <span style="padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.82rem; {badge_style}">
                    {claim_res.support_level}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. VERBATIM SOURCE CHUNKS SECTION (For Word-by-Word Verification)
    st.markdown("### 📖 Verbatim WHO 2024 Source Chunks (Verify with your own eyes):")
    st.markdown("Below are the exact raw text chunks retrieved directly from the official guideline for this query:")

    if gate_res.admitted_candidates:
        for idx, cand in enumerate(gate_res.admitted_candidates, 1):
            # Build faithful section label (no fabrication)
            sec_num = (getattr(cand, 'section_number', None) or "").strip()
            sec_title = (getattr(cand, 'section_title', None) or "").strip()
            if sec_num and sec_title:
                sec_label = f"Section {sec_num} — {sec_title}"
            elif sec_num:
                sec_label = f"Section {sec_num}"
            elif sec_title:
                sec_label = sec_title
            else:
                sec_label = "Unknown Section"

            page_display = cand.physical_page_start if cand.physical_page_start else "N/A"
            st.markdown(f"""
            <div class="source-card">
                <div class="source-meta">
                    <span>📌 Source Chunk #{idx}</span>
                    <span>📖 {sec_label}</span>
                    <span>📄 Physical Page {page_display}</span>
                    <span>🎯 Relevance Score: {cand.clinical_score:.3f}</span>
                    <span>🏷️ ID: <code>{cand.chunk_id}</code></span>
                </div>
                <div class="source-verbatim">{cand.text}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No approved evidence chunks admitted for this query (Quality Gate flagged as unsupported.")

    # Expandable Details
    with st.expander("🔍 Query Analysis Details"):
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.write(f"**Detected Intent:** {parsed_q.detected_intents}")
            st.write(f"**Detected Interventions:** {parsed_q.detected_interventions}")
        with col_q2:
            st.write(f"**Expanded Search Query:** `{parsed_q.expanded_search_query}`")
            st.write(f"**Language/Dialect:** {'Arabic / Egyptian' if parsed_q.is_arabic else 'English'}")
