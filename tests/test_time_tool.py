from rag_agent_system.tools.time_tool import get_current_time
import pytest
from datetime import datetime, timedelta, timezone
@pytest.mark.parametrize(
    "timezone_name,expected_offset",
    [
        ("UTC", timedelta(0)),
        ("Asia/Shanghai", timedelta(hours=8)),
    ],
)
def test_time_returns_expected_offset(timezone_name, expected_offset):
    before = datetime.now(timezone.utc)
    result = get_current_time(timezone_name)
    after = datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(result)
    assert before <= parsed <= after
    assert parsed.utcoffset() == expected_offset
def test_reject_unsupported_timezone():
    with pytest.raises(ValueError, match="Unsupported timezone"):
        get_current_time("abc")