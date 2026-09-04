import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from app.core.math_checker import MathChecker

checker = MathChecker()

def check(s):
    print(f"\n--- Checking '{s}' ---")
    cs = checker.sanitize_input(s)
    print(f"Sanitized: {cs}")
    pe = checker._parse_expression(cs)
    print(f"Parsed: {pe} ({type(pe)})")

check("x = 3, x = 5")
check("x=3, x=5")
