from collections import namedtuple
import re
import traceback
from typing import Iterator


BASE_OPERATORS = "+-*/^"
DIGITS = "0123456789."
PARENTHESIS = "()"


def validate_expression(expression: str) -> bool:
    """Return True if expression in a valid mathematical expression"""
    if not expression:
        raise Exception("The expression is empty")

    valid_chars = "0123456789+-*/().^ "

    if any(char not in valid_chars for char in expression):
        raise Exception("The expression contains invalid characters")

    if re.search(r"\d\s+\d", expression):
        raise Exception(
            "The expression is invalid: two numbers are separated only by whitespace"
        )

    parentheses_count = 0
    for char in expression:
        if char == "(":
            parentheses_count += 1
        elif char == ")":
            parentheses_count -= 1
        # If there is an extra closing parenthesis the loop can exit
        if parentheses_count < 0:
            raise Exception("The expression contains mismatched ')' parentheses")
    if parentheses_count > 0:
        raise Exception("The expression contains mismatched '(' parentheses")

    return True


def insert_assumed_multiplication(expression: str) -> str:
    """Inserts assumed multiplications into the expression."""
    # Remove all white spaces from the expression
    expression = "".join(expression.split())

    # Case 1: Between a number and an open parenthesis
    expression = re.sub(r"(\d)(\()", r"\1*\2", expression)

    # Case 2: Between a close parenthesis and a number
    expression = re.sub(r"(\))(\d)", r"\1*\2", expression)

    # Case 3: Between two parentheses
    expression = re.sub(r"(\))(\()", r"\1*\2", expression)
    return expression


def tokenize(expression: str) -> Iterator[str]:
    """Yields tokens from a mathematical expression."""

    cursor = 0
    is_infix = False

    while cursor < len(expression):
        char = expression[cursor]

        # Handle unary minus
        if not is_infix and char == "-":
            yield "~"  # A sequence for unary negation
            cursor += 1

        # Emit base operators and separators directly
        elif char in BASE_OPERATORS or char in PARENTHESIS:
            yield char
            cursor += 1
            is_infix = (
                char == ")"
            )  # After closing parenthesis, expect infix operators (or could be end of expression)

        # Emit a sequence of number characters as a single token
        elif char in DIGITS:
            cursor_end = cursor + 1
            while cursor_end < len(expression) and expression[cursor_end] in DIGITS:
                cursor_end += 1
            yield expression[cursor:cursor_end]  # Emit the number as a whole token
            cursor = cursor_end
            is_infix = True  # After a number, we expect infix operators

        # Skip unrecognized characters and reset the infix status
        else:
            is_infix = False
            cursor += 1


def is_float(token: str) -> bool:
    """Returns True if string is a number."""
    try:
        float(token)
        return True
    except ValueError:
        return False


def shunting_yard(tokens: Iterator[str] | list[str]) -> list:
    """Converts infix expression to postfix expression using Shunting Yard algorithm"""

    # A named tuple to hold pecedence and assiciativity of an operator
    OperatorInfo = namedtuple("OperatorInfo", ["precedence", "associativity"])
    operators = {
        "+": OperatorInfo(10, "Left"),
        "-": OperatorInfo(10, "Left"),
        "/": OperatorInfo(20, "Left"),
        "*": OperatorInfo(20, "Left"),
        "~": OperatorInfo(30, "Right"),  # Unary negation
        "^": OperatorInfo(30, "Right"),
    }

    operator_stack = []
    output_queue = []

    for token in tokens:
        if is_float(token):
            output_queue.append(token)
        elif token in operators.keys():
            while (operator_stack and operator_stack[-1] != "(") and (
                operators[operator_stack[-1]].precedence > operators[token].precedence
                or (
                    operators[operator_stack[-1]].precedence
                    == operators[token].precedence
                    and operators[token].associativity == "Left"
                )
            ):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack[-1] != "(":
                assert (
                    len(operator_stack) != 0
                ), "Invalid expression: mismatched parentheses"
                output_queue.append(operator_stack.pop())
            assert operator_stack[-1] == "(", "Missing opening parenthesis"
            operator_stack.pop()

    while operator_stack:
        assert operator_stack[-1] != "(", "Missing closing parenthesis"
        output_queue.append(operator_stack.pop())

    return output_queue


def evaluate_postfix(postfix_expression: list) -> float | int:
    """Evaluates a postfix expression and returns the result"""
    stack = []

    for token in postfix_expression:
        if is_float(token):
            stack.append(float(token))
        elif token == "~":
            stack.append(-stack.pop())
        else:
            right = stack.pop()
            left = stack.pop()

            match token:
                case "+":
                    stack.append(left + right)
                case "-":
                    stack.append(left - right)
                case "*":
                    stack.append(left * right)
                case "/":
                    if right == 0:
                        raise Exception("Can't divide by 0")
                    else:
                        stack.append(left / right)
                case "^":
                    stack.append(left**right)
                case _:
                    raise Exception(f"Invalid operator: {token}")

    return stack.pop()


def app_main():
    print("This is MyEval, a mathematical expressions interpreter")
    print("Type 'exit' to exit the program")
    while True:
        expression = input("Enter a mathematical expression: ")
        if expression.lower() == "exit":
            print("Bye")
            break
        try:
            validate_expression(expression)

            expression = insert_assumed_multiplication(expression)
            print(expression)

            tokens = list(tokenize(expression))
            print(tokens)

            postfix = shunting_yard(tokens)
            print(" ".join(postfix))

            result = evaluate_postfix(postfix)
            print(f"The result is: {result}")
            # expected = eval(expression)
            # print(f"expected is: {expected}")
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    app_main()
