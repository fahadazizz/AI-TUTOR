"""Tests for the Guardrail layer."""

from app.tutor.guardrails import Guardrails


def test_guardrail_passes_valid_text():
    guard = Guardrails()
    res = guard.check_response("یہ ایک اچھا جواب ہے۔", {})
    assert res.passed is True


def test_guardrail_blocks_hindi_script():
    guard = Guardrails()
    res = guard.check_response("यह एक अच्छा जवाब है।", {})
    assert res.passed is False
    assert "Hindi" in res.reason


def test_guardrail_blocks_long_text():
    guard = Guardrails()
    res = guard.check_response("A" * 801, {})
    assert res.passed is False
    assert "too long" in res.reason


def test_guardrail_blocks_answer_leak():
    guard = Guardrails()
    ctx = {"session": {"current_question_expected_answer": "4.5"}}
    res = guard.check_response("The answer is 4.5!", ctx)
    assert res.passed is False
    assert "leaked" in res.reason


def test_guardrail_ignores_short_answer_leaks():
    guard = Guardrails()
    # A 1-character answer might false-positive too much, 
    # but based on our logic, it requires length > 1
    ctx = {"session": {"current_question_expected_answer": "4"}}
    res = guard.check_response("The answer is 4!", ctx)
    assert res.passed is True
