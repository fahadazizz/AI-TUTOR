# Generalized AI Tutor — Master Blueprint Architecture

**A single global reference architecture for a multi-subject, multi-level, budget-constrained AI tutoring system**

---

## 0. Purpose of this document

This document is the master blueprint for evolving the original Urdu-speaking Class 10 tutor (built for one student, one subject) into a **Generalized AI Tutor** — a system that can teach any subject, at any grade level within a curriculum, to any student, while staying within four hard constraints. It is meant to be the single reference you build against: every component, every workflow, every data boundary, and every constraint is defined here once, so that adding a new subject, grade, or feature later means extending this document, not rewriting it.

The document has five parts:

1. Guiding principles and hard constraints
2. The master architecture (every component, deeply explained)
3. The core tutoring workflow (how a single turn actually happens, end to end)
4. The multi-subject generalization strategy
5. A validation section — an honest, critical review of where this architecture is strong, where it is fragile, and what will break first

---

## 1. Guiding principles

These five principles are the foundation everything else is derived from. Whenever a design decision is unclear later, it should be resolved by asking which option best satisfies these.

**Principle 1 — The LLM is a component, not the brain.** The system decides what should happen next: which concept to teach, whether the student is ready, whether an answer is correct, what mistake was made. The LLM is called *inside* that decision process to do language and reasoning work — explaining, phrasing, rephrasing, holding a Socratic exchange — never to make the pedagogical decision itself. This is the single most important idea in the whole design, because it is what separates a tutor from a chatbot with a system prompt.

**Principle 2 — Deterministic wherever possible, generative only where necessary.** Anything that can be checked with a rule, a symbolic engine, a rubric, or a lookup table should be. The LLM is reserved for the parts of tutoring that are genuinely linguistic or judgment-based: explaining a concept in the student's language, generating a hint calibrated to a specific mistake, holding a natural conversation. This reduces hallucination risk and — just as importantly under a free-tier budget — reduces how often the LLM needs to be called at all.

**Principle 3 — Subject-agnostic core, subject-specific plugins.** The orchestration logic (deciding what to teach next, tracking mastery, running the tutoring loop) must never contain subject-specific code or knowledge. Everything that differs between Mathematics, Physics, Biology, and Urdu language arts lives behind a small, well-defined plugin interface. A new subject should be addable by writing a new plugin, without touching the core at all.

**Principle 4 — Generate once, reuse forever.** Under a free-tier LLM budget, the sustainable pattern is not "call the LLM every time a student needs an explanation." It is "call the LLM once per concept, review the output, store it, and serve it to every student who needs it from then on." Live LLM calls are reserved for the parts that genuinely must be personalized in the moment.

**Principle 5 — The tutor must always be able to respond.** Because the system depends on free and low-cost external APIs that can be rate-limited or briefly unavailable, no student-facing failure mode should exist where the tutor simply cannot answer. There must always be a deterministic, pre-authored fallback beneath every generative step.

---

## 2. Hard constraints

These are fixed boundaries, not preferences. Every component below is designed to respect all four simultaneously.

**Constraint 1 — No high-end model APIs.** The system must run entirely on free-tier or very low-cost API access (for example, free tiers on fast hosted-inference providers, or a paid tier priced in fractions of a cent per thousand tokens). No component may assume access to a frontier-tier, expensive model as a load-bearing dependency.

**Constraint 2 — No image-generation models.** The system may never rely on an image-generation model to produce visuals. This does not mean the tutor is text-only — it means every visual (diagrams, graphs, equations) must be produced by a different technique: rendering, plotting from data, or code-based vector graphics, all covered in the Visual Engine section below.

**Constraint 3 — No live avatar or live tutor.** There is no synthetic on-screen presence, no real-time face, no persona performing the tutoring live. The interface is a structured application, not a simulated person.

**Constraint 4 — No live recording or real-time tutoring session.** The system does not process live audio or video, and does not operate as a real-time in-session tutor watching a student work in real time. All interaction happens through the turn-based interface described below.

Two supporting realities shape the design further, though they are not hard constraints in the same sense:

- **Local hardware is not a serving environment.** Development happens on modest local hardware, which is more than sufficient for building and testing the application, but the system's live components (LLM calls, hosted retrieval, the student-facing app) must run against cloud-hosted free or cheap services rather than local inference — there is no expectation of running a large model locally.
- **One board, multiple subjects, built to expand.** V1 targets a single curriculum board across multiple subjects and grade levels, with the schema designed so that a second board can be added later without restructuring anything already built.

---

## 3. Master architecture — full pipeline overview

At the highest level, every student turn moves through the same nine components, in the same order, regardless of subject. This is the diagram to keep pinned above your desk — everything else in this document is a deep dive into one box from this picture.

```
                                   STUDENT
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     STUDENT APPLICATION   │
                         │  Chat surface + Dashboard │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    CONVERSATION LAYER     │
                         │  Language detection, mix   │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      TUTOR CONTROLLER     │
                         │   Decides what happens     │
                         │          next              │
                         └────────────┬─────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
     ┌─────────────────┐   ┌─────────────────────┐   ┌─────────────────┐
     │  STUDENT MODEL   │   │  CURRICULUM MODEL    │   │  SESSION STATE   │
     │  What THIS       │   │  What CAN be         │   │  Where we are    │
     │  student knows   │   │  taught, and how      │   │  right now       │
     └────────┬─────────┘   └──────────┬───────────┘   └────────┬─────────┘
              └───────────────────────┼───────────────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │    PEDAGOGY ROUTER        │
                         │  Picks the teaching plugin │
                         │  for this subject type     │
                         └────────────┬─────────────┘
                                      │
        ┌─────────────────┬──────────┼──────────┬─────────────────┐
        ▼                 ▼          ▼          ▼                 ▼
 ┌─────────────┐  ┌──────────────┐ ┌──────────┐ ┌─────────────┐  ┌───────────┐
 │ CONTENT BANK│  │  VERIFIER    │ │  VISUAL  │ │  LLM ENGINE  │  │MISCONCEPT-│
 │ Pre-built   │  │  ENGINE      │ │  ENGINE  │ │  Budget-     │  │ION LIBRARY│
 │ lessons     │  │  Checks      │ │  Diagrams,│ │  routed,     │  │ Known     │
 │ per concept │  │  answers     │ │  graphs   │ │  cached      │  │ mistakes  │
 └──────┬──────┘  └──────┬───────┘ └────┬─────┘ └──────┬───────┘  └─────┬─────┘
        └────────────────┴──────────────┴──────────────┴────────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  VERIFICATION & SAFETY    │
                         │  LAYER                     │
                         │  Nothing reaches the       │
                         │  student unchecked         │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │        RESPONSE           │
                         │  Text + visuals + next     │
                         │  question                  │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                                   STUDENT
```

Two things about this diagram are structural, not incidental. First, the three boxes in the middle row — Student Model, Curriculum Model, Session State — are three **separate** stores, never merged, because they answer three different questions ("what does this student know", "what exists to be taught", "where are we in this specific conversation"). Second, everything below the Pedagogy Router is a set of interchangeable engines the router calls into; none of them know or care which subject is being taught. That separation is what makes the system generalizable rather than a pile of if-Math-then / if-Physics-then logic.

---

## 4. Component deep dive

### 4.1 Student Application (the interface layer)

The application has two surfaces, and this split is deliberate — it is one of the main things that keeps this from feeling like a chatbot.

The **chat surface** is where the actual tutoring conversation happens: the student asks something or answers a question, the tutor responds. But unlike a plain chatbot, every message on this surface can carry more than text — an equation rendered properly instead of typed with asterisks and carets, a graph or diagram sitting inline where it's relevant, and for objective questions, structured input controls (multiple-choice buttons, a numeric field with a unit selector) rather than forcing the student to type everything freeform. Freeform text input is always available for open-ended answers and questions, but objective questions should offer the faster, less error-prone structured option too.

The **dashboard surface** is a persistent, separate view the student (or your sister, or a parent) can check at any time, independent of the current conversation. It shows the concept tree with mastery levels marked, which concepts are ready to start, which are flagged with a recorded misconception, and a simple sense of progress over time. This surface is what makes the system *feel* like ongoing tuition rather than a series of disconnected Q&A sessions — chat history alone never conveys "I am getting better at this," but a mastery map does.

Both surfaces read from the same underlying stores (Student Model, Curriculum Model) so they are always consistent with each other; the dashboard is not a separate reporting system bolted on afterward.

### 4.2 Conversation Layer

This sits between the raw student application and the Tutor Controller, and its only job is language handling. Your original insight — that Urdu, Roman Urdu, English, and mixed-language input must all be understood, and that technical terms should stay in their natural form rather than being force-translated — is treated as a first-class architectural layer here, not an afterthought bolted onto the LLM prompt.

Concretely, this layer detects which language or mixture the student is using, normalizes mixed-script input into something the rest of the system can reason about consistently, and — critically — keeps the **concept representation itself language-independent**. A concept like "Newton's Second Law" is stored once, with its formula, prerequisites, and metadata all in a neutral, language-agnostic form; only the explanation text is authored per language. This means adding support for a new language later is a content-authoring task (write explanations in that language), not a re-architecture.

### 4.3 Tutor Controller

This is the central orchestrator, and the only component that talks to every other component. Its job on every turn is to figure out, from the student's message and everything currently known about them, what should happen next: teach a new concept, ask a follow-up question, evaluate an answer just given, deliver a hint, or diagnose a mistake and remediate.

The decision logic itself is a sequence of questions the controller works through: What is the student actually asking for — a new concept, help with something specific, or are they answering a question that's already pending? If it's a new concept, does the student already have the prerequisites, according to the Student Model, or does a prerequisite need to be taught first? If it's an answer, what does the Verifier Registry say about whether it's correct, partially correct, or wrong — and if wrong, what does that specific wrong answer suggest about the underlying misconception? Every one of these questions is answered by consulting one of the three knowledge stores or one of the engines below; the controller itself holds no subject knowledge and makes no judgment calls about correctness — it only sequences the process and decides what happens as a result of what other components report back.

This is also the only component permitted to write to the Student Model and Session State. Centralizing writes here — rather than letting the LLM or any engine update mastery scores directly — is what keeps the Student Model trustworthy: mastery updates always follow the same rules, regardless of which subject or which engine produced the underlying evaluation.

### 4.4 Curriculum Model — what can be taught, and how

This store answers one question: what exists in this curriculum, and how does it relate to everything else in it? It is not the textbook — it is a structured map built *from* the textbook.

Every concept in the curriculum is represented with the same fields, regardless of subject: an identifier that encodes the board, grade, subject, and chapter it belongs to; the concept's prerequisites, so the system always knows what must be true before this concept can be taught; the textbook sources it comes from, for citation and retrieval; a difficulty rating; the learning objectives a student should be able to demonstrate after mastering it; a list of common misconceptions specifically associated with it (feeding directly into the Misconception Library); and a declared "visual need" — whether this concept typically requires a graph, a diagram, an equation render, or nothing visual at all, which tells the Visual Engine what to prepare in advance.

Because the identifier scheme includes board and grade from the start, even though V1 only populates one board, the same structure holds without modification when a second board or a different grade range is added later — it is additive, not a rewrite. This is the piece of the whole architecture most worth getting right before writing anything else, because every other component reads from it.

### 4.5 Student Model — what this specific student knows

This store answers a different question: not what exists to be taught, but what has actually been learned, by this particular student, right now. It holds a mastery value per concept (a simple staged progression — unknown, introduced, practicing, partially mastered, mastered — is sufficient to start; a continuous probability-like score can replace it later without changing anything else), a running record of misconceptions detected for this student with the evidence that led to each one, and a history of attempts and outcomes that the Assessment System (described below) draws on.

The Student Model is intentionally the only place personalization lives. The Curriculum Model is shared across every student; the Student Model is what makes two students working through the same concept get genuinely different treatment — one gets sent to a prerequisite, the other moves straight to a challenge question, because their Student Models say different things.

### 4.6 Session State — where we are right now

This is deliberately the smallest and shortest-lived of the three stores. It holds only what's needed to make sense of the very next message without re-sending an entire conversation history to anything: the current subject, chapter, and concept; the specific task or question in progress; which attempt number this is; what the last recorded error was; and what hint level has already been given.

The reason this exists separately from the Student Model is that Session State is disposable and turn-scoped, while the Student Model is durable and long-term. Conflating them would mean either losing the sense of "where we are in this exact exchange" between turns, or bloating the durable student record with transient, in-the-moment detail that has no value once the concept is done.

### 4.7 Pedagogy Router and Subject Pedagogy plugins

This is the mechanism that makes the system genuinely generalized rather than "one tutor with a lot of special cases." Every concept in the Curriculum Model carries a subject type — not the subject name itself, but a category of *how that subject is best taught*. A useful starting set of categories: quantitative science (mathematics, and the numerical parts of physics and chemistry), conceptual/descriptive science (biology, the mechanism-and-terminology parts of chemistry), and language arts (Urdu, English, comprehension and writing).

Each subject type has its own registered teaching flow — the ordered pedagogical steps a lesson moves through — because good pedagogy genuinely differs by category. Quantitative science moves from a worked example, to a guided problem, to an independent problem, to a varied version of the same problem, to mastery. Conceptual science moves from explanation, to a diagram or visual, to correct terminology, to recall practice, to application. Language arts moves from comprehension, to vocabulary, to grammar, to guided writing, to correction. The Pedagogy Router's only job is to look up a concept's subject type and hand control to the matching plugin; it never contains subject knowledge itself.

This is the piece that proves generalization actually worked: adding Physics after Mathematics should mean writing one new plugin that mostly reuses the "quantitative science" flow already built for Math, with no changes to the Controller, the Student Model, or the Session State. If adding a second subject ever requires touching the Controller, that is a signal the abstraction has leaked somewhere and needs to be fixed before a third subject is attempted.

### 4.8 Problem Engine

This is the structured bank of practice questions the tutor draws from, and it exists because a tutor that generates a fresh question from scratch every single time cannot guarantee difficulty is calibrated, cannot guarantee coverage of the syllabus, and cannot reliably reuse the same question for two students without an expensive live generation call each time.

For every concept, the question bank is organized by level of demand — from simple recognition ("which of these is a quadratic equation") through identification, procedural calculation, application, board-exam-style phrasing, and challenge-level extension. The Tutor Controller, informed by the Student Model's current mastery score for that concept, picks the appropriate level rather than the student or the LLM choosing arbitrarily. A student who has just been introduced to a concept gets a recognition-level question; a student who is close to mastery gets a board-style or challenge question. Repeated failure at a given level triggers a drop back to the prerequisite concept rather than more attempts at the same level, following the same principle your original design established.

### 4.9 Verifier Registry

This is where the "don't let the LLM grade" principle becomes concrete, and it has to support more than one method, because not every subject has an objectively checkable answer the way mathematics does.

For quantitative subjects, a symbolic verifier parses both the expected and the given answer and compares them algebraically or numerically — this is exact, fast, and free, with no API call involved at all. For structured numerical problems, such as physics word problems, a step-based verifier checks the solution path itself, not just the final number: was the correct formula selected, were units handled correctly, was the substitution correct, is the final answer in the right units — mirroring exactly the four-step check your original design specified for physics.

For subjects without a symbolic ground truth — language comprehension, short written answers, essay-style responses — a rubric-based verifier is used instead. The rubric itself is written once per question, by a person, listing the specific criteria a correct answer must satisfy. The LLM's role here is narrow and constrained: it checks the student's answer against that fixed rubric and returns a structured verdict, rather than being asked to freely judge whether the answer is "good." This keeps even the LLM-assisted grading path far more consistent and far cheaper to run than open-ended evaluation would be.

### 4.10 Visual Engine

This component exists specifically to resolve the apparent tension between "the tutor needs images, graphs, and diagrams" and "no image-generation models are allowed." The resolution is that visuals in an educational context are almost never freeform pictures — they are precise representations of structured data or of known shapes — which means they can be produced without an image model at all, using three distinct techniques depending on what's needed.

Anything mathematical — equations, formulas, expressions — is rendered directly from mathematical notation into a properly typeset display, which is fully deterministic and costs nothing. Anything numeric with a shape — a velocity-time graph, a function plot, a bar chart of exam results — is generated by a plotting library directly from the numbers involved in the specific problem, which is also fully deterministic, exact, and free. Anything structural — a geometric figure, a circuit diagram, a labeled biological diagram, a number line — is handled through a small, growing library of parameterized diagram templates: a template for "triangle with labeled sides and angles" gets built once, and every future question that needs a triangle just supplies the specific numbers into the existing template, rather than generating a new diagram from scratch. Only for a genuinely novel diagram type that no template yet covers does the system fall back to asking the LLM to produce vector graphics code directly — which is a text-generation task, not image generation — and even then, that output is reviewed once and then cached and reused as a new template going forward, so the same fallback is never paid for twice.

Each concept in the Curriculum Model already declares its visual need, so the Visual Engine knows in advance, before a student ever asks, whether a given concept typically requires a graph, a diagram, or nothing at all — it does not have to figure this out live.

### 4.11 Content Bank (pre-generated lesson content)

This component is the single biggest lever for making the whole system survive on a free-tier budget, and it works by inverting the usual assumption about when generation happens. Rather than generating an explanation, a worked example, or a hint sequence live, the moment a student asks for it, the content for every concept — the worked examples, the Socratic question sequence, the ladder of progressively stronger hints, the misconception-specific remediation explanations — is generated once, offline, per language, reviewed for correctness, and stored. From that point forward, serving that content to any number of students costs nothing beyond a lookup.

This has a second, equally important benefit beyond cost: it makes quality control possible. Content that will be seen by potentially many students can be checked once, by a person, before it ever reaches anyone, rather than trusting whatever a live model happens to generate in the moment for each individual student.

Textbook material feeds into this component through hybrid retrieval rather than through a single technique: a concept can be located by its identifier directly, by keyword match against the textbook text, by semantic similarity search, by which textbook section it belongs to, or by walking the prerequisite graph outward from a related concept — combining these is significantly more reliable than semantic search alone, which on its own can retrieve textbook passages that are topically similar but pedagogically wrong for what the student actually needs next.

### 4.12 LLM Engine (budget-aware routing and caching)

Everything upstream of this component has already minimized how much needs to happen live. What remains for the LLM Engine to actually do at runtime is comparatively small: rephrasing a piece of cached content to fit a specific student's wrong answer, generating one hint calibrated to the exact mistake just made, or holding a short Socratic exchange in the right language and register. These are short, bounded tasks, which matters because it means even a fast, free-tier model is generally sufficient for them — the heavy pedagogical authoring already happened offline in the Content Bank.

The Engine itself is structured as a router with a fallback chain rather than a single hardcoded provider: a call first tries a free, fast provider; if that provider is rate-limited or unavailable at that moment, the call automatically falls through to a second free or very-low-cost provider; only if every option in the chain is exhausted does the system fall back to serving the closest matching pre-authored content from the Content Bank rather than failing outright. Every live response is also cached, keyed by the concept, the specific type of mistake, and the language — because the same misconceptions recur across many students (a classic algebra error, for instance, will be made by dozens of different students), meaning the second, third, and hundredth student to trigger that exact explanation get it served for free, from cache, with no live call at all.

The practical effect of this design, as the Content Bank matures and the cache fills, is that the proportion of tutoring turns requiring a live LLM call drops substantially over time even as the number of students grows — the system gets cheaper to run per-student the longer it operates, rather than scaling cost linearly with usage.

### 4.13 Misconception Library

This is a small but high-value store that sits alongside the Curriculum Model rather than inside it. For every major concept, it holds the well-known ways students get that concept wrong, a diagnostic question or answer-pattern that reveals each specific misconception, and a recommended remediation strategy for it — exactly the structure your original design specified for things like the discriminant sign error or the "square of a binomial" mistake.

What makes this valuable operationally is that it converts a repeated wrong answer from something the LLM has to freshly interpret each time into a lookup: when a student's answer pattern matches a known misconception, the system already knows what's wrong and already has a reviewed remediation for it, rather than needing to reason about it from scratch. Over time, this library also becomes the most reusable asset the whole system produces — it is largely subject-specific but not student-specific, so it compounds in value as more students are taught.

### 4.14 Verification and Safety Layer

Nothing generated anywhere upstream — not a cached explanation, not a live hint, not a diagram — reaches the student without passing through this layer first. Its role is to catch the failure modes specific to an educational tool: a numeric answer that doesn't match what the Verifier actually computed, a rendered equation that doesn't parse, a diagram whose labels don't match the values in the question, an explanation that contradicts the curriculum's own stated definition for a concept. This layer is what makes it safe to rely on cheap, free-tier models for the generative parts of the system — the ceiling on how wrong a response can be is set by this layer, not by how capable the underlying model is.

### 4.15 Assessment and Analytics

Every completed session produces a structured record: how many questions were attempted, how many were correct, which specific mistakes occurred, and the mastery score for the relevant concept before and after the session. This is what allows the tutor to open a new session with genuine continuity — starting the next day with a short retrieval check on yesterday's concept, rather than either repeating everything from scratch or assuming nothing needs review — and it is also the raw data the spaced-repetition scheduler below depends on.

### 4.16 Spaced Practice and Review Scheduling

Mastery, once reached, is not treated as permanent. This component tracks when each mastered concept was last reviewed and schedules brief re-exposure at increasing intervals — a short review shortly after first learning it, a couple of questions a few days later, mixed practice further out, and an exam-style problem well after that. The Student Model is what determines which concepts are due for review at any given time, which is what turns the system from something that only ever answers the question currently in front of it into something that actively maintains what's already been learned.

### 4.17 Exam Preparation Mode

Understanding a concept and being ready to perform under exam conditions are related but distinct goals, and this mode formalizes that distinction rather than treating them as the same thing. It sits on top of everything already built rather than requiring new machinery: the same Curriculum Model, Problem Engine, and Verifier Registry are reused, but the Session State shifts from a scaffolded, hint-forward flow into a timed, board-style flow — full board questions, past-paper-style questions, timed sections, and a final error-analysis pass that feeds straight back into the Student Model and, where appropriate, back into a remedial lesson through the normal tutoring flow. This mode is explicitly a later addition, built once the core tutoring loop itself is proven — building it first would mean testing exam mechanics on top of a teaching loop that hasn't yet been validated.

### 4.18 Explicitly deferred capabilities

Two capabilities appear in the original design as future phases and remain deliberately out of scope here, consistent with the stated constraints rather than as an oversight: processing a photographed textbook question (which would require an image-understanding pipeline, separate from image *generation*, and is a meaningfully larger undertaking involving diagram interpretation) and voice interaction (speech-to-text in, text-to-speech out). Both are architecturally compatible with everything above — they would sit in front of the Conversation Layer as additional input/output modes — but neither is needed to prove the core tutoring loop, and both are explicitly excluded by the current constraints around live, real-time interaction.

---

## 5. The core tutoring workflow

This is the same loop your original design identified as the most important workflow in the entire project — it is preserved essentially unchanged here, because generalizing the system did not require changing *how* tutoring happens, only *what* gets plugged into each step.

```
                              START
                                │
                                ▼
                  What does the student want?
                                │
                                ▼
                     Identify the concept
                                │
                                ▼
                Check the Student Model for it
                                │
                                ▼
                   Check its prerequisites
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
             Missing                       Available
                 │                             │
                 ▼                             ▼
        Teach the prerequisite          Teach the concept
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                         Ask a question
                                │
                                ▼
                      Student responds
                                │
                                ▼
                     Verifier evaluates it
                                │
                ┌───────────────┼───────────────┐
                ▼                ▼                ▼
            Correct           Partial           Incorrect
                │                │                │
                ▼                ▼                ▼
         Raise mastery       Give a hint     Diagnose against the
                │                │            Misconception Library
                │                ▼                │
                │              Retry               ▼
                │                │          Targeted remediation
                └────────────────┴────────────────┘
                                ▼
                    Update the Student Model
                                │
                                ▼
                  Ready for the next concept?
                        │              │
                       Yes             No
                        │              │
                        ▼              ▼
                    Continue      Remediate
```

Walking through what actually happens at each step, with the generalized components now in place: when a student says something like "explain quadratic equations to me" or "I don't understand this question," the Conversation Layer first resolves the language and mixed-script input into something the Controller can work with, and the Controller identifies which concept is being referred to using the Curriculum Model. It then checks the Student Model for that student's current mastery of the concept and of every prerequisite the Curriculum Model lists for it. If a prerequisite is missing, the Controller redirects to teaching that prerequisite first, using the same loop recursively, rather than proceeding into a concept the student isn't ready for — this is the guardrail that prevents the tutor from doing what a plain chatbot does by default, which is answer exactly the question asked even when that isn't pedagogically the right next step.

Once prerequisites are satisfied, the Pedagogy Router selects the teaching flow appropriate to the concept's subject type and the Tutor Controller begins moving the student through it, pulling explanations and worked examples from the Content Bank rather than generating them fresh, and pulling any needed visual from the Visual Engine using the concept's declared visual need. A question is then drawn from the Problem Engine at a level matched to the student's current mastery score, and the student's response goes to the Verifier Registry — a symbolic check for math, a step-based check for a physics numerical, or a rubric check for a written answer.

If the answer is correct, the Student Model's mastery score for that concept is raised and the Controller either presents a harder question at the next level or, if mastery is now sufficient, moves on to the next concept in the curriculum sequence. If the answer is partially correct, a hint is generated — pulled from a pre-authored hint ladder in the Content Bank where one exists, escalated in specificity if the student is still stuck, with a live LLM call only invoked when the situation genuinely doesn't match anything already prepared. If the answer is wrong, the specific error is checked against the Misconception Library for that concept; a matching known misconception triggers its associated, already-reviewed remediation, while a genuinely new error pattern is diagnosed live and, once resolved, is a candidate to be added to the Misconception Library for that concept so the same diagnosis never needs to happen from scratch again.

Every step in this loop writes back to the Student Model and Session State through the Controller alone, which is what keeps the mastery record trustworthy regardless of which subject, which engine, or which language was involved in producing the outcome.

---

## 6. Multi-subject generalization strategy

The test for whether generalization has actually succeeded, rather than merely being claimed, is this: adding a second subject after the first one is fully working should cost approximately one new Pedagogy plugin, one new set of Content Bank entries, and possibly one new Verifier type — and nothing else. If adding Physics after Mathematics requires any change to the Tutor Controller, the Student Model's structure, or the Session State's structure, that is a sign the boundary between "generic core" and "subject-specific plugin" was drawn in the wrong place, and it needs to be corrected before a third subject is attempted, not patched around.

In practice, this means the subject type categories (quantitative science, conceptual science, language arts) are expected to absorb most new subjects with only a new plugin, since a numerical chemistry problem behaves like a numerical physics problem from the Controller's point of view, and a biology diagram-and-terminology lesson behaves like a chemistry mechanism lesson. Some concepts will genuinely straddle categories — a chemistry unit that has both a conceptual mechanism and a quantitative stoichiometry calculation, for instance — and the right response to that is to let subject type live at the level of the individual concept rather than the whole subject, so a single chapter can mix concepts of different pedagogical types without forcing the whole subject into one flow.

Adding a second curriculum board later follows the same logic at the Curriculum Model level: because the concept identifier already encodes board and grade, a second board's curriculum tree is added as new entries in the same structure, not a parallel structure — the only genuinely new work is populating that board's concepts, prerequisites, and content, not changing how any component reads or writes curriculum data.

---

## 7. Validation — an honest critical review

This section exists because a blueprint that only lists strengths isn't trustworthy. Here is where this architecture is solid, where it is genuinely fragile, and what is likely to go wrong first when it's actually built.

**Where the design is strong.** The separation of Curriculum Model, Student Model, and Session State is the right foundation and should not be revisited later — it is what makes personalization, multi-subject support, and multi-student support all possible without the three concerns tangling into each other. The deterministic-first approach to verification is correct for anything with an objective answer, and it is the reason the system can run safely on cheap models: the ceiling on correctness is set by the symbolic and rubric checks, not by model capability. The Content Bank as the primary cost-control mechanism is the single decision that makes the free-tier constraint realistic rather than aspirational — without it, a live-generation-per-turn design would exhaust free-tier rate limits almost immediately under any real usage.

**Where it is genuinely fragile, and why.** The Content Bank's biggest strength — quality controlled, reviewed-once content — is also its biggest practical cost: someone has to actually author or review that content for every concept before students see good output for it, and that is a substantial amount of upfront human effort that doesn't show up in the architecture diagram itself. This is worth planning for explicitly rather than discovering midway through building the second subject.

The rubric-based verifier for language and essay-type answers is inherently softer than symbolic math verification, and no amount of good rubric design will make LLM-assisted grading as reliable as a symbolic comparison — this is a real limitation of the approach, not a solvable engineering gap, and it means language-subject mastery scores should be treated as somewhat less precise than math or physics mastery scores when the Controller uses them to make decisions.

The Visual Engine's fallback path — asking the LLM to author vector graphics code for a diagram type with no existing template — is the least reliable part of the whole visual pipeline. Numeric plotting from real data and equation rendering are both fully deterministic and trustworthy; hand-authored diagram code from a free-tier model is not, and any diagram produced this way needs a human review pass before it's promoted into the permanent template library, not just before its first use.

The subject type categorization (quantitative science, conceptual science, language arts) is a reasonable starting abstraction, but real curricula don't split this cleanly — chemistry in particular mixes mechanism-based conceptual content with quantitative stoichiometry within the same chapter. Assigning subject type per concept rather than per subject, as noted in the generalization strategy above, resolves this, but it's worth flagging now rather than after the plugin interface has already been built assuming one subject type per subject.

Free-tier and low-cost API rate limits, even with a fallback chain across multiple providers, place a real ceiling on how many students can be served concurrently before the caching strategy has had time to mature — the Content Bank and cache reduce this pressure significantly over time, but in the early weeks of a new subject, before its cache has filled, usage spikes could still hit rate limits across the whole fallback chain. The pre-authored fallback in the LLM Engine exists specifically to make this a degraded experience rather than a broken one, but it is a degraded experience, and that tradeoff should be understood going in rather than treated as a solved problem.

**What is most likely to reveal a real design flaw first.** The most informative test of this entire blueprint will be building the second subject, not the first — the first subject can be made to work through effort even if a boundary was drawn slightly wrong, but the second subject is what will actually prove or disprove whether the Controller, Student Model, and Session State are truly subject-agnostic. Any point where building the second subject requires touching code or structure that was supposed to be generic is the signal to stop and fix the abstraction, rather than a signal to add another special case.