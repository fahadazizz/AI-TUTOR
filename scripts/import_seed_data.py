"""
AI Tutor — Seed Data Import Script.

Imports curriculum data from the JSON seed files into the PostgreSQL
database. This script is IDEMPOTENT — safe to run multiple times.
All inserts use ON CONFLICT ... DO UPDATE (upsert pattern).

Usage:
    python -m scripts.import_seed_data

Requires:
    - DATABASE_URL set in .env or environment
    - Seed JSON files in data/curriculum/mathematics/
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.connection import create_pool, close_pool, run_migrations
from app.repositories.curriculum_repo import CurriculumRepository
from app.logging import setup_logging, get_logger

logger = get_logger(__name__)

# ── Path Configuration ──────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "curriculum" / "mathematics"

CONCEPTS_FILE = DATA_DIR / "concepts.json"
PREREQUISITES_FILE = DATA_DIR / "prerequisites.json"
QUESTIONS_DIR = DATA_DIR / "questions"
MISCONCEPTIONS_FILE = DATA_DIR / "misconceptions.json"


def load_json(filepath: Path) -> dict:
    """Load a JSON file with UTF-8 encoding."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


async def import_subjects(repo: CurriculumRepository) -> None:
    """Create the mathematics subject entry."""
    await repo.upsert_subject(
        subject_id="mathematics",
        name_en="Mathematics",
        name_ur="ریاضی",
    )
    logger.info("imported_subject", subject="mathematics")


async def import_concepts(repo: CurriculumRepository) -> int:
    """Import concepts from concepts.json."""
    data = load_json(CONCEPTS_FILE)
    count = 0

    for concept in data["concepts"]:
        await repo.upsert_concept(
            concept_id=concept["concept_id"],
            subject_id=concept.get("subject", "mathematics"),
            chapter=concept["chapter"],
            chapter_name=concept["chapter_name"],
            name_en=concept["name_en"],
            name_ur=concept["name_ur"],
            difficulty=concept["difficulty"],
            textbook_page=concept.get("textbook_page"),
            pedagogy_type=concept["pedagogy_type"],
            learning_objectives=concept.get("learning_objectives", []),
            formulas=concept.get("formulas", []),
            explanation_ur=concept["explanation_ur"],
            key_terms=[kt if isinstance(kt, dict) else kt for kt in concept.get("key_terms", [])],
            worked_examples=concept.get("worked_examples", []),
        )
        count += 1

    logger.info("imported_concepts", count=count)
    return count


async def import_prerequisites(repo: CurriculumRepository) -> int:
    """Import prerequisite edges from prerequisites.json."""
    data = load_json(PREREQUISITES_FILE)
    count = 0

    for edge in data["edges"]:
        for prereq_id in edge["prerequisites"]:
            await repo.upsert_prerequisite(edge["concept_id"], prereq_id)
            count += 1

    logger.info("imported_prerequisites", count=count)
    return count


async def import_questions(repo: CurriculumRepository) -> int:
    """Import questions from all question bank JSON files."""
    count = 0

    for question_file in sorted(QUESTIONS_DIR.glob("*.json")):
        data = load_json(question_file)

        for q in data["questions"]:
            # Convert solution_steps to the format expected by the DB
            solution_steps = []
            for step in q.get("solution_steps", []):
                solution_steps.append({
                    "step": step.get("step", 0),
                    "description_ur": step.get("description_ur", ""),
                    "math": step.get("math", ""),
                })

            await repo.upsert_question(
                question_id=q["question_id"],
                concept_id=q["concept_id"],
                difficulty=q["difficulty"],
                question_type=q["question_type"],
                question_text_ur=q["question_text_ur"],
                question_text_en=q["question_text_en"],
                expected_answer=q["expected_answer"],
                answer_tolerance=q.get("answer_tolerance"),
                expected_answer_unit=q.get("expected_answer_unit"),
                solution_steps=solution_steps,
                hints=q.get("hints", []),
                tags=q.get("tags", []),
            )
            count += 1

        logger.info("imported_questions_file", file=question_file.name, count=count)

    logger.info("imported_questions_total", count=count)
    return count


async def import_misconceptions(repo: CurriculumRepository) -> int:
    """Import misconceptions from misconceptions.json."""
    data = load_json(MISCONCEPTIONS_FILE)
    count = 0

    for m in data["misconceptions"]:
        await repo.upsert_misconception(
            misconception_id=m["misconception_id"],
            concept_id=m["concept_id"],
            subject_key=m.get("subject", "mathematics"),
            description_en=m["description_en"],
            description_ur=m["description_ur"],
            severity=m["severity"],
            error_patterns=m.get("error_patterns", []),
            prerequisite_gap=m.get("prerequisite_gap"),
            remediation_strategy=m["remediation_strategy"],
            remediation_explanation_ur=m["remediation_explanation_ur"],
            diagnostic_question_ids=m.get("diagnostic_question_ids", []),
            practice_question_ids=m.get("practice_question_ids", []),
        )
        count += 1

    logger.info("imported_misconceptions", count=count)
    return count


async def main() -> None:
    """Run the complete seed data import pipeline."""
    setup_logging()
    logger.info("seed_import_starting")

    try:
        await create_pool()
        await run_migrations()
    except Exception as e:
        logger.error("db_connection_failed", error=str(e))
        print(f"\n❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is set correctly.")
        print("   See backend/.env.example for the expected format.\n")
        return

    repo = CurriculumRepository()

    try:
        # Order matters: subjects → concepts → prerequisites → questions → misconceptions
        await import_subjects(repo)
        concepts = await import_concepts(repo)
        prereqs = await import_prerequisites(repo)
        questions = await import_questions(repo)
        misconceptions = await import_misconceptions(repo)

        print(f"\n✅ Seed data import complete!")
        print(f"   Subjects:       1")
        print(f"   Concepts:       {concepts}")
        print(f"   Prerequisites:  {prereqs}")
        print(f"   Questions:      {questions}")
        print(f"   Misconceptions: {misconceptions}\n")

    except Exception as e:
        logger.error("import_failed", error=str(e))
        print(f"\n❌ Import failed: {e}\n")
        raise
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
