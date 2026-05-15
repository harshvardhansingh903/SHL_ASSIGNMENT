"""
Constraint extraction for SHL Recommender.
Extracts hiring constraints from user messages.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Constraints:
    """Represents extracted hiring constraints from conversation."""
    role: Optional[str] = None
    seniority: Optional[str] = None
    assessment_types: List[str] = field(default_factory=list)
    job_family: Optional[str] = None
    duration_max: Optional[int] = None
    languages: List[str] = field(default_factory=list)
    comparison_target: Optional[str] = None
    specific_assessments: List[str] = field(default_factory=list)
    exclude_assessments: List[str] = field(default_factory=list)


class ConstraintExtractor:
    """Extracts constraints from user input."""
    
    def __init__(self):
        pass
    
    def extract(self, message: str) -> Constraints:
        """Extract constraints from message."""
        constraints = Constraints()
        
        # Simple keyword-based extraction
        lower_msg = message.lower()
        
        # Role detection
        if 'engineer' in lower_msg:
            constraints.role = 'engineer'
        elif 'manager' in lower_msg:
            constraints.role = 'manager'
        elif 'leader' in lower_msg:
            constraints.role = 'leadership'
        
        # Seniority detection
        if 'senior' in lower_msg:
            constraints.seniority = 'senior'
        elif 'junior' in lower_msg:
            constraints.seniority = 'junior'
        elif 'lead' in lower_msg or 'principal' in lower_msg:
            constraints.seniority = 'senior'
        
        return constraints
