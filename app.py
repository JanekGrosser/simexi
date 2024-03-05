import re


def validate_expression(expression: str) -> bool:
    """Return True if expression in a valid mathematical expression"""
    if not expression:
        print("Error: The expression is empty")
        return False

    valid_chars = "0123456789+-*/(). "
    if any(char not in valid_chars for char in expression):
        print("Error: The expression contains invalid characters")
        return False

    parentheses_count = 0
    for char in expression:
        if char == "(":
            parentheses_count += 1
        elif char == ")":
            parentheses_count -= 1
        if parentheses_count < 0:
            print("Error: The expression contains mismatched parentheses")
            return False
    if parentheses_count > 0:
        print("Error: The expression contains mismatched parentheses")
        return False

    return True


def tokenize(expression: str) -> list:
    """Use regex to capture numbers and operators/parentheses"""
    token_pattern = r"\s*(?:(\d+(\.\d+)?)|(.))\s*"
    tokens = re.findall(token_pattern, expression)

    return [(t[0] if t[0] else t[2]).strip() for t in tokens]


def is_number(token: str) -> bool:
    """Returns True if string is a number."""
    try:
        float(token)
        return True
    except ValueError:
        return False


def shunting_yard(tokens: list) -> list:
    """Converts infix expression to postfix expression using Shunting Yard algorithm"""
    # A dictionary mapping each operator to its precedence level. Higher numbers mean higher precedence.
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}
    operator_stack = []
    output_queue = []

    for token in tokens:
        # If the token is a number, add it directly to the output queue. In postfix notation, numbers are output as soon as they are seen.
        if is_number(token):
            output_queue.append(token)
        elif token in precedence:
            while (
                operator_stack
                and operator_stack[-1] != "("
                and precedence[operator_stack[-1]] >= precedence[token]
            ):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                output_queue.append(operator_stack.pop())
            operator_stack.pop()

    while operator_stack:
        output_queue.append(operator_stack.pop())

    return output_queue


def evaluate_postfix(postfix_expression: list):
    stack = []
    for token in postfix_expression:
        if is_number(token):
            stack.append(float(token))
        else:
            right = stack.pop()
            left = stack.pop()
            if token == "+":
                stack.append(left + right)
            elif token == "-":
                stack.append(left - right)
            elif token == "*":
                stack.append(left * right)
            elif token == "/":
                stack.append(left / right)

    return stack.pop()


def app_main():
    print("This is MyEval, a mathematical expressions interpreter")
    print("Type 'exit' to exit the program")
    while True:
        expression = input("Enter a mathematical expression: ")
        if expression.lower() == "exit":
            break
        if not validate_expression(expression):
            continue
        try:
            tokens = tokenize(expression)
            postfix = shunting_yard(tokens)
            result = evaluate_postfix(postfix)
            print(f"The result is: {result}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    app_main()
