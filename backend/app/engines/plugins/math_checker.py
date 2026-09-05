"""
AI Tutor — Math Answer Checking Engine.

Uses SymPy for deterministic, algebraic verification of student answers.
This ensures we never rely on the LLM to do math or grade math.
"""

import re
from typing import Optional

import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

from app.core.models import AnswerResult
from app.engines.evaluation_engine import AnswerEvaluator
from app.logging import get_logger

logger = get_logger(__name__)


class MathChecker(AnswerEvaluator):
    """Deterministic mathematical answer verification using SymPy."""

    def __init__(self) -> None:
        # Transformations to allow implicit multiplication (e.g. 2x -> 2*x)
        self.transformations = standard_transformations + (implicit_multiplication_application,)

    def sanitize_input(self, text: str) -> str:
        """Clean and normalize student mathematical input for SymPy."""
        if not text:
            return ""

        text = text.lower()
        
        text = text.replace("==", "=")
        
        # Replace unicode fractions and superscripts
        replacements = {
            "½": "1/2", "⅓": "1/3", "¼": "1/4", "¾": "3/4",
            "²": "**2", "³": "**3", "^": "**",
            "×": "*", "÷": "/", "=": "==", "$": "",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Common student typo: "x2" instead of "x^2" or "x**2"
        # Only replace if it's at the end of a term
        text = re.sub(r'([a-z])2(?!\d)', r'\1**2', text)
        text = re.sub(r'([a-z])3(?!\d)', r'\1**3', text)

        # Remove spaces around operators
        text = re.sub(r'\s+([+\-*/=])\s+', r'\1', text)
        
        return text.strip()

    def _parse_expression(self, text: str) -> Optional[sympy.Expr]:
        """Safely parse a string into a SymPy expression."""
        if not text:
            return None
            
        try:
            # Handle multiple answers (e.g. "x=3, x=5" or "a=3, b=7")
            if "," in text:
                parts = [p.strip() for p in text.split(",")]
                exprs = []
                for p in parts:
                    if "==" in p:
                        sub_parts = p.split("==")
                        if len(sub_parts) == 2:
                            lhs = parse_expr(sub_parts[0], transformations=self.transformations)
                            rhs = parse_expr(sub_parts[1], transformations=self.transformations)
                            exprs.append(sympy.Eq(lhs, rhs))
                        else:
                            exprs.append(parse_expr(p, transformations=self.transformations))
                    else:
                        exprs.append(parse_expr(p, transformations=self.transformations))
                return sympy.Tuple(*exprs)

            # If it explicitly says "x=3", just extract the 3
            text_no_space = text.replace(" ", "")
            if text_no_space.startswith("x=="):
                text = text_no_space.replace("x==", "")
            elif text_no_space.startswith("-x=="):
                # Handle edge case where student typed -x=3
                pass

            # If it's an equation (contains ==), parse LHS and RHS separately
            if "==" in text:
                parts = text.split("==")
                if len(parts) != 2:
                    return None
                lhs = parse_expr(parts[0], transformations=self.transformations)
                rhs = parse_expr(parts[1], transformations=self.transformations)
                return sympy.Eq(lhs, rhs)

            return parse_expr(text, transformations=self.transformations)
        except Exception as e:
            logger.debug("sympy_parse_error", text=text, error=str(e))
            return None

    def _are_equivalent(self, expr1: sympy.Expr, expr2: sympy.Expr) -> bool:
        """Check if two SymPy expressions are mathematically equivalent."""
        if expr1 is None or expr2 is None:
            return False
            
        # If they are both tuples (multiple roots), order shouldn't matter
        if isinstance(expr1, sympy.Tuple) and isinstance(expr2, sympy.Tuple):
            set1 = set(expr1)
            set2 = set(expr2)
            if len(set1) != len(set2):
                return False
            
            # For each element in set1, find an equivalent element in set2
            for e1 in set1:
                found = False
                for e2 in set2:
                    try:
                        if isinstance(e1, sympy.Eq) and isinstance(e2, sympy.Eq):
                            diff1 = sympy.simplify(sympy.expand(e1.lhs) - sympy.expand(e1.rhs))
                            diff2 = sympy.simplify(sympy.expand(e2.lhs) - sympy.expand(e2.rhs))
                            if sympy.simplify(diff1 - diff2) == 0 or sympy.simplify(diff1 + diff2) == 0:
                                found = True
                                break
                        elif sympy.simplify(sympy.expand(e1) - sympy.expand(e2)) == 0:
                            found = True
                            break
                    except:
                        pass
                if not found:
                    return False
            return True

        # Fallback for equations (Eq objects)
        if isinstance(expr1, sympy.Eq) and isinstance(expr2, sympy.Eq):
            try:
                # Compare (LHS1 - RHS1) to (LHS2 - RHS2)
                diff1 = sympy.simplify(sympy.expand(expr1.lhs) - sympy.expand(expr1.rhs))
                diff2 = sympy.simplify(sympy.expand(expr2.lhs) - sympy.expand(expr2.rhs))
                # They are equivalent if diff1 - diff2 == 0 or diff1 + diff2 == 0
                return sympy.simplify(diff1 - diff2) == 0 or sympy.simplify(diff1 + diff2) == 0
            except Exception:
                return False

        # Standard algebraic equivalence (expr1 - expr2 == 0)
        try:
            return sympy.simplify(sympy.expand(expr1) - sympy.expand(expr2)) == 0
        except Exception:
            return False

    def check_answer(
        self, student_input: str, expected: str, question_type: str = "procedural", misconception_map: dict[str, str] = None
    ) -> AnswerResult:
        """Evaluate a student's answer against the expected answer."""
        
        # 1. Sanitize
        clean_student = self.sanitize_input(student_input)
        clean_expected = self.sanitize_input(expected)
        
        # 2. Parse
        student_expr = self._parse_expression(clean_student)
        expected_expr = self._parse_expression(clean_expected)
        
        # 3. Handle Parse Errors
        if student_expr is None:
            # If it's a word problem or yes/no, do a simple string check before failing
            if question_type in ("recognition", "word_problem"):
                if clean_student == clean_expected or clean_expected in clean_student.split():
                    return AnswerResult(is_correct=True)
            
            return AnswerResult(
                is_correct=False,
                error_type="parse_error",
                feedback_hint="مجھے آپ کا جواب سمجھ نہیں آیا۔ براہ کرم ریاضی کی علامتیں واضح لکھیں۔"
            )
            
        if expected_expr is None:
            # Fallback for text answers if expected can't be parsed
            return AnswerResult(is_correct=(clean_student == clean_expected))
            
        # 4. Exact/Algebraic Equivalence
        if self._are_equivalent(student_expr, expected_expr):
            return AnswerResult(is_correct=True)
            
        # 5. Misconception Map Check
        if misconception_map:
            for trigger, mis_id in misconception_map.items():
                # Word problem plain text fallbacks
                if trigger == "no roots" or trigger == "imaginary":
                    if trigger in clean_student:
                        return AnswerResult(is_correct=False, error_type="known_misconception", misconception_id=mis_id)
                elif "kaise equation" in clean_student or "don't know" in clean_student:
                    if mis_id == "math.ch2.wp_no_equation":
                        return AnswerResult(is_correct=False, error_type="known_misconception", misconception_id=mis_id)
                        
                clean_trigger = self.sanitize_input(trigger)
                trigger_expr = self._parse_expression(clean_trigger)
                if trigger_expr and self._are_equivalent(student_expr, trigger_expr):
                    return AnswerResult(
                        is_correct=False,
                        error_type="known_misconception",
                        misconception_id=mis_id
                    )

        # 6. Diagnostic Checks
        
        # 5a. Sign Error Check (Student answered -X instead of X, or x-3 instead of x+3)
        try:
            # Check global negative
            neg_expected = None
            if isinstance(expected_expr, sympy.Tuple):
                neg_expected = sympy.Tuple(*[-e for e in expected_expr])
            else:
                neg_expected = -expected_expr

            if self._are_equivalent(student_expr, neg_expected):
                return AnswerResult(
                    is_correct=False,
                    error_type="sign_error",
                    feedback_hint="آپ کا جواب بالکل قریب ہے۔ کیا آپ نے + یا - کی کوئی غلطی کی ہے؟"
                )
            
            # Check internal sign flips (x-3 vs x+3)
            clean_student_plus = clean_student.replace("-", "+")
            clean_expected_plus = clean_expected.replace("-", "+")
            expr_s_plus = self._parse_expression(clean_student_plus)
            expr_e_plus = self._parse_expression(clean_expected_plus)
            if expr_s_plus and expr_e_plus and self._are_equivalent(expr_s_plus, expr_e_plus):
                return AnswerResult(
                    is_correct=False,
                    error_type="sign_error",
                    feedback_hint="آپ کا جواب بالکل قریب ہے۔ کیا آپ نے + یا - کی کوئی غلطی کی ہے؟"
                )
        except:
            pass
            
        # 5b. Partial Roots Check (Student gave 1 root, expected 2)
        if isinstance(expected_expr, sympy.Tuple):
            if not isinstance(student_expr, sympy.Tuple):
                # Student gave a single expression. Is it one of the expected roots?
                for root in expected_expr:
                    if self._are_equivalent(student_expr, root):
                        return AnswerResult(
                            is_correct=False,
                            is_partial=True,
                            error_type="incomplete_solution",
                            feedback_hint="یہ ایک جڑ بالکل درست ہے! لیکن یاد رکھیں، مربعی مساوات کی دو جڑیں (roots) ہوتی ہیں۔ دوسری جڑ کیا ہوگی؟"
                        )
            else:
                # Student gave multiple roots, check if they got at least one right
                correct_count = sum(
                    1 for s_root in student_expr 
                    if any(self._are_equivalent(s_root, e_root) for e_root in expected_expr)
                )
                if correct_count > 0 and correct_count < len(expected_expr):
                     return AnswerResult(
                        is_correct=False,
                        is_partial=True,
                        error_type="incomplete_solution",
                        feedback_hint="آپ کی ایک جڑ درست ہے۔ مساوات کو دوبارہ چیک کریں اور دوسری جڑ معلوم کریں۔"
                    )

        # 6. Completely Wrong
        return AnswerResult(is_correct=False)
