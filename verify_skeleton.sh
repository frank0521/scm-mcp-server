#!/bin/bash
# Skeleton Verification Script
# Tests all acceptance criteria for project skeleton

set -e

echo "======================================================"
echo "SCM MCP Server - Skeleton Verification"
echo "======================================================"
echo ""

cd ~/vibe-coding/scm-mcp-server
source venv/bin/activate

# Test 1: Installation
echo "[1/6] Testing installation..."
pip show scm-mcp-server > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "    ✓ Package installed"
else
    echo "    ✗ Package not installed"
    exit 1
fi
echo ""

# Test 2: Config validation (missing credentials)
echo "[2/6] Testing config validation (missing credentials)..."
unset SCM_CLIENT_ID SCM_CLIENT_SECRET SCM_TSG_ID
python -c "from scm_mcp_server.config import Config" 2>&1 | grep -q "缺少必填环境变量"
if [ $? -eq 0 ]; then
    echo "    ✓ Config validation works (raises error on missing vars)"
else
    echo "    ✗ Config validation failed"
    exit 1
fi
echo ""

# Test 3: Config validation (with credentials)
echo "[3/6] Testing config validation (with credentials)..."
export SCM_CLIENT_ID="test-id"
export SCM_CLIENT_SECRET="test-secret"
export SCM_TSG_ID="test-tsg"
BASE_URL=$(python -c "from scm_mcp_server.config import Config; print(Config.BASE_URL)")
if [ "$BASE_URL" = "https://api.strata.paloaltonetworks.com" ]; then
    echo "    ✓ Config loaded successfully"
    echo "    BASE_URL: $BASE_URL"
else
    echo "    ✗ Config loading failed"
    exit 1
fi
echo ""

# Test 4: Module imports
echo "[4/6] Testing module imports..."
python -c "
from scm_mcp_server import auth, rest_client, server, check
from scm_mcp_server import tools
print('    ✓ All modules import successfully')
"
if [ $? -ne 0 ]; then
    echo "    ✗ Module import failed"
    exit 1
fi
echo ""

# Test 5: Server startup (non-blocking test)
echo "[5/6] Testing server startup..."
python -c "
import sys
from scm_mcp_server import server

# Test that server module loads without crash
# (Full server test requires MCP client handshake)
print('    ✓ Server module loads successfully')
print('    (Full MCP protocol test requires MCP client)')
"
if [ $? -ne 0 ]; then
    echo "    ✗ Server startup failed"
    exit 1
fi
echo ""

# Test 6: Check script (will fail without real credentials, but should handle gracefully)
echo "[6/6] Testing check script structure..."
python -c "
from scm_mcp_server import check
print('    ✓ Check module loads successfully')
print('    (Connectivity test requires valid SCM credentials)')
"
if [ $? -ne 0 ]; then
    echo "    ✗ Check module failed"
    exit 1
fi
echo ""

# Summary
echo "======================================================"
echo "✓ Skeleton verification complete"
echo "======================================================"
echo ""
echo "Next steps:"
echo "1. Set valid SCM credentials in environment variables"
echo "2. Run: python -m scm_mcp_server.check"
echo "3. For MCP client test, configure Claude CLI or Cursor"
echo ""
