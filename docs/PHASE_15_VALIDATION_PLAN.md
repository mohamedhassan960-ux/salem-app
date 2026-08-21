# SALEM (سالم) — Phase 15 Production Validation Plan

---

## 1. Objectives & Scope
This plan defines the end-to-end real-world behavioral validation of Salem prior to serving real customers.

### Validation Matrix:
1. **User Journey A (New User Experience)**: Splash → Onboarding (7 Steps) → Auth → Welcome Chat → Clinical Question → WHO Evidence Citations → Plan Creation.
2. **User Journey B (Acute Urge / Craving)**: Urgent Craving Trigger → 60s Elapsed Delay → 4-7-8 Breathing Method → Sensory Disruption → Intensity Check-In → Local & Supabase Persistence.
3. **User Journey C (Relapse / Slip Scenario)**: Non-judgmental slip reporting → Safe cognitive reframing → Plan adjustment without streak shame.
4. **User Journey D (Emergency Safety Circuit Breaker)**: Chest pain / severe dyspnea symptoms → Deterministic escalation to Emergency Ambulance (`123`).
5. **User Journey E (Multi-Tenant Data Isolation)**: User A vs User B access rejection across all PostgreSQL tables.

---

## 2. Methodology & Evidence Criteria
- **Pass Threshold**: Behavior is executed and recorded with real output.
- **Fail Threshold**: Any data leak, unhandled crash, fabricated citation, or missing security boundary.
