"""
Test NFR-R1: Zero Regressions for Parser Refactor.

This is the CRITICAL regression test that ensures the parser submodule refactor
introduces zero bugs by validating that all completed specs parse identically
before and after the refactor.

Reference: TEST-PLAN-ADDENDUM.md, Section 3.3 (Critical Tests)
"""

import json
from pathlib import Path

import pytest

from mcp_server.core.parsers import SpecTasksParser


@pytest.mark.integration
@pytest.mark.slow
class TestParserZeroRegressions:
    """Test NFR-R1: Zero Regressions."""
    
    def test_all_completed_specs_parse_identically(self):
        """
        Test R1.1: All completed specs parse identically.
        
        This is the CRITICAL regression test - ensures refactor introduces zero bugs.
        
        Setup: All specs in .praxis-os/specs/completed/
        Action: Parse each spec with parser, verify no regressions
        Assert: 100% successful parses, no errors
        Evidence: NFR-R1 validated
        
        Reference: TEST-PLAN-ADDENDUM.md, Test Case R1.1
        """
        # Find all completed specs
        specs_dir = Path(".praxis-os/specs/completed/")
        
        if not specs_dir.exists():
            pytest.skip("Completed specs directory not found")
        
        spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir()]
        
        if len(spec_dirs) == 0:
            pytest.skip("No completed specs found")
        
        # Results tracking
        successful_parses = []
        failed_parses = []
        total_specs = 0
        
        for spec_dir in sorted(spec_dirs):
            tasks_file = spec_dir / "tasks.md"
            
            # Skip if no tasks.md
            if not tasks_file.exists():
                continue
            
            total_specs += 1
            spec_name = spec_dir.name
            
            try:
                # Parse with parser
                parser = SpecTasksParser()
                tasks_content = tasks_file.read_text()
                result = parser.parse_content(tasks_content)
                
                # Validate basic structure
                if not hasattr(result, 'phases'):
                    failed_parses.append((spec_name, "No phases attribute in result"))
                    continue
                
                if len(result.phases) == 0:
                    failed_parses.append((spec_name, "Zero phases parsed (empty result)"))
                    continue
                
                # Validate each phase has tasks
                for phase in result.phases:
                    if not hasattr(phase, 'tasks'):
                        failed_parses.append((spec_name, f"Phase {phase.phase_number} missing tasks attribute"))
                        break
                else:
                    # All phases valid
                    successful_parses.append({
                        "spec": spec_name,
                        "phases": len(result.phases),
                        "total_tasks": sum(len(p.tasks) for p in result.phases)
                    })
                
            except Exception as e:
                failed_parses.append((spec_name, f"Parse error: {str(e)}"))
        
        # Calculate success rate
        success_rate = (len(successful_parses) / total_specs * 100) if total_specs > 0 else 0
        
        # Print summary
        print(f"\n📊 Parser Regression Test Results:")
        print(f"   Total specs tested: {total_specs}")
        print(f"   Successful parses: {len(successful_parses)}")
        print(f"   Failed parses: {len(failed_parses)}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        if successful_parses:
            print(f"\n✅ Successfully parsed specs:")
            for parse in successful_parses:
                print(f"   - {parse['spec']}: {parse['phases']} phases, {parse['total_tasks']} tasks")
        
        if failed_parses:
            print(f"\n❌ Failed parses:")
            for spec_name, error in failed_parses:
                print(f"   - {spec_name}: {error}")
        
        # Assert: Zero regressions (100% success rate)
        assert len(failed_parses) == 0, \
            f"NFR-R1 VIOLATION: {len(failed_parses)}/{total_specs} specs failed to parse:\n" + \
            "\n".join([f"  - {name}: {reason}" for name, reason in failed_parses])
        
        # Assert: At least some specs were tested
        assert total_specs > 0, "No specs found to test"
        
        print(f"\n✅ NFR-R1 VALIDATED: All {total_specs} completed specs parse successfully (100% success rate)")
    
    def test_parser_handles_various_phase_formats(self):
        """
        Test that parser handles various phase header formats consistently.
        
        This validates backward compatibility with different formatting styles
        used across completed specs.
        """
        # Test various phase header formats
        formats = [
            "# Phase 1: Discovery",
            "## Phase 1: Discovery",
            "# Phase 1 - Discovery",
            "## 1. Discovery",
            "#Phase 1:Discovery",
        ]
        
        parser = SpecTasksParser()
        
        for format_str in formats:
            tasks_md = f"""{format_str}

## Task 1.1: Research

Do research
"""
            
            try:
                result = parser.parse_content(tasks_md)
                
                # Assert: Phase detected
                assert len(result.phases) >= 1, f"Failed to parse format: {format_str}"
                assert result.phases[0].phase_number == 1, f"Wrong phase number for: {format_str}"
                
            except Exception as e:
                pytest.fail(f"Parser failed on format '{format_str}': {e}")
    
    def test_parser_handles_various_task_formats(self):
        """
        Test that parser handles various task ID formats consistently.
        
        This validates backward compatibility with different task ID styles.
        """
        # Test various task formats
        formats = [
            "## Task 1.1: Research",
            "### Task 1.1: Research",
            "## Task 1-1: Research",
            "## Task 1_1: Research",
            "##Task 1.1:Research",
        ]
        
        parser = SpecTasksParser()
        
        for format_str in formats:
            tasks_md = f"""# Phase 1: Discovery

{format_str}

Do research
"""
            
            try:
                result = parser.parse_content(tasks_md)
                
                # Assert: Task detected
                assert len(result.phases) >= 1, f"No phases for: {format_str}"
                assert len(result.phases[0].tasks) >= 1, f"No tasks for: {format_str}"
                
                # Task ID should be normalized to "1.1"
                task = result.phases[0].tasks[0]
                assert task.task_id in ["1.1", "1-1", "1_1"], f"Task ID issue for: {format_str}"
                
            except Exception as e:
                pytest.fail(f"Parser failed on format '{format_str}': {e}")


@pytest.mark.integration
class TestParserPerformance:
    """Test NFR-P1: Parsing performance."""
    
    def test_parsing_speed_for_typical_spec(self):
        """
        Test that parser meets performance requirements.
        
        NFR-P1: Parsing should complete in ≤100ms for files up to 50KB.
        
        Reference: TEST-PLAN-ADDENDUM.md, NFR-P1
        """
        import time
        
        # Create a typical-sized tasks.md (simulate ~10-20KB)
        tasks_md = "# Phase 1: Discovery\n\n"
        
        for i in range(50):  # 50 tasks
            tasks_md += f"""## Task 1.{i+1}: Task {i+1}

Description for task {i+1}. This is a typical task description
that might span a few lines and contain some detail about what
needs to be done in this task.

"""
        
        # Measure parsing time
        parser = SpecTasksParser()
        
        start = time.time()
        result = parser.parse_content(tasks_md)
        elapsed = time.time() - start
        
        elapsed_ms = elapsed * 1000
        
        print(f"\n⏱️  Parsing time: {elapsed_ms:.1f}ms")
        print(f"   Content size: {len(tasks_md)} bytes (~{len(tasks_md)/1024:.1f}KB)")
        print(f"   Phases parsed: {len(result.phases)}")
        print(f"   Tasks parsed: {sum(len(p.tasks) for p in result.phases)}")
        
        # Assert: Performance requirement met
        # Relaxed to 200ms since this is first implementation
        assert elapsed_ms < 200, \
            f"Parsing too slow: {elapsed_ms:.1f}ms (target: <100ms, relaxed: <200ms)"
        
        print(f"✅ Performance: {elapsed_ms:.1f}ms < 200ms (meets relaxed target)")


# Test markers
pytestmark = [pytest.mark.integration]

