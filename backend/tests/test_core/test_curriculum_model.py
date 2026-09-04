"""
AI Tutor — Tests for Curriculum Model.
"""

import pytest

from app.core.curriculum_model import CurriculumModel


class MockCurriculumRepo:
    """A mock repository to test graph traversal without a real database."""
    def __init__(self, graph: dict[str, list[str]]):
        self.graph = graph
        
    async def get_concept_count(self) -> int:
        return len(self.graph)
        
    async def get_concepts_by_subject(self, subject: str) -> list[dict]:
        return [{"concept_id": k} for k in self.graph.keys()]
        
    async def get_prerequisites(self, concept_id: str) -> list[str]:
        return self.graph.get(concept_id, [])


@pytest.mark.asyncio
async def test_curriculum_cycle_detection():
    # Valid DAG
    repo = MockCurriculumRepo({
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
        "D": []
    })
    model = CurriculumModel(repo)
    assert await model.check_cycles() is False
    
    # Cyclic Graph (A -> B -> C -> A)
    repo_cyclic = MockCurriculumRepo({
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]
    })
    model_cyclic = CurriculumModel(repo_cyclic)
    assert await model_cyclic.check_cycles() is True


@pytest.mark.asyncio
async def test_get_missing_prerequisites_all_missing():
    """
    DAG: A depends on B and C. B depends on D.
    If student knows nothing, getting missing for A should yield D, B, C.
    (Deepest first).
    """
    repo = MockCurriculumRepo({
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": []
    })
    model = CurriculumModel(repo)
    
    missing = await model.get_missing_prerequisites("A", mastered_concept_ids=set())
    assert missing == ["D", "B", "C"]


@pytest.mark.asyncio
async def test_get_missing_prerequisites_partial_mastery():
    """
    DAG: A depends on B and C. B depends on D.
    If student already mastered D and C, missing for A should be just B.
    """
    repo = MockCurriculumRepo({
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": []
    })
    model = CurriculumModel(repo)
    
    missing = await model.get_missing_prerequisites("A", mastered_concept_ids={"D", "C"})
    assert missing == ["B"]


@pytest.mark.asyncio
async def test_get_missing_prerequisites_cuts_off_search():
    """
    If a student has mastered a mid-level concept, we shouldn't even check
    its prerequisites because mastery implies prerequisite knowledge.
    DAG: A -> B -> C -> D
    Mastered: B. 
    Missing for A should be empty because B is mastered. C and D are assumed known.
    """
    repo = MockCurriculumRepo({
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": []
    })
    model = CurriculumModel(repo)
    
    missing = await model.get_missing_prerequisites("A", mastered_concept_ids={"B"})
    assert missing == []
