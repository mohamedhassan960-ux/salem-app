# دليل حالة ومعمارية مشروع أوكسجين (WHO Medical RAG — Streamlined Architecture)
## Medical RAG — WHO Tobacco Cessation Guideline 2024
### التحديث المعماري الأخير: 2026-08-19

---

## 1. بطاقة تعريف المشروع

| | |
|:---|:---|
| **اسم المشروع** | أوكسجين — WHO Medical RAG (Tobacco Cessation) |
| **مسار المشروع** | `C:\Users\moham\OneDrive\Apps\اوكسجين\` |
| **المصدر الطبي الوحيد** | WHO Clinical Treatment Guideline for Tobacco Cessation in Adults (2024) |
| **المعمارية الإنتاجية المعتمدة** | **Streamlined Production Architecture**:<br>1. **Medical RAG**: "ما هي الحقيقة الطبية؟" (Grounded WHO 2024 Evidence)<br>2. **System Prompt**: "كيف تُشرح المعلومة للمريض بوضوح؟" (Medical Explanation Policy)<br>3. **LLM Generation**: صياغة دافئة ومبسطة بالعامية المصرية مقيدة تماماً بالسياق الطبي<br>4. **Post-Generation Verifier**: التدقيق الصارم لسلامة الجرعات والأرقام واليقين الإكلينيكي |
| **هدف المشروع** | مساعد طبي سلوكي بالعامية المصرية للإقلاع عن التدخين، مقيّد 100% بأدلة WHO ومعايير التواصل الواضح |

---

## 2. المعمارية الإنتاجية المعتمدة (Streamlined Production Architecture)

```text
                     ┌─────────────────────────┐
                     │      رسالة المريض       │
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │ Clinical Query Analysis │
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │       Medical RAG       │
                     │  "ما هي الحقيقة الطبية؟" │
                     │  (WHO Guideline 2024)   │
                     │  (BM25 + Dense E5 + RRF)│
                     └────────────┬────────────┘
                                  ↓
                           الأدلة الطبية
                                  ↓
                     ┌─────────────────────────┐
                     │  System Prompt Policy   │
                     │ "كيف تُشرح بوضوح وأمان؟" │
                     │ (14 Communication Rules)│
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │   LLM Generator Layer   │
                     │ (عامية مصرية دافئة ومقيدة)│
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │ Simplification Verifier │
                     │ (تدقيق الأرقام والجرعات)│
                     └────────────┬────────────┘
                                  ↓
              الرد الإكلينيكي المعتمد والمبسط + توثيق WHO
```

---

## 3. جرد ملفات النظام الكامل

### Scripts (محرك النظام الإنتاجي)
| الملف | الغرض |
|:---|:---|
| `scripts/query_understanding.py` | فهم الاستعلام السريري (قصد / كيان / لهجة / خارج نطاق) |
| `scripts/bm25_retriever.py` | استرجاع BM25 (Sparse) للأدلة الطبية |
| `scripts/dense_retriever.py` | استرجاع كثيف (Multilingual-E5-small) للأدلة الطبية |
| `scripts/hybrid_retriever.py` | دمج RRF (BM25 + Dense) |
| `scripts/reranker.py` | إعادة ترتيب سريري متعدد الأبعاد |
| `scripts/evidence_quality_gate.py` | بوابة جودة الأدلة وحماية التوصيات السلبية |
| `scripts/context_assembler.py` | تجميع السياق الطبي مع الحفاظ على الاستشهادات |
| `scripts/llm_generator.py` | طبقة التوليد بالذكاء الاصطناعي مع Prompt الأمان والتأصيل |
| `scripts/llm_generation_pipeline.py` | **خط الأنابيب الإنتاجي الرئيسي (Single Medical RAG + Verifier)** |
| `scripts/simplification_verifier.py` | مدقق ما بعد التوليد لفحص الجرعات والأرقام واليقين وموانع الاستعمال |
| `scripts/simplification_pipeline.py` | [مُحدَّث كـ Legacy Wrapper] للتوافقية الخلفية |
| `scripts/run_all_tests.py` | مشغّل شامل لجميع مجموعات الاختبار (13 مجموعة اختبار) |

### Prompts
| الملف | الغرض |
|:---|:---|
| `prompts/clinical_assistant_system.txt` | موجه النظام الرئيسي مدعم بالقسم 6 (سياسة الشرح والتواصل ومبادئ التبسيط الـ 14) |
