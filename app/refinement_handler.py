"""
Advanced refinement handling for dynamic recommendation modifications.

Supports user requests like:
- "add personality tests"
- "remove simulations"
- "make it shorter"
- "focus more on communication"
- "need remote testing"
"""

import re
from typing import List, Optional, Tuple
from constraint_extraction import Constraints
from dataclasses import dataclass, field

@dataclass
class Refinement:
    """Represents a refinement request."""
    refinement_type: str  # e.g., 'add', 'remove', 'modify', 'filter'
    dimension: str  # e.g., 'personality', 'technical', 'duration'
    value: Optional[str]  # e.g., 'shorter', 'english', 'remote'
    intensity: str = 'moderate'  # 'light', 'moderate', 'strong'
    
    def __repr__(self):
        return f"Refinement({self.refinement_type} {self.dimension}={self.value})"


class RefinementHandler:
    """Handles dynamic recommendation refinements."""
    
    # Refinement patterns with regex
    REFINEMENT_PATTERNS = {
        'add_assessment_type': {
            'pattern': r'add\s+(?:more\s+)?(\w+)\s+(?:assessments?|tests?|evaluations?)',
            'type': 'add',
            'dimension': 'assessment_type',
        },
        'remove_assessment_type': {
            'pattern': r'(?:remove|drop|exclude|no)\s+(\w+)\s+(?:assessments?|tests?|evaluations?)',
            'type': 'remove',
            'dimension': 'assessment_type',
        },
        'duration_shorter': {
            'pattern': r'(?:make\s+it\s+)?(?:shorter|quicker|faster|less|minimal|brief|quick)',
            'type': 'filter',
            'dimension': 'duration',
            'value': 'shorter',
        },
        'duration_longer': {
            'pattern': r'(?:longer|more|comprehensive|thorough|detailed|extended)',
            'type': 'filter',
            'dimension': 'duration',
            'value': 'longer',
        },
        'focus_dimension': {
            'pattern': r'(?:focus|emphasize|prioritize|more|stronger)\s+(?:on\s+)?(\w+(?:\s+\w+)?)',
            'type': 'modify',
            'dimension': 'focus',
        },
        'remove_dimension': {
            'pattern': r'(?:remove|drop|less|no)\s+(?:focus\s+)?on\s+(\w+(?:\s+\w+)?)',
            'type': 'remove',
            'dimension': 'focus',
        },
        'language_requirement': {
            'pattern': r'(?:in\s+|language:\s*)?(?:english|french|spanish|german|mandarin|japanese|arabic)',
            'type': 'filter',
            'dimension': 'language',
        },
        'remote_requirement': {
            'pattern': r'(?:remote|online|web-based|virtual|digital)\s+(?:testing|delivery|assessments?)',
            'type': 'filter',
            'dimension': 'remote',
            'value': 'remote',
        },
        'job_level_refinement': {
            'pattern': r'(?:entry-level|beginner|advanced|senior|executive)',
            'type': 'filter',
            'dimension': 'job_level',
        },
    }
    
    # Assessment type synonyms and mappings
    ASSESSMENT_TYPES = {
        'personality': ['personality', 'behavior', 'behavioral', 'traits', 'opq'],
        'technical': ['technical', 'coding', 'programming', 'skill', 'skills', 'development'],
        'cognitive': ['cognitive', 'ability', 'reasoning', 'logic', 'numerical', 'verbal', 'inductive'],
        'behavioral': ['behavioral', 'competency', 'scenario', 'judgment', 'situational'],
        'leadership': ['leadership', 'management', 'strategy', 'vision', 'executive'],
        'language': ['language', 'spoken', 'english', 'communication', 'verbal', 'accent'],
        'simulation': ['simulation', 'exercise', 'interactive', 'case', 'scenario'],
    }
    
    # Dimension synonyms
    DIMENSION_SYNONYMS = {
        'personality': ['personality', 'behavior', 'behavioral', 'soft_skills', 'traits', 'fit'],
        'technical': ['technical', 'coding', 'programming', 'skills', 'hard_skills', 'technical_skills'],
        'cognitive': ['cognitive', 'ability', 'reasoning', 'mental', 'iq', 'intelligence'],
        'communication': ['communication', 'verbal', 'spoken', 'language', 'english'],
        'duration': ['duration', 'time', 'length', 'quick', 'fast', 'long', 'lengthy'],
        'remote': ['remote', 'online', 'virtual', 'web-based', 'digital'],
        'job_level': ['level', 'seniority', 'junior', 'senior', 'entry', 'executive'],
    }
    
    def __init__(self):
        """Initialize refinement handler."""
        self.patterns = self.REFINEMENT_PATTERNS
    
    def extract_refinements(self, message: str) -> List[Refinement]:
        """
        Extract refinements from a message.
        
        Args:
            message: User message potentially containing refinements
        
        Returns:
            List of Refinement objects
        """
        refinements = []
        message_lower = message.lower()
        
        # Check each pattern
        for pattern_name, pattern_info in self.REFINEMENT_PATTERNS.items():
            pattern = pattern_info['pattern']
            matches = re.finditer(pattern, message_lower)
            
            for match in matches:
                refinement = Refinement(
                    refinement_type=pattern_info['type'],
                    dimension=pattern_info['dimension'],
                    value=pattern_info.get('value'),
                )
                
                # Extract value from capture group if present
                if match.groups():
                    refinement.value = match.group(1)
                
                # Determine intensity
                if any(word in message_lower[:match.start() + 30] for word in ['very', 'much', 'more', 'definitely', 'strongly']):
                    refinement.intensity = 'strong'
                elif any(word in message_lower[:match.start() + 30] for word in ['slightly', 'maybe', 'perhaps', 'bit']):
                    refinement.intensity = 'light'
                
                refinements.append(refinement)
        
        return refinements
    
    def normalize_dimension(self, dimension: str) -> Optional[str]:
        """
        Normalize a dimension to standard form.
        
        Args:
            dimension: Any dimension variant
        
        Returns:
            Normalized dimension or None
        """
        dimension_lower = dimension.lower().strip()
        
        for canonical, synonyms in self.DIMENSION_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in dimension_lower or dimension_lower in synonym:
                    return canonical
        
        return None
    
    def normalize_assessment_type(self, assessment_type: str) -> Optional[str]:
        """Normalize assessment type to standard form."""
        assessment_lower = assessment_type.lower().strip()
        
        for canonical, variations in self.ASSESSMENT_TYPES.items():
            for variation in variations:
                if variation in assessment_lower:
                    return canonical
        
        return None
    
    def apply_refinement_to_constraints(self,
                                        constraints: Constraints,
                                        refinement: Refinement) -> Constraints:
        """
        Apply a refinement to constraints.
        
        Args:
            constraints: Original constraints
            refinement: Refinement to apply
        
        Returns:
            Modified constraints
        """
        # Create a modified copy
        import copy
        modified = copy.deepcopy(constraints)
        
        normalized_dim = self.normalize_dimension(refinement.dimension)
        
        if not normalized_dim:
            return modified  # Can't apply unknown dimension
        
        # Apply based on type and dimension
        if refinement.refinement_type == 'add':
            if normalized_dim == 'assessment_type':
                # Add assessment need
                assessment_type = self.normalize_assessment_type(refinement.value)
                if assessment_type == 'personality':
                    modified.needs_personality = True
                elif assessment_type == 'cognitive':
                    modified.needs_cognitive = True
                elif assessment_type == 'behavioral':
                    modified.needs_behavioral = True
                elif assessment_type == 'simulation':
                    modified.needs_simulation = True
                elif assessment_type == 'leadership':
                    modified.needs_leadership = True
        
        elif refinement.refinement_type == 'remove':
            if normalized_dim == 'assessment_type':
                # Disable assessment need
                assessment_type = self.normalize_assessment_type(refinement.value)
                if assessment_type == 'personality':
                    modified.needs_personality = False
                elif assessment_type == 'cognitive':
                    modified.needs_cognitive = False
                elif assessment_type == 'behavioral':
                    modified.needs_behavioral = False
                elif assessment_type == 'simulation':
                    modified.needs_simulation = False
                elif assessment_type == 'leadership':
                    modified.needs_leadership = False
        
        elif refinement.refinement_type == 'filter':
            if normalized_dim == 'duration':
                if refinement.value == 'shorter':
                    modified.needs_remote_testing = True  # Shorter tests often remote
            elif normalized_dim == 'remote':
                modified.needs_remote_testing = True
            elif normalized_dim == 'language':
                if refinement.value:
                    if 'english' in refinement.value.lower():
                        modified.languages = ['English']
                    else:
                        modified.languages = [refinement.value.title()]
        
        elif refinement.refinement_type == 'modify':
            if normalized_dim == 'focus':
                focus_target = refinement.value.lower() if refinement.value else ''
                
                # Increase focus on specific dimension
                if any(word in focus_target for word in ['communication', 'verbal', 'language']):
                    modified.needs_personality = True
                    if refinement.intensity == 'strong':
                        modified.languages = modified.languages or ['English']
                elif any(word in focus_target for word in ['technical', 'coding', 'programming']):
                    if not modified.technical_skills:
                        modified.technical_skills = ['General Technical']
                elif any(word in focus_target for word in ['leadership', 'management']):
                    modified.needs_leadership = True
                elif any(word in focus_target for word in ['cognitive', 'reasoning', 'ability']):
                    modified.needs_cognitive = True
        
        return modified
    
    def apply_refinements_to_constraints(self,
                                         constraints: Constraints,
                                         refinements: List[Refinement]) -> Constraints:
        """Apply multiple refinements to constraints."""
        modified = constraints
        for refinement in refinements:
            modified = self.apply_refinement_to_constraints(modified, refinement)
        return modified
    
    def filter_assessments_by_refinement(self,
                                         assessments: List[object],
                                         refinement: Refinement) -> List[object]:
        """
        Filter assessments based on a refinement.
        
        Args:
            assessments: List of Assessment objects
            refinement: Refinement to apply
        
        Returns:
            Filtered list
        """
        if refinement.refinement_type not in ['filter', 'remove']:
            return assessments  # Only filter/remove
        
        normalized_dim = self.normalize_dimension(refinement.dimension)
        filtered = assessments
        
        if normalized_dim == 'duration':
            if refinement.value == 'shorter':
                # Keep only short assessments (< 30 minutes)
                filtered = [
                    a for a in filtered
                    if self._parse_duration_minutes(a.duration) < 30
                ]
            elif refinement.value == 'longer':
                # Keep only longer assessments
                filtered = [
                    a for a in filtered
                    if self._parse_duration_minutes(a.duration) > 30
                ]
        
        elif normalized_dim == 'remote':
            if refinement.value == 'remote':
                # Keep only remote-compatible assessments (< 60 min)
                filtered = [
                    a for a in filtered
                    if self._parse_duration_minutes(a.duration) <= 60
                ]
        
        elif normalized_dim == 'language':
            if refinement.value:
                target_lang = refinement.value
                filtered = [
                    a for a in filtered
                    if target_lang in a.languages
                ]
        
        elif normalized_dim == 'assessment_type':
            assessment_type = self.normalize_assessment_type(refinement.value)
            if assessment_type == 'personality':
                filtered = [a for a in filtered if 'Personality' in ' '.join(a.keys) or 'Behavior' in ' '.join(a.keys)]
            elif assessment_type == 'technical':
                filtered = [a for a in filtered if 'Knowledge' in ' '.join(a.keys) or 'Skills' in ' '.join(a.keys)]
            elif assessment_type == 'cognitive':
                filtered = [a for a in filtered if 'Ability' in ' '.join(a.keys)]
            elif assessment_type == 'behavioral':
                filtered = [a for a in filtered if any(key in ' '.join(a.keys) for key in ['Judgment', 'Competencies', 'Exercises'])]
            elif assessment_type == 'simulation':
                filtered = [a for a in filtered if 'Simulations' in ' '.join(a.keys)]
        
        return filtered
    
    def _parse_duration_minutes(self, duration_str: str) -> int:
        """Parse duration string to minutes."""
        duration_lower = duration_str.lower()
        
        try:
            if 'hour' in duration_lower:
                hours = int(duration_lower.split()[0])
                return hours * 60
            elif 'minute' in duration_lower or 'min' in duration_lower:
                minutes = int(duration_lower.split()[0])
                return minutes
        except:
            pass
        
        return 30  # Default estimate
    
    def is_refinement_query(self, message: str) -> bool:
        """
        Detect if a message is primarily a refinement (vs new request).
        
        Args:
            message: User message
        
        Returns:
            True if message appears to be a refinement
        """
        refinements = self.extract_refinements(message)
        
        # If we found refinements and message is relatively short, likely refinement
        if refinements and len(message) < 150:
            return True
        
        # Check for refinement keywords
        refinement_keywords = [
            'add', 'remove', 'also', 'instead', 'except', 'without', 'shorter',
            'longer', 'focus', 'emphasize', 'exclude', 'more', 'less',
            'adjust', 'modify', 'change', 'update', 'better',
        ]
        
        for keyword in refinement_keywords:
            if keyword in message.lower():
                return True
        
        return False
