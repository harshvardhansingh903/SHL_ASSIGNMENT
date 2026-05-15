"""
Semantic role clustering and normalization.

Maps similar role variations to normalized role clusters,
enabling generalization to hidden traces.
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RoleCluster:
    """A normalized role cluster with synonyms and related skills."""
    canonical_name: str  # e.g., 'engineer'
    synonyms: List[str]  # e.g., ['developer', 'programmer', 'architect']
    related_skills: List[str]  # e.g., ['coding', 'debugging', 'design']
    assessment_needs: List[str]  # e.g., ['technical', 'cognitive', 'personality']
    typical_seniority: List[str]  # e.g., ['entry', 'mid', 'senior']
    similar_roles: List[str]  # e.g., ['data engineer', 'backend engineer']


class SemanticRoleClusterer:
    """Clusters and normalizes hiring roles."""
    
    # Comprehensive role clustering
    ROLE_CLUSTERS = {
        'engineer': RoleCluster(
            canonical_name='engineer',
            synonyms=['developer', 'programmer', 'coder', 'software engineer',
                     'backend engineer', 'frontend engineer', 'full-stack engineer',
                     'platform engineer', 'systems engineer', 'architect',
                     'technical lead', 'engineering lead', 'tech lead',
                     'distributed systems', 'devops engineer', 'infrastructure engineer'],
            related_skills=['coding', 'debugging', 'design', 'architecture',
                           'problem solving', 'technical depth', 'system design',
                           'database design', 'api design', 'performance optimization',
                           'java', 'python', 'rust', 'go', 'c++', 'typescript', 'javascript',
                           'spring', 'django', 'fastapi', 'node.js', 'sql', 'nosql'],
            assessment_needs=['technical', 'cognitive', 'personality', 'coding'],
            typical_seniority=['entry', 'mid', 'senior', 'lead'],
            similar_roles=['qa engineer', 'test engineer', 'database engineer'],
        ),
        
        'leadership': RoleCluster(
            canonical_name='leadership',
            synonyms=['manager', 'director', 'executive', 'cxo', 'c-level',
                     'ceo', 'cto', 'cfo', 'coo', 'head of', 'vp', 'vice president',
                     'president', 'principal', 'lead', 'senior manager',
                     'team lead', 'engineering manager', 'product manager',
                     'program manager', 'project manager'],
            related_skills=['strategic thinking', 'vision setting', 'motivation',
                           'team building', 'delegation', 'decision making',
                           'business acumen', 'stakeholder management',
                           'leadership', 'influence', 'communication',
                           'conflict resolution', 'mentoring'],
            assessment_needs=['personality', 'leadership', 'cognitive', 'motivation'],
            typical_seniority=['senior', 'executive'],
            similar_roles=['manager', 'director'],
        ),
        
        'sales': RoleCluster(
            canonical_name='sales',
            synonyms=['salesperson', 'sales representative', 'account executive',
                     'sales manager', 'business development', 'bd', 'account manager',
                     'customer success manager', 'sales director',
                     'territory manager', 'relationship manager', 'vendor manager'],
            related_skills=['communication', 'persuasion', 'negotiation', 'resilience',
                           'relationship building', 'customer focus', 'closing',
                           'prospecting', 'pipeline management', 'consultative selling',
                           'upselling', 'cross-selling', 'product knowledge'],
            assessment_needs=['personality', 'motivation', 'behavioral', 'cognitive'],
            typical_seniority=['entry', 'mid', 'senior'],
            similar_roles=['business development', 'account management'],
        ),
        
        'finance': RoleCluster(
            canonical_name='finance',
            synonyms=['accountant', 'financial analyst', 'accounting', 'auditor',
                     'finance manager', 'financial controller', 'treasurer',
                     'cfo', 'investment analyst', 'financial planner',
                     'tax specialist', 'bookkeeper', 'cost accountant'],
            related_skills=['numerical reasoning', 'financial analysis', 'accounting',
                           'audit', 'compliance', 'attention to detail',
                           'spreadsheet', 'excel', 'sql', 'data analysis',
                           'risk assessment', 'tax knowledge', 'reporting'],
            assessment_needs=['cognitive', 'technical', 'personality', 'attention'],
            typical_seniority=['entry', 'mid', 'senior'],
            similar_roles=['accounting', 'treasury', 'audit'],
        ),
        
        'healthcare': RoleCluster(
            canonical_name='healthcare',
            synonyms=['nurse', 'doctor', 'physician', 'pharmacist', 'medical',
                     'healthcare provider', 'clinical staff', 'health professional',
                     'care coordinator', 'medical assistant', 'clinical manager',
                     'hospital administrator', 'medical technician', 'health officer'],
            related_skills=['medical knowledge', 'clinical skills', 'empathy',
                           'patient care', 'hipaa', 'compliance', 'precision',
                           'attention to detail', 'emergency response', 'teamwork',
                           'communication', 'bedside manner', 'technical knowledge'],
            assessment_needs=['technical', 'personality', 'behavioral', 'cognitive'],
            typical_seniority=['entry', 'mid', 'senior'],
            similar_roles=['medical', 'clinical', 'nursing'],
        ),
        
        'contact_center': RoleCluster(
            canonical_name='contact_center',
            synonyms=['call centre', 'call center', 'customer service', 'support',
                     'customer support', 'technical support', 'help desk',
                     'customer service representative', 'csr', 'customer care',
                     'inbound agent', 'outbound agent', 'service agent',
                     'support specialist', 'support agent', 'contact centre agent',
                     'call centre operator', 'customer agent'],
            related_skills=['communication', 'spoken english', 'listening', 'empathy',
                           'customer focus', 'problem solving', 'patience',
                           'multitasking', 'typing', 'system navigation',
                           'conflict resolution', 'stress tolerance', 'professionalism'],
            assessment_needs=['language', 'personality', 'behavioral', 'simulation'],
            typical_seniority=['entry', 'mid'],
            similar_roles=['customer service', 'support'],
        ),
        
        'graduate': RoleCluster(
            canonical_name='graduate',
            synonyms=['graduate trainee', 'graduate scheme', 'management trainee',
                     'early career', 'entry level', 'junior', 'analyst',
                     'associate', 'coordinator', 'trainee', 'rotational program'],
            related_skills=['learning agility', 'problem solving', 'communication',
                           'teamwork', 'analytical thinking', 'business acumen',
                           'adaptability', 'motivation', 'potential', 'work ethic'],
            assessment_needs=['cognitive', 'personality', 'situational_judgment', 'behavioral'],
            typical_seniority=['entry'],
            similar_roles=['entry level', 'junior roles'],
        ),
        
        'manufacturing': RoleCluster(
            canonical_name='manufacturing',
            synonyms=['production', 'plant operator', 'factory worker',
                     'manufacturing technician', 'production technician',
                     'plant technician', 'machine operator', 'assembly',
                     'quality assurance', 'qa', 'production manager',
                     'plant manager', 'manufacturing engineer'],
            related_skills=['safety', 'reliability', 'attention to detail',
                           'technical knowledge', 'equipment operation',
                           'safety protocols', 'compliance', 'teamwork',
                           'quality focus', 'problem solving', 'efficiency',
                           'dependability', 'precision'],
            assessment_needs=['behavioral', 'technical', 'cognitive', 'safety'],
            typical_seniority=['entry', 'mid', 'senior'],
            similar_roles=['production', 'operations'],
        ),
        
        'administrative': RoleCluster(
            canonical_name='administrative',
            synonyms=['admin', 'assistant', 'secretary', 'administrative assistant',
                     'office manager', 'executive assistant', 'clerical',
                     'admin officer', 'office assistant', 'receptionist',
                     'office coordinator', 'administrative coordinator',
                     'administrative professional', 'business support'],
            related_skills=['organization', 'microsoft office', 'excel', 'word',
                           'communication', 'scheduling', 'email management',
                           'documentation', 'attention to detail', 'multitasking',
                           'customer service', 'data entry', 'administrative procedures'],
            assessment_needs=['technical', 'personality', 'behavioral', 'administrative'],
            typical_seniority=['entry', 'mid', 'senior'],
            similar_roles=['office support', 'clerical'],
        ),
        
        'hr': RoleCluster(
            canonical_name='hr',
            synonyms=['human resources', 'recruiter', 'talent acquisition',
                     'people ops', 'hr manager', 'hr coordinator', 'hr specialist',
                     'recruiting manager', 'technical recruiter', 'hr analyst',
                     'talent manager', 'people manager', 'organizational development'],
            related_skills=['communication', 'relationship building', 'assessment',
                           'candidate evaluation', 'recruitment', 'policy knowledge',
                           'employee relations', 'compliance', 'data analysis',
                           'conflict resolution', 'negotiation', 'business understanding'],
            assessment_needs=['personality', 'behavioral', 'cognitive', 'communication'],
            typical_seniority=['entry', 'mid', 'senior'],
            similar_roles=['recruiting', 'talent acquisition'],
        ),
    }
    
    def __init__(self):
        """Initialize role clusterer with built-in clusters."""
        self.clusters = self.ROLE_CLUSTERS
        self._build_reverse_mapping()
    
    def _build_reverse_mapping(self):
        """Build mapping from any role variant to canonical name."""
        self.role_to_cluster = {}
        
        for canonical_name, cluster in self.clusters.items():
            # Add canonical name
            self.role_to_cluster[canonical_name.lower()] = canonical_name
            
            # Add all synonyms
            for synonym in cluster.synonyms:
                self.role_to_cluster[synonym.lower()] = canonical_name
    
    def normalize_role(self, role: str) -> Optional[str]:
        """
        Normalize a role to its canonical cluster.
        
        Args:
            role: Any role variant (e.g., 'backend developer')
        
        Returns:
            Canonical role name or None if not found
        """
        if not role:
            return None
        
        role_lower = role.lower().strip()
        
        # Exact match
        if role_lower in self.role_to_cluster:
            return self.role_to_cluster[role_lower]
        
        # Substring matching (prioritize longer matches)
        best_match = None
        best_length = 0
        
        for role_variant, canonical in self.role_to_cluster.items():
            if role_variant in role_lower and len(role_variant) > best_length:
                best_match = canonical
                best_length = len(role_variant)
        
        return best_match
    
    def get_cluster(self, role: str) -> Optional[RoleCluster]:
        """Get the full cluster for a role."""
        canonical = self.normalize_role(role)
        if canonical:
            return self.clusters[canonical]
        return None
    
    def get_assessment_needs(self, role: str) -> List[str]:
        """Get recommended assessment needs for a role."""
        cluster = self.get_cluster(role)
        if cluster:
            return cluster.assessment_needs
        return []
    
    def get_related_skills(self, role: str) -> List[str]:
        """Get related skills for a role."""
        cluster = self.get_cluster(role)
        if cluster:
            return cluster.related_skills
        return []
    
    def get_similar_roles(self, role: str) -> List[str]:
        """Get similar roles in the same cluster."""
        cluster = self.get_cluster(role)
        if cluster:
            return cluster.similar_roles
        return []
    
    def expand_skills_from_role(self, role: str) -> List[str]:
        """
        Expand inferred skills from a role.
        
        Useful for constraint extraction - if role is specified,
        we can infer likely technical and soft skills.
        """
        cluster = self.get_cluster(role)
        if cluster:
            return cluster.related_skills
        return []
    
    def infer_assessment_needs_from_seniority(self, seniority: str) -> List[str]:
        """Infer assessment needs from seniority level."""
        seniority_lower = seniority.lower() if seniority else ''
        
        if 'executive' in seniority_lower or 'c-level' in seniority_lower:
            return ['personality', 'leadership', 'cognitive', 'motivation']
        elif 'senior' in seniority_lower:
            return ['personality', 'cognitive', 'technical', 'behavioral']
        elif 'mid' in seniority_lower or 'manager' in seniority_lower:
            return ['personality', 'cognitive', 'technical', 'behavioral']
        elif 'entry' in seniority_lower or 'junior' in seniority_lower:
            return ['cognitive', 'personality', 'situational_judgment', 'behavioral']
        elif 'graduate' in seniority_lower:
            return ['cognitive', 'personality', 'situational_judgment']
        
        return ['personality', 'cognitive']  # Default
    
    def merge_role_clusters(self, role1: str, role2: str) -> RoleCluster:
        """
        Merge two role clusters to create hybrid assessment needs.
        
        Used for complex roles like 'Sales Engineering' or 'Product Management'.
        """
        cluster1 = self.get_cluster(role1)
        cluster2 = self.get_cluster(role2)
        
        if not cluster1 and not cluster2:
            return None
        elif not cluster1:
            return cluster2
        elif not cluster2:
            return cluster1
        
        # Merge assessment needs, prioritizing both
        merged_needs = list(set(cluster1.assessment_needs + cluster2.assessment_needs))
        merged_skills = list(set(cluster1.related_skills + cluster2.related_skills))
        
        return RoleCluster(
            canonical_name=f"{cluster1.canonical_name}_{cluster2.canonical_name}",
            synonyms=cluster1.synonyms + cluster2.synonyms,
            related_skills=merged_skills,
            assessment_needs=merged_needs,
            typical_seniority=cluster1.typical_seniority,
            similar_roles=cluster1.similar_roles + cluster2.similar_roles,
        )
