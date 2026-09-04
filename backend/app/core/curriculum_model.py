"""
AI Tutor — Curriculum Model.

Core logic engine for curriculum data. Traverses the prerequisite DAG,
resolves concepts, and validates the curriculum structure.
"""

from typing import List, Set

from app.repositories.curriculum_repo import CurriculumRepository
from app.logging import get_logger

logger = get_logger(__name__)


class CurriculumModel:
    """Business logic for curriculum concepts and prerequisites."""

    def __init__(self, repo: CurriculumRepository) -> None:
        self.repo = repo

    async def get_concept(self, concept_id: str) -> dict | None:
        """Get a single concept by ID."""
        return await self.repo.get_concept(concept_id)

    async def resolve_concept(self, hint_text: str, subject_id: str = "mathematics") -> str | None:
        """Resolve a fuzzy text string (like 'discriminant') to a concept_id."""
        if not hint_text:
            return None
            
        concepts = await self.repo.get_concepts_by_subject(subject_id)
        hint_lower = hint_text.lower()
        
        # Exact match on ID
        for c in concepts:
            if c["concept_id"] == hint_lower:
                return c["concept_id"]
                
        # Match on English or Urdu name
        for c in concepts:
            if hint_lower in c.get("name_en", "").lower() or hint_lower in c.get("name_ur", "").lower():
                return c["concept_id"]
                
        # Match on key terms
        for c in concepts:
            key_terms = c.get("key_terms", [])
            for term in key_terms:
                if hint_lower in term.lower():
                    return c["concept_id"]
                    
        return None

    async def check_cycles(self) -> bool:
        """Check if the prerequisite graph has any circular dependencies.
        
        Returns:
            True if a cycle exists, False if the graph is a valid DAG.
        """
        # Note: In a real app we'd load all edges, but since this is small:
        count = await self.repo.get_concept_count()
        if count == 0:
            return False
            
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        # We need all concept IDs to check disconnected components
        # For simplicity in this pilot, we'll assume we can get all concepts
        # by checking subjects. Mathematics is our only subject right now.
        concepts = await self.repo.get_concepts_by_subject("mathematics")
        concept_ids = [c["concept_id"] for c in concepts]
        
        async def is_cyclic(curr_id: str) -> bool:
            visited.add(curr_id)
            rec_stack.add(curr_id)
            
            prereqs = await self.repo.get_prerequisites(curr_id)
            for prereq in prereqs:
                if prereq not in visited:
                    if await is_cyclic(prereq):
                        return True
                elif prereq in rec_stack:
                    return True
                    
            rec_stack.remove(curr_id)
            return False

        for cid in concept_ids:
            if cid not in visited:
                if await is_cyclic(cid):
                    return True
                    
        return False

    async def get_missing_prerequisites(
        self, target_concept_id: str, mastered_concept_ids: Set[str]
    ) -> List[str]:
        """Find the deepest unmastered prerequisites for a target concept.
        
        Traverses the prerequisite graph (DFS). If a prerequisite is NOT in
        `mastered_concept_ids`, it recursively checks ITS prerequisites.
        Returns the deepest unmastered concepts first, so the student can
        build foundational knowledge from the bottom up.
        """
        missing_ordered = []
        visited = set()
        
        async def dfs(curr_id: str):
            if curr_id in visited:
                return
            visited.add(curr_id)
            
            # Don't drill down if they've already mastered this node
            # (unless it's the target node itself, we just check its prereqs)
            if curr_id != target_concept_id and curr_id in mastered_concept_ids:
                return
                
            prereqs = await self.repo.get_prerequisites(curr_id)
            for prereq in prereqs:
                await dfs(prereq)
                
            # Post-order traversal: add deepest dependencies first
            if curr_id != target_concept_id and curr_id not in mastered_concept_ids:
                if curr_id not in missing_ordered:
                    missing_ordered.append(curr_id)
                    
        await dfs(target_concept_id)
        return missing_ordered
