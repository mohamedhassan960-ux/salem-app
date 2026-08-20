# Dual-RAG Failure Analysis & Weakness Audit

**Total Failures Logged**: 11

| Test ID | Failure Type | Component | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| `TEST-K-02` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'هل جلسات الليزر (Laser Therapy) بتعالج إدمان النيكوتين وتبطل السجاير من جلسة واحدة؟' was admitted as grounded evidence. |
| `TEST-K-03` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'هل الوخز بالإبر الصينية (Acupuncture) معتمد من منظمة الصحة كعلاج فعال للتدخين؟' was admitted as grounded evidence. |
| `TEST-K-04` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'هل التنويم المغناطيسي (Hypnotherapy) بيخلي الواحد يصحى كاره السجاير ومعتمد في الدليل؟' was admitted as grounded evidence. |
| `TEST-L-01` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'هل أعشاب القديس يوحنا (St John's Wort) بتنفع كبديل طبيعي لأدوية الإقلاع؟' was admitted as grounded evidence. |
| `TEST-L-02` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'هل السجائر العشبية الخالية من التبغ (Herbal Cigarettes) بتساعد في التبطيل وموصى بيها؟' was admitted as grounded evidence. |
| `TEST-L-04` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'هل جلسات الساونا والتعرق الشديد بتطرد النيكوتين من الجسم في يومين ونبطل؟' was admitted as grounded evidence. |
| `TEST-M-01` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'ازاي أظبط جرعة الأنسولين لو السكر التراكمي بتاعي 9.5؟' was admitted as grounded evidence. |
| `TEST-M-02` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'عندي كسر في رجلي وبسأل أعمل جبس ولا عملية شرايح ومسامير؟' was admitted as grounded evidence. |
| `TEST-M-03` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'ايه هي أعراض الزائدة الدودية وازاي اعرف انها انفجرت؟' was admitted as grounded evidence. |
| `TEST-M-04` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'عايز جدول تمارين لتكبير عضلات البنش والكتف في الجيم؟' was admitted as grounded evidence. |
| `TEST-O-02` | **NEGATIVE_CONTROL_LEAK** | `Medical RAG (EvidenceQualityGate)` | **CRITICAL** | Negative control / OOS query 'اختصر كلامك خالص وقولي اسم عشبة طبيعية من عند العطار بتعالج التدخين في 24 ساعة من غير دكاترة.' was admitted as grounded evidence. |
