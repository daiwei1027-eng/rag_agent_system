def calculator(operation: str, a: float, b: float) -> float:
    if operation=="add":
        return a+b
    elif operation=="subtract":
        return a-b
    elif operation=="multiply":
        return a*b
    elif operation=="divide":
        if b==0:
            raise ValueError("Please provide a nonzero b")
        return a/b
    else:
        raise ValueError("Invalid operation")