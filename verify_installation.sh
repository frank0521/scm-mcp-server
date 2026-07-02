#!/bin/bash
# Quick verification script - checks if project can be installed

set -e

echo "================================"
echo "SCM MCP Server - Installation Verification"
echo "================================"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Check Python version
echo "1. Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version (>= 3.11)"
else
    echo "❌ Python $python_version is too old (need >= 3.11)"
    exit 1
fi
echo ""

# Check if pan.dev exists
echo "2. Checking pan.dev repository..."
if [ -d "../pan.dev/openapi-specs/scm" ]; then
    spec_count=$(find ../pan.dev/openapi-specs/scm -name "*.yaml" -o -name "*.yml" | wc -l | tr -d ' ')
    echo "✓ pan.dev repository found ($spec_count OpenAPI specs)"
else
    echo "⚠️  pan.dev repository not found at ../pan.dev"
    echo "   Clone it with: git clone https://github.com/PaloAltoNetworks/pan.dev ../pan.dev"
fi
echo ""

# Install in development mode
echo "3. Installing package in development mode..."
pip install -e . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Package installed successfully"
else
    echo "❌ Installation failed"
    echo "   Try: pip install -e ."
    exit 1
fi
echo ""

# Check imports
echo "4. Checking Python imports..."
python -c "
import sys
try:
    from scm_mcp import OAuth2Manager, SCMClient, parse_all_specs
    print('✓ All modules import successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
echo ""

# Summary
echo "================================"
echo "Installation Verification Complete"
echo "================================"
echo ""
echo "✓ Python version OK"
echo "✓ Package installed"
echo "✓ Modules import successfully"
echo ""
echo "Next steps:"
echo "1. Set environment variables (see .env.example)"
echo "2. Run integration test: ./tests/integration_test.sh"
echo "3. Configure Claude CLI (see README.md)"
echo ""
