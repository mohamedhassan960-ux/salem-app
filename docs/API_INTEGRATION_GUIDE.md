# Oxygen Medical RAG — API Integration Guide (Frontend / Client)

دليل تكامل واجهة برمجة التطبيقات الطبية المعتمدة على إرشادات منظمة الصحة العالمية (WHO 2024) للإقلاع عن التدخين.

---

## 1. نظرة عامة (Overview)

- **نوع الخدمة:** RESTful HTTP JSON API
- **بروتوكول النقل:** HTTPS
- **المصادقة (Authentication):** الترويسة `X-API-Key`
- **التشفير:** UTF-8
- **مزود الذكاء الاصطناعي (LLM Provider):** Google Gemini (`google_gemini`)
- **النموذج النشط (Model):** `gemini-3.5-flash-lite` (أو `gemini-2.5-flash-lite` حسب توفر الحساب)
- **الـ URL الحالي:** `https://control-round-occur-friend.trycloudflare.com`
- **زمن الاستجابة المتوقع:** ~1 إلى 3 ثوانٍ

> 💡 **إعداد المفتاح في الخادم:** يتم تمرير المفتاح عبر متغير البيئة `GEMINI_API_KEY` دون وضعه في الكود أو التوثيق العام.

---


## 2. نقاط النهاية المتاحة (Endpoints)

### أ. فحص الحياة (Liveness Probe)
`GET /api/v1/health` أو `GET /health`
- **الوصف:** فحص خفيف وسريع للتحقق من عمل الخادم (0 استدعاءات RAG / 0 توكنز).
- **الاستجابة:**
  ```json
  {
    "status": "ok",
    "service": "oxygen-medical-rag-api"
  }
  ```

---

### ب. فحص الجاهزية (Readiness Probe)
`GET /api/v1/ready` أو `GET /ready`
- **الوصف:** يتحقق من اكتمال تحميل قاعدة المتجهات (171 Chunks) في الذاكرة.
- **الاستجابة:**
  ```json
  {
    "status": "ready",
    "pipeline_ready": true,
    "vector_store_chunks": 171
  }
  ```

---

### ج. فحص البيانات الوصفية (Metadata Probe)
`GET /api/v1/meta`
- **الوصف:** استرجاع إصدار الـ RAG ونوع المزود والموديل النشط بأمان تام وبدون كشف أي مسارات أو مفاتيح سرية.
- **الاستجابة:**
  ```json
  {
    "api_version": "1.0.0",
    "rag_version": "WHO-Tobacco-Cessation-2024-Phase5",
    "provider": "google_gemini",
    "model": "gemini-3.5-flash-lite",
    "circuit_breaker_enabled": true
  }
  ```

---

### ج. المحادثة الإكلينيكية (Clinical Chat)
`POST /api/v1/chat`

#### Headers المطلوبة:
| Header | القيمة | إلزامي؟ |
|---|---|:---:|
| `Content-Type` | `application/json` | نعم |
| `X-API-Key` | `<YOUR_OXYGEN_API_KEY>` | نعم (عند تفعيل المصادقة) |
| `X-Request-ID` | `req_custom_123` *(اختياري للـ Tracing)* | لا |

#### Request Body:
```json
{
  "query": "ما هي العلاجات الدوائية الموصى بها للإقلاع عن التدخين؟",
  "conversation_history": [
    {
      "role": "user",
      "content": "أهلاً دكتور سالم"
    },
    {
      "role": "assistant",
      "content": "أهلاً بحضرتك، أنا دكتور سالم معاك..."
    }
  ]
}
```

#### Success Response (`200 OK`):
```json
{
  "request_id": "req_57e3d5e4f21a",
  "answer": "أهلاً بحضرتك يا فندم... بناءً على التوصيات الطبية المتاحة، فإن الخيارات الدوائية الموصى بها تتضمن استخدام دواء الفارينيكلين... [WHO — Section 3.3.1 — Page 35]",
  "contract_state": "SUPPORTED",
  "grounded": true,
  "safety_status": "DIRECT_EVIDENCE",
  "provider": "google_gemini",
  "model": "gemini-3.5-flash-lite",
  "citations": [
    {
      "source_id": 1,
      "section_number": "3.3.1",
      "physical_page_start": 35,
      "title": "3.3.1. Recommendations",
      "chunk_id": "chunk_sec_3_3_1"
    }
  ],
  "latency_ms": 2128.9,
  "metadata": {
    "query_understanding": {
      "is_arabic": true,
      "detected_intents": ["RECOMMENDATION_SEEKING"]
    },
    "retrieval_metrics": {
      "admitted_evidence_count": 5,
      "is_grounded_in_guideline": true
    },
    "verification": {
      "safety_status": "DIRECT_EVIDENCE"
    }
  }
}
```

#### قاطع الدائرة الحتمي (Deterministic Circuit Breaker — `200 OK`):
في حال السؤال عن أدوية غير معتمدة (مثل مخدر السيلوسيبين) أو خارج النطاق (مثل وقاية المدارس لغير المدخنين):
```json
{
  "request_id": "req_f7e8d9c0b1a2",
  "answer": "أهلاً بحضرتك، بناءً على إرشادات منظمة الصحة العالمية (2024)، هذا التدخل غير مدعوم أو مثبت بالأدلة العلمية المعتمدة للإقلاع عن التدخين، ولا يمكنني تقديم أي جرعات أو جداول علاجية غير مثبتة رسمياً.",
  "contract_state": "UNSUPPORTED",
  "grounded": false,
  "safety_status": "UNSUPPORTED_INTERVENTION_NOT_VERIFIED",
  "provider": "deterministic",
  "model": "grounded_answer_contract_v1",
  "citations": [],
  "latency_ms": 35.2
}
```

---

## 3. حالات الخطأ (Error Responses)

| كود الحالة | المعنى | سبب الحدوث | مثال الاستجابة |
|:---:|---|---|---|
| `401` | Unauthorized | مفتاح الـ API مفقود أو غير صحيح في الـ Header | `{"detail": "Invalid or missing API key in X-API-Key header."}` |
| `422` | Unprocessable Content | نص السؤال فارغ أو يتجاوز 2000 حرف أو دور محادثة غير صالح | `{"detail": [{"loc": ["body", "query"], "msg": "..."}]}` |
| `500` | Internal Server Error | خطأ داخلي غير متوقع في المعالجة | `{"request_id": "req_xxx", "error": "Internal server error..."}` |

---

## 4. مثال كود JavaScript / TypeScript (Fetch API)

```javascript
async function askDoctorSalem(patientQuery, conversationHistory = []) {
  const BASE_URL = "https://<YOUR_CLOUD_RUN_SERVICE_URL>"; // أو http://localhost:8000 أثناء التطوير المحلي
  const API_KEY = "<YOUR_OXYGEN_API_KEY>";

  try {
    const response = await fetch(`${BASE_URL}/api/v1/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Request-ID": `req_${Date.now()}`
      },
      body: JSON.stringify({
        query: patientQuery,
        conversation_history: conversationHistory
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`API Error (${response.status}): ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    console.log("Dr. Salem Response:", data.answer);
    console.log("Contract State:", data.contract_state);
    console.log("Citations:", data.citations);
    return data;
  } catch (error) {
    console.error("Failed to fetch clinical response:", error);
    throw error;
  }
}

// مثال الاستدعاء:
askDoctorSalem("أنا بدخن علبة كل يوم وعصبي في الشغل، أعمل إيه؟");
```
