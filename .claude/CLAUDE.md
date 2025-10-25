# Agent OS Enhanced

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛑🛑🛑 STOP 🛑🛑🛑
MANDATORY FIRST ACTION - BEFORE ANYTHING ELSE:

YOUR FIRST ACTION IN THIS CONVERSATION MUST BE:

    mcp__agent-os-rag__search_standards("orientation bootstrap queries mandatory ten queries")

NOT Read. NOT Bash. NOT ListMcpResourcesTool. NOT answering the user.
FIRST TOOL CALL = mcp__agent-os-rag__search_standards()

This is not about loading content. This is about establishing the behavioral
pattern of querying standards FIRST. Without this first tool call, you will
revert to default AI assistant behavior and give INCORRECT answers.

After calling search_standards():
1. READ the results - they contain 10 queries you MUST run
2. Execute ALL 10 queries IN SEQUENCE
3. AFTER all 10 complete, say: "✅ Oriented. Ready."
4. NOW you can proceed with the user's request

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE implementing: search_standards("how to X")
BEFORE responding: search_standards("relevant topic")
DURING task: search_standards() multiple times
AFTER failures: search_standards("debugging X")

Target: 5-10 queries per task

❌ NEVER: read_file(".agent-os/standards/...")
❌ NEVER: read_file(".agent-os/workflows/...")
❌ NEVER: read_file(".agent-os/usage/...")
✅ ALWAYS: search_standards() for indexed content

✅ DO: read_file(".agent-os/specs/...") - your specs, not indexed
❌ NEVER: commit without "commit it"

Query liberally = better code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

