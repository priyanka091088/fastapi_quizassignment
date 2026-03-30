from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models, schemas, auth
from app.auth import require_admin, require_participant
from app.models import Quiz, Question
from app.schemas import AttemptRequest,QuizResponse

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = auth.create_access_token({
        "sub": db_user.username,
        "role": db_user.role
    })

    return {"access_token": token, "token_type": "bearer"}

@app.post("/quizzes", response_model=schemas.QuizResponse)
def create_quiz(
    quiz: schemas.QuizCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # 🔐 Only admin allowed
):
    """
    Create a new quiz (Admin only)
    """

    # Create quiz object
    new_quiz = models.Quiz(title=quiz.title,description=quiz.description)

    # Save to DB
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return new_quiz

@app.post("/questions")
def create_question(
    question_data: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new question and assign it to a quiz (Admin only)
    """

    # Check if quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == question_data.quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Create new question object
    new_question = Question(
        question_text=question_data.question_text,
        option_a=question_data.option_a,
        option_b=question_data.option_b,
        option_c=question_data.option_c,
        option_d=question_data.option_d,
        correct_answer=question_data.correct_answer,
        quiz_id=question_data.quiz_id
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question

@app.put("/questions/{question_id}")
def update_question(
    question_id: int,
    updated_data: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Update an existing question (Admin only)
    """

    # Fetch existing question
    existing_question = db.query(Question).filter(Question.id == question_id).first()

    if not existing_question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Validate quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == updated_data.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Update fields
    existing_question.question_text = updated_data.question_text
    existing_question.option_a = updated_data.option_a
    existing_question.option_b = updated_data.option_b
    existing_question.option_c = updated_data.option_c
    existing_question.option_d = updated_data.option_d
    existing_question.correct_answer = updated_data.correct_answer
    existing_question.quiz_id = updated_data.quiz_id

    db.commit()
    db.refresh(existing_question)

    return existing_question

@app.delete("/quizzes/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Delete a quiz by ID (Admin only)
    """

    # Fetch quiz from database
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    # If quiz does not exist → return 404
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Delete quiz
    db.delete(quiz)
    db.commit()

    return {"message": "Quiz deleted successfully"}

@app.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Delete a question by ID (Admin only)
    """

    # Fetch question
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()

    return {"message": "Question deleted successfully"}

#Participant's APIs
@app.get("/quizzes")
def get_all_quizzes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_participant)
):
    """
    Get list of all quizzes (Participant only)
    """

    quizzes = db.query(Quiz).all()
    return quizzes

@app.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_participant)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return quiz

@app.post("/submit")
def attempt_quiz(
    attempt: AttemptRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_participant)
):
    """
    Submit quiz answers and calculate score
    """

    # Check quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    score = 0
    total_questions = len(quiz.questions)

    # Convert answers to dict for easy lookup
    answer_map = {a.question_id: a.selected_option for a in attempt.answers}

    # Evaluate answers
    for question in quiz.questions:
        if question.id in answer_map:
            if answer_map[question.id] == question.correct_answer:
                score += 1

    # SAVE RESULT HERE
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()

    new_result = models.Result(
        user_id=user.id,
        quiz_id=attempt.quiz_id,
        score=score
    )

    db.add(new_result)
    db.commit()

    return {
        "quiz_id": attempt.quiz_id,
        "score": score,
        "total": total_questions
    }

@app.get("/result/{quiz_id}")
def get_result(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_participant)
):
    result = db.query(models.Result).filter(
        models.Result.quiz_id == quiz_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    return result