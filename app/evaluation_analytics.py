"""
Extended evaluation analytics for Phase 3 assessment and improvement planning.

Provides detailed analysis of:
- Missing expected assessments (false negatives)
- False positive recommendations
- Ranking quality
- Category diversity
- Refinement effectiveness
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
from collections import defaultdict

@dataclass
class TraceAnalysis:
    """Detailed analysis of a single trace."""
    trace_name: str
    turns: int
    recall_at_10: float
    precision: float
    
    # Detailed metrics
    total_expected: int
    total_recommended: int
    correct_recommendations: int
    missing_assessments: List[str] = field(default_factory=list)
    false_positives: List[str] = field(default_factory=list)
    
    # Category analysis
    category_distribution: Dict[str, int] = field(default_factory=dict)
    expected_categories: Dict[str, int] = field(default_factory=dict)
    
    # Per-turn analysis
    per_turn_metrics: Dict[int, Dict] = field(default_factory=dict)
    
    # Ranking quality
    average_rank_of_correct: float = 0.0
    max_rank_of_correct: int = 0
    
    # Recommendations
    primary_issue: str = ""
    secondary_issues: List[str] = field(default_factory=list)


class ExtendedEvaluator:
    """Extended evaluation framework for Phase 3."""
    
    def __init__(self, catalog: object):
        """
        Initialize extended evaluator.
        
        Args:
            catalog: CatalogLoader instance
        """
        self.catalog = catalog
        self.category_keywords = {
            'technical': ['Programming', 'Java', 'Spring', 'SQL', 'Rust', 'Python',
                         'Smart Interview', 'Verify', 'Financial', 'Accounting', 'Excel'],
            'cognitive': ['Verify', 'Inductive', 'Deductive', 'Numerical', 'Reasoning', 'G+'],
            'personality': ['OPQ', 'Personality', 'Behavior', 'Team Types', 'Engagement'],
            'behavioral': ['Situational', 'SJQ', 'Scenarios', 'Simulation', 'Competency'],
            'leadership': ['Leadership', 'Manager', 'Executive', 'Enterprise'],
            'language': ['SVAR', 'Spoken', 'English', 'Communication'],
            'simulation': ['Simulation', 'Exercise', 'Interactive', 'Case Study'],
        }
    
    def analyze_trace_performance(self,
                                  trace_name: str,
                                  recommended_names: List[str],
                                  expected_names: List[str],
                                  per_turn_data: Dict[int, Dict] = None) -> TraceAnalysis:
        """
        Perform detailed analysis of a trace.
        
        Args:
            trace_name: Name of trace (e.g., 'C1')
            recommended_names: List of recommended assessment names
            expected_names: List of expected assessment names
            per_turn_data: Optional per-turn metrics
        
        Returns:
            TraceAnalysis object with detailed findings
        """
        recommended_set = set(name.lower() for name in recommended_names)
        expected_set = set(name.lower() for name in expected_names)
        
        # Calculate basic metrics
        correct = recommended_set & expected_set
        missing = expected_set - recommended_set
        false_pos = recommended_set - expected_set
        
        recall = len(correct) / len(expected_set) if expected_set else 1.0
        precision = len(correct) / len(recommended_set) if recommended_set else 1.0
        
        # Categorize assessments
        recommended_categories = self._categorize_assessments(recommended_names)
        expected_categories = self._categorize_assessments(expected_names)
        
        # Analyze missing assessments
        primary_issue = self._identify_primary_issue(
            missing, expected_categories, trace_name
        )
        secondary_issues = self._identify_secondary_issues(
            recommended_set, expected_set, recommended_categories, expected_categories
        )
        
        # Average rank of correct assessments
        avg_rank, max_rank = self._calculate_recommendation_ranks(
            recommended_names, list(correct)
        )
        
        analysis = TraceAnalysis(
            trace_name=trace_name,
            turns=per_turn_data.get('total_turns', 0) if per_turn_data else 0,
            recall_at_10=recall,
            precision=precision,
            total_expected=len(expected_set),
            total_recommended=len(recommended_set),
            correct_recommendations=len(correct),
            missing_assessments=list(missing),
            false_positives=list(false_pos),
            category_distribution=recommended_categories,
            expected_categories=expected_categories,
            average_rank_of_correct=avg_rank,
            max_rank_of_correct=max_rank,
            primary_issue=primary_issue,
            secondary_issues=secondary_issues,
        )
        
        return analysis
    
    def _categorize_assessments(self, assessment_names: List[str]) -> Dict[str, int]:
        """Categorize assessments and count by category."""
        categories = defaultdict(int)
        
        for name in assessment_names:
            name_lower = name.lower()
            
            for category, keywords in self.category_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in name_lower:
                        categories[category] += 1
                        break
        
        return dict(categories)
    
    def _identify_primary_issue(self,
                                missing: Set[str],
                                expected_categories: Dict[str, int],
                                trace_name: str) -> str:
        """Identify the primary issue causing low recall."""
        if not missing:
            return "None - all expected assessments recommended"
        
        if not expected_categories:
            return f"No expected assessments found in catalog (possible catalog gap)"
        
        if len(missing) > len(expected_categories) * 0.5:
            # Missing more than half of expected
            dominant_category = max(expected_categories.items(), key=lambda x: x[1])[0]
            return f"Systematic miss on {dominant_category} assessments"
        
        # Check if missing specific role patterns
        trace_lower = trace_name.lower()
        if 'c1' in trace_lower or 'leadership' in trace_lower:
            if 'opq' in ' '.join(missing).lower():
                return "Missing OPQ leadership battery"
        elif 'c2' in trace_lower or 'engineer' in trace_lower:
            if 'smart interview' in ' '.join(missing).lower():
                return "Missing Smart Interview coding assessment"
        elif 'c3' in trace_lower or 'contact' in trace_lower:
            if 'svar' in ' '.join(missing).lower():
                return "Missing SVAR language assessment"
        elif 'c4' in trace_lower or 'finance' in trace_lower:
            if 'verify' in ' '.join(missing).lower():
                return "Missing Verify cognitive assessments"
        
        # Generic issue
        return f"Missing {len(missing)}/{len(missing) + len(expected_categories)} expected assessments"
    
    def _identify_secondary_issues(self,
                                    recommended_set: Set[str],
                                    expected_set: Set[str],
                                    recommended_categories: Dict[str, int],
                                    expected_categories: Dict[str, int]) -> List[str]:
        """Identify secondary issues affecting ranking/diversity."""
        issues = []
        
        # Check category imbalance
        total_rec_categories = sum(recommended_categories.values())
        for category, expected_count in expected_categories.items():
            rec_count = recommended_categories.get(category, 0)
            if expected_count > 0 and rec_count == 0:
                issues.append(f"No {category} assessments (expected {expected_count})")
        
        # Check for category over-representation
        for category, rec_count in recommended_categories.items():
            expected_count = expected_categories.get(category, 0)
            if expected_count < rec_count and rec_count > 3:
                issues.append(f"Over-represented {category} ({rec_count} vs {expected_count} expected)")
        
        return issues[:3]  # Top 3 secondary issues
    
    def _calculate_recommendation_ranks(self,
                                        recommended_names: List[str],
                                        correct_names: List[str]) -> Tuple[float, int]:
        """Calculate average and max rank of correct assessments."""
        if not correct_names:
            return 0.0, 0
        
        correct_lower = set(name.lower() for name in correct_names)
        ranks = []
        
        for i, name in enumerate(recommended_names, 1):
            if name.lower() in correct_lower:
                ranks.append(i)
        
        if not ranks:
            return 0.0, 0
        
        avg_rank = sum(ranks) / len(ranks)
        max_rank = max(ranks)
        
        return avg_rank, max_rank
    
    def generate_improvement_recommendations(self,
                                            analyses: List[TraceAnalysis]) -> Dict:
        """
        Generate improvement recommendations based on analyses.
        
        Args:
            analyses: List of TraceAnalysis objects
        
        Returns:
            Dictionary of improvement recommendations
        """
        recommendations = {
            'pattern_gaps': [],  # Role/scenario patterns not recognized
            'retrieval_gaps': [],  # Assessments in catalog but not retrieved
            'ranking_issues': [],  # Retrieved but ranked poorly
            'category_gaps': [],  # Missing assessment categories
            'hidden_trace_risks': [],  # Patterns that might fail on hidden traces
        }
        
        # Analyze patterns across traces
        low_recall_traces = [a for a in analyses if a.recall_at_10 < 0.5]
        zero_recall_traces = [a for a in analyses if a.recall_at_10 == 0.0]
        
        # Pattern gaps
        if zero_recall_traces:
            gap_traces = ', '.join(a.trace_name for a in zero_recall_traces)
            recommendations['pattern_gaps'].append(
                f"Traces {gap_traces} have 0% recall - likely catalog gaps or " +
                "role not recognized"
            )
        
        # Missing categories across traces
        category_gaps = defaultdict(int)
        for analysis in analyses:
            for category in analysis.expected_categories:
                if category not in analysis.category_distribution:
                    category_gaps[category] += 1
        
        for category, count in sorted(category_gaps.items(), key=lambda x: x[1], reverse=True)[:3]:
            recommendations['category_gaps'].append(
                f"{category.capitalize()} assessments missing in {count}/{len(analyses)} traces"
            )
        
        # Ranking issues (correct assessments ranked poorly)
        high_rank_issues = [a for a in analyses if a.max_rank_of_correct > 8 and a.correct_recommendations > 0]
        if high_rank_issues:
            traces = ', '.join(a.trace_name for a in high_rank_issues)
            recommendations['ranking_issues'].append(
                f"Correct assessments ranked poorly (>8) in traces: {traces}"
            )
        
        # Hidden trace risks
        if len(zero_recall_traces) > 2:
            recommendations['hidden_trace_risks'].append(
                "Multiple traces with 0% recall suggest overfitting to known scenarios. " +
                "Risk of failure on hidden traces with similar patterns."
            )
        
        avg_recall = sum(a.recall_at_10 for a in analyses) / len(analyses)
        if avg_recall < 0.4:
            recommendations['hidden_trace_risks'].append(
                "Low average recall (< 40%) indicates core patterns not captured. " +
                "Focus on expanding role/scenario coverage."
            )
        
        return recommendations
    
    def export_analysis_report(self,
                               analyses: List[TraceAnalysis],
                               output_file: str = "evaluation_analysis.md"):
        """
        Export detailed analysis report as markdown.
        
        Args:
            analyses: List of TraceAnalysis objects
            output_file: Output file path
        """
        with open(output_file, 'w') as f:
            f.write("# SHL-Recommender Evaluation Analysis Report\n\n")
            
            # Summary statistics
            f.write("## Summary Statistics\n\n")
            total_traces = len(analyses)
            avg_recall = sum(a.recall_at_10 for a in analyses) / total_traces
            avg_precision = sum(a.precision for a in analyses) / total_traces
            zero_recall_count = sum(1 for a in analyses if a.recall_at_10 == 0)
            
            f.write(f"- **Total Traces:** {total_traces}\n")
            f.write(f"- **Average Recall@10:** {avg_recall:.1%}\n")
            f.write(f"- **Average Precision:** {avg_precision:.1%}\n")
            f.write(f"- **Zero Recall Traces:** {zero_recall_count}\n\n")
            
            # Per-trace analysis
            f.write("## Per-Trace Analysis\n\n")
            for analysis in sorted(analyses, key=lambda a: a.recall_at_10):
                f.write(f"### {analysis.trace_name}\n\n")
                f.write(f"- **Recall@10:** {analysis.recall_at_10:.1%}\n")
                f.write(f"- **Precision:** {analysis.precision:.1%}\n")
                f.write(f"- **Expected:** {analysis.total_expected}, **Recommended:** {analysis.total_recommended}, **Correct:** {analysis.correct_recommendations}\n")
                f.write(f"- **Primary Issue:** {analysis.primary_issue}\n")
                
                if analysis.secondary_issues:
                    f.write("- **Secondary Issues:**\n")
                    for issue in analysis.secondary_issues:
                        f.write(f"  - {issue}\n")
                
                if analysis.missing_assessments:
                    f.write(f"- **Missing ({len(analysis.missing_assessments)}):** {', '.join(analysis.missing_assessments[:3])}\n")
                
                f.write("\n")
            
            # Improvement recommendations
            f.write("## Improvement Recommendations\n\n")
            recommendations = self.generate_improvement_recommendations(analyses)
            
            for category, items in recommendations.items():
                if items:
                    f.write(f"### {category.replace('_', ' ').title()}\n\n")
                    for item in items:
                        f.write(f"- {item}\n")
                    f.write("\n")
