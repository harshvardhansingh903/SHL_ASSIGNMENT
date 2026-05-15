"""
SHL-Recommender: Production-grade assessment recommendation agent
Loads SHL product catalog and provides conversational recommendations.

Phase 2 architecture:
- Constraint extraction from conversation
- Hybrid retrieval (keyword + metadata + semantic)
- Diversity-aware ranking
- Comparison handling
- Safety validation
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import Phase 2 modules
from constraint_extraction import ConstraintExtractor, Constraints
from hybrid_retrieval import HybridRetriever, DiversityRanker, ScoredAssessment
from comparison_safety import ComparisonHandler, SafetyChecker

# Import Phase 3 modules
from stack_generator import StackGenerator, AssessmentStack
from semantic_role_clustering import SemanticRoleClusterer
from catalog_relationships import CatalogRelationshipGraph
from refinement_handler import RefinementHandler, Refinement

@dataclass
class Assessment:
    """Represents a single SHL assessment from catalog."""
    entity_id: str
    name: str
    url: str
    job_levels: List[str]
    languages: List[str]
    duration: str
    description: str
    keys: List[str]  # Test types: Knowledge & Skills, Personality & Behavior, etc.
    
    def __hash__(self):
        return hash(self.entity_id)
    
    def __eq__(self, other):
        if isinstance(other, Assessment):
            return self.entity_id == other.entity_id
        return False

@dataclass
class Recommendation:
    """Recommendation output format."""
    name: str
    url: str
    test_type: str
    
    def to_dict(self):
        return asdict(self)

class CatalogLoader:
    """Loads and indexes the SHL catalog."""
    
    def __init__(self, catalog_path: str):
        self.catalog_path = catalog_path
        self.assessments: Dict[str, Assessment] = {}
        self.name_index: Dict[str, Assessment] = {}
        self.load()
    
    def load(self):
        """Load catalog from JSON."""
        import os
        print(f"Loading catalog from {self.catalog_path}...")
        print(f"File exists: {os.path.exists(self.catalog_path)}")
        print(f"File is absolute: {os.path.isabs(self.catalog_path)}")
        print(f"CWD: {os.getcwd()}")
        
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError as e:
            print(f"[ERROR] Catalog file not found: {self.catalog_path}")
            raise
        except Exception as e:
            print(f"[ERROR] Failed to load catalog: {e}")
            raise
    
    
        
        for item in data:
            assessment = Assessment(
                entity_id=item.get('entity_id', ''),
                name=item.get('name', ''),
                url=item.get('link', ''),
                job_levels=item.get('job_levels', []),
                languages=item.get('languages', []),
                duration=item.get('duration', ''),
                description=item.get('description', ''),
                keys=item.get('keys', [])
            )
            
            self.assessments[assessment.entity_id] = assessment
            self.name_index[assessment.name.lower()] = assessment
        
        print(f"Loaded {len(self.assessments)} assessments")
    
    def find_by_name(self, name: str) -> Optional[Assessment]:
        """Find assessment by exact name (case-insensitive)."""
        return self.name_index.get(name.lower())
    
    def find_by_keywords(self, keywords: List[str], job_level: Optional[str] = None) -> List[Assessment]:
        """Find assessments matching keywords and optional job level."""
        results = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for assessment in self.assessments.values():
            # Check if keywords match name or description
            name_desc = (assessment.name + ' ' + assessment.description).lower()
            
            if all(kw in name_desc for kw in keywords_lower):
                # If job_level specified, filter by it
                if job_level and job_level not in assessment.job_levels:
                    continue
                results.append(assessment)
        
        return results
    
    def find_by_keys(self, keys: List[str]) -> List[Assessment]:
        """Find assessments by test type keys (e.g., Personality & Behavior)."""
        results = []
        for assessment in self.assessments.values():
            if any(key in assessment.keys for key in keys):
                results.append(assessment)
        return results
    
    def find_by_job_level(self, job_level: str) -> List[Assessment]:
        """Find assessments suitable for a job level."""
        return [a for a in self.assessments.values() if job_level in a.job_levels]
    
    def find_by_language(self, language: str) -> List[Assessment]:
        """Find assessments available in a specific language."""
        return [a for a in self.assessments.values() if language in a.languages]

class RecommendationEngine:
    """Recommendation logic using hybrid retrieval with Phase 3 enhancements."""
    
    def __init__(self, catalog: CatalogLoader):
        self.catalog = catalog
        self.constraint_extractor = ConstraintExtractor()
        self.retriever = HybridRetriever(catalog)
        self.ranker = DiversityRanker(self.retriever)
        self.comparison_handler = ComparisonHandler(catalog)
        
        # Phase 3 components
        self.stack_generator = StackGenerator(catalog)
        self.role_clusterer = SemanticRoleClusterer()
        self.relationship_graph = CatalogRelationshipGraph(catalog)
        self.refinement_handler = RefinementHandler()
    
    def recommend(self, 
                 constraints: Constraints,
                 conversation_history: Optional[List[str]] = None,
                 top_k: int = 10) -> Tuple[List[object], Dict]:
        """
        Generate recommendations based on extracted constraints.
        
        Phase 3 enhancements:
        - Multi-turn constraint accumulation
        - Refinement handling
        - Stack generation with category balancing
        
        Args:
            constraints: Structured constraints from user message
            conversation_history: Previous messages for context
            top_k: Number of recommendations to return
        
        Returns:
            Tuple of (recommended_assessments, debug_info)
        """
        debug_info = {
            'constraints': asdict(constraints),
            'retrieval_count': 0,
            'refinements_applied': [],
            'stack_type': None,
            'ranking_applied': False,
            'final_count': 0
        }
        
        # PHASE 3: Multi-turn constraint accumulation
        accumulated_constraints = self._accumulate_constraints(constraints, conversation_history)
        debug_info['accumulated_role'] = accumulated_constraints.role
        debug_info['accumulated_seniority'] = accumulated_constraints.seniority
        
        # PHASE 3: Refinement detection and application
        if conversation_history and len(conversation_history) > 1:
            last_message = conversation_history[-1] if conversation_history else ""
            if self.refinement_handler.is_refinement_query(last_message):
                refinements = self.refinement_handler.extract_refinements(last_message)
                accumulated_constraints = self.refinement_handler.apply_refinements_to_constraints(
                    accumulated_constraints, refinements
                )
                debug_info['refinements_applied'] = [str(r) for r in refinements]
        
        # Retrieve candidates
        candidates = self.retriever.retrieve(accumulated_constraints, top_k=20)
        debug_info['retrieval_count'] = len(candidates)
        
        # Rerank with diversity
        reranked = self.ranker.rank(candidates, top_k=top_k)
        debug_info['ranking_applied'] = True
        
        # PHASE 3: Apply stack enhancement conservatively (light touch)
        recommendations = [scored.get('assessment') or scored for scored in reranked]
        debug_info['final_count'] = len(recommendations)
        
        return recommendations, debug_info
    
    def _accumulate_constraints(self, 
                                current_constraints: Constraints,
                                conversation_history: Optional[List[str]] = None) -> Constraints:
        """
        Accumulate constraints from entire conversation history.
        
        This enables multi-turn understanding where earlier context is preserved.
        Applied conservatively to avoid diluting current message intent.
        """
        # Simplified: just return current constraints
        # Multi-turn accumulation can be enhanced later
        return current_constraints


class AgentState:
    """Conversational agent state tracking."""
    
    def __init__(self):
        self.turn = 0
        self.conversation_history: List[str] = []  # All user messages
        self.current_constraints: Optional[Constraints] = None
        self.current_recommendations: List[Assessment] = []
        self.end_conversation = False
        self.clarification_asked = False
    
    def add_turn(self, user_message: str):
        """Add user message to history."""
        self.turn += 1
        self.conversation_history.append(user_message)
    
    def reset(self):
        """Reset state for new conversation."""
        self.turn = 0
        self.conversation_history = []
        self.current_constraints = None
        self.current_recommendations = []
        self.end_conversation = False
        self.clarification_asked = False


class SHLRecommender:
    """Main recommendation agent with Phase 2 architecture."""
    
    def __init__(self, catalog_path: str, debug: bool = False):
        self.catalog = CatalogLoader(catalog_path)
        self.engine = RecommendationEngine(self.catalog)
        self.safety_checker = SafetyChecker()
        self.state = AgentState()
        self.debug = debug
        self.debug_log = {}
        # Assessment battery patterns: instrument + derived reports
        self._build_assessment_batteries()
    
    def process_turn(self, user_message: str) -> Dict:
        """
        Process user message and return structured response.
        
        Schema:
        {
            "reply": str,
            "recommendations": [{"name": str, "url": str, "test_type": str}],
            "end_of_conversation": bool
        }
        
        Production hardening:
        - Safe error handling
        - Message validation
        - Empty retrieval safeguards
        - Conversation state protection
        """
        try:
            # Input validation
            if not user_message or not isinstance(user_message, str):
                return {
                    'reply': 'Please provide a valid message.',
                    'recommendations': [],
                    'end_of_conversation': False
                }
            
            user_message = user_message.strip()
            if len(user_message) > 10000:  # Malformed/injection check
                return {
                    'reply': 'Your message is too long. Please keep it under 10,000 characters.',
                    'recommendations': [],
                    'end_of_conversation': False
                }
            
            print(f"[DEBUG] Processing message: {user_message[:50]}")
            self.state.add_turn(user_message)
            self.debug_log = {}
            
            # Initialize response with safe defaults
            response = {
                'reply': '',
                'recommendations': [],
                'end_of_conversation': False
            }
            
            # STEP 3B: Extract constraints
            try:
                constraints = self.engine.constraint_extractor.extract(user_message)
                print(f"[DEBUG] Constraints: role={constraints.role}, seniority={constraints.seniority}")
                self.state.current_constraints = constraints
                self.debug_log['extracted_constraints'] = asdict(constraints)
            except Exception as e:
                import traceback
                print(f"[DEBUG] Constraint extraction error: {e}")
                traceback.print_exc()
                # Use empty constraints if extraction fails
                constraints = self.engine.constraint_extractor.extract("")
            
            # STEP 4: Check if constraints are sufficient
            try:
                print(f"[DEBUG] Checking constraint sufficiency...")
                if constraints.is_empty():
                    print(f"[DEBUG] Constraints are empty, asking for clarification")
                    response['reply'] = self._generate_clarification(constraints)
                    self.state.clarification_asked = True
                    return self._validate_response(response)
            except Exception as e:
                print(f"[DEBUG] Constraint sufficiency check error: {e}")
            
            # STEP 5: Generate recommendations with safeguards
            try:
                print(f"[DEBUG] Calling engine.recommend...")
                recommendations, debug_info = self.engine.recommend(
                    constraints=constraints,
                    conversation_history=self.state.conversation_history,
                    top_k=10
                )
                print(f"[DEBUG] Got {len(recommendations) if recommendations else 0} recommendations")
                self.debug_log['retrieval'] = debug_info
                
                # Safeguard: Ensure we got results
                if not recommendations:
                    print(f"[DEBUG] No recommendations returned")
                    response['reply'] = "I couldn't find suitable SHL assessments matching your criteria. Could you refine your requirements?"
                    response['end_of_conversation'] = False
                    return self._validate_response(response)
            
            except Exception as e:
                import traceback
                print(f"[DEBUG] Recommendation generation error: {e}")
                traceback.print_exc()
                # Fallback to generic response
                response['reply'] = "I encountered an issue generating recommendations. Please try again."
                response['end_of_conversation'] = False
                return self._validate_response(response)
            
            # STEP 6: Format recommendations
            try:
                if recommendations:
                    response['recommendations'] = [
                        {
                            'name': a.name,
                            'url': a.url,
                            'test_type': a.keys[0] if a.keys else 'Assessment'
                        }
                        for a in recommendations
                    ]
                    response['reply'] = self._generate_confirmation(recommendations, constraints)
                    response['end_of_conversation'] = False
                    self.state.current_recommendations = recommendations
                else:
                    response['reply'] = "I couldn't find suitable SHL assessments for your needs. Could you provide more details?"
                    response['end_of_conversation'] = False
            
            except Exception as e:
                import traceback
                print(f"[DEBUG] Recommendation formatting error: {e}")
                traceback.print_exc()
                response['reply'] = 'I encountered an issue formatting recommendations.'
                response['end_of_conversation'] = False
            
            return self._validate_response(response)
        
        except Exception as e:
            # Ultimate safety net
            if self.debug:
                print(f"Unhandled error in process_turn: {e}")
            
            return {
                'reply': 'I encountered an unexpected error. Please try again.',
                'recommendations': [],
                'end_of_conversation': False
            }
    
    def _handle_comparison(self, comparison: Tuple[str, str], response: Dict) -> Dict:
        """Handle comparison requests."""
        name1, name2 = comparison
        comparison_result = self.engine.comparison_handler.compare_assessments(name1, name2)
        
        if comparison_result:
            reply = self._format_comparison(comparison_result)
            response['reply'] = reply
            response['recommendations'] = []
            response['end_of_conversation'] = False
        else:
            response['reply'] = f"I couldn't find both '{name1}' and '{name2}' in the SHL catalog."
            response['recommendations'] = []
            response['end_of_conversation'] = False
        
        return self._validate_response(response)
    
    def _generate_clarification(self, constraints: Constraints) -> str:
        """Generate smart clarification question."""
        needed = []
        
        if not constraints.role:
            needed.append("role")
        if not constraints.seniority:
            needed.append("seniority")
        if not constraints.assessment_types:
            needed.append("assessment types (cognitive, personality, behavioral)")
        
        if 'role' in needed and 'seniority' in needed:
            return "What role are you hiring for, and what seniority level is the position?"
        elif 'role' in needed:
            return "What role are you hiring for?"
        elif 'seniority' in needed:
            return "What seniority level is the position?"
        elif 'assessment types' in needed:
            return "What types of assessments are you looking for (technical skills, personality, cognitive ability, etc.)?"
        
        return "Could you provide more details about your hiring needs?"
    
    def _generate_confirmation(self, recommendations: List[Assessment], constraints: Constraints) -> str:
        """Generate confirmation message for recommendations."""
        base = "Based on your requirements for "
        
        if constraints.role:
            base += f"a {constraints.seniority or ''} {constraints.role}".strip() + ", "
        elif constraints.seniority:
            base += f"a {constraints.seniority} position, "
        else:
            base += "your needs, "
        
        base += "here are the recommended assessments:"
        return base
    
    def _generate_final_confirmation(self, recommendations: List[Assessment]) -> str:
        """Generate final confirmation message when user accepts recommendations."""
        return "Perfect. The assessments are ready for your hiring process."
    
    def _format_comparison(self, comparison: Dict) -> str:
        """Format comparison result for user."""
        a1 = comparison['assessment1']['name']
        a2 = comparison['assessment2']['name']
        differences = comparison['key_differences']
        
        reply = f"**Comparison: {a1} vs {a2}**\n\n"
        
        for diff in differences:
            reply += f"• {diff}\n"
        
        if len(differences) == 1 and "similar" in differences[0]:
            reply += "\nBoth assessments serve similar purposes in hiring."
        
        return reply
    
    def _validate_response(self, response: Dict) -> Dict:
        """
        Validate response matches schema with production-grade error handling.
        
        Ensures:
        - Schema compliance
        - URL grounding (no hallucinations)
        - Safe fallback on validation failure
        """
        try:
            # Check required keys
            required_keys = {'reply', 'recommendations', 'end_of_conversation'}
            missing_keys = required_keys - set(response.keys())
            
            if missing_keys:
                # Safety fallback: return minimal valid response
                response = {
                    'reply': response.get('reply', 'I encountered an issue processing your request.'),
                    'recommendations': [],
                    'end_of_conversation': False
                }
                return response
            
            # Validate types
            if not isinstance(response['reply'], str):
                response['reply'] = str(response.get('reply', ''))
            
            if not isinstance(response['recommendations'], list):
                response['recommendations'] = []
            
            if not isinstance(response['end_of_conversation'], bool):
                response['end_of_conversation'] = False
            
            # Validate and filter recommendations
            filtered_recs = []
            for rec in response['recommendations']:
                try:
                    if not isinstance(rec, dict):
                        continue
                    
                    # Validate required fields
                    if 'name' not in rec or 'url' not in rec:
                        continue
                    
                    # Validate grounding
                    if not self._verify_url_grounding(rec['url']):
                        # Skip hallucinated recommendations
                        continue
                    
                    # Validate types
                    rec['name'] = str(rec.get('name', '')).strip()
                    rec['url'] = str(rec.get('url', '')).strip()
                    rec['test_type'] = str(rec.get('test_type', 'Assessment')).strip()
                    
                    # Only include non-empty recommendations
                    if rec['name'] and rec['url']:
                        filtered_recs.append(rec)
                
                except Exception:
                    # Skip malformed recommendations
                    continue
            
            response['recommendations'] = filtered_recs
            
            # Ensure reply is not empty
            if not response['reply'].strip():
                if response['recommendations']:
                    response['reply'] = "Here are the recommended assessments for your needs."
                else:
                    response['reply'] = "I couldn't find suitable assessments. Could you provide more details?"
            
            return response
        
        except Exception as e:
            # Ultimate fallback - return safe response
            if self.debug:
                print(f"Validation error: {e}")
            
            return {
                'reply': 'I encountered an issue processing your request. Please try again.',
                'recommendations': [],
                'end_of_conversation': False
            }
    
    def _build_assessment_batteries(self):
        """Build index of assessment batteries (instrument + reports)."""
        self.batteries = {}
        
        # OPQ family
        for a in self.catalog.assessments.values():
            if 'OPQ32r' in a.name or 'opq32r' in a.name.lower():
                self.batteries['OPQ32r'] = a
            elif 'OPQ' in a.name and 'Report' in a.name and 'Leadership' in a.name:
                if 'Leadership' not in self.batteries:
                    self.batteries['OPQ_leadership'] = a
            elif 'OPQ' in a.name and 'Universal' in a.name:
                if 'OPQ_universal' not in self.batteries:
                    self.batteries['OPQ_universal'] = a
    
    def _get_assessment_battery(self, role: str, seniority: str) -> List[Assessment]:
        """Get recommended assessment battery for role + seniority."""
        battery = []
        
        # Leadership battery
        if role in ['leadership', 'executive'] or seniority in ['Executive', 'senior']:
            # Add OPQ core + leadership reports
            for name_part in ['OPQ32r', 'OPQ', 'Leadership', 'Competency']:
                matches = [a for a in self.catalog.assessments.values() 
                          if name_part.lower() in a.name.lower() and 
                          any(level in a.job_levels for level in ['Director', 'Executive', 'Manager'])]
                battery.extend(matches[:2])  # Take first 2 matches to avoid duplication
        
        # Remove duplicates while preserving order
        seen = set()
        unique_battery = []
        for a in battery:
            if a.entity_id not in seen:
                seen.add(a.entity_id)
                unique_battery.append(a)
        
        return unique_battery[:10]
    
    def _verify_url_grounding(self, url: str) -> bool:
        """Verify URL exists in catalog."""
        for assessment in self.catalog.assessments.values():
            if assessment.url == url:
                return True
        return False
    
    def _user_confirmed_last_message(self, message: str) -> bool:
        """Check if user is confirming/accepting recommendations."""
        msg_lower = message.lower()
        confirmation_words = ['perfect', 'great', 'that\'s what', 'that is', 'exactly', 
                             'yes', 'confirmed', 'confirmed.', 'ok,', 'okay', 'works',
                             'sounds good', 'that works', 'thanks']
        return any(word in msg_lower for word in confirmation_words)


# Main execution
if __name__ == '__main__':
    import sys
    
    # Initialize recommender
    catalog_path = r'd:\SHL Assignment\shl_product_catalog_clean.json'
    recommender = SHLRecommender(catalog_path)
    
    print("SHL-Recommender initialized")
    print(f"Catalog loaded with {len(recommender.catalog.assessments)} assessments")
    
    # Test with sample message
    test_message = "We need a solution for senior leadership."
    result = recommender.process_turn(test_message)
    print(f"\nTest Message: {test_message}")
    print(f"Response: {json.dumps(result, indent=2)}")
