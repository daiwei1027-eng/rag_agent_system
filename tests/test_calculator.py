import pytest
from rag_agent_system.tools.calculator_tool import calculator
@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", 2, 3, 5),
        ("subtract", 2, 3, -1),
        ("multiply", 2, 3, 6),
        ("divide", 7, 2, 3.5),
        ("add", 0, 3, 3),
    ],
)
def test_calculator_returns_expected_result(operation, a, b, expected):
    result = calculator(operation, a, b)
    assert result == expected
def test_divide_zero():
    with pytest.raises(ValueError,match="nonzero"):
        calculator("divide", 5, 0)
def test_unknown_operation():
    with pytest.raises(ValueError,match="Invalid operation"):
        calculator("unknown", 5, 4)