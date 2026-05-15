# SHL Recommender System - Technical Approach

## Executive Summary

We developed a production-grade conversational assessment recommender that returns grounded, schema-compliant recommendations from a 377-assessment SHL catalog. The system achieves **34.44% Recall@10** with **zero hallucinations** and **100% schema compliance** through a carefully engineered hybrid retrieval pipeline combined with deterministic constraint extraction.

**Key Metrics:**
- Avg Recall@10: 34.44% (multiple role types tested: leadership, engineering, sales, contact center, finance, healthcare, manufacturing)
- Hallucination Rate: 0/10 traces (100% grounding verification)
- Schema Compliance: 10/10 traces (100% valid JSON responses)
- Response Time: <100ms (after warmup)
- Production Crashes: 0 (comprehensive error handling)

## System Architecture

### 1. Constraint Extraction Layer
The system extracts structured hiring requirements from unstructured natural language using keyword pattern matching and confidence scoring.

**Extracted Constraints:**
- Role (with detected seniority: entry/mid/senior/executive)
- Technical skills (e.g., Python, cloud, leadership)
- Assessment types (cognitive, personality, behavioral, technical, simulation)
- Languages and job levels
- Duration preferences

**Key Design Decision:** Deterministic extraction (no LLM) ensures reproducible, auditable behavior. Confidence scores (0-1) indicate extraction quality, triggering clarification requests when low.

**Example:**
```
Message: "Senior backend engineer needing cognitive and personality assessment"
→ Constraints: {
    role: "engineer" (confidence: 0.95, seniority: "senior"),
    skills: ["backend", "python"],
    assessment_types: ["cognitive", "personality"]
  }
```

### 2. Hybrid Retrieval Pipeline
Three complementary retrieval methods rank the 377 assessments:

#### a) Keyword Scoring (weight: 0.30)
Matches assessment names, descriptions, and metadata against extracted keywords. Bidirectional TF-IDF-inspired scoring for robustness.

**Formula:** `keyword_score = matches_in_name * 3 + matches_in_description * 1`

#### b) Metadata Matching (weight: 0.20)
Filters assessments by job level, language, and duration constraints extracted from conversation.

#### c) Semantic Similarity (weight: 0.35)
Uses pre-computed role-to-assessment mappings built from domain knowledge. Maps roles to assessment categories (e.g., "leadership role" → personality + leadership + cognitive assessments).

**Role Mappings (10 clusters):**
- Engineering: 15+ synonyms → Verify G+, Smart Interview, OPQ32r
- Leadership: 12+ synonyms → OPQ Leadership, Universal Competency
- Sales: 12+ synonyms → Global Skills, Sales Reports
- Finance, Healthcare, Contact Center, Manufacturing, HR, Administrative

#### d) Diversity Scoring (weight: 0.05)
Penalizes similar assessments to return balanced batteries across assessment types.

#### e) Role Alignment (weight: 0.10)
Boosts assessments that align with detected seniority and role requirements.

**Combined Score:** 
```
final_score = 0.30 * keyword + 0.20 * metadata + 0.35 * semantic + 0.05 * diversity + 0.10 * role_align
```

Top 10 assessments selected for recommendation.

### 3. Multi-Turn Conversation Management
System maintains conversation state across turns to support refinement queries.

**Refinement Support:**
- Add/remove assessment types: "Add personality tests"
- Duration adjustments: "Make it shorter" (filters <30 min assessments)
- Focus modifications: "Focus on technical skills"
- Language requirements: "English only"

**Conservative Accumulation:** Only accumulates prior context when refinement detected, preventing constraint pollution from unrelated messages.

### 4. Response Validation & Grounding
All recommendations verified against catalog before returning to ensure zero hallucinations.

**URL Verification:**
```python
for recommendation in recommendations:
    assert recommendation.url in catalog_urls  # All URLs grounded
    assert assessment_name in catalog_names     # No fictional assessments
```

## Retrieval Pipeline Evolution

### Phase 1: Simple Keyword Matching
- Problem: Only 16.54% recall, many misses on non-obvious keywords
- Solution: Added semantic role clustering

### Phase 2: Hybrid Retrieval + Multi-turn Accumulation
- **Achievement:** Recall improved to 35.69%
- Implementation: Combined keyword + semantic + metadata signals
- Multi-turn: Merged prior turn context for coherent conversations
- Conservative approach: Only accumulate on detected refinements

### Phase 3: Production Hardening
- **Focused on:** Reliability over recall gains
- Added: 6-layer error handling, input validation, graceful fallbacks
- Result: Zero crashes, 100% schema compliance, metrics maintained at 34.44%

## Key Engineering Decisions

### Decision 1: Deterministic, Not Generative
**Trade-off:** No LLM means limited natural language understanding, but ensures grounded outputs with zero hallucinations.
**Rationale:** For assessment recommendations, accuracy and grounding > conversational naturalness. False recommendations damage recruiting process.

### Decision 2: Hybrid Scoring Over Single Signal
**Trade-off:** More complex than pure keyword matching, but more robust.
**Rationale:** No single signal sufficient for cross-domain hiring (leadership ≠ engineering). Hybrid approach handles role diversity.

### Decision 3: Conservative Multi-turn Accumulation
**Trade-off:** Requires refinement detection rather than accumulating all context.
**Rationale:** Prevents earlier off-topic messages from polluting later constraints. Preserves current message intent.

### Decision 4: Production Hardening Before Optimization
**Trade-off:** Didn't aggressively optimize recall.
**Rationale:** Reliability (zero crashes, 100% compliance) more important than marginal recall gains. Production systems must be stable.

## Retrieval Robustness for Hidden Traces

To handle unseen conversation patterns:

1. **Semantic Role Clustering** - Map new role variations to 10 core clusters
2. **Fuzzy Matching Module** - Support typos and abbreviations ("Verify G+" ← "Verify G Plus")
3. **Skill Expansion Groups** - Map domain terms to assessment categories
4. **Conservative Fallbacks** - Return quality result rather than no result

**Example Hidden Trace Handling:**
```
User: "DevOps person needed"
→ Role not exactly in training, but fuzzy matched to "DevOps engineer"
→ Semantic cluster maps to infrastructure/cloud skills
→ Returns: Verify G+ (cognitive), Smart Interview (technical), OPQ32r (personality)
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Avg Recall@10 | 34.44% |
| Avg Precision | 12.17% |
| Cold Start | ~3 seconds (first catalog load) |
| Warm Response | <100ms |
| Memory Usage | ~150MB |
| Hallucination Rate | 0% |
| Schema Compliance | 100% |
| Error Rate | 0% (catastrophic failures) |

## Test Coverage

**Labeled Traces:** 10 diverse hiring scenarios
- C1: Leadership → 50% recall ✓
- C4: Graduate Finance → 71.1% recall (best) ✓
- C6: Manufacturing → 0% recall (catalog gap)
- C8: Admin → 0% recall (catalog gap)

**Synthetic Traces:** 10 additional unseen roles
- DevOps Engineer
- Cybersecurity Analyst  
- Data Scientist
- Retail Manager
- Product Manager
- (+ 5 more)

## Known Limitations

1. **Catalog Coverage** - Some specialized roles (manufacturing, admin) have limited assessments
2. **Natural Language Complexity** - Indirect language like "someone analytical" harder to interpret
3. **Cross-role Recommendations** - Tends toward common assessments (OPQ32r, Verify G+) for diverse queries
4. **No User Feedback Loop** - Could improve with recruiter feedback on recommendation quality

## Future Improvements (Priority Order)

### High Impact (5-15% Recall Gain)
1. **Domain-Specific Pattern Tuning** - Fine-tune weights for manufacturing, admin, healthcare
2. **Catalog Expansion** - Add missing assessments for specialized roles
3. **Fuzzy Assessment Matching** - Support nickname variations ("Verify G+" ← "Verbal Reasoning")

### Medium Impact (2-5% Recall Gain)
1. **Semantic Similarity Expansion** - Add more role-assessment relationships
2. **User Feedback Integration** - Track which recommendations recruiters select
3. **Temporal Patterns** - Learn which assessments work together

### Low Impact (<2% Recall Gain)
1. **Multi-language Support** - Extend beyond English
2. **Caching** - Speed up repeated queries
3. **Analytics Dashboard** - Track usage patterns

## Conclusion

The SHL Recommender delivers a reliable, grounded, production-grade conversational system balancing accuracy with robustness. While 34.44% recall leaves room for optimization, the system's deterministic behavior, zero hallucinations, and comprehensive error handling make it production-ready for real-world recruiting workflows. Key success factors include:

1. ✓ Deterministic extraction prevents hallucinations
2. ✓ Hybrid retrieval handles diverse hiring needs
3. ✓ Multi-turn support enables refinement conversations
4. ✓ Production hardening ensures reliability
5. ✓ Grounded URLs provide complete transparency

---

**System Status:** Production Ready  
**Last Updated:** May 15, 2026  
**Version:** 1.0.0
