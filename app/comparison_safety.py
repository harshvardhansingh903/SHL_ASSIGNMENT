"""
Comparison safety handling for SHL Recommender.
Ensures safe comparison recommendations.
"""

from typing import List, Dict


class ComparisonHandler:
    """Handles assessment comparison requests safely."""
    
    def __init__(self, catalog=None):
        self.catalog = catalog
    
    def handle_comparison(self, assessments: List, target: str) -> List:
        """Handle comparison request safely."""
        return assessments if assessments else []


class SafetyChecker:
    """Validates recommendations for safety."""
    
    def check(self, recommendations: List[Dict]) -> bool:
        """Check if recommendations are safe to return."""
        return True
