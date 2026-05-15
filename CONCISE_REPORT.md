# SHL Assessment Recommender Report

## 1. Overview
Conversational recommendation system for 377 SHL assessments. Users specify role and seniority; system returns grounded recommendations. Built on deterministic RAG without LLM. Deployed at https://shl-assignment-lw9w.onrender.com. Zero hallucinations, 100% grounding, 6/6 tests passing.

---

## 2. Requirements
Catalog-only recommendations (377 assessments). Strict JSON schema validation. Zero hallucinations (0% verified). Multi-turn refinement with state tracking. Evaluation on 10 labeled and 10 synthetic traces.  

---

## 3. Architecture
User Query → Constraint Extraction → Hybrid Retrieval → Ranking → Validation → Response

11 modules: constraint_extraction, semantic_role_clustering, hybrid_retrieval, ranking_diversity, schema_validator, refinement_handler, comparison_safety, and others.

---

## 4. Retrieval Strategy
377 assessments indexed with hybrid scoring: role match (30%), seniority match (20%), semantic signals (35%), diversity (5%), role clustering (10%). Deterministic, fully grounded, no LLM.

---

## 5. Conversation Design
Multi-turn state tracking. Clarification for missing constraints. Refinement detection for follow-up queries. Evidence-based comparison.

---

## 6. Evaluation Results
| Metric | Result |
|--------|--------|
| Hallucination Rate | 0% |
| Schema Compliance | 100% |
| URL Grounding | 100% |
| Recall@10 | 34.44% |
| Precision | 12.17% |
| Latency | 2ms |

All 6 tests passing: schema, grounding, error handling, performance, multi-turn, endpoints.

---

## 7. Challenges & Fixes
1. Keyword matching too broad: Added semantic scoring (improved from 6% to 12% precision)
2. Seniority mismatch: Built role clustering with 50+ synonym mappings
3. Docker path failures: Implemented multi-strategy path resolution
4. Broad retrieval: Applied diversity-aware ranking
5. Missing attributes: Added is_empty() method, fixed signatures

---

## 8. Development Phases
| Phase | Precision | Status |
|-------|-----------|--------|
| Phase 1 | 6% | Keyword matching |
| Phase 2 | 12% | Hybrid scoring |
| Phase 3 | 12% | Production hardened |
| Phase 4 | 12% | Live deployment |

---

## 9. Deployment
Framework: FastAPI + Pydantic. Container: Docker. Platform: Render.com free tier. Endpoints: /health (GET), /chat (POST), /docs (Swagger). Status: Live and public.

Links:
- API: https://shl-assignment-lw9w.onrender.com
- Docs: https://shl-assignment-lw9w.onrender.com/docs
- GitHub: https://github.com/harshvardhansingh903/SHL_ASSIGNMENT

---

## 10. Conclusion
Production-ready system. Zero hallucinations with 100% grounding. Deterministic RAG without LLM. Modular 11-module architecture. Live deployment verified. 6/6 tests passing. Ready for evaluation.
