#!/bin/bash
# Test MCP access by calling CLI wrapper and saving to temp file

python mcp_tool_cli.py search_standards '{"query": "Agent OS orientation guide", "n_results": 3}' > /tmp/mcp_test_result.json 2>&1
echo "Exit code: $?" >> /tmp/mcp_test_result.json
