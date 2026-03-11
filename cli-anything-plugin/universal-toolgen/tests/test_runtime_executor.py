from cli_anything.universal.runtime_executor import RuntimeExecutor
from cli_anything.universal.schema import ExecutionType, ToolSchema


def test_execute_python_function():
    ex = RuntimeExecutor()

    def add(a: int, b: int) -> int:
        return a + b

    ex.register_function("calc.add", add)
    tool = ToolSchema(
        name="calc.add",
        description="Add numbers",
        execution_type=ExecutionType.PYTHON_FUNCTION,
        execution_target="calc.add",
    )

    result = ex.execute(tool, {"a": 2, "b": 3})
    assert result["result"] == 5
