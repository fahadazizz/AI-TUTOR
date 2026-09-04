import sympy
from app.core.math_checker import MathChecker
checker = MathChecker()

text = "x == 3, x == 5"
print(text.split(","))
parts = [p.strip() for p in text.split(",")]
exprs = []
for p in parts:
    print(f"part: '{p}'")
    if "x==" in p:
        p = p.replace("x==", "")
    print(f"after replace: '{p}'")
    exprs.append(sympy.parsing.sympy_parser.parse_expr(p))
print(sympy.Tuple(*exprs))
