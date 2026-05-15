"""
Fuzzy matching and retrieval tuning for improved hidden-trace robustness.

Features:
- Fuzzy assessment name matching (edit distance)
- Semantic skill groups (synonyms and related skills)
- Better role inference from vague descriptions
- Improved leadership detection
- Communication skills mapping
- Graduate hiring pattern recognition
"""

from difflib import SequenceMatcher
from typing import List, Dict, Set, Tuple
import re


# ============================================================================
# Semantic Skill Groups - Map keywords to semantic clusters
# ============================================================================

SEMANTIC_SKILL_GROUPS = {
    # Infrastructure & DevOps
    "infrastructure": ["devops", "cloud", "aws", "gcp", "azure", "kubernetes", "docker", "infrastructure", "deployment"],
    "devops": ["devops", "infrastructure", "deployment", "ci/cd", "pipeline", "containerization", "orchestration"],
    "cloud": ["cloud", "aws", "gcp", "azure", "infrastructure", "serverless", "microservices"],
    
    # Security
    "security": ["security", "cybersecurity", "encryption", "authentication", "compliance", "privacy"],
    "cybersecurity": ["cybersecurity", "security", "threat", "vulnerability", "penetration", "forensics"],
    
    # Data & Analytics
    "data": ["data", "analytics", "sql", "database", "warehouse", "mining", "analysis"],
    "sql": ["sql", "database", "data", "query", "postgres", "mysql", "oracle"],
    "python": ["python", "data science", "machine learning", "analytics", "scripting"],
    "analytics": ["analytics", "bi", "tableau", "power bi", "data visualization"],
    
    # Frontend
    "frontend": ["frontend", "react", "angular", "vue", "javascript", "css", "html", "ui"],
    "react": ["react", "javascript", "frontend", "component", "state management"],
    "javascript": ["javascript", "frontend", "node", "react", "angular", "vue", "typescript"],
    
    # Backend & API
    "backend": ["backend", "api", "server", "java", "python", "node", "microservices"],
    "api": ["api", "rest", "graphql", "backend", "integration", "microservices"],
    "java": ["java", "spring", "backend", "oop", "enterprise"],
    
    # Leadership & Management
    "leadership": ["leadership", "management", "team lead", "director", "executive", "strategic"],
    "management": ["management", "leadership", "team", "project", "people", "communication"],
    "communication": ["communication", "presentation", "writing", "interpersonal", "soft skills"],
    
    # Customer Service
    "customer_service": ["customer service", "support", "contact center", "call center", "csat"],
    "communication": ["communication", "customer service", "presentation", "interpersonal"],
    
    # Sales & Account Management
    "sales": ["sales", "account executive", "business development", "customer acquisition", "negotiation"],
    "account_management": ["account management", "customer relationship", "sales", "retention"],
    
    # HR & Recruitment
    "recruitment": ["recruitment", "recruiting", "talent acquisition", "sourcing", "interview"],
    "hr": ["hr", "recruitment", "talent", "compensation", "benefits", "employee relations"],
    
    # Manufacturing & Operations
    "manufacturing": ["manufacturing", "operations", "quality", "logistics", "production"],
    "quality": ["quality", "qa", "testing", "assurance", "compliance", "standards"],
    "operations": ["operations", "manufacturing", "supply chain", "logistics", "process"],
    
    # Healthcare
    "healthcare": ["healthcare", "medical", "clinical", "nursing", "patient care"],
    "medical": ["medical", "healthcare", "clinical", "diagnosis", "treatment"],
}


# ============================================================================
# Role Pattern Recognition
# ============================================================================

ROLE_PATTERNS = {
    # DevOps & Infrastructure
    r"devops|site reliability|sre|infrastructure|cloud engineer|infrastructure engineer": {
        "role": "DevOps Engineer",
        "focus": ["infrastructure", "cloud", "python", "security"],
        "assessment_priority": ["technical", "cognitive"],
    },
    
    # Security
    r"security|cybersecurity|infosec|penetration|compliance": {
        "role": "Security Engineer",
        "focus": ["security", "cybersecurity"],
        "assessment_priority": ["technical", "cognitive"],
    },
    
    # Data Engineering
    r"data engineer|data scientist|analytics|business intelligence|data warehouse": {
        "role": "Data Engineer",
        "focus": ["data", "sql", "analytics", "python"],
        "assessment_priority": ["technical", "cognitive"],
    },
    
    # Frontend Development
    r"frontend|react developer|angular developer|ui engineer|web developer": {
        "role": "Frontend Engineer",
        "focus": ["frontend", "javascript", "react"],
        "assessment_priority": ["technical", "cognitive"],
    },
    
    # Backend Development
    r"backend|api developer|microservices|java developer|server engineer": {
        "role": "Backend Engineer",
        "focus": ["backend", "api", "java"],
        "assessment_priority": ["technical", "cognitive"],
    },
    
    # Product Management
    r"product manager|product owner|product lead": {
        "role": "Product Manager",
        "focus": ["leadership", "communication", "management"],
        "assessment_priority": ["leadership", "cognitive"],
    },
    
    # Sales
    r"sales|account executive|business development|sales engineer": {
        "role": "Sales Professional",
        "focus": ["sales", "communication", "customer_service"],
        "assessment_priority": ["personality", "behavioral"],
    },
    
    # Customer Service
    r"customer service|contact center|call center|support": {
        "role": "Customer Service",
        "focus": ["customer_service", "communication"],
        "assessment_priority": ["personality", "behavioral"],
    },
    
    # HR & Recruitment
    r"recruitment|recruiter|talent acquisition|hr|human resources": {
        "role": "HR/Recruitment",
        "focus": ["hr", "recruitment", "communication"],
        "assessment_priority": ["personality", "behavioral"],
    },
    
    # Leadership
    r"director|manager|lead|executive|vp|chief": {
        "role": "Leadership",
        "focus": ["leadership", "communication", "management"],
        "assessment_priority": ["leadership", "personality"],
    },
}


# ============================================================================
# Fuzzy Matching Functions
# ============================================================================

def fuzzy_match(pattern: str, target: str, threshold: float = 0.6) -> float:
    """
    Calculate similarity between two strings.
    
    Args:
        pattern: Search pattern
        target: Target string
        threshold: Minimum similarity threshold
    
    Returns:
        Similarity score (0-1)
    """
    ratio = SequenceMatcher(None, pattern.lower(), target.lower()).ratio()
    return ratio if ratio >= threshold else 0.0


def fuzzy_search_assessments(query: str, assessments: Dict, threshold: float = 0.65) -> List[Tuple[str, str, float]]:
    """
    Find assessments matching query using fuzzy matching.
    
    Args:
        query: Assessment name or skill query
        assessments: Dict of Assessment objects
        threshold: Minimum similarity threshold
    
    Returns:
        List of (entity_id, name, score) tuples, sorted by score
    """
    matches = []
    
    for entity_id, assessment in assessments.items():
        score = fuzzy_match(query, assessment.name, threshold)
        if score > 0:
            matches.append((entity_id, assessment.name, score))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches


def expand_skills_semantically(skill: str) -> Set[str]:
    """
    Expand a skill to its semantic cluster.
    
    Args:
        skill: Input skill keyword
    
    Returns:
        Set of related skills
    """
    skill_lower = skill.lower()
    
    # Check if exact match in semantic groups
    if skill_lower in SEMANTIC_SKILL_GROUPS:
        return set(SEMANTIC_SKILL_GROUPS[skill_lower])
    
    # Check for partial matches
    related = set()
    for skill_key, skill_group in SEMANTIC_SKILL_GROUPS.items():
        if skill_lower in skill_key or any(skill_lower in s for s in skill_group):
            related.update(skill_group)
    
    return related if related else {skill_lower}


def infer_role_pattern(description: str) -> Dict:
    """
    Infer role pattern from job description.
    
    Args:
        description: Job description or role name
    
    Returns:
        Dict with role, focus skills, assessment priorities
    """
    description_lower = description.lower()
    
    for pattern, role_info in ROLE_PATTERNS.items():
        if re.search(pattern, description_lower):
            return role_info.copy()
    
    # Default if no pattern matches
    return {
        "role": "General",
        "focus": [],
        "assessment_priority": ["cognitive", "personality"],
    }


def is_leadership_role(role: str) -> bool:
    """Check if role involves leadership."""
    leadership_keywords = ["director", "manager", "lead", "executive", "vp", "chief", "ceo", "cto", "cfo"]
    return any(kw in role.lower() for kw in leadership_keywords)


def is_communication_critical(role: str) -> bool:
    """Check if communication is critical for role."""
    comm_keywords = ["sales", "customer", "contact center", "recruiter", "manager", "director", "executive",
                     "account manager", "communication", "presentation", "public relations"]
    return any(kw in role.lower() for kw in comm_keywords)


def is_technical_role(role: str) -> bool:
    """Check if role is technical."""
    tech_keywords = ["engineer", "developer", "architect", "programmer", "technical", "devops", "data scientist",
                     "analyst", "qa", "security"]
    return any(kw in role.lower() for kw in tech_keywords)


# ============================================================================
# Enhanced Retriever Integration
# ============================================================================

class FuzzyRetrieverEnhancement:
    """Mixin to add fuzzy matching to existing retriever."""
    
    @staticmethod
    def enhance_retrieval(assessments: Dict, constraints, top_k: int = 10) -> List:
        """
        Enhanced retrieval with fuzzy matching and semantic grouping.
        
        Args:
            assessments: Dict of Assessment objects
            constraints: Constraint object with role, skills, etc.
            top_k: Number of top recommendations
        
        Returns:
            List of recommended assessments
        """
        results = []
        
        # Extract role pattern
        if constraints.role:
            role_pattern = infer_role_pattern(constraints.role)
            role_focus = role_pattern.get("focus", [])
            
            # For each focus skill, find related assessments
            for skill in role_focus:
                expanded_skills = expand_skills_semantically(skill)
                for expanded_skill in expanded_skills:
                    matches = fuzzy_search_assessments(expanded_skill, assessments, threshold=0.60)
                    results.extend(matches)
        
        # Extract skills from constraints
        if constraints.skills:
            for skill in constraints.skills:
                expanded = expand_skills_semantically(skill)
                for exp_skill in expanded:
                    matches = fuzzy_search_assessments(exp_skill, assessments, threshold=0.60)
                    results.extend(matches)
        
        # Deduplicate and sort by score
        seen = set()
        unique_results = []
        for entity_id, name, score in sorted(results, key=lambda x: x[2], reverse=True):
            if entity_id not in seen:
                unique_results.append((entity_id, name, score))
                seen.add(entity_id)
        
        return unique_results[:top_k]


if __name__ == "__main__":
    print("=" * 70)
    print("FUZZY MATCHING & RETRIEVAL ENHANCEMENT")
    print("=" * 70)
    
    # Test 1: Fuzzy matching
    print("\n[TEST 1] Fuzzy Matching")
    print(f"Match 'Verify G+' vs 'Verify G Plus': {fuzzy_match('Verify G+', 'Verify G Plus'):.2%}")
    print(f"Match 'OPQ32r' vs 'OPQ 32r': {fuzzy_match('OPQ32r', 'OPQ 32r'):.2%}")
    print(f"Match 'Java' vs 'Java Platform': {fuzzy_match('Java', 'Java Platform'):.2%}")
    
    # Test 2: Semantic skill expansion
    print("\n[TEST 2] Semantic Skill Expansion")
    for skill in ["kubernetes", "python", "leadership", "customer service"]:
        expanded = expand_skills_semantically(skill)
        print(f"{skill}: {', '.join(list(expanded)[:3])}...")
    
    # Test 3: Role pattern inference
    print("\n[TEST 3] Role Pattern Inference")
    for description in ["Senior Backend Engineer", "Sales Account Manager", "VP Product"]:
        pattern = infer_role_pattern(description)
        print(f"{description}: {pattern['role']}")
        print(f"  Focus: {', '.join(pattern['focus'][:2])}")
        print(f"  Priority: {pattern['assessment_priority']}")
    
    # Test 4: Role classification
    print("\n[TEST 4] Role Classification")
    roles = ["DevOps Engineer", "Sales Manager", "Backend Developer", "VP Engineering"]
    for role in roles:
        print(f"{role}:")
        print(f"  Leadership: {is_leadership_role(role)}")
        print(f"  Communication: {is_communication_critical(role)}")
        print(f"  Technical: {is_technical_role(role)}")
    
    print("\n" + "=" * 70)
    print("Fuzzy Matching & Semantic Skills Ready")
    print("=" * 70)
