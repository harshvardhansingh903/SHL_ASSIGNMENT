"""
Catalog relationship graph mapping.

Infers commonly paired assessments and category complements
to improve recommendation stacking.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class AssessmentRelationship:
    """Represents a relationship between two assessments."""
    assessment1_id: str
    assessment2_id: str
    co_occurrence_score: float  # 0-1 how often paired together
    category_complement: bool  # Whether they complement each other
    typical_order: Tuple[str, str]  # Which typically comes first


class CatalogRelationshipGraph:
    """Builds and manages assessment relationship graph."""
    
    # Known battery combinations from SHL best practices
    KNOWN_BATTERIES = {
        'opq_leadership_bundle': {
            'assessments': ['OPQ32r', 'OPQ Leadership', 'OPQ Universal Competency', 'Enterprise Leadership'],
            'typical_contexts': ['leadership', 'executive', 'management'],
            'co_occurrence_weight': 0.9,
        },
        'engineering_bundle': {
            'assessments': ['Smart Interview Live Coding', 'Verify Interactive G+', 'OPQ32r'],
            'typical_contexts': ['engineer', 'developer', 'technical'],
            'co_occurrence_weight': 0.85,
        },
        'graduate_bundle': {
            'assessments': ['Verify Interactive G+', 'Graduate Scenarios', 'OPQ32r'],
            'typical_contexts': ['graduate', 'entry', 'trainee'],
            'co_occurrence_weight': 0.8,
        },
        'sales_bundle': {
            'assessments': ['Global Skills Assessment', 'OPQ32r', 'OPQ Sales Report', 'Sales Transformation'],
            'typical_contexts': ['sales', 'business development', 'account management'],
            'co_occurrence_weight': 0.8,
        },
        'contact_center_bundle': {
            'assessments': ['SVAR Spoken English', 'Contact Center Call Simulation', 'Entry Level Customer Service'],
            'typical_contexts': ['contact_center', 'customer_service', 'call_centre'],
            'co_occurrence_weight': 0.85,
        },
        'finance_bundle': {
            'assessments': ['Verify Numerical', 'Financial Accounting', 'Basic Statistics', 'OPQ32r'],
            'typical_contexts': ['finance', 'accounting', 'financial_analyst'],
            'co_occurrence_weight': 0.8,
        },
    }
    
    # Category complementarity matrix
    # How well different assessment categories complement each other
    CATEGORY_COMPLEMENTS = {
        ('technical', 'cognitive'): 0.9,  # Very complementary
        ('technical', 'personality'): 0.7,
        ('technical', 'behavioral'): 0.6,
        ('cognitive', 'personality'): 0.8,
        ('cognitive', 'behavioral'): 0.7,
        ('cognitive', 'leadership'): 0.85,
        ('personality', 'behavioral'): 0.85,
        ('personality', 'leadership'): 0.9,
        ('behavioral', 'leadership'): 0.8,
        ('cognitive', 'language'): 0.6,
        ('personality', 'language'): 0.7,
        ('language', 'behavioral'): 0.85,
        ('technical', 'language'): 0.5,
        ('simulation', 'personality'): 0.7,
        ('simulation', 'behavioral'): 0.85,
        ('simulation', 'cognitive'): 0.75,
    }
    
    def __init__(self, catalog: object):
        """
        Initialize relationship graph.
        
        Args:
            catalog: CatalogLoader instance
        """
        self.catalog = catalog
        self.relationships: Dict[str, List[AssessmentRelationship]] = defaultdict(list)
        self.batteries = self.KNOWN_BATTERIES
        self._build_graph()
    
    def _build_graph(self):
        """Build assessment relationship graph from catalog."""
        # Index assessments by category (simplified)
        self.assessment_categories = {}
        self._index_assessments_by_category()
        
        # Build co-occurrence relationships
        self._build_co_occurrence_relationships()
        
        # Build category complement relationships
        self._build_category_complement_relationships()
    
    def _index_assessments_by_category(self):
        """Index each assessment by its category."""
        category_keywords = {
            'technical': ['Programming', 'Java', 'Spring', 'SQL', 'Smart Interview',
                         'Verify', 'C++', 'Python', 'Financial', 'Accounting', 'Excel'],
            'cognitive': ['Verify', 'Inductive', 'Deductive', 'Numerical', 'Reasoning', 'G+'],
            'personality': ['OPQ', 'Personality', 'Behavior', 'Engagement', 'Motivation'],
            'behavioral': ['Situational', 'SJQ', 'Simulation', 'Call', 'Competency'],
            'leadership': ['Leadership', 'Manager', 'Executive', 'Enterprise'],
            'language': ['SVAR', 'Spoken', 'English', 'Language'],
            'simulation': ['Simulation', 'Scenarios', 'Interactive', 'Case Study'],
        }
        
        for assessment in self.catalog.assessments.values():
            name_desc = (assessment.name + ' ' + assessment.description).lower()
            
            for category, keywords in category_keywords.items():
                for kw in keywords:
                    if kw.lower() in name_desc:
                        self.assessment_categories[assessment.entity_id] = category
                        break
    
    def _build_co_occurrence_relationships(self):
        """Build relationships from known batteries."""
        for battery_name, battery_info in self.KNOWN_BATTERIES.items():
            assessment_names = battery_info['assessments']
            weight = battery_info['co_occurrence_weight']
            
            # Find actual assessment IDs matching these names
            assessment_ids = []
            for name_keyword in assessment_names:
                for assessment in self.catalog.assessments.values():
                    if name_keyword.lower() in assessment.name.lower():
                        assessment_ids.append(assessment.entity_id)
                        break
            
            # Create pairwise relationships
            for i, id1 in enumerate(assessment_ids):
                for id2 in assessment_ids[i+1:]:
                    rel = AssessmentRelationship(
                        assessment1_id=id1,
                        assessment2_id=id2,
                        co_occurrence_score=weight,
                        category_complement=True,
                        typical_order=(id1, id2),
                    )
                    self.relationships[id1].append(rel)
    
    def _build_category_complement_relationships(self):
        """Build relationships based on category complements."""
        category_assessments = defaultdict(list)
        
        # Group assessments by category
        for aid, category in self.assessment_categories.items():
            category_assessments[category].append(aid)
        
        # Create relationships between categories
        for (cat1, cat2), complement_score in self.CATEGORY_COMPLEMENTS.items():
            for aid1 in category_assessments.get(cat1, []):
                for aid2 in category_assessments.get(cat2, []):
                    # Avoid duplicates
                    if aid1 < aid2:  # Simple ordering to prevent bidirectional duplicates
                        rel = AssessmentRelationship(
                            assessment1_id=aid1,
                            assessment2_id=aid2,
                            co_occurrence_score=complement_score,
                            category_complement=True,
                            typical_order=(aid1, aid2),
                        )
                        self.relationships[aid1].append(rel)
    
    def get_complementary_assessments(self,
                                      assessment_id: str,
                                      top_k: int = 5,
                                      min_score: float = 0.6) -> List[Tuple[str, float]]:
        """
        Get assessments that complement the given assessment.
        
        Args:
            assessment_id: ID of reference assessment
            top_k: Number of complementary assessments to return
            min_score: Minimum co-occurrence score
        
        Returns:
            List of (assessment_id, co_occurrence_score) tuples
        """
        complementary = []
        
        for rel in self.relationships.get(assessment_id, []):
            if rel.co_occurrence_score >= min_score:
                complementary.append((rel.assessment2_id, rel.co_occurrence_score))
        
        # Sort by score
        complementary.sort(key=lambda x: x[1], reverse=True)
        
        return complementary[:top_k]
    
    def get_battery_for_context(self, context: str) -> Optional[List[str]]:
        """
        Get a known battery for a hiring context.
        
        Args:
            context: Hiring context (e.g., 'leadership', 'engineering', 'sales')
        
        Returns:
            List of assessment keywords in recommended order
        """
        for battery_name, battery_info in self.KNOWN_BATTERIES.items():
            for ctx in battery_info.get('typical_contexts', []):
                if ctx.lower() in context.lower():
                    return battery_info['assessments']
        
        return None
    
    def score_assessment_pair(self,
                             assessment1_id: str,
                             assessment2_id: str) -> float:
        """
        Score how well two assessments pair together.
        
        Args:
            assessment1_id: ID of first assessment
            assessment2_id: ID of second assessment
        
        Returns:
            Pair score 0-1
        """
        # Direct relationship
        for rel in self.relationships.get(assessment1_id, []):
            if rel.assessment2_id == assessment2_id:
                return rel.co_occurrence_score
        
        # Category complement
        cat1 = self.assessment_categories.get(assessment1_id, 'unknown')
        cat2 = self.assessment_categories.get(assessment2_id, 'unknown')
        
        if (cat1, cat2) in self.CATEGORY_COMPLEMENTS:
            return self.CATEGORY_COMPLEMENTS[(cat1, cat2)]
        elif (cat2, cat1) in self.CATEGORY_COMPLEMENTS:
            return self.CATEGORY_COMPLEMENTS[(cat2, cat1)]
        
        return 0.0  # No relationship
    
    def optimize_assessment_order(self,
                                  assessment_ids: List[str]) -> List[str]:
        """
        Reorder assessments for optimal pairing.
        
        Uses co-occurrence scores to arrange assessments
        in their natural testing order.
        
        Args:
            assessment_ids: List of assessment IDs
        
        Returns:
            Reordered list
        """
        if len(assessment_ids) <= 1:
            return assessment_ids
        
        ordered = []
        remaining = set(assessment_ids)
        
        # Start with first assessment
        current = assessment_ids[0]
        ordered.append(current)
        remaining.remove(current)
        
        # Greedily add most complementary next assessment
        while remaining:
            best_next = None
            best_score = -1
            
            for candidate_id in remaining:
                score = self.score_assessment_pair(current, candidate_id)
                if score > best_score:
                    best_score = score
                    best_next = candidate_id
            
            if best_next:
                ordered.append(best_next)
                remaining.remove(best_next)
                current = best_next
            else:
                # No more relationships, just add remaining
                ordered.extend(list(remaining))
                break
        
        return ordered
    
    def detect_battery_pattern(self,
                              assessment_ids: List[str]) -> Optional[str]:
        """
        Detect if this set of assessments matches a known battery.
        
        Args:
            assessment_ids: List of assessment IDs
        
        Returns:
            Battery name or None
        """
        # Get assessment names
        assessment_names = set()
        for aid in assessment_ids:
            if aid in self.catalog.assessments:
                assessment_names.add(self.catalog.assessments[aid].name.lower())
        
        # Check against known batteries
        for battery_name, battery_info in self.KNOWN_BATTERIES.items():
            battery_keywords = set(kw.lower() for kw in battery_info['assessments'])
            
            # Check if significant overlap
            overlap = 0
            for name in assessment_names:
                for keyword in battery_keywords:
                    if keyword in name:
                        overlap += 1
                        break
            
            if overlap >= len(battery_keywords) * 0.7:  # 70% match
                return battery_name
        
        return None
