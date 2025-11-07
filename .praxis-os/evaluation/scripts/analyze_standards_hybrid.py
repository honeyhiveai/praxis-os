"""
Analyze all standards against hybrid search optimization requirements.

Checks:
1. Has "Questions This Answers" section (CRITICAL for FTS)
2. Has TL;DR/Quick Reference section (front-loading)
3. Header quality (specific combinations vs broad terms)
4. Keyword density patterns
5. Query hooks present
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Broad single-keyword headers that fail with FTS
BROAD_KEYWORDS = [
    'usage', 'examples', 'notes', 'overview', 'introduction',
    'testing', 'operations', 'configuration', 'setup', 'installation',
    'description', 'implementation', 'background', 'details',
    'guide', 'reference', 'documentation', 'patterns', 'principles'
]

def analyze_standard(file_path: Path) -> Dict:
    """Analyze a single standard file for hybrid search compliance."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract headers
    headers = re.findall(r'^##+ (.+)$', content, re.MULTILINE)
    
    # Check for required sections
    has_questions_section = bool(re.search(
        r'##.*Questions.*This.*Answers', content, re.IGNORECASE
    ))
    
    has_tldr_section = bool(re.search(
        r'##.*(Quick Reference|TL;?DR|Summary)', content, re.IGNORECASE
    ))
    
    # Analyze headers
    broad_headers = []
    good_headers = []
    
    for header in headers:
        header_lower = header.lower().strip()
        # Remove common prefixes
        clean_header = re.sub(r'^(what|how|when|why|where)\s+(is|are|do|does)\s+', '', header_lower)
        
        words = clean_header.split()
        
        # Check if it's a broad single keyword
        if len(words) <= 2:
            # Check if first word is broad
            first_word = words[0] if words else ''
            if any(broad in first_word for broad in BROAD_KEYWORDS):
                broad_headers.append(header)
            elif len(words) == 1:
                broad_headers.append(header)
        else:
            # Multi-word headers are generally good
            good_headers.append(header)
    
    # Check for keyword stuffing patterns
    keyword_stuffing = []
    for line in content.split('\n'):
        # Look for repeated words in titles/headers
        if line.startswith('#'):
            words = re.findall(r'\b\w+\b', line.lower())
            word_counts = defaultdict(int)
            for word in words:
                if len(word) > 4:  # Only check meaningful words
                    word_counts[word] += 1
            
            for word, count in word_counts.items():
                if count >= 3:  # Same word 3+ times in header
                    keyword_stuffing.append(f"{line.strip()} ('{word}' x{count})")
    
    # Check for query hooks
    has_query_hooks = bool(re.search(
        r'(When to (use|query|search)|Common (questions|queries|scenarios)|How to)',
        content,
        re.IGNORECASE
    ))
    
    # Count total headers
    total_headers = len(headers)
    
    # Calculate compliance score
    issues = []
    score = 100
    
    if not has_questions_section:
        issues.append("Missing 'Questions This Answers' section (CRITICAL)")
        score -= 30
    
    if not has_tldr_section:
        issues.append("Missing TL;DR/Quick Reference section")
        score -= 20
    
    if broad_headers:
        broad_ratio = len(broad_headers) / max(total_headers, 1)
        if broad_ratio > 0.5:
            issues.append(f"Many broad headers ({len(broad_headers)}/{total_headers})")
            score -= 25
        elif broad_ratio > 0.25:
            issues.append(f"Some broad headers ({len(broad_headers)}/{total_headers})")
            score -= 15
    
    if keyword_stuffing:
        issues.append(f"Keyword stuffing detected ({len(keyword_stuffing)} instances)")
        score -= 15
    
    if not has_query_hooks:
        issues.append("Few/no query hooks found")
        score -= 10
    
    # Determine severity
    if score >= 80:
        severity = "GOOD"
    elif score >= 60:
        severity = "MEDIUM"
    else:
        severity = "NEEDS_WORK"
    
    return {
        'file': str(file_path.relative_to(file_path.parents[2])),
        'total_headers': total_headers,
        'broad_headers': len(broad_headers),
        'broad_header_list': broad_headers[:5],  # First 5
        'has_questions_section': has_questions_section,
        'has_tldr': has_tldr_section,
        'has_query_hooks': has_query_hooks,
        'keyword_stuffing': keyword_stuffing,
        'issues': issues,
        'score': score,
        'severity': severity
    }


def main():
    """Analyze all standards."""
    base_path = Path('/Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os')
    standards_dir = base_path / 'standards'
    
    # Find all markdown files
    md_files = list(standards_dir.rglob('*.md'))
    
    print(f"Analyzing {len(md_files)} standards files...\n")
    
    results = []
    for file_path in sorted(md_files):
        result = analyze_standard(file_path)
        results.append(result)
    
    # Categorize by severity
    by_severity = defaultdict(list)
    for r in results:
        by_severity[r['severity']].append(r)
    
    # Summary statistics
    print("=" * 80)
    print("HYBRID SEARCH COMPLIANCE ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Standards: {len(results)}")
    print(f"  ✅ GOOD (80-100):     {len(by_severity['GOOD']):3d} ({len(by_severity['GOOD'])/len(results)*100:.1f}%)")
    print(f"  ⚠️  MEDIUM (60-79):   {len(by_severity['MEDIUM']):3d} ({len(by_severity['MEDIUM'])/len(results)*100:.1f}%)")
    print(f"  ❌ NEEDS_WORK (<60): {len(by_severity['NEEDS_WORK']):3d} ({len(by_severity['NEEDS_WORK'])/len(results)*100:.1f}%)")
    
    # Key findings
    missing_questions = sum(1 for r in results if not r['has_questions_section'])
    missing_tldr = sum(1 for r in results if not r['has_tldr'])
    has_broad_headers = sum(1 for r in results if r['broad_headers'] > 0)
    has_stuffing = sum(1 for r in results if r['keyword_stuffing'])
    
    print("\n" + "=" * 80)
    print("KEY ISSUES SUMMARY")
    print("=" * 80)
    print(f"Missing 'Questions This Answers': {missing_questions:3d} ({missing_questions/len(results)*100:.1f}%)")
    print(f"Missing TL;DR/Quick Reference:    {missing_tldr:3d} ({missing_tldr/len(results)*100:.1f}%)")
    print(f"Has broad single-keyword headers: {has_broad_headers:3d} ({has_broad_headers/len(results)*100:.1f}%)")
    print(f"Keyword stuffing detected:        {has_stuffing:3d} ({has_stuffing/len(results)*100:.1f}%)")
    
    # Show worst offenders
    worst = sorted(results, key=lambda x: x['score'])[:10]
    
    print("\n" + "=" * 80)
    print("TOP 10 FILES NEEDING WORK (Lowest Scores)")
    print("=" * 80)
    for i, r in enumerate(worst, 1):
        print(f"\n{i}. {r['file']}")
        print(f"   Score: {r['score']}/100")
        print(f"   Issues:")
        for issue in r['issues']:
            print(f"     - {issue}")
    
    # Show examples of broad headers
    print("\n" + "=" * 80)
    print("EXAMPLES OF BROAD HEADERS (Need specific combinations)")
    print("=" * 80)
    broad_examples = []
    for r in results:
        if r['broad_header_list']:
            for header in r['broad_header_list'][:2]:
                broad_examples.append((r['file'], header))
    
    for file, header in broad_examples[:15]:
        print(f"  ❌ '{header}'")
        print(f"     in {file}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print(f"\n1. CRITICAL (affects {missing_questions} files):")
    print("   Add 'Questions This Answers' section with 3-5 natural queries")
    print(f"\n2. HIGH (affects {missing_tldr} files):")
    print("   Add TL;DR/Quick Reference section at top with keyword diversity")
    print(f"\n3. MEDIUM (affects {has_broad_headers} files):")
    print("   Replace broad headers like 'Usage' with specific combinations")
    print("   Example: 'Usage' → 'How to Execute Specifications (Usage)'")
    print(f"\n4. LOW (affects {has_stuffing} files):")
    print("   Remove keyword stuffing, use natural diversity instead")
    
    # Effort estimate
    avg_issues_per_file = sum(len(r['issues']) for r in results) / len(results)
    
    print("\n" + "=" * 80)
    print("EFFORT ESTIMATE")
    print("=" * 80)
    print(f"Files needing work: {len(by_severity['MEDIUM']) + len(by_severity['NEEDS_WORK'])}")
    print(f"Average issues per file: {avg_issues_per_file:.1f}")
    print(f"\nEstimated time per file:")
    print(f"  - Add Questions section: 5-10 minutes")
    print(f"  - Add TL;DR section: 5-10 minutes")
    print(f"  - Fix broad headers: 2-5 minutes")
    print(f"  - Total per file: ~15-25 minutes")
    print(f"\nTotal estimated effort:")
    files_to_fix = len(by_severity['MEDIUM']) + len(by_severity['NEEDS_WORK'])
    print(f"  - Best case: {files_to_fix * 15 / 60:.1f} hours")
    print(f"  - Worst case: {files_to_fix * 25 / 60:.1f} hours")
    print(f"  - Average: {files_to_fix * 20 / 60:.1f} hours")
    
    # Save detailed results
    output_file = base_path / 'evaluation' / 'results' / 'standards_hybrid_analysis.txt'
    with open(output_file, 'w') as f:
        f.write("DETAILED ANALYSIS BY FILE\n")
        f.write("=" * 80 + "\n\n")
        
        for severity in ['NEEDS_WORK', 'MEDIUM', 'GOOD']:
            f.write(f"\n{severity} FILES\n")
            f.write("-" * 80 + "\n\n")
            
            for r in sorted(by_severity[severity], key=lambda x: x['score']):
                f.write(f"File: {r['file']}\n")
                f.write(f"Score: {r['score']}/100\n")
                f.write(f"Issues: {', '.join(r['issues']) if r['issues'] else 'None'}\n")
                if r['broad_header_list']:
                    f.write(f"Broad headers: {', '.join(repr(h) for h in r['broad_header_list'])}\n")
                f.write("\n")
    
    print(f"\n📄 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()

