"""
AI Tutor — Tests for the Math Checking Engine.

Verifies SymPy equivalence, sign errors, partial roots, and parse handling.
"""

from app.core.math_checker import MathChecker


class TestMathChecker:
    checker = MathChecker()

    def test_exact_number_match(self):
        res = self.checker.check_answer("3", "3")
        assert res.is_correct
        assert not res.is_partial

    def test_fraction_equivalence(self):
        res = self.checker.check_answer("1.5", "3/2")
        assert res.is_correct

    def test_algebraic_equivalence(self):
        # (x+1)^2 should match x^2 + 2x + 1
        res = self.checker.check_answer("(x+1)^2", "x^2 + 2x + 1")
        assert res.is_correct

        # 3x - 5 = 10 should match 3x = 15
        res = self.checker.check_answer("3x - 5 = 10", "3x = 15")
        assert res.is_correct

    def test_input_normalization(self):
        # x2 should normalize to x**2
        res = self.checker.check_answer("x2 - 4", "x^2 - 4")
        assert res.is_correct
        
        # Unicode superscripts
        res = self.checker.check_answer("x² - 4", "x^2 - 4")
        assert res.is_correct

        # Implicit multiplication
        res = self.checker.check_answer("2x + 4", "2*x + 4")
        assert res.is_correct

    def test_sign_error_detection(self):
        res = self.checker.check_answer("-5", "5")
        assert not res.is_correct
        assert res.error_type == "sign_error"
        assert "غلطی" in res.feedback_hint

        res = self.checker.check_answer("x - 3", "x + 3")
        assert not res.is_correct
        assert res.error_type == "sign_error"

    def test_multiple_roots_exact(self):
        res = self.checker.check_answer("x = 3, x = 5", "x=3, x=5")
        assert res.is_correct

        # Order shouldn't matter
        res = self.checker.check_answer("5, 3", "3, 5")
        assert res.is_correct

    def test_multiple_roots_partial(self):
        # Expected two roots, student provided one correct root
        res = self.checker.check_answer("3", "3, 5")
        assert not res.is_correct
        assert res.is_partial
        assert res.error_type == "incomplete_solution"
        assert "دوسری جڑ" in res.feedback_hint

    def test_parse_error_handling(self):
        # Garbage input shouldn't crash, should return parse_error
        res = self.checker.check_answer("x + + /", "3")
        assert not res.is_correct
        assert res.error_type == "parse_error"

    def test_word_problem_fallback(self):
        # If expected is text, just do string match fallback
        res = self.checker.check_answer("yes", "yes", "recognition")
        assert res.is_correct

        res = self.checker.check_answer("no", "yes", "recognition")
        assert not res.is_correct
