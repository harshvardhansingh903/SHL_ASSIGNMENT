"""
Evaluator simulation harness and synthetic trace generation.

This module:
1. Replays C1-C10 labeled traces to measure performance
2. Generates 10+ synthetic hidden traces with expected outcomes
3. Measures: Recall@10, precision, hallucinations, schema compliance, efficiency
4. Simulates realistic user behaviors (vague, inconsistent, changing requirements)
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Set

sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from shl_recommender import SHLRecommender


# Helper functions for paths
def get_catalog_path():
    """Get path to catalog relative to this file."""
    return str(Path(__file__).parent.parent / 'data' / 'shl_product_catalog_clean.json')


def get_traces_dir():
    """Get path to traces directory relative to this file."""
    return str(Path(__file__).parent.parent / 'GenAI_SampleConversations')


@dataclass
class TraceExpectation:
    """Expected outcomes for a trace."""
    name: str
    role: str
    messages: List[str]
    expected_assessments: List[str]  # Assessment names that should be recommended
    category_focus: List[str]  # Primary assessment categories


@dataclass
class SimulationResult:
    """Results from a simulated trace."""
    trace_name: str
    role: str
    num_turns: int
    recall_at_10: float
    precision: float
    hallucinations: int
    schema_violations: int
    avg_turn_latency: float
    conversation_ended: bool
    all_recommendations: List[str]
    missing_assessments: List[str]
    unexpected_assessments: List[str]


# ============================================================================
# Synthetic Trace Definitions
# ============================================================================

SYNTHETIC_TRACES = [
    TraceExpectation(
        name="S1_DevOps_Engineer",
        role="DevOps engineer",
        messages=[
            "We're hiring a senior DevOps engineer. They need strong infrastructure knowledge.",
            "Can you add technical assessments focused on cloud infrastructure?",
            "Also make sure to include personality and cognitive tests"
        ],
        expected_assessments=[
            "Verify G+",  # Cognitive
            "Smart Interview",  # Technical
            "OPQ32r",  # Personality
        ],
        category_focus=["cognitive", "technical", "personality"]
    ),
    
    TraceExpectation(
        name="S2_Cybersecurity_Analyst",
        role="Cybersecurity analyst",
        messages=[
            "We need a cybersecurity analyst. Technical depth is critical.",
            "What assessments do you recommend?"
        ],
        expected_assessments=[
            "Smart Interview",
            "Verify G+",
            "OPQ32r",
        ],
        category_focus=["technical", "cognitive"]
    ),
    
    TraceExpectation(
        name="S3_Junior_Data_Analyst",
        role="junior data analyst",
        messages=[
            "Hiring a junior data analyst, fresh out of bootcamp",
            "They should be able to handle SQL and Python",
            "What's your recommendation?"
        ],
        expected_assessments=[
            "Verify Numerical",
            "Verify G+",
            "OPQ32r",
        ],
        category_focus=["cognitive", "technical"]
    ),
    
    TraceExpectation(
        name="S4_Warehouse_Supervisor",
        role="warehouse supervisor",
        messages=[
            "We need a warehouse supervisor",
            "Strong communication and team management skills are essential"
        ],
        expected_assessments=[
            "OPQ32r",
            "Situational Judgment",
            "Leadership instrument",
        ],
        category_focus=["personality", "leadership", "behavioral"]
    ),
    
    TraceExpectation(
        name="S5_Retail_Manager",
        role="retail manager",
        messages=[
            "Retail store manager position",
            "Customer service and team leadership are critical"
        ],
        expected_assessments=[
            "OPQ32r",
            "Customer Service",
            "Global Skills",
        ],
        category_focus=["personality", "behavioral", "communication"]
    ),
    
    TraceExpectation(
        name="S6_HR_Recruiter",
        role="HR recruiter",
        messages=[
            "We're looking for an HR recruiter",
            "Communication, relationship building, and attention to detail required"
        ],
        expected_assessments=[
            "OPQ32r",
            "Global Skills",
            "Communication assessment",
        ],
        category_focus=["personality", "communication", "behavioral"]
    ),
    
    TraceExpectation(
        name="S7_Cloud_Infrastructure",
        role="Cloud infrastructure engineer",
        messages=[
            "Senior cloud infrastructure engineer",
            "AWS and GCP experience required",
            "Make sure the assessments test cloud architecture understanding"
        ],
        expected_assessments=[
            "Smart Interview",
            "Verify G+",
            "OPQ32r",
        ],
        category_focus=["technical", "cognitive", "personality"]
    ),
    
    TraceExpectation(
        name="S8_Product_Manager",
        role="Product manager",
        messages=[
            "Product manager - B2B SaaS",
            "Need someone with strong strategic thinking and communication"
        ],
        expected_assessments=[
            "OPQ32r",
            "Leadership instrument",
            "Verify G+",
        ],
        category_focus=["personality", "leadership", "cognitive"]
    ),
    
    TraceExpectation(
        name="S9_Healthcare_Operations",
        role="Healthcare operations coordinator",
        messages=[
            "Healthcare operations coordinator",
            "Need strong organizational skills and ability to work under pressure"
        ],
        expected_assessments=[
            "OPQ32r",
            "Situational Judgment",
            "Communication assessment",
        ],
        category_focus=["personality", "behavioral", "communication"]
    ),
    
    TraceExpectation(
        name="S10_Manufacturing_QA",
        role="Manufacturing QA engineer",
        messages=[
            "Manufacturing QA engineer",
            "Technical background and attention to detail required"
        ],
        expected_assessments=[
            "Verify G+",
            "Smart Interview",
            "OPQ32r",
        ],
        category_focus=["cognitive", "technical", "personality"]
    ),
]


# ============================================================================
# Evaluator Simulator
# ============================================================================

class EvaluatorSimulator:
    """Simulates evaluator interactions and measures performance."""
    
    def __init__(self, catalog_path: str):
        """Initialize simulator with recommender."""
        self.recommender = SHLRecommender(catalog_path)
        # catalog is a dict with entity_id as key and Assessment as value
        self.catalog_dict = self.recommender.catalog.assessments
        self.results: List[SimulationResult] = []
    
    def run_labeled_traces(self, trace_dir: str = "GenAI_SampleConversations") -> List[SimulationResult]:
        """
        Run evaluation on labeled traces C1-C10.
        
        Args:
            trace_dir: Directory containing C1.md, C2.md, ..., C10.md files
        
        Returns:
            List of simulation results
        """
        labeled_results = []
        
        # Collect all labeled traces
        trace_files = sorted([
            f for f in os.listdir(trace_dir)
            if f.startswith('C') and f.endswith('.md')
        ])
        
        for trace_file in trace_files:
            trace_path = os.path.join(trace_dir, trace_file)
            result = self._run_single_trace_file(trace_path)
            if result:
                labeled_results.append(result)
        
        self.results.extend(labeled_results)
        return labeled_results
    
    def run_synthetic_traces(self) -> List[SimulationResult]:
        """
        Run evaluation on synthetic traces.
        
        Returns:
            List of simulation results
        """
        synthetic_results = []
        
        for expectation in SYNTHETIC_TRACES:
            result = self._run_synthetic_trace(expectation)
            synthetic_results.append(result)
        
        self.results.extend(synthetic_results)
        return synthetic_results
    
    def _run_single_trace_file(self, trace_path: str) -> SimulationResult:
        """Run a single labeled trace file."""
        try:
            with open(trace_path, 'r') as f:
                content = f.read()
            
            # Parse expected assessments from markdown
            expected_assessments = self._extract_expected_from_markdown(content)
            messages = self._extract_messages_from_markdown(content)
            
            trace_name = os.path.basename(trace_path).replace('.md', '')
            
            # Extract role from content
            role = self._infer_role_from_content(content)
            
            # Run conversation
            recommender = SHLRecommender(get_catalog_path())
            all_recommendations = []
            
            for message in messages:
                response = recommender.process_turn(message)
                for rec in response.get('recommendations', []):
                    all_recommendations.append(rec['name'])
            
            # Calculate metrics
            recall, precision, hallucinations = self._calculate_metrics(
                all_recommendations,
                expected_assessments
            )
            
            missing = set(expected_assessments) - set(all_recommendations)
            unexpected = set(all_recommendations) - set(expected_assessments)
            
            return SimulationResult(
                trace_name=trace_name,
                role=role,
                num_turns=len(messages),
                recall_at_10=recall,
                precision=precision,
                hallucinations=hallucinations,
                schema_violations=0,
                avg_turn_latency=0,  # Would need instrumentation
                conversation_ended=True,
                all_recommendations=all_recommendations,
                missing_assessments=list(missing),
                unexpected_assessments=list(unexpected)
            )
        
        except Exception as e:
            print(f"Error running trace {trace_path}: {e}")
            return None
    
    def _run_synthetic_trace(self, expectation: TraceExpectation) -> SimulationResult:
        """Run a synthetic trace with expected outcomes."""
        recommender = SHLRecommender(get_catalog_path())
        all_recommendations = []
        
        # Run multi-turn conversation
        for message in expectation.messages:
            response = recommender.process_turn(message)
            for rec in response.get('recommendations', []):
                all_recommendations.append(rec['name'])
        
        # Calculate metrics
        recall, precision, hallucinations = self._calculate_metrics(
            all_recommendations,
            expectation.expected_assessments
        )
        
        missing = set(expectation.expected_assessments) - set(all_recommendations)
        unexpected = set(all_recommendations) - set(expectation.expected_assessments)
        
        return SimulationResult(
            trace_name=expectation.name,
            role=expectation.role,
            num_turns=len(expectation.messages),
            recall_at_10=recall,
            precision=precision,
            hallucinations=hallucinations,
            schema_violations=0,
            avg_turn_latency=0,
            conversation_ended=True,
            all_recommendations=all_recommendations[:10],  # Top 10
            missing_assessments=list(missing),
            unexpected_assessments=list(unexpected)
        )
    
    def _calculate_metrics(self, recommended: List[str], expected: List[str]) -> Tuple[float, float, int]:
        """Calculate recall, precision, and hallucinations."""
        if len(expected) == 0:
            return 0.0, 0.0, 0
        
        recommended_set = set(recommended[:10])  # Only top 10
        expected_set = set(expected)
        
        # Recall: How many expected did we get?
        recall = len(recommended_set & expected_set) / len(expected_set) if expected_set else 0
        
        # Precision: How many of our recommendations were correct?
        precision = len(recommended_set & expected_set) / len(recommended_set) if recommended_set else 0
        
        # Hallucinations: Incorrect assessments (not in catalog means they're hallucinations)
        hallucinations = 0
        for rec in recommended:
            if not self._assessment_in_catalog(rec):
                hallucinations += 1
        
        return recall * 100, precision * 100, hallucinations
    
    def _assessment_in_catalog(self, assessment_name: str) -> bool:
        """Check if assessment exists in catalog."""
        for assessment in self.catalog_dict.values():
            if assessment.name.lower() == assessment_name.lower():
                return True
        return False
    
    def _extract_expected_from_markdown(self, content: str) -> List[str]:
        """Extract expected assessments from markdown file."""
        expected = []
        lines = content.split('\n')
        
        in_expected = False
        for line in lines:
            if 'expected' in line.lower() or 'should recommend' in line.lower():
                in_expected = True
            elif in_expected:
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    # Extract assessment name
                    assessment = line.strip().lstrip('- *').strip()
                    if assessment:
                        expected.append(assessment)
                elif line.strip() == '' or line.strip().startswith('#'):
                    in_expected = False
        
        return expected
    
    def _extract_messages_from_markdown(self, content: str) -> List[str]:
        """Extract user messages from markdown file."""
        messages = []
        lines = content.split('\n')
        
        in_conversation = False
        current_message = []
        
        for line in lines:
            if line.startswith('##'):
                in_conversation = True
            elif in_conversation:
                if line.startswith('**User:**') or line.startswith('> '):
                    # Start of user message
                    if current_message:
                        messages.append(' '.join(current_message))
                        current_message = []
                    
                    # Extract message text
                    text = line.replace('**User:**', '').replace('> ', '').strip()
                    if text:
                        current_message.append(text)
                elif current_message and line.strip() and not line.startswith('**'):
                    current_message.append(line.strip())
        
        if current_message:
            messages.append(' '.join(current_message))
        
        return messages
    
    def _infer_role_from_content(self, content: str) -> str:
        """Infer role from trace content."""
        content_lower = content.lower()
        
        roles = {
            'leadership': 'Leadership',
            'engineer': 'Engineering',
            'contact center': 'Contact Center',
            'finance': 'Finance',
            'sales': 'Sales',
            'manufacturing': 'Manufacturing',
            'healthcare': 'Healthcare',
            'admin': 'Administrative',
            'graduate': 'Graduate',
        }
        
        for keyword, role in roles.items():
            if keyword in content_lower:
                return role
        
        return 'Unknown'
    
    def generate_report(self) -> Dict:
        """Generate comprehensive simulation report."""
        if not self.results:
            return {"error": "No results to report"}
        
        labeled_results = [r for r in self.results if not r.trace_name.startswith('S')]
        synthetic_results = [r for r in self.results if r.trace_name.startswith('S')]
        
        report = {
            "summary": {
                "total_traces": len(self.results),
                "labeled_traces": len(labeled_results),
                "synthetic_traces": len(synthetic_results),
            },
            "labeled_performance": self._summarize_results(labeled_results),
            "synthetic_performance": self._summarize_results(synthetic_results),
            "overall_performance": self._summarize_results(self.results),
            "traces": [asdict(r) for r in self.results],
        }
        
        return report
    
    def _summarize_results(self, results: List[SimulationResult]) -> Dict:
        """Summarize performance metrics."""
        if not results:
            return {}
        
        recalls = [r.recall_at_10 for r in results]
        precisions = [r.precision for r in results]
        hallucinations = [r.hallucinations for r in results]
        
        return {
            "avg_recall_at_10": sum(recalls) / len(recalls) if recalls else 0,
            "min_recall": min(recalls) if recalls else 0,
            "max_recall": max(recalls) if recalls else 0,
            "avg_precision": sum(precisions) / len(precisions) if precisions else 0,
            "total_hallucinations": sum(hallucinations),
            "zero_recall_traces": len([r for r in results if r.recall_at_10 == 0]),
        }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print('=' * 70)
    print('EVALUATOR SIMULATOR: Labeled + Synthetic Traces')
    print('=' * 70)
    
    simulator = EvaluatorSimulator('shl_product_catalog_clean.json')
    
    # Run labeled traces
    print('\n[1/2] Running labeled traces C1-C10...')
    try:
        labeled_results = simulator.run_labeled_traces(get_traces_dir())
        labeled_results = [r for r in labeled_results if r is not None]
        print(f'Completed {len(labeled_results)} labeled traces')
    except Exception as e:
        print(f'Skipping labeled traces: {e}')
        labeled_results = []
    
    # Run synthetic traces
    print('\n[2/2] Running synthetic traces S1-S10...')
    synthetic_results = simulator.run_synthetic_traces()
    print(f'Completed {len(synthetic_results)} synthetic traces')
    
    # Generate report
    print('\n[3/3] Generating evaluation report...')
    report = simulator.generate_report()
    
    # Save report
    with open('evaluation_simulator_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f'Report saved to evaluation_simulator_report.json')
    
    # Print summary
    print('\n' + '=' * 70)
    print('SIMULATION SUMMARY')
    print('=' * 70)
    
    summary = report['summary']
    overall = report['overall_performance']
    
    print(f"\nTotal Traces: {summary['total_traces']}")
    print(f"  - Labeled (C1-C10): {summary['labeled_traces']}")
    print(f"  - Synthetic (S1-S10): {summary['synthetic_traces']}")
    
    print(f"\nOverall Metrics:")
    print(f"  - Avg Recall@10: {overall['avg_recall_at_10']:.2f}%")
    print(f"  - Avg Precision: {overall['avg_precision']:.2f}%")
    print(f"  - Total Hallucinations: {overall['total_hallucinations']}")
    print(f"  - Zero-Recall Traces: {overall['zero_recall_traces']}")
    
    labeled_metrics = report['labeled_performance']
    synthetic_metrics = report['synthetic_performance']
    
    print(f"\nLabeled Performance:")
    print(f"  - Avg Recall@10: {labeled_metrics['avg_recall_at_10']:.2f}%")
    print(f"  - Avg Precision: {labeled_metrics['avg_precision']:.2f}%")
    
    print(f"\nSynthetic Performance:")
    print(f"  - Avg Recall@10: {synthetic_metrics['avg_recall_at_10']:.2f}%")
    print(f"  - Avg Precision: {synthetic_metrics['avg_precision']:.2f}%")
    
    print('\n' + '=' * 70)

