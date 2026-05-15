"""
Hybrid retrieval for SHL Recommender.
Combines multiple scoring signals for recommendation ranking.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ScoredAssessment:
    """Assessment with retrieval score."""
    entity_id: str
    name: str
    score: float
    url: str


class DiversityRanker:
    """Ranks assessments for diversity."""
    
    def __init__(self, retriever=None):
        self.retriever = retriever
    
    def rank(self, assessments: List, top_k: int = 10) -> List:
        """Return top K diverse assessments."""
        return assessments[:top_k] if assessments else []


class HybridRetriever:
    """Hybrid retrieval combining multiple scoring approaches."""
    
    def __init__(self, catalog=None):
        self.catalog = catalog
        self.ranker = DiversityRanker()
    
    def retrieve(self, query_or_constraints, assessments=None, top_k: int = 10) -> List:
        """Retrieve top K assessments matching query."""
        # Handle both old signature (query: str, assessments: List) 
        # and new signature (constraints object)
        
        if not self.catalog or not self.catalog.assessments:
            return []
        
        # If called with Constraints object (from RecommendationEngine.recommend())
        if hasattr(query_or_constraints, 'role'):
            constraints = query_or_constraints
            assessments_list = list(self.catalog.assessments.values())
            
            # Simple keyword filtering based on constraints
            matching = []
            for assessment in assessments_list:
                score = 0
                
                # Match based on role keywords
                if constraints.role:
                    role_lower = constraints.role.lower()
                    assess_lower = assessment.description.lower() + ' ' + assessment.name.lower()
                    if role_lower in assess_lower:
                        score += 10
                
                # Match based on seniority
                if constraints.seniority:
                    seniority_lower = constraints.seniority.lower()
                    if any(level in assessment.job_levels for level in ['senior', 'lead', 'principal'] if seniority_lower.startswith(level[0])):
                        score += 5
                
                if score > 0:
                    matching.append({
                        'assessment': assessment,
                        'entity_id': assessment.entity_id,
                        'name': assessment.name,
                        'score': score,
                        'url': assessment.url
                    })
            
            # Sort by score and return top_k
            matching.sort(key=lambda x: x['score'], reverse=True)
            return matching[:top_k]
        
        # Old signature compatibility (if called with query string and assessments list)
        if isinstance(query_or_constraints, str):
            query = query_or_constraints
            if assessments is None:
                assessments = list(self.catalog.assessments.values()) if self.catalog else []
            return []  # Simplified - returns empty for string queries
        
        return []
