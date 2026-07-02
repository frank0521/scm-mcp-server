"""Unit tests for tool dispatch and execution.

Tests verify:
- Tool routing (list vs get-by-ID)
- Request construction (path, params)
- Response handling (success vs error)
"""

import pytest
from unittest.mock import Mock, patch

from scm_mcp_server.tools import call


@pytest.fixture
def mock_rest_client():
    """Mock rest_client.request for isolated testing."""
    with patch("scm_mcp_server.rest_client.request") as mock:
        yield mock


class TestToolScaffold:
    """Verify test infrastructure is working."""

    def test_pytest_working(self):
        """Sanity check: pytest can run."""
        assert True

    def test_mock_fixture_available(self, mock_rest_client):
        """Verify mock fixture is injectable."""
        assert mock_rest_client is not None


class TestToolDispatch:
    """Test tool routing and dispatch logic (to be implemented in 4.2)."""

    def test_unknown_tool_raises_not_implemented(self):
        """Unknown tool names should raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Tool 'unknown_tool' not implemented"):
            call("unknown_tool", {})
