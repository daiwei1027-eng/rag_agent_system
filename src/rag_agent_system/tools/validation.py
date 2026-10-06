from typing import Any

def validate_arguments(
    arguments: dict[str, Any],
    parameters_schema: dict[str, Any],
) -> None:
    if not isinstance(arguments, dict):
        raise TypeError("Arguments must be a dict")
    for name in parameters_schema.get("required", []):
        if name not in arguments:
            raise ValueError(f"Missing required argument: {name}")
    properties = parameters_schema.get("properties", {})

    if parameters_schema.get("additionalProperties", True) is False:
        for name in arguments:
            if name not in properties:
                raise ValueError(f"AdditionalProperties are not allowed: {name}")
    for name, value in arguments.items():
        if name not in properties:
            continue

        rule = properties[name]
        expected_type = rule.get("type")

        if "minLength" in rule:
            minlength = rule["minLength"]
            if len(value) < minlength:
                raise ValueError(
                    f"Argument '{name}' must contain at least {minlength} characters"
                )
        if "minimum" in rule:
            minimum = rule["minimum"]
            if value<minimum:
                raise ValueError(f"Please provide value >= minimum{minimum}")

        if "maximum" in rule:
            maximum = rule["maximum"]
            if value>maximum:
                raise ValueError(f"Please provide value <= maximum{maximum}")



        if expected_type == "string":
            if not isinstance(value, str):
                raise TypeError(f"Argument '{name}' must be a string")
            if "enum" in rule:
                if value not in rule["enum"]:
                    raise ValueError(
                        f"Argument '{name}' must be one of {rule['enum']}"
                    )

        elif expected_type == "integer":
            # 检查 type(value) is int；不满足时抛异常
            if type(value) is not int:
                raise TypeError(f"Argument '{name}' must be a integer")

        elif expected_type == "number":
            if not(type(value) in( float,int)):
                raise TypeError(f"Argument '{name}' must be a number(integer or float)")
        else:
            raise ValueError(f"Unsupported schema type: {expected_type}")