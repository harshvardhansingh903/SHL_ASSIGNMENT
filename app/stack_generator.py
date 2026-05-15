"""
Recommendation stack generation for layered assessment batteries.

Intelligently combines cognitive, technical, personality, leadership,
simulation, and situational judgment tests to form cohesive assessment stacks.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
from constraint_extraction import Constraints

@dataclass
class AssessmentStack:
    """Represents a layered assessment battery."""
    name: str  # e.g., "Senior Engineering Stack"
    description: str
    assessments: List[object]  # List of Assessment objects
    category_coverage: Dict[str, int]  # Count per category
    estimated_duration_min: int
    stack_type: str  # e.g., 'technical', 'leadership', 'graduate', 'hybrid'


class StackGenerator:
    """Generates assessment stacks based on hiring role and constraints."""
    
    # Stack templates for different scenarios
    STACK_TEMPLATES = {
        'senior_engineering': {
            'description': 'Technical depth + problem solving + behavioral',
            'categories': {
                'technical': 40,  # High weight on coding/technical
                'cognitive': 30,  # Problem solving
                'personality': 20,  # Team fit
                'behavioral': 10,
            },
            'min_assessments': 4,
            'max_assessments': 7,
        },
        'leadership': {
            'description': 'Personality + leadership + motivation + reasoning',
            'categories': {
                'personality': 40,  # Core behavioral fit
                'leadership': 30,  # Leadership capability
                'cognitive': 20,  # Reasoning/strategy
                'motivation': 10,
            },
            'min_assessments': 3,
            'max_assessments': 6,
        },
        'graduate': {
            'description': 'Ability + personality + situational judgment',
            'categories': {
                'cognitive': 35,  # Ability testing
                'personality': 30,  # Behavioral fit
                'situational_judgment': 25,  # Job simulation
                'technical': 10,  # Role-specific skills
            },
            'min_assessments': 3,
            'max_assessments': 5,
        },
        'sales': {
            'description': 'Communication + motivation + resilience + cognitive',
            'categories': {
                'personality': 35,  # Sales fit, resilience
                'cognitive': 25,  # Numerical reasoning
                'behavioral': 20,  # Customer interaction
                'simulation': 20,  # Sales scenarios
            },
            'min_assessments': 3,
            'max_assessments': 6,
        },
        'contact_center': {
            'description': 'Communication + personality + technical language',
            'categories': {
                'personality': 30,  # Emotional intelligence
                'language': 40,  # Spoken/written English (SVAR)
                'behavioral': 20,  # Customer service fit
                'simulation': 10,  # Call handling
            },
            'min_assessments': 2,
            'max_assessments': 4,
        },
        'finance': {
            'description': 'Numerical + technical + detail orientation + judgment',
            'categories': {
                'cognitive': 40,  # Numerical reasoning
                'technical': 30,  # Financial/accounting
                'personality': 20,  # Conscientiousness
                'behavioral': 10,
            },
            'min_assessments': 3,
            'max_assessments': 5,
        },
        'healthcare': {
            'description': 'Technical knowledge + empathy + precision + compliance',
            'categories': {
                'technical': 40,  # Medical/HIPAA knowledge
                'personality': 30,  # Empathy, patience
                'behavioral': 20,  # Compliance, attention
                'cognitive': 10,
            },
            'min_assessments': 3,
            'max_assessments': 5,
        },
        'manufacturing': {
            'description': 'Safety + reliability + technical + situational',
            'categories': {
                'behavioral': 40,  # Safety, dependability
                'technical': 30,  # Industrial knowledge
                'cognitive': 20,  # Problem solving
                'simulation': 10,
            },
            'min_assessments': 3,
            'max_assessments': 5,
        },
        'administrative': {
            'description': 'Organization + technical office skills + attention',
            'categories': {
                'technical': 40,  # MS Office
                'personality': 30,  # Conscientiousness, organization
                'behavioral': 20,  # Administrative fit
                'cognitive': 10,
            },
            'min_assessments': 3,
            'max_assessments': 5,
        },
    }
    
    # Category definitions
    CATEGORY_KEYWORDS = {
        'technical': [
            'Programming', 'Java', 'Spring', 'SQL', 'Rust', 'Python', 'C++',
            'Smart Interview', 'Verify', 'Django', 'RESTful', 'Docker', 'Kubernetes',
            'Financial', 'Accounting', 'Medical Terminology', 'HIPAA', 'Excel',
            'Word', 'Office', 'Manufacturing', 'Safety', 'Industrial', 'Linux', 'Networking',
        ],
        'cognitive': [
            'Verify', 'Inductive', 'Deductive', 'Numerical', 'Reasoning', 'Problem',
            'Abstract', 'Verbal', 'Logic', 'G+',
        ],
        'personality': [
            'OPQ', 'Personality', 'Behavior', 'Engagement', 'Motivation', 'Values',
            'Fit', 'Culture', 'Team Types', 'Sales', 'Emotional Intelligence',
        ],
        'behavioral': [
            'Situational Judgment', 'SJQ', 'Scenarios', 'Call Simulation', 'Call Centre',
            'Customer Service', 'Simulation', 'Interaction', 'Competency', 'Interview',
            'Service', 'Communication',
        ],
        'leadership': [
            'Leadership', 'Manager', 'Executive', 'OPQ', 'Competency', 'Enterprise',
            'Report', 'Motivation', 'Strategy', 'Vision',
        ],
        'language': [
            'SVAR', 'Spoken', 'English', 'Language', 'Interview', 'Accent',
            'Communication', 'Verbal',
        ],
        'simulation': [
            'Simulation', 'Scenarios', 'Call', 'SJQ', 'Interactive', 'Exercise',
            'Case Study', 'In-Basket',
        ],
        'situational_judgment': [
            'Situational Judgment', 'SJQ', 'Scenarios', 'Graduate', 'Judgment',
        ],
    }
    
    def __init__(self, catalog: object):
        """
        Initialize stack generator.
        
        Args:
            catalog: CatalogLoader instance
        """
        self.catalog = catalog
        self._build_category_index()
    
    def _build_category_index(self):
        """Index assessments by category."""
        self.category_index = {cat: [] for cat in self.CATEGORY_KEYWORDS}
        
        for assessment in self.catalog.assessments.values():
            name_desc = (assessment.name + ' ' + assessment.description).lower()
            
            for category, keywords in self.CATEGORY_KEYWORDS.items():
                for kw in keywords:
                    if kw.lower() in name_desc:
                        self.category_index[category].append(assessment)
                        break
    
    def determine_stack_type(self, constraints: Constraints) -> str:
        """Determine which stack template to use."""
        role = (constraints.role or '').lower()
        seniority = (constraints.seniority or '').lower()
        
        # Exact matches
        if 'leadership' in role or 'executive' in role or 'cxo' in role or 'director' in role:
            return 'leadership'
        elif 'engineer' in role or 'developer' in role or 'programmer' in role:
            if 'senior' in seniority:
                return 'senior_engineering'
            else:
                return 'senior_engineering'
        elif 'graduate' in role or (seniority and 'graduate' in seniority.lower()):
            return 'graduate'
        elif 'sales' in role:
            return 'sales'
        elif 'contact' in role or 'centre' in role or 'center' in role or 'call' in role:
            return 'contact_center'
        elif 'finance' in role or 'accounting' in role or 'financial' in role:
            return 'finance'
        elif 'healthcare' in role or 'medical' in role or 'nurse' in role or 'doctor' in role:
            return 'healthcare'
        elif 'manufacturing' in role or 'production' in role or 'plant' in role:
            return 'manufacturing'
        elif 'admin' in role or 'assistant' in role or 'clerical' in role or 'secretary' in role:
            return 'administrative'
        
        # Fallback: infer from constraints
        if constraints.needs_leadership or 'leadership' in constraints.soft_skills:
            return 'leadership'
        elif constraints.needs_personality:
            return 'graduate'  # Personality focus common in early career
        
        return 'senior_engineering'  # Default
    
    def generate_stack(self,
                       constraints: Constraints,
                       available_assessments: List[object],
                       top_k: int = 10) -> AssessmentStack:
        """
        Generate a layered assessment stack.
        
        Args:
            constraints: Extracted hiring constraints
            available_assessments: Candidates already retrieved/scored
            top_k: Target number of assessments in stack
        
        Returns:
            AssessmentStack object with organized batteries
        """
        stack_type = self.determine_stack_type(constraints)
        template = self.STACK_TEMPLATES.get(stack_type, self.STACK_TEMPLATES['senior_engineering'])
        
        stack_assessments = []
        category_counts = {cat: 0 for cat in template['categories']}
        used_ids = set()
        
        # Strategy: Fill categories according to weights
        # Higher-weighted categories get more assessments
        sorted_categories = sorted(
            template['categories'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for category, weight in sorted_categories:
            target_count = max(
                1,
                int((weight / 100.0) * top_k)
            )
            
            # Get candidates for this category
            category_candidates = [
                a for a in available_assessments
                if a.entity_id not in used_ids and a in self.category_index.get(category, [])
            ]
            
            # Add assessments from this category
            for assessment in category_candidates[:target_count]:
                if assessment.entity_id not in used_ids:
                    stack_assessments.append(assessment)
                    used_ids.add(assessment.entity_id)
                    category_counts[category] += 1
                    
                    if len(stack_assessments) >= top_k:
                        break
            
            if len(stack_assessments) >= top_k:
                break
        
        # Fill remaining slots with best remaining candidates
        if len(stack_assessments) < top_k:
            for assessment in available_assessments:
                if assessment.entity_id not in used_ids:
                    stack_assessments.append(assessment)
                    used_ids.add(assessment.entity_id)
                    
                    # Categorize the filler
                    for category in self.CATEGORY_KEYWORDS:
                        if assessment in self.category_index.get(category, []):
                            category_counts[category] += 1
                            break
                    
                    if len(stack_assessments) >= top_k:
                        break
        
        # Estimate duration
        estimated_duration = self._estimate_stack_duration(stack_assessments)
        
        return AssessmentStack(
            name=f"{stack_type.replace('_', ' ').title()} Stack",
            description=template['description'],
            assessments=stack_assessments[:top_k],
            category_coverage=category_counts,
            estimated_duration_min=estimated_duration,
            stack_type=stack_type,
        )
    
    def _estimate_stack_duration(self, assessments: List[object]) -> int:
        """Estimate total duration in minutes."""
        total_minutes = 0
        
        for assessment in assessments:
            duration_str = assessment.duration.lower()
            
            # Parse duration strings like "25 minutes", "1 hour", etc.
            if 'hour' in duration_str:
                try:
                    hours = int(duration_str.split()[0])
                    total_minutes += hours * 60
                except:
                    total_minutes += 60
            elif 'minute' in duration_str or 'min' in duration_str:
                try:
                    minutes = int(duration_str.split()[0])
                    total_minutes += minutes
                except:
                    total_minutes += 30
            else:
                total_minutes += 30  # Default estimate
        
        return total_minutes
    
    def enhance_with_stack_logic(self,
                                 recommendations: List[object],
                                 constraints: Constraints) -> List[object]:
        """
        Reorder recommendations using stack logic.
        
        This ensures complementary assessments are positioned together,
        and category diversity is maintained.
        """
        if not recommendations:
            return recommendations
        
        # Group assessments by category
        categorized = {}
        uncategorized = []
        
        for assessment in recommendations:
            found_category = False
            for category in self.CATEGORY_KEYWORDS:
                if assessment in self.category_index.get(category, []):
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(assessment)
                    found_category = True
                    break
            
            if not found_category:
                uncategorized.append(assessment)
        
        # Reorder: alternate between high-priority categories
        stack_type = self.determine_stack_type(constraints)
        template = self.STACK_TEMPLATES.get(stack_type, {})
        sorted_categories = sorted(
            template.get('categories', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        reordered = []
        category_indices = {cat: 0 for cat, _ in sorted_categories}
        
        # Interleave assessments from each category
        for _ in range(len(recommendations)):
            for category, _ in sorted_categories:
                if category in categorized and category_indices[category] < len(categorized[category]):
                    reordered.append(categorized[category][category_indices[category]])
                    category_indices[category] += 1
                    if len(reordered) >= len(recommendations):
                        break
            
            if len(reordered) >= len(recommendations):
                break
        
        # Add any uncategorized
        reordered.extend(uncategorized)
        
        return reordered[:len(recommendations)]
