# Pre-commit Validation Scripts

**Scripts used by pre-commit hooks for validation checks**

## 📁 Structure

```
scripts/pre-commit/
├── README.md                        # This file
└── validate-installation-docs.sh   # Installation file completeness check
```

## 🎯 Purpose

These scripts are called by `.pre-commit-config.yaml` hooks to perform validation checks. 

**Why scripts instead of inline commands?**
- Multi-line commands in YAML behave badly
- Scripts are easier to maintain and test
- Better error handling and output formatting
- Can be run independently for debugging

## 📜 Available Scripts

### validate-installation-docs.sh

**Purpose**: Ensures critical installation files exist

**Checks**:
- `installation/00-START.md` - Installation entry point
- `installation/02-copy-files.md` - File copy instructions
- `scripts/build_rag_index.py` - RAG index builder (CRITICAL)
- `.agent-os/standards/development/code-quality.md` - Quality standards

**Usage**:
```bash
# Run manually
./scripts/pre-commit/validate-installation-docs.sh

# Called by pre-commit automatically
git commit -m "update installation docs"
```

**Exit Codes**:
- `0`: All files present
- `1`: One or more files missing

## 🔧 Creating New Validation Scripts

### Guidelines

1. **Keep scripts simple and focused** - One validation per script
2. **Use descriptive names** - `validate-<what>-<aspect>.sh`
3. **Make them executable** - `chmod +x script.sh`
4. **Add color output** - Use RED/GREEN/YELLOW for readability
5. **Exit codes matter** - `0` = success, non-zero = failure
6. **Test independently** - Run script manually before adding to hook

### Template

```bash
#!/usr/bin/env bash
# Brief description of what this script validates

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Validating <what>..."

# Your validation logic here
if [[ condition ]]; then
    echo -e "${GREEN}✅ Validation passed${NC}"
    exit 0
else
    echo -e "${RED}❌ Validation failed${NC}"
    echo -e "${YELLOW}Helpful error message${NC}"
    exit 1
fi
```

### Adding to Pre-commit

```yaml
- id: your-validation-check
  name: "Your Validation Name"
  entry: scripts/pre-commit/your-validation-script.sh
  language: system
  pass_filenames: false
  files: '^pattern/to/match.*$'
  stages: [pre-commit]
  verbose: true
```

## 🐛 Debugging Scripts

### Run Manually

```bash
# Run script directly
./scripts/pre-commit/validate-installation-docs.sh

# Run with bash for debugging
bash -x scripts/pre-commit/validate-installation-docs.sh
```

### Test with Pre-commit

```bash
# Run specific hook
pre-commit run installation-docs-check --all-files

# Run with verbose output
pre-commit run installation-docs-check --all-files --verbose
```

## 📚 Best Practices

### DO:
- ✅ Use scripts for all non-trivial validations
- ✅ Make scripts executable (`chmod +x`)
- ✅ Use `set -euo pipefail` for safety
- ✅ Provide clear, colored output
- ✅ Test scripts independently before adding to hooks
- ✅ Keep scripts focused (one validation per script)

### DON'T:
- ❌ Embed multi-line commands in YAML
- ❌ Use complex Python one-liners in `entry:`
- ❌ Forget to make scripts executable
- ❌ Skip error messages (users need to know what's wrong)
- ❌ Make scripts that modify files (pre-commit does that)

## 🆘 Troubleshooting

### Script not found

```bash
# Check if script exists
ls -l scripts/pre-commit/your-script.sh

# Check if executable
file scripts/pre-commit/your-script.sh

# Make executable if needed
chmod +x scripts/pre-commit/your-script.sh
```

### Script fails but works manually

```bash
# Check script path in .pre-commit-config.yaml
# Should be: scripts/pre-commit/script.sh
# Not: ./scripts/pre-commit/script.sh

# Run from repo root
cd /path/to/agent-os-enhanced
./scripts/pre-commit/script.sh
```

### Permission denied

```bash
# Make script executable
chmod +x scripts/pre-commit/your-script.sh

# Commit the permission change
git add scripts/pre-commit/your-script.sh
git commit -m "fix: make validation script executable"
```

## 📖 Related Documentation

- **Pre-commit Setup**: `.agent-os/standards/development/pre-commit-setup.md`
- **Pre-commit Config**: `.pre-commit-config.yaml`
- **Code Quality Standards**: `.agent-os/standards/development/code-quality.md`

---

**Pattern**: Script-based validation (aligned with python-sdk)  
**Rule**: NO multi-line commands in YAML  
**Benefit**: Maintainable, testable, reliable validation

