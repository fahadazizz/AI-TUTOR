The first version should have one clear job:

An Urdu-speaking personal tutor for a Class 10 student that teaches the actual syllabus, explains concepts step by step, detects misunderstanding, gives guided practice, checks answers, and adapts the next lesson to the student's weaknesses.

The student should be able to say:

"مجھے یہ سوال سمجھ نہیں آ رہا۔"

or:

"مجھے quadratic equation سمجھاؤ۔"

The system should not immediately give a long answer.

Instead:

Identify the topic.
Determine the student's current level.
Explain the prerequisite concept if required.
Teach one small concept.
Ask a simple question.
Evaluate the response.
Detect the mistake.
Give a targeted explanation.
Ask another question.
Increase difficulty gradually.
Record the student's mastery.
Continue or move to the next concept.

That is tuition.

2. The most important architectural decision

I would not make the LLM the tutor's brain.

I would make the LLM the language and reasoning engine inside a controlled tutoring system.

Conceptually:

                    STUDENT
                       │
                       ▼
              ┌─────────────────┐
              │ Student Interface│
              │ Urdu / English   │
              │ Text / Image     │
              └────────┬────────┘
                       │
                       ▼
             ┌─────────────────────┐
             │   Tutor Controller  │
             │                     │
             │ What should happen? │
             └─────────┬───────────┘
                       │
        ┌──────────────┼─────────────────┐
        │              │                 │
        ▼              ▼                 ▼
   Student Model   Curriculum Model   Session State
        │              │                 │
        └──────────────┼─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Teaching Engine │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Retrieval     Problem       LLM
       Engine       Engine      Explanation
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                ┌──────────────┐
                │ Verification │
                │ / Guardrails │
                └──────┬───────┘
                       │
                       ▼
                    STUDENT

This separation is important.

3. The system needs a Curriculum Model

This is one of the first things I would build.

Do not simply upload the entire textbook into a vector database.

Convert the curriculum into a structured representation.

For example:

Class 10
│
├── Mathematics
│
│   ├── Chapter 1: Complex Numbers
│   │
│   ├── Chapter 2: Quadratic Equations
│   │   │
│   │   ├── Concept: quadratic equation
│   │   ├── Concept: standard form
│   │   ├── Concept: roots
│   │   ├── Concept: discriminant
│   │   ├── Concept: quadratic formula
│   │   └── Concept: word problems
│   │
│   ├── Chapter 3
│   └── ...

But we go one level deeper.

Each concept gets metadata:

{
  "concept_id": "math10.quadratic.discriminant",
  "name": "Discriminant",
  "prerequisites": [
    "math10.quadratic.standard_form",
    "basic_algebra"
  ],
  "textbook_sources": [
    "chapter_2",
    "page_47"
  ],
  "difficulty": 3,
  "learning_objectives": [
    "understand discriminant",
    "calculate discriminant",
    "determine nature of roots"
  ],
  "common_misconceptions": [
    "incorrect sign of b²",
    "forgetting 4ac",
    "confusing discriminant with roots"
  ]
}

Now the AI knows that “discriminant” is not just text in a PDF.

It is a learning concept.

4. The second critical component: Student Model

This is what turns the system from chatbot → tutor.

The system needs a representation of what the student currently knows.

For example:

Student
│
├── Algebra
│   ├── Basic algebra       0.91
│   ├── Factorisation       0.72
│   ├── Quadratic equations 0.38
│   └── Discriminant        0.21
│
├── Geometry
│   ├── Angles              0.84
│   └── Circle theorems     0.43
│
└── Physics
    ├── Units               0.90
    ├── Motion              0.67
    └── Force               0.31

These numbers do not need to be perfect probabilities in V1.

Initially, a simpler mastery state is enough:

UNKNOWN
↓
INTRODUCED
↓
PRACTICING
↓
PARTIALLY_MASTERED
↓
MASTERED

Later we can implement a proper knowledge-tracing model.

5. Do not ask the LLM to decide mastery by itself

This is an important engineering rule.

Suppose the student answers:

"x = 4"

The LLM should not simply say:

Correct!

The system should know:

Question:
2x + 4 = 12

Expected:
x = 4

Student:
x = 4

Result:
CORRECT

For mathematics, use a deterministic mathematics engine where possible.

For example:

Student answer
      │
      ▼
Normalize
      │
      ▼
Math parser
      │
      ▼
Symbolic comparison
      │
      ▼
Correct / Incorrect

The LLM can then explain the result in Urdu.

This is much safer than asking an LLM to perform every calculation.

6. The system needs a Problem Engine

This is another major difference between a chatbot and tuition.

The tutor needs a structured bank of questions.

For every concept:

Concept
   │
   ├── Recognition questions
   ├── Basic questions
   ├── Procedural questions
   ├── Application questions
   ├── Board-style questions
   └── Challenge questions

Example:

Quadratic equations

Level 1

Identify which equation is quadratic.

Level 2

Identify a, b and c.

Level 3

Calculate the discriminant.

Level 4

Determine the nature of roots.

Level 5

Solve the complete equation.

Level 6

Solve a word problem using a quadratic equation.

The system should not randomly generate questions.

It should know:

Student mastery = 0.35

Next activity:
Level 2

After success:

Mastery = 0.58

Next activity:
Level 3

After repeated failure:

Mastery = 0.28

Action:
Return to prerequisite concept.

That is adaptive tutoring.

7. The actual tutoring loop

This is probably the most important workflow in the whole project.

              START
                │
                ▼
       What does student want?
                │
                ▼
         Identify concept
                │
                ▼
       Check student model
                │
                ▼
       Check prerequisites
                │
        ┌───────┴────────┐
        │                │
     Missing          Available
        │                │
        ▼                ▼
 Teach prerequisite   Teach concept
        │                │
        └───────┬────────┘
                ▼
          Ask question
                │
                ▼
        Student response
                │
                ▼
          Evaluate answer
                │
        ┌───────┼────────┐
        │       │        │
     Correct  Partial  Incorrect
        │       │        │
        ▼       ▼        ▼
     Increase  Hint    Diagnose
     mastery   │        │
        │      ▼        ▼
        │    Retry   Find misconception
        │              │
        └───────┬──────┘
                ▼
          Update student
             model
                │
                ▼
       Ready for next concept?
          │             │
         Yes            No
          │             │
          ▼             ▼
      Continue      Remediate

This loop should be implemented before fancy UI.

8. How the AI should actually teach mathematics

The tutor needs a teaching policy.

For example, if the student asks:

"یہ سوال حل کر دو"

The tutor should not always provide the entire solution.

Instead:

Step 1

Explain what the question asks.

Step 2

Ask:

"سب سے پہلے ہمیں equation کو standard form میں لانا ہے۔ کیا تم بتا سکتی ہو کہ یہاں \(a\), \(b\), اور \(c\) کیا ہیں؟"

Student answers.

Step 3

If correct:

"بالکل۔ اب discriminant کا formula کیا ہے؟"

Student answers.

Step 4

If wrong:

The system identifies:

Misconception:
Student does not understand coefficient b.

Then teaches only that.

This is called scaffolding.

Research on generative tutoring systems also shows why unrestricted answer generation is not necessarily the correct educational behavior. One recent study compared an unrestricted ChatGPT condition with a tutor that provided calibrated hints and withheld full solutions.

9. Urdu should be a first-class part of the architecture

This is especially important for your sister.

Do not translate an English tutor into Urdu at the final stage.

The tutor should internally represent the concept independently of language.

For example:

Concept:
Newton's Second Law

Internal representation:
F = ma

Student language:
Urdu

Explanation:
اردو

Formula:
Universal mathematical notation

Technical terms:
English + Urdu

The tutor can say:

"Force کو ہم F سے ظاہر کرتے ہیں، mass کو m اور acceleration کو a سے۔ اس لیے Newton's Second Law کے مطابق F = ma."

This is better than forcing every technical term into Urdu.

The student can also ask in mixed language:

"sir ye velocity aur acceleration ka difference kya hai"

The language layer should understand:

Urdu + English + Roman Urdu

That means the language pipeline should support:

Urdu
Roman Urdu
English
Urdu + English mixed
10. The textbook must be the source of truth

Suppose the student asks:

"اس chapter میں یہ کیسے solve کرنا ہے؟"

The tutor should retrieve the relevant textbook content.

Architecture:

                    TEXTBOOK
                       │
                       ▼
                PDF processing
                       │
              ┌────────┴────────┐
              │                 │
           Text             Diagrams
              │                 │
              ▼                 ▼
          Structure         Image data
              │                 │
              └────────┬────────┘
                       ▼
               Curriculum DB
                       │
                       ▼
                Retrieval layer
                       │
                       ▼
                  Tutor LLM

But I would not use vector search alone.

Use hybrid retrieval:

Question
   │
   ├── concept ID
   ├── keyword search
   ├── semantic search
   ├── textbook section
   └── prerequisite graph
              │
              ▼
        Relevant material

RAG is useful here because it lets the educational content control what the model uses, but published research also shows that RAG does not automatically remove incorrect answers.

11. We need two separate knowledge systems

This is subtle but important.

A. Curriculum knowledge
What should the student learn?

Contains:

textbook
syllabus
chapter structure
concepts
learning objectives
examples
formulas
board questions
B. Student knowledge
What does THIS student know?

Contains:

attempts
mistakes
mastery
misconceptions
response history
weak prerequisites
learning progress

Do not mix them.

12. A third system: Session memory

Then we need short-term tutoring state.

For example:

{
  "subject": "mathematics",
  "chapter": "quadratic equations",
  "concept": "discriminant",
  "current_task": "calculate_discriminant",
  "attempt_number": 2,
  "last_error": "sign_error",
  "hint_level": 1
}

This lets the tutor understand:

"اب ہم کہاں تھے؟"

without sending the entire conversation to the LLM every time.

13. The Tutor Controller

This should be the central orchestrator.

I would design its decision logic approximately like this:

def tutor_turn(student_message, student_state, session_state):

    intent = detect_intent(student_message)

    if intent == "ask_concept":
        concept = identify_concept(student_message)

        prerequisites = get_prerequisites(concept)

        missing = check_mastery(
            prerequisites,
            student_state
        )

        if missing:
            return teach_prerequisite(missing)

        return start_concept_lesson(concept)

    if intent == "answer_question":

        result = evaluate_answer(
            student_message,
            session_state.current_question
        )

        diagnosis = diagnose(result)

        update_student_model(
            student_state,
            diagnosis
        )

        return choose_next_instruction(
            result,
            diagnosis,
            student_state
        )

The LLM is then used inside functions such as:

detect_intent()
identify_concept()
generate_explanation()
diagnose_misconception()
generate_hint()
generate_feedback()

But important operations should remain deterministic.

14. What should be deterministic?

I would make these deterministic or tool-based whenever possible:

Function	Preferred method
Mathematical calculation	Symbolic/math engine
Numerical calculation	Calculator/code
Equation checking	Symbolic comparison
Correct answer	Problem database / solver
Curriculum mapping	Curriculum DB
Textbook citation	Retrieval
Prerequisite relationship	Curriculum graph
Student mastery update	Tutoring algorithm
Question difficulty	Problem metadata
Board pattern	Question database

The LLM should mainly handle:

Function	LLM
Urdu explanation	Yes
Conversational interaction	Yes
Explanation adaptation	Yes
Hint generation	Yes
Misconception explanation	Yes
Natural-language understanding	Yes
Socratic questioning	Yes

This division greatly reduces hallucination risk.

15. Physics needs a slightly different engine

Physics is not only question answering.

Suppose:

"ایک گاڑی 20 m/s کی رفتار سے چل رہی ہے..."

The tutor needs:

Given:
v = 20 m/s

Find:
...

Formula:
...

Substitution:
...

Calculation:
...

Unit:
...

And it should check:

formula
↓
units
↓
substitution
↓
calculation
↓
final answer

So physics should have a problem-solving representation.

For example:

{
  "type": "numerical",
  "concept": "kinematics",
  "given": {
    "initial_velocity": 10,
    "final_velocity": 30,
    "time": 5
  },
  "find": "acceleration",
  "formula": "a=(v-u)/t",
  "answer": 4,
  "unit": "m/s²"
}

The LLM can teach the student how to reach the answer.

16. The system should teach different subjects differently

Do not create one generic TutorAgent.

The pedagogy should depend on the subject.

Mathematics
Concept
→ worked example
→ guided problem
→ independent problem
→ variation
→ mastery
Physics
Concept
→ physical intuition
→ formula
→ units
→ worked example
→ numerical problem
→ conceptual question
Chemistry
Concept
→ definition
→ mechanism/process
→ example
→ equation
→ recall
→ application
Biology
Concept
→ explanation
→ diagram
→ terminology
→ recall
→ application
Urdu / English
Reading
→ comprehension
→ vocabulary
→ grammar
→ writing
→ correction

This is why the architecture needs a subject pedagogy layer.

17. A better architecture

Putting everything together:

                         STUDENT
                            │
                            ▼
                 ┌────────────────────┐
                 │ Student Application│
                 │                    │
                 │ Urdu/Roman Urdu    │
                 │ Text                │
                 │ Image              │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Conversation Layer │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │  TUTOR CONTROLLER  │
                 │                    │
                 │ Decide next action │
                 └─────────┬──────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
 ┌────────────────┐ ┌───────────────┐ ┌───────────────┐
 │ Student Model  │ │ Curriculum    │ │ Session State │
 │                │ │ Model         │ │               │
 │ mastery        │ │ concepts      │ │ current task  │
 │ mistakes       │ │ prerequisites │ │ current topic │
 │ misconceptions │ │ objectives    │ │ hints         │
 └───────┬────────┘ └───────┬───────┘ └───────┬───────┘
         │                  │                 │
         └──────────────────┼─────────────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Teaching Strategy │
                  └─────────┬─────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌────────────┐ ┌───────────┐
        │ RAG      │  │ Problem    │ │ LLM       │
        │ Engine   │  │ Engine     │ │ Engine    │
        └────┬─────┘  └─────┬──────┘ └─────┬─────┘
             │              │              │
             ▼              ▼              ▼
        Textbook       Question DB     Urdu Tutor
        Curriculum     Math Solver     Explanation
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                   ┌─────────────────┐
                   │ Verification    │
                   │ & Safety Layer  │
                   └────────┬────────┘
                            │
                            ▼
                         STUDENT

That is the architecture I would use.

18. The biggest mistake we should avoid

Do not start by building:

mobile app
fancy UI
voice assistant
multi-agent swarm
autonomous agents
MCP
complex vector database
avatar
animations
RAG over 10 books
all Class 10 subjects

Those are not the core problem.

We need to prove:

Can the system teach one difficult concept to one real student better than a normal chatbot?

If we cannot prove that, adding 20 agents will not fix it.


21. Misconception detection is where this becomes powerful

Suppose she repeatedly writes:

(a+b)² = a²+b²

A normal chatbot may correct it.

Our tutor should record:

Misconception:
square of binomial

Evidence:
3 incorrect attempts

Severity:
high

Prerequisite:
algebraic identities

Recommended intervention:
visual explanation + worked example + 3 targeted questions

Then the tutor changes its teaching strategy.

This is much more valuable than remembering the conversation.

22. We should maintain a misconception library

For every major concept:

Concept
│
├── Correct understanding
│
├── Common mistake #1
├── Common mistake #2
├── Common mistake #3
│
├── Diagnostic question
│
└── Remediation strategy

Example:

Quadratic formula

Misconception:
Student thinks ± is optional.

Diagnostic:
Ask student to identify both roots.

Remediation:
Explain why square root produces two values.

Practice:
Generate three controlled examples.

This can become one of the most valuable parts of the system.

23. We also need an assessment system

Every session should produce structured data.

For example:

{
  "student": "student_01",
  "subject": "mathematics",
  "concept": "quadratic_formula",

  "questions_attempted": 8,
  "correct": 5,

  "mistakes": [
    "sign_error",
    "substitution_error"
  ],

  "mastery_before": 0.42,
  "mastery_after": 0.63,

  "recommended_next": [
    "quadratic_formula_practice"
  ]
}

Then the next day:

"کل ہم quadratic formula پر کام کر رہے تھے۔ آج پہلے دیکھتے ہیں کہ تمہیں وہ کتنا یاد ہے۔"

Give a short retrieval test.

This creates continuity.

24. Spaced practice should eventually be included

Learning should not end when she answers three questions correctly.

For example:

Day 1
Learn concept

Day 2
5-minute review

Day 4
2 questions

Day 7
mixed practice

Day 14
board-style problem

The student model determines what needs review.

This turns the system from:

question-answer machine

into:

learning system.

25. Board preparation should be a separate layer

There are actually two goals:

Understanding
"مجھے concept سمجھاؤ"
Examination
"مجھے board exam کے لیے تیار کرو"

They are not identical.

The system should eventually have:

LEARNING MODE
    ↓
CONCEPT MASTERY
    ↓
PRACTICE MODE
    ↓
EXAM MODE
    ↓
MOCK TEST
    ↓
ERROR ANALYSIS
    ↓
REMEDIAL LESSON

The exam mode can include:

textbook questions
exercise questions
past-paper questions
timed questions
short questions
long questions
numerical problems
MCQs

But only after the core tutor works.

26. We should also support textbook images

This matters for Pakistani textbooks because many questions contain diagrams.

The student should eventually be able to take a picture:

"یہ سوال سمجھ نہیں آ رہا۔"

The pipeline:

Camera/Image
     ↓
OCR / Vision
     ↓
Question extraction
     ↓
Concept identification
     ↓
Textbook retrieval
     ↓
Tutor

For a geometry question:

Image
 ↓
Diagram understanding
 ↓
Known values
 ↓
Required quantity
 ↓
Relevant theorem
 ↓
Guided solution

But again: not V1.

27. Voice can come later

Voice would be useful because the student may find typing difficult.

Eventually:

Student speaks Urdu
       ↓
Speech-to-text
       ↓
Tutor
       ↓
Urdu response
       ↓
Text-to-speech

But voice is not required to prove the tutor.

First prove the educational loop with text.
