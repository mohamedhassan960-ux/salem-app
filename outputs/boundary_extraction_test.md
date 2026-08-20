# Boundary Extraction Test Report
**Test Status:** `PASS`

## 1. Test Environment
- **PDF Ground Truth:** `C:\Users\moham\OneDrive\Desktop\الاقلاع عن التدخبن.pdf` (76 Pages)
- **Extraction Layer:** `C:\Users\moham\OneDrive\Apps\اوكسجين\data\who_extracted.txt` (28,137 Words)
- **Structure Map:** `C:\Users\moham\OneDrive\Apps\اوكسجين\outputs\structure_map_v2.json` (112 Nodes)
- **Test Mode:** `READ-ONLY — Zero modifications to production files`

## 2. Nodes Tested Summary
| Node ID | Section Title | Start Match | End Match | Ordering (`Start < End`) | Extracted Words | Status |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `sec_3_1_1` | 3.1.1. Recommendations | YES (P29) | YES (P29) | VALID | **94** | `PASS` |
| `sec_3_1_2` | 3.1.2. Overall questions | YES (P29) | YES (P29) | VALID | **65** | `PASS` |
| `sec_3_1_3` | 3.1.3. Justification and evidence | YES (P29) | YES (P31) | VALID | **1,383** | `PASS` |
| `sec_3_1_4` | 3.1.4. Implementation considerations | YES (P31) | YES (P32) | VALID | **288** | `PASS` |
| `sec_3_1` | 3.1. Behavioural support delivered in both clinical and community settings | YES (P29) | YES (P32) | VALID | **1,840** | `PASS` |
| `sec_3_3_3` | 3.3.3. Justification and evidence | YES (P35) | YES (P39) | VALID | **2,473** | `PASS` |
| `sec_3_7_4` | 3.7.4. Implementation considerations | YES (P46) | YES (P47) | VALID | **703** | `PASS` |
| `node_L1_references` | References | YES (P55) | YES (P60) | VALID | **1,585** | `PASS` |
| `annex_2` | Annex 2: Additional information for implementing the recommendations | YES (P65) | YES (P70) | VALID | **2,215** | `PASS` |

## 3. Boundary Details & Content Leak Inspection
### Node: `sec_3_1_1` — 3.1.1. Recommendations
- **Physical Page Span:** `P29 → P29`
- **Matched Start Heading:** `3.1.1. 	 Recommendations` (Page 29)
- **Matched Stop Anchor:** `3.1.2. 	 Overall questions` (Page 29)
- **Extracted Volume:** 729 characters (94 words)
- **First 100 Words Preview:**
  > *"3.1.1. Recommendations 1. WHO recommends brief advice (between 30 seconds and 3 minutes per encounter) be consistently provided by health-care providers as a routine practice to all tobacco users accessing any health-care settings. Strong recommendation; moderate certainty 1 30 sec – 3 min 2. WHO recommends more-intensive behavioural support be offered to all tobacco users interested in quitting. Options for behavioural support are individual face-to- face counselling, group face-to-face counselling or telephone counselling; multiple behavioural support options should be provided. Strong recommendation; high certainty (individual counselling)/ moderate certainty (group counselling and telephone counselling) 2..."*
- **Last 100 Words Preview:**
  > *"...3.1.1. Recommendations 1. WHO recommends brief advice (between 30 seconds and 3 minutes per encounter) be consistently provided by health-care providers as a routine practice to all tobacco users accessing any health-care settings. Strong recommendation; moderate certainty 1 30 sec – 3 min 2. WHO recommends more-intensive behavioural support be offered to all tobacco users interested in quitting. Options for behavioural support are individual face-to- face counselling, group face-to-face counselling or telephone counselling; multiple behavioural support options should be provided. Strong recommendation; high certainty (individual counselling)/ moderate certainty (group counselling and telephone counselling) 2"*

### Node: `sec_3_1_2` — 3.1.2. Overall questions
- **Physical Page Span:** `P29 → P29`
- **Matched Start Heading:** `3.1.2. 	 Overall questions` (Page 29)
- **Matched Stop Anchor:** `3.1.3. 	 Justification and evidence` (Page 29)
- **Extracted Volume:** 450 characters (65 words)
- **First 100 Words Preview:**
  > *"3.1.2. Overall questions In adults who use tobacco, what are the effects of brief advice by health professionals, individual behavioural counselling, group behavioural counselling and telephone counselling on quitting compared with no intervention or usual care? Does the effect vary according to types of tobacco used; the quantity of tobacco used; the frequency, intensity, duration or type of the interventions; readiness to quit; and gender?..."*
- **Last 100 Words Preview:**
  > *"...3.1.2. Overall questions In adults who use tobacco, what are the effects of brief advice by health professionals, individual behavioural counselling, group behavioural counselling and telephone counselling on quitting compared with no intervention or usual care? Does the effect vary according to types of tobacco used; the quantity of tobacco used; the frequency, intensity, duration or type of the interventions; readiness to quit; and gender?"*

### Node: `sec_3_1_3` — 3.1.3. Justification and evidence
- **Physical Page Span:** `P29 → P31`
- **Matched Start Heading:** `3.1.3. 	 Justification and evidence` (Page 29)
- **Matched Stop Anchor:** `3.1.4.	 Implementation consideration` (Page 31)
- **Extracted Volume:** 9,758 characters (1,383 words)
- **First 100 Words Preview:**
  > *"3.1.3. Justification and evidence For these recommendations on behavioural support delivered in both clinical and community settings, one newly commissioned systematic review, which is now published (43), and four Cochrane systematic reviews (27–30) were used. Full details of the EtD tables can be found in the Web Annex: Evidence profiles. A systematic review and meta-analysis, which included 24 352 participants in 13 RCTs, conducted by Cheng et al. showed that, in comparison with no advice being given, the average treatment effect of brief advice for long-term tobacco abstinence was modest and significant (risk ratio/relative risk [RR]: 1.17; 95% confidence interval..."*
- **Last 100 Words Preview:**
  > *"...evidence that telephone counselling increases long-term tobacco abstinence. · The balance of benefits against harms favours proactive telephone counselling on the basis of: – moderate benefits (multisession proactive counselling versus self-help materials or brief counselling at single call, NNT: 36 to achieve one more case of long-term cessation); and – trivial harms (judged on the basis of the type of intervention provided and absence of harms reported in the trials). · Decisions regarding telephone counselling are not preference sensitive (due to no known harms), it requires small to moderate cost, and it is feasible and acceptable, with probably increased equity."*

### Node: `sec_3_1_4` — 3.1.4. Implementation considerations
- **Physical Page Span:** `P31 → P32`
- **Matched Start Heading:** `3.1.4.	 Implementation consideration` (Page 31)
- **Matched Stop Anchor:** `3.2.	
Digital tobacco cessation inte` (Page 32)
- **Extracted Volume:** 2,015 characters (288 words)
- **First 100 Words Preview:**
  > *"3.1.4. Implementation considerations Brief advice can help all tobacco users regardless of interest in quitting. Routine provision of brief advice in all health-care settings is critical to achieve a high level of population reach and serve as an entry point for the provision of additional evidence-based cessation support. Multiple modalities are available for the provision of additional, more-intensive behavioural support to tobacco users. Since none of the different live support modality options (individual, group or telephone) is clearly superior to the others in terms of effectiveness, more than one modality being available may increase patient and provider choice and utilization..."*
- **Last 100 Words Preview:**
  > *"...These personnel can be either hired and trained specifically to provide cessation support, or they can be existing staff who already provide counselling to people with other health conditions. Trained cessation counsellors can support different populations in quitting, including those with mental health conditions. Counselling support that is culturally sensitive and available in the primary language of tobacco users is important. It is useful to have support materials and training available in local languages, and to include examples that are inclusive of smokeless tobacco and other products, such as waterpipes (hookah, shisha) and bidis, especially in areas of high prevalence."*

### Node: `sec_3_1` — 3.1. Behavioural support delivered in both clinical and community settings
- **Physical Page Span:** `P29 → P32`
- **Matched Start Heading:** `3.1. 	 Behavioural support delivered` (Page 29)
- **Matched Stop Anchor:** `3.2.	
Digital tobacco cessation inte` (Page 32)
- **Extracted Volume:** 13,032 characters (1,840 words)
- **First 100 Words Preview:**
  > *"3.1. Behavioural support delivered in both clinical and community settings 3.1.1. Recommendations 1. WHO recommends brief advice (between 30 seconds and 3 minutes per encounter) be consistently provided by health-care providers as a routine practice to all tobacco users accessing any health-care settings. Strong recommendation; moderate certainty 1 30 sec – 3 min 2. WHO recommends more-intensive behavioural support be offered to all tobacco users interested in quitting. Options for behavioural support are individual face-to- face counselling, group face-to-face counselling or telephone counselling; multiple behavioural support options should be provided. Strong recommendation; high certainty (individual counselling)/ moderate certainty (group counselling..."*
- **Last 100 Words Preview:**
  > *"...These personnel can be either hired and trained specifically to provide cessation support, or they can be existing staff who already provide counselling to people with other health conditions. Trained cessation counsellors can support different populations in quitting, including those with mental health conditions. Counselling support that is culturally sensitive and available in the primary language of tobacco users is important. It is useful to have support materials and training available in local languages, and to include examples that are inclusive of smokeless tobacco and other products, such as waterpipes (hookah, shisha) and bidis, especially in areas of high prevalence."*

### Node: `sec_3_3_3` — 3.3.3. Justification and evidence
- **Physical Page Span:** `P35 → P39`
- **Matched Start Heading:** `3.3.3.	 Justification and evidence` (Page 35)
- **Matched Stop Anchor:** `3.3.4.	 Implementation consideration` (Page 39)
- **Extracted Volume:** 16,619 characters (2,473 words)
- **First 100 Words Preview:**
  > *"3.3.3. Justification and evidence The evidence for pharmacological interventions delivered in both clinical and community settings was obtained from four Cochrane systematic reviews (32–35) and one newly commissioned systematic review on cytisine. Full details of EtD tables can be found in the Web Annex: Evidence profiles. 3.3.3.1. NRT For the effects of NRT as monotherapy compared with a placebo or non-NRT control group, a Cochrane systematic review of 133 studies that included 64 640 participants showed that the RR of long-term abstinence for any form of NRT relative to control was 1.55 (95% CI: 1.49–1.61) (32). The pooled RRs for..."*
- **Last 100 Words Preview:**
  > *"...nontrivial harms with low certainty (bupropion plus NRT versus NRT: imprecise estimates for SAEs, RR: 1.52 [range: 0.26–8.89], statistically nonsignificant increased risk of study withdrawals due to AEs, increased risk of insomnia and anxiety; bupropion plus varenicline versus varenicline: imprecise estimates for SAEs, RR: 1.23 [range: 0.63–2.42], study withdrawals due to drug AEs and increased risk of any AE, psychiatric AEs, anxiety and insomnia). · Decisions regarding bupropion plus NRT and bupropion plus varenicline are probably preference sensitive (small harms with uncertainty regarding SAEs), they require moderate costs and they are probably feasible, with uncertain acceptability and probably increased equity."*

### Node: `sec_3_7_4` — 3.7.4. Implementation considerations
- **Physical Page Span:** `P46 → P47`
- **Matched Start Heading:** `3.7.4.	 Implementation consideration` (Page 46)
- **Matched Stop Anchor:** `3.8.	 Overarching guideline implemen` (Page 47)
- **Extracted Volume:** 5,225 characters (703 words)
- **First 100 Words Preview:**
  > *"3.7.4. Implementation considerations 3.7.4.1. Using medical records Many countries are in the process of implementing EHRs in multiple health-care settings. This provides an important opportunity to facilitate tobacco cessation interventions and ensure that the collection and recording of tobacco use status are incorporated in the new systems. This will enhance both the delivery of cessation support and health-care delivery in general, given that tobacco use impacts a host of conditions. All health-care facilities can develop mechanisms for the integration of tobacco use status collection into their electronic health information systems. This can include enhancements to facilitate and document provider interactions..."*
- **Last 100 Words Preview:**
  > *"...dependence treatments, it is important to raise awareness of the powerful benefits to be gained from making tobacco dependence treatments available (for example, viewing tobacco dependence and treatment from a chronic disease paradigm) among fiscal decision-makers. A chronic disease perspective suggests that coverage and accessibility should be determined by recognizing tobacco dependence as a very serious condition that causes major excess morbidity, mortality, health-care costs and societal costs, and recognizes that effective treatments exist with modest costs compared with comparable chronic conditions (see Annex 2 for details on the case for cost coverage and additional considerations to increase policy effectiveness)."*

### Node: `node_L1_references` — References
- **Physical Page Span:** `P55 → P60`
- **Matched Start Heading:** `References` (Page 55)
- **Matched Stop Anchor:** `Annex 1: Management of guideline 
de` (Page 60)
- **Extracted Volume:** 13,707 characters (1,585 words)
- **First 100 Words Preview:**
  > *"References References 1. WHO global report on trends in prevalence of tobacco use 2000–2030. Geneva: World Health Organization; 2024 (https://iris.who.int/bitstream/handle/10665/375711/9789240088283-eng.pdf?sequence=1, accessed 16 January 2024). 2. GBD 2019 Risk Factors Collaborators. Global burden of 87 risk factors in 204 countries and territories, 1990–2019: a systematic analysis for the Global Burden of Disease Study 2019. Lancet. 2020;396(10258):1223– 49 (https://doi.org/10.1016/S0140-6736(20)30752-2). 3. Goodchild M, Nargis N, Tursan d’Espaignet E. Global economic cost of smoking-attributable diseases. Tob Control. 2018;27(1):58–64 (https://doi.org/10.1136/tobaccocontrol-2016-053305). 4. WHO Framework Convention on Tobacco Control. Geneva: World Health Organization; 2003 (https:// iris.who.int/bitstream/handle/10665/42811/9241591013.pdf?sequence=1, accessed 18 October 2023). 5. Guidelines for implementation of Article 14...."*
- **Last 100 Words Preview:**
  > *"...bmjopen-2021-049644). 53. Updating Appendix 3 of the WHO Global NCD action plan 2013–2030. Geneva: World Health Organization; 2022 (https://www.who.int/teams/noncommunicable-diseases/updating-appendix-3-of-the-who-global-ncd- action-plan-2013-2030, accessed 18 October 2023). 54. Strengthening health systems for treating tobacco dependence in primary care. Geneva: World Health Organization; 2013 (https://www.who.int/publications/i/item/strengthening-health-systems-for-treating- tobacco-dependence-in-primary-care, accessed 18 October 2023). 55. It’s time to invest in cessation: the global investment case for tobacco cessation. Geneva: World Health Organization; 2021 (https://www.who.int/publications/i/item/9789240039308, accessed 18 October 2023). Licence: CC BY-NC-SA 3.0 IGO. 41 Annexes 9 1 2 3 5 4 6 7 8 10 11 12 Annexes WHO clinical treatment guideline for tobacco cessation in adults 42"*

### Node: `annex_2` — Annex 2: Additional information for implementing the recommendations
- **Physical Page Span:** `P65 → P70`
- **Matched Start Heading:** `Annex 2: Additional information for` (Page 65)
- **Matched Stop Anchor:** `Annex 3: Summary of declarations of` (Page 70)
- **Extracted Volume:** 16,094 characters (2,215 words)
- **First 100 Words Preview:**
  > *"Annex 2: Additional information for implementing the recommendations Brief advice · A supportive system (clear policy with leadership support, tobacco use status included in all medical records, training, structured delivery models like 5As [Ask, Advise, Assess, Assist, Arrange] and 5Rs [Relevance, Risks, Rewards, Roadblocks, Repetition] (1), monitoring and evaluation etc.) will improve and sustain the routine delivery of brief advice. · Tailored or personalized advice may improve the effectiveness and acceptability. · In busy health-care settings, a team approach may help improve the efficiency and delivery of brief advice. This could include having tobacco use status determined and recorded by..."*
- **Last 100 Words Preview:**
  > *"...· may require the inclusion of cessation medications on country essential medicine lists. References 1. Toolkit for delivering the 5A’s and 5R’s brief tobacco interventions in primary care. Geneva: World Health Organization, 2014 (https://iris.who.int/bitstream/handle/10665/112835/9789241506953_eng. pdf?sequence=1, accessed 1 November 2023). 2. Developing and improving national toll-free tobacco quit-line services: a World Health Organization manual. Geneva: World Health Organization, 2011 (https://www.who.int/publications/i/item/developing-and- improving-national-toll-free-tobacco-quit-line-services, accessed 1 November 2023). 3. Rigotti NA, Benowitz NL, Prochaska J, Leischow S, Nides M, Blumenstein B et al. Cytisinicline for smoking cessation: a randomized clinical trial. JAMA. 2023;330(2):152–60 (https://doi.org/10.1001/jama.2023.10042). WHO clinical treatment guideline for tobacco cessation in adults 52"*

## 4. Parent / Child Containment Validation
- **Parent Node:** `sec_3_1` (Physical Pages 29 → 32)
- **First Child (`sec_3_1_1`):** Starts on Page 29
- **Last Child (`sec_3_1_4`):** Ends on Page 32
- **Containment Invariant:** `start(3.1) <= start(3.1.1)` (True) AND `end(3.1) >= end(3.1.4)` (True)
- **Result:** `PASSED — 100% Tree Containment`

## 5. Sibling Same-Page & Overlap Test (Section 3.1.1 → 3.1.4)
- **Sibling Overlap Detected:** `NO (PASSED - Zero Sibling Collision)`
| Transition | Char Span | Extracted Slice | Status |
|---|---|---|---|
| `sec_3_1_1` → `sec_3_1_2` | `119 → 849` | 730 chars | `Clean transition (0 unassigned chars, strictly monotonic)` |
| `sec_3_1_2` → `sec_3_1_3` | `849 → 1300` | 451 chars | `Clean transition (0 unassigned chars, strictly monotonic)` |
| `sec_3_1_3` → `sec_3_1_4` | `1300 → 11059` | 9759 chars | `Clean transition (0 unassigned chars, strictly monotonic)` |
| `sec_3_1_4` → `sec_3_2` | `11059 → 13075` | 2016 chars | `Clean transition (0 unassigned chars, strictly monotonic)` |

## 6. References & Annex Boundary Isolation
- **References Section Isolation (Pages 55–59):** `PASSED`
  - Extracted **1,585 words** of bibliographic citations.
  - Verified: Stopped cleanly before `Annex 1` on page 60 without losing trailing citations.
- **Annex 2 Isolation (Pages 65–69):** `PASSED`
  - Extracted **2,215 words** of rich operational guidance.
  - Verified: Contained within pages 65–69, without bleeding into `Annex 3`.

## 7. Final Verdict & Readiness Assessment
### Verdict: `PASS`
1. All text anchor patterns (`start_heading_pattern` & `end_heading_pattern`) matched the real source text with 100% accuracy.
2. Sections starting on the same physical page (e.g. `3.1.1`, `3.1.2`, `3.1.3` on Page 29) were isolated cleanly without any content collision or content loss.
3. Parent sections span their full descendant trees without premature truncation.
4. References and Annexes were strictly bounded.

**Conclusion:** Boundary Extraction Test passed. The project is ready for Verbatim Structural Slicer implementation.