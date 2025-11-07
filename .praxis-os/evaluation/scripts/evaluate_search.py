"""
RAG Search Quality Evaluation

Measures search performance using standard IR metrics:
- NDCG@K (Normalized Discounted Cumulative Gain)
- MRR (Mean Reciprocal Rank)
- Precision@K
- Recall@K
- MAP (Mean Average Precision)

Usage:
    # Evaluate single method
    python evaluate_search.py --method hybrid
    
    # Compare multiple methods
    python evaluate_search.py --compare vector fts hybrid hybrid_rerank
    
    # Evaluate at different K values
    python evaluate_search.py --method hybrid --k 5
    
    # Output to custom directory
    python evaluate_search.py --compare vector hybrid --output ../results/

100% AI-authored via human orchestration.
"""

import argparse
import json
import logging
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Add ouroboros to path
# Path hierarchy: scripts/evaluate_search.py -> evaluation/ -> .praxis-os/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ouroboros.subsystems.rag.index_manager import IndexManager
from ouroboros.subsystems.rag.base import SearchResult
from ouroboros.config.loader import load_config

logger = logging.getLogger(__name__)


class SearchEvaluator:
    """Evaluates search quality using ground truth dataset."""
    
    def __init__(
        self,
        ground_truth_path: Path,
        index_manager: IndexManager
    ):
        """Initialize evaluator.
        
        Args:
            ground_truth_path: Path to queries.yaml with test queries
            index_manager: IndexManager instance for executing searches
        """
        self.ground_truth = self._load_ground_truth(ground_truth_path)
        self.index_manager = index_manager
        self.standards_index = index_manager.get_index("standards")
        
        if not self.standards_index:
            raise ValueError("StandardsIndex not available in IndexManager")
        
    def _load_ground_truth(self, path: Path) -> dict:
        """Load ground truth queries and expected results."""
        if not path.exists():
            raise FileNotFoundError(
                f"Ground truth file not found: {path}\n"
                f"Expected queries.yaml at this location."
            )
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'test_queries' not in data:
            raise ValueError("Ground truth file missing 'test_queries' section")
        
        logger.info(f"Loaded {len(data['test_queries'])} test queries")
        return data
    
    def evaluate(
        self,
        method: str = "hybrid",
        k: int = 10
    ) -> Dict[str, Any]:
        """Evaluate search quality using specified method.
        
        Args:
            method: Search method to evaluate:
                - "vector": Vector-only search
                - "fts": Full-text search only
                - "hybrid": Vector + FTS + RRF (no re-ranking)
                - "hybrid_rerank": Full hybrid with cross-encoder re-ranking
            k: Number of results to evaluate (default: 10)
            
        Returns:
            Dictionary containing:
            - method: Method name
            - k: K value used
            - timestamp: Evaluation timestamp
            - per_query_results: Results for each test query
            - aggregated_metrics: Overall metrics across all queries
        """
        logger.info(f"Evaluating method: {method} (k={k})")
        
        results = []
        
        for query_data in self.ground_truth['test_queries']:
            query_id = query_data['id']
            query_text = query_data['query']
            category = query_data.get('category', 'unknown')
            difficulty = query_data.get('difficulty', 'unknown')
            expected_docs = query_data['expected_docs']
            
            logger.debug(f"Evaluating query {query_id}: {query_text}")
            
            # Execute search
            try:
                search_results = self._search_with_method(
                    query_text,
                    method=method,
                    n=k
                )
            except Exception as e:
                logger.error(f"Search failed for query {query_id}: {e}")
                search_results = []
            
            # Calculate metrics for this query
            query_metrics = self._calculate_query_metrics(
                search_results,
                expected_docs,
                k=k
            )
            
            results.append({
                'query_id': query_id,
                'query': query_text,
                'category': category,
                'difficulty': difficulty,
                'method': method,
                'metrics': query_metrics,
                'top_5_results': [
                    {
                        'rank': i + 1,
                        'file_path': r.file_path if hasattr(r, 'file_path') else r.get('file_path', ''),
                        'relevance_score': float(r.relevance_score) if hasattr(r, 'relevance_score') else r.get('_distance', 0.0),
                    }
                    for i, r in enumerate(search_results[:5])
                ] if search_results else []
            })
        
        # Aggregate metrics across all queries
        aggregated = self._aggregate_metrics(results)
        
        logger.info(f"Evaluation complete: NDCG@{k}={aggregated['ndcg@k']:.3f}, MRR={aggregated['mrr']:.3f}")
        
        return {
            'method': method,
            'k': k,
            'timestamp': datetime.now().isoformat(),
            'num_queries': len(results),
            'per_query_results': results,
            'aggregated_metrics': aggregated
        }
    
    def _search_with_method(
        self,
        query: str,
        method: str,
        n: int
    ) -> List[Any]:
        """Execute search using specified method.
        
        Args:
            query: Search query text
            method: Search method (vector, fts, hybrid, hybrid_rerank)
            n: Number of results to return
            
        Returns:
            List of search results (SearchResult objects or dicts)
        """
        # Ensure embedding model is loaded for vector/hybrid methods
        if method in ("vector", "hybrid", "hybrid_rerank"):
            self.standards_index._ensure_embedding_model()
        
        if method == "vector":
            # Vector-only search
            # Note: Ouroboros _vector_search takes query_vector, not query text
            query_vector = self.standards_index._embedding_model.encode(query).tolist()
            return self.standards_index._vector_search(query_vector, where_clause=None, limit=n)
        
        elif method == "fts":
            # FTS-only search
            return self.standards_index._fts_search(query, where_clause=None, limit=n)
        
        elif method == "hybrid":
            # Hybrid (vector + FTS + RRF) but NO re-ranking
            query_vector = self.standards_index._embedding_model.encode(query).tolist()
            vec_results = self.standards_index._vector_search(query_vector, where_clause=None, limit=20)
            fts_results = self.standards_index._fts_search(query, where_clause=None, limit=20)
            fused = self.standards_index._reciprocal_rank_fusion(vec_results, fts_results)
            return fused[:n]
        
        elif method == "hybrid_rerank":
            # Full hybrid + cross-encoder re-ranking
            # Note: Ouroboros search() method takes n_results, not n
            return self.standards_index.search(query, n_results=n, filters=None)
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _calculate_query_metrics(
        self,
        search_results: List[Any],
        expected_docs: List[Dict],
        k: int
    ) -> Dict[str, float]:
        """Calculate IR metrics for a single query.
        
        Args:
            search_results: Actual search results returned by method
            expected_docs: Expected relevant documents with relevance ratings
            k: Number of results to evaluate
            
        Returns:
            Dictionary of metrics for this query
        """
        # Build relevance map: doc_path -> relevance (0-3)
        relevance_map = {
            doc['path']: doc['relevance']
            for doc in expected_docs
        }
        
        # Extract relevances at each rank
        relevances_at_k = []
        first_relevant_rank = None
        num_relevant_found = 0
        relevant_ranks = []
        
        for rank, result in enumerate(search_results[:k], start=1):
            # Extract file path (handle both SearchResult objects and dicts)
            if hasattr(result, 'file_path'):
                doc_path = result.file_path
            else:
                doc_path = result.get('file_path', '')
            
            # Normalize path (remove leading standards/ if present)
            if doc_path.startswith('standards/'):
                doc_path = doc_path[len('standards/'):]
            
            # Check relevance
            relevance = 0
            for expected_path, expected_rel in relevance_map.items():
                # Flexible matching (handles path variations)
                if expected_path in doc_path or doc_path in expected_path:
                    relevance = expected_rel
                    break
            
            relevances_at_k.append(relevance)
            
            if relevance > 0:
                num_relevant_found += 1
                relevant_ranks.append(rank)
                if first_relevant_rank is None:
                    first_relevant_rank = rank
        
        # Calculate NDCG@K
        ndcg = self._calculate_ndcg(relevances_at_k)
        
        # Calculate MRR (Mean Reciprocal Rank)
        mrr = 1.0 / first_relevant_rank if first_relevant_rank else 0.0
        
        # Calculate Precision@K
        precision = num_relevant_found / k if k > 0 else 0.0
        
        # Calculate Recall@K
        total_relevant = len(expected_docs)
        recall = num_relevant_found / total_relevant if total_relevant > 0 else 0.0
        
        # Calculate Average Precision (for MAP)
        ap = self._calculate_average_precision(relevances_at_k)
        
        return {
            'ndcg@k': ndcg,
            'mrr': mrr,
            'precision@k': precision,
            'recall@k': recall,
            'average_precision': ap,
            'num_relevant_found': num_relevant_found,
            'total_relevant': total_relevant,
            'first_relevant_rank': first_relevant_rank or 0,
            'relevant_ranks': relevant_ranks
        }
    
    def _calculate_ndcg(self, relevances: List[int]) -> float:
        """Calculate Normalized Discounted Cumulative Gain.
        
        NDCG measures ranking quality by comparing actual ranking to ideal.
        Higher is better (max 1.0 = perfect ranking).
        
        Args:
            relevances: List of relevance scores (0-3) at each rank position
            
        Returns:
            NDCG score (0.0 to 1.0)
        """
        if not relevances or sum(relevances) == 0:
            return 0.0
        
        # DCG: Discounted Cumulative Gain
        # Formula: Σ (rel_i / log₂(rank_i + 1))
        dcg = sum(
            rel / math.log2(rank + 1)
            for rank, rel in enumerate(relevances, start=1)
            if rel > 0
        )
        
        # IDCG: Ideal DCG (perfect ranking - all relevant docs first)
        ideal_relevances = sorted(relevances, reverse=True)
        idcg = sum(
            rel / math.log2(rank + 1)
            for rank, rel in enumerate(ideal_relevances, start=1)
            if rel > 0
        )
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _calculate_average_precision(self, relevances: List[int]) -> float:
        """Calculate Average Precision for a single query.
        
        AP measures precision at each relevant result position.
        Used to compute MAP (Mean Average Precision).
        
        Args:
            relevances: List of relevance scores at each rank
            
        Returns:
            Average Precision score (0.0 to 1.0)
        """
        if not relevances:
            return 0.0
        
        num_relevant = sum(1 for r in relevances if r > 0)
        if num_relevant == 0:
            return 0.0
        
        precision_sum = 0.0
        relevant_count = 0
        
        for rank, rel in enumerate(relevances, start=1):
            if rel > 0:
                relevant_count += 1
                precision_at_k = relevant_count / rank
                precision_sum += precision_at_k
        
        return precision_sum / num_relevant
    
    def _aggregate_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Aggregate per-query metrics into overall metrics.
        
        Args:
            results: List of per-query evaluation results
            
        Returns:
            Dictionary of aggregated metrics across all queries
        """
        if not results:
            return {}
        
        metrics = ['ndcg@k', 'mrr', 'precision@k', 'recall@k', 'average_precision']
        
        aggregated = {}
        for metric in metrics:
            values = [r['metrics'][metric] for r in results]
            aggregated[metric] = sum(values) / len(values) if values else 0.0
        
        # MAP (Mean Average Precision) is the mean of average_precision across queries
        aggregated['map'] = aggregated['average_precision']
        
        # Additional stats
        aggregated['num_queries'] = len(results)
        
        # Count queries with relevant result in top 3
        aggregated['top3_hit_rate'] = sum(
            1 for r in results
            if r['metrics']['first_relevant_rank'] > 0 and
               r['metrics']['first_relevant_rank'] <= 3
        ) / len(results)
        
        # Count queries with relevant result in top 5
        aggregated['top5_hit_rate'] = sum(
            1 for r in results
            if r['metrics']['first_relevant_rank'] > 0 and
               r['metrics']['first_relevant_rank'] <= 5
        ) / len(results)
        
        # Average rank of first relevant result (lower is better)
        first_ranks = [
            r['metrics']['first_relevant_rank']
            for r in results
            if r['metrics']['first_relevant_rank'] > 0
        ]
        aggregated['avg_first_relevant_rank'] = (
            sum(first_ranks) / len(first_ranks) if first_ranks else 0.0
        )
        
        # Breakdown by category
        categories = set(r['category'] for r in results)
        aggregated['by_category'] = {}
        for cat in categories:
            cat_results = [r for r in results if r['category'] == cat]
            if cat_results:
                aggregated['by_category'][cat] = {
                    'ndcg@k': sum(r['metrics']['ndcg@k'] for r in cat_results) / len(cat_results),
                    'mrr': sum(r['metrics']['mrr'] for r in cat_results) / len(cat_results),
                    'num_queries': len(cat_results)
                }
        
        # Breakdown by difficulty
        difficulties = set(r['difficulty'] for r in results)
        aggregated['by_difficulty'] = {}
        for diff in difficulties:
            diff_results = [r for r in results if r['difficulty'] == diff]
            if diff_results:
                aggregated['by_difficulty'][diff] = {
                    'ndcg@k': sum(r['metrics']['ndcg@k'] for r in diff_results) / len(diff_results),
                    'mrr': sum(r['metrics']['mrr'] for r in diff_results) / len(diff_results),
                    'num_queries': len(diff_results)
                }
        
        return aggregated


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate RAG search quality using ground truth dataset"
    )
    parser.add_argument(
        '--method',
        choices=['vector', 'fts', 'hybrid', 'hybrid_rerank'],
        default='hybrid',
        help="Search method to evaluate (default: hybrid)"
    )
    parser.add_argument(
        '--k',
        type=int,
        default=10,
        help="Number of results to evaluate (default: 10)"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help="Output directory for results (default: .praxis-os/evaluation/results)"
    )
    parser.add_argument(
        '--compare',
        nargs='+',
        metavar='METHOD',
        help="Compare multiple methods (e.g., --compare vector hybrid hybrid_rerank)"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Setup paths
    script_dir = Path(__file__).parent  # .praxis-os/evaluation/scripts
    eval_dir = script_dir.parent  # .praxis-os/evaluation
    base_dir = eval_dir.parent  # .praxis-os
    ground_truth_path = eval_dir / "ground_truth" / "queries.yaml"
    config_path = base_dir / "config" / "mcp.yaml"
    
    if args.output:
        output_dir = args.output
    else:
        output_dir = script_dir.parent / "results"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("RAG Search Quality Evaluation (Ouroboros)")
    logger.info("=" * 80)
    logger.info(f"Ground truth: {ground_truth_path}")
    logger.info(f"Config: {config_path}")
    logger.info(f"Output: {output_dir}")
    logger.info("")
    
    # Load configuration
    try:
        logger.info("Loading configuration...")
        # Skip path validation - we only need index configs for evaluation
        mcp_config = load_config(config_path=config_path, validate_paths=False)
        logger.info("✅ Configuration loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        sys.exit(1)
    
    # Initialize IndexManager
    try:
        logger.info("Initializing IndexManager...")
        index_manager = IndexManager(
            config=mcp_config.indexes,
            base_path=base_dir
        )
        
        # Check if standards index is healthy (only index needed for evaluation)
        standards_index = index_manager.get_index("standards")
        if not standards_index:
            logger.error("❌ Standards index not available")
            sys.exit(1)
        
        # Check health and rebuild if needed
        health_status = standards_index.health_check()
        if not health_status.healthy:
            logger.warning("Standards index not healthy, rebuilding...")
            try:
                index_manager.rebuild_index("standards")
                logger.info("✅ Standards index rebuilt")
            except Exception as e:
                logger.error(f"❌ Failed to rebuild standards index: {e}")
                sys.exit(1)
        
        logger.info("✅ IndexManager initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize IndexManager: {e}")
        sys.exit(1)
    
    # Initialize evaluator
    try:
        evaluator = SearchEvaluator(ground_truth_path, index_manager)
    except Exception as e:
        logger.error(f"❌ Failed to initialize evaluator: {e}")
        sys.exit(1)
    
    if args.compare:
        # Compare multiple methods
        logger.info(f"🔍 Comparing methods: {', '.join(args.compare)}")
        logger.info("=" * 80)
        logger.info("")
        
        comparison = {}
        for method in args.compare:
            logger.info(f"📊 Evaluating {method}...")
            logger.info("-" * 80)
            
            try:
                results = evaluator.evaluate(method=method, k=args.k)
                comparison[method] = results
                
                # Print summary
                metrics = results['aggregated_metrics']
                logger.info(f"Results for {method}:")
                logger.info(f"  NDCG@{args.k}: {metrics['ndcg@k']:.3f}")
                logger.info(f"  MRR: {metrics['mrr']:.3f}")
                logger.info(f"  Precision@{args.k}: {metrics['precision@k']:.3f}")
                logger.info(f"  Recall@{args.k}: {metrics['recall@k']:.3f}")
                logger.info(f"  MAP: {metrics['map']:.3f}")
                logger.info(f"  Top-3 Hit Rate: {metrics['top3_hit_rate']:.1%}")
                logger.info(f"  Avg First Rank: {metrics['avg_first_relevant_rank']:.2f}")
                logger.info("")
            
            except Exception as e:
                logger.error(f"❌ Evaluation failed for {method}: {e}")
                logger.error("", exc_info=True)
        
        # Save comparison
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"comparison_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info("=" * 80)
        logger.info(f"✅ Comparison saved to {output_file}")
        
        # Generate comparison report
        _generate_comparison_report(comparison, output_dir, args.k, timestamp)
        
    else:
        # Single method evaluation
        logger.info(f"📊 Evaluating method: {args.method}")
        logger.info("=" * 80)
        logger.info("")
        
        try:
            results = evaluator.evaluate(method=args.method, k=args.k)
            
            # Print results
            metrics = results['aggregated_metrics']
            logger.info("=" * 80)
            logger.info(f"✅ Results for {args.method}:")
            logger.info("-" * 80)
            logger.info(f"  NDCG@{args.k}: {metrics['ndcg@k']:.3f}")
            logger.info(f"  MRR: {metrics['mrr']:.3f}")
            logger.info(f"  Precision@{args.k}: {metrics['precision@k']:.3f}")
            logger.info(f"  Recall@{args.k}: {metrics['recall@k']:.3f}")
            logger.info(f"  MAP: {metrics['map']:.3f}")
            logger.info(f"  Top-3 Hit Rate: {metrics['top3_hit_rate']:.1%}")
            logger.info(f"  Top-5 Hit Rate: {metrics['top5_hit_rate']:.1%}")
            logger.info(f"  Avg First Relevant Rank: {metrics['avg_first_relevant_rank']:.2f}")
            logger.info("")
            
            # Category breakdown
            if metrics.get('by_category'):
                logger.info("By Category:")
                for cat, cat_metrics in metrics['by_category'].items():
                    logger.info(f"  {cat}: NDCG={cat_metrics['ndcg@k']:.3f}, "
                              f"MRR={cat_metrics['mrr']:.3f} "
                              f"({cat_metrics['num_queries']} queries)")
                logger.info("")
            
            # Difficulty breakdown
            if metrics.get('by_difficulty'):
                logger.info("By Difficulty:")
                for diff, diff_metrics in metrics['by_difficulty'].items():
                    logger.info(f"  {diff}: NDCG={diff_metrics['ndcg@k']:.3f}, "
                              f"MRR={diff_metrics['mrr']:.3f} "
                              f"({diff_metrics['num_queries']} queries)")
            
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f"{args.method}_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"✅ Results saved to {output_file}")
        
        except Exception as e:
            logger.error(f"❌ Evaluation failed: {e}")
            logger.error("", exc_info=True)
            sys.exit(1)


def _generate_comparison_report(
    comparison: Dict,
    output_dir: Path,
    k: int,
    timestamp: str
):
    """Generate markdown comparison report."""
    report = ["# RAG Search Methods Comparison", ""]
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Evaluation K:** {k}")
    report.append(f"**Number of Test Queries:** {list(comparison.values())[0]['num_queries']}")
    report.append("")
    
    # Summary table
    report.append("## Overall Performance")
    report.append("")
    report.append("| Method | NDCG@10 | MRR | Precision@10 | Recall@10 | MAP | Top-3 Hit % |")
    report.append("|--------|---------|-----|--------------|-----------|-----|-------------|")
    
    for method, results in comparison.items():
        metrics = results['aggregated_metrics']
        report.append(
            f"| **{method}** | "
            f"{metrics['ndcg@k']:.3f} | "
            f"{metrics['mrr']:.3f} | "
            f"{metrics['precision@k']:.3f} | "
            f"{metrics['recall@k']:.3f} | "
            f"{metrics['map']:.3f} | "
            f"{metrics['top3_hit_rate']:.1%} |"
        )
    
    # Calculate improvements
    if 'vector' in comparison and len(comparison) > 1:
        report.append("")
        report.append("## Improvements Over Vector-Only Baseline")
        report.append("")
        baseline = comparison['vector']['aggregated_metrics']
        
        for method, results in comparison.items():
            if method == 'vector':
                continue
            metrics = results['aggregated_metrics']
            ndcg_improvement = ((metrics['ndcg@k'] - baseline['ndcg@k']) / baseline['ndcg@k'] * 100)
            mrr_improvement = ((metrics['mrr'] - baseline['mrr']) / baseline['mrr'] * 100)
            
            report.append(f"### {method}")
            report.append(f"- NDCG improvement: **{ndcg_improvement:+.1f}%**")
            report.append(f"- MRR improvement: **{mrr_improvement:+.1f}%**")
            report.append("")
    
    report.append("## Metric Definitions")
    report.append("")
    report.append("- **NDCG@10**: Normalized Discounted Cumulative Gain - measures ranking quality (0.0-1.0, higher is better)")
    report.append("- **MRR**: Mean Reciprocal Rank - measures how quickly first relevant result appears (0.0-1.0, higher is better)")
    report.append("- **Precision@10**: Proportion of returned results that are relevant (0.0-1.0, higher is better)")
    report.append("- **Recall@10**: Proportion of relevant documents found in top 10 (0.0-1.0, higher is better)")
    report.append("- **MAP**: Mean Average Precision - overall precision across all ranks (0.0-1.0, higher is better)")
    report.append("- **Top-3 Hit %**: Percentage of queries with relevant result in top 3 positions")
    report.append("")
    
    report.append("## Interpretation")
    report.append("")
    report.append("**NDCG Score Translation:**")
    report.append("- 0.90-1.00: Excellent (near-perfect ranking)")
    report.append("- 0.80-0.90: Very Good (relevant results consistently in top positions)")
    report.append("- 0.70-0.80: Good (mostly relevant results, some misordering)")
    report.append("- 0.60-0.70: Fair (relevant results found but poorly ordered)")
    report.append("- <0.60: Needs improvement")
    report.append("")
    
    # Breakdown by category (if available)
    first_result = list(comparison.values())[0]
    if 'by_category' in first_result['aggregated_metrics']:
        report.append("## Performance by Category")
        report.append("")
        
        # Get all categories
        all_categories = set()
        for results in comparison.values():
            all_categories.update(results['aggregated_metrics']['by_category'].keys())
        
        for category in sorted(all_categories):
            report.append(f"### {category}")
            report.append("")
            report.append("| Method | NDCG@10 | MRR |")
            report.append("|--------|---------|-----|")
            
            for method, results in comparison.items():
                cat_metrics = results['aggregated_metrics']['by_category'].get(category)
                if cat_metrics:
                    report.append(
                        f"| {method} | {cat_metrics['ndcg@k']:.3f} | {cat_metrics['mrr']:.3f} |"
                    )
            report.append("")
    
    # Save report
    report_file = output_dir / f"comparison_report_{timestamp}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    logger.info(f"📄 Comparison report saved to {report_file}")


if __name__ == "__main__":
    main()

