from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # Expected values: "admin" or "participant"

    @field_validator("role")
    def validate_user_role(cls, role_value: str) -> str:
        """
        Validates that the role provided during registration
        is either 'admin' or 'participant'.
        """

        allowed_roles = ["admin", "participant"]

        if role_value not in allowed_roles:
            raise ValueError(
                f"Invalid role '{role_value}'. Allowed roles are: {allowed_roles}"
            )

        return role_value


class UserLogin(BaseModel):
    username: str
    password: str


class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    quiz_id: int  

    @field_validator("correct_answer")
    def validate_correct_answer(cls, ans):
        if ans not in ["A", "B", "C", "D"]:
            raise ValueError("Correct answer must be A, B, C, or D")
        return ans

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    quiz_id: int

    class Config:
        from_attributes = True


class QuizCreate(BaseModel):
    title: str
    description: Optional[str]=None


class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]=None
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


class Answer(BaseModel):
    question_id: int
    selected_option: str  # A / B / C / D

    @field_validator("selected_option")
    def validate_option(cls, ans):
        if ans not in ["A", "B", "C", "D"]:
            raise ValueError("Option must be A, B, C, or D")
        return ans


class AttemptRequest(BaseModel):
    quiz_id: int
    answers: List[Answer]