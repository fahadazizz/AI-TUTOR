from pydantic import BaseModel
import uuid

class AssessmentAnswer(BaseModel):
    question_id: str
    concept_id: str
    student_answer: str

class AssessmentSubmitRequest(BaseModel):
    student_id: uuid.UUID
    answers: list[AssessmentAnswer]
