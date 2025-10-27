#!/bin/bash
# Validate all search_standards queries from tasks-template.md

echo "Validating Agent OS Dual Estimation Framework Queries"
echo "====================================================="
echo ""

# Query 1: Core Formula & Calculation
echo "Query 1: Core Formula & Calculation"
python mcp_tool_cli.py search_standards '{
  "query": "H W A L variables wall clock duration human active time",
  "n_results": 3
}' > /tmp/query1_formula.json
echo "✓ Saved to /tmp/query1_formula.json"
echo ""

# Query 2: Task Type Multipliers
echo "Query 2: Task Type Multipliers"
python mcp_tool_cli.py search_standards '{
  "query": "table boilerplate setup straightforward logic complex algorithm",
  "n_results": 3
}' > /tmp/query2_multipliers.json
echo "✓ Saved to /tmp/query2_multipliers.json"
echo ""

# Query 3: What Counts as Active Time
echo "Query 3: What Counts as Active Time"
python mcp_tool_cli.py search_standards '{
  "query": "INCLUDES EXCLUDES human active time",
  "n_results": 3
}' > /tmp/query3_active_time.json
echo "✓ Saved to /tmp/query3_active_time.json"
echo ""

# Query 4: Task Format
echo "Query 4: Task Format"
python mcp_tool_cli.py search_standards '{
  "query": "task format example Human Baseline Agent OS",
  "n_results": 3
}' > /tmp/query4_task_format.json
echo "✓ Saved to /tmp/query4_task_format.json"
echo ""

# Query 5: Parallel Multiplier Effect
echo "Query 5: Parallel Multiplier Effect"
python mcp_tool_cli.py search_standards '{
  "query": "parallel multiplier effect",
  "n_results": 3
}' > /tmp/query5_parallel.json
echo "✓ Saved to /tmp/query5_parallel.json"
echo ""

# Query 6: Calibration Guidance
echo "Query 6: Calibration Guidance"
python mcp_tool_cli.py search_standards '{
  "query": "calibration new to Agent OS Enhanced",
  "n_results": 3
}' > /tmp/query6_calibration.json
echo "✓ Saved to /tmp/query6_calibration.json"
echo ""

echo "====================================================="
echo "All queries completed! Results in /tmp/query*.json"
echo "Run: cat /tmp/query1_formula.json | jq '.result' | jq -r '.results[0].content' | head -50"
