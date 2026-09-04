"""
AI Tutor — Tests for Question Selector.
"""

import pytest
import uuid

from app.core.question_selector import QuestionSelector
from app.models.enums import MasteryState
from app.models.mastery import ConceptMastery


class MockCurriculumRepo:
    async def get_questions_by_concept(self, concept_id: str) -> list[dict]:
        # Return a mock bank of questions across difficulties 1-6
        return [
            {"question_id": f"q{i}", "concept_id": concept_id, "difficulty": i}
            for i in range(1, 7)
        ]


@pytest.mark.asyncio
async def test_unknown_gets_difficulty_2():
    repo = MockCurriculumRepo()
    selector = QuestionSelector(repo)
    
    q = await selector.select_next_question("c1", None, set())
    assert q["difficulty"] == 2


@pytest.mark.asyncio
async def test_struggling_gets_difficulty_1():
    repo = MockCurriculumRepo()
    selector = QuestionSelector(repo)
    
    student_id = uuid.uuid4()
    mastery = ConceptMastery(student_id=student_id, concept_id="c1", mastery_state=MasteryState.STRUGGLING)
    q = await selector.select_next_question("c1", mastery, set())
    assert q["difficulty"] == 1


@pytest.mark.asyncio
async def test_practicing_escalates_difficulty():
    repo = MockCurriculumRepo()
    selector = QuestionSelector(repo)
    
    student_id = uuid.uuid4()
    # 0 correct -> diff 2
    m1 = ConceptMastery(student_id=student_id, concept_id="c1", mastery_state=MasteryState.PRACTICING, consecutive_correct=0)
    q1 = await selector.select_next_question("c1", m1, set())
    assert q1["difficulty"] == 2
    
    # 2 correct -> diff 4
    m2 = ConceptMastery(student_id=student_id, concept_id="c1", mastery_state=MasteryState.PRACTICING, consecutive_correct=2)
    q2 = await selector.select_next_question("c1", m2, set())
    assert q2["difficulty"] == 4


@pytest.mark.asyncio
async def test_filters_seen_questions():
    repo = MockCurriculumRepo()
    selector = QuestionSelector(repo)
    
    # We ask for diff 2. It should normally return q2.
    # But if q2 is seen, it returns the next closest (q1 or q3).
    q = await selector.select_next_question("c1", None, seen_question_ids={"q2"})
    assert q["question_id"] != "q2"
    assert q["difficulty"] in (1, 3)


@pytest.mark.asyncio
async def test_exhausted_bank_falls_back():
    repo = MockCurriculumRepo()
    selector = QuestionSelector(repo)
    
    # Student has seen every single question
    seen = {f"q{i}" for i in range(1, 7)}
    
    # It shouldn't crash, it should return a previously seen question
    q = await selector.select_next_question("c1", None, seen)
    assert q is not None
