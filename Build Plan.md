# Generalized AI Tutor — Master Build Plan & Tracking

**Companion document to the Master Blueprint Architecture. This document turns that architecture into a version-by-version, phase-by-phase build sequence, with tracking status and real-world success metrics for every version.**

---

## 0. How to use this document

This is meant to be a living tracker, not a one-time read. Every version below has the same five fields: what it covers, what it deliberately excludes, what it depends on, how you'll know it actually worked in the real world, and its current status. As you work, update the Status field for each version — Not Started, In Progress, Blocked, or Done — and treat a version as Done only when its success metrics have actually been checked against real usage, not when the feature is merely built. A feature that works in isolation but hasn't been validated against a real student session is still In Progress, not Done. This distinction matters more here than in most software projects, because the entire point of the system is pedagogical effectiveness, which code review alone cannot confirm.

Where you already have working code from the original sister-focused build, treat it as a rough first draft of the matching Phase A version below, not as already-complete — expect to refactor it into the generalized schema and plugin interfaces described in the blueprint, rather than keeping it as-is.

---

## 1. Versioning and phase scheme

Versions are grouped into four phases, each answering a different question:

- **Phase A — Foundation (V0.0 – V0.8):** Does the core tutoring loop work at all, for one subject, for one real student?
- **Phase B — Generalization Proof (V1.0 – V1.6):** Does the architecture actually generalize, or does adding a second subject break the abstraction?
- **Phase C — Multi-Subject Stability (V2.0 – V2.5):** Does the system hold up as more subjects, more features, and more real usage are added?
- **Phase D — Platform Maturity & Scale (V3.0 – V3.4):** Does the system extend to a second curriculum board, more students, and a polished mobile experience?

Within each phase, a `.0` version marks a checkpoint or milestone release — a point where you stop and confirm the phase's core question has been answered — rather than new build work in itself.

```
PHASE A            PHASE B                 PHASE C                    PHASE D
Foundation         Generalization Proof    Multi-Subject Stability    Platform Maturity
V0.0 → V0.8         V1.0 → V1.6              V2.0 → V2.5                V3.0 → V3.4
   │                    │                        │                          │
One subject,      Second subject added,    More subjects, spaced      Second board,
text-first,       pedagogy plugin proven,   repetition, analytics,     mobile polish,
one real student  content bank + budget     exam mode, multi-         multi-student
                  router live               language parity           scale test
```

---

## 2. Master tracking table

Use this table as the at-a-glance view. The detailed breakdown for every row is in the phase sections that follow.

| Phase | Version | Name | Primary Components Touched | Status |
|---|---|---|---|---|
| A | V0.0 | Pre-build setup | Infra, tooling, provider accounts | Done |
| A | V0.1 | Curriculum schema + Subject 1 | Curriculum Model | Done |
| A | V0.2 | Core loop, text-only | Tutor Controller, Student Model, Session State | Done |
| A | V0.3 | Symbolic verifier | Verifier Registry | Not Started |
| A | V0.4 | Equation rendering | Visual Engine | Not Started |
| A | V0.5 | Graphs and diagram templates | Visual Engine | Not Started |
| A | V0.6 | Misconception library seed | Misconception Library | Not Started |
| A | V0.7 | Dashboard surface | Student Application | Not Started |
| A | V0.8 | Internal dogfood validation | Full Phase A stack | Not Started |
| B | V1.0 | First stable release checkpoint | — (validation checkpoint) | Not Started |
| B | V1.1 | Pedagogy Router formalized | Pedagogy Router | Not Started |
| B | V1.2 | Second subject added | Pedagogy plugins, Curriculum Model | Not Started |
| B | V1.3 | Verifier Registry expanded | Verifier Registry | Not Started |
| B | V1.4 | Content Bank pipeline | Content Bank | Not Started |
| B | V1.5 | Budget LLM router + caching | LLM Engine | Not Started |
| B | V1.6 | Safety layer hardened | Verification & Safety Layer | Not Started |
| C | V2.0 | Multi-subject stable checkpoint | — (validation checkpoint) | Not Started |
| C | V2.1 | Third+ subject added | Pedagogy plugins, Curriculum Model | Not Started |
| C | V2.2 | Spaced repetition scheduler | Review Scheduler | Not Started |
| C | V2.3 | Assessment & analytics | Assessment and Analytics | Not Started |
| C | V2.4 | Exam Preparation Mode | Exam Mode, Problem Engine | Not Started |
| C | V2.5 | Multi-language content parity | Content Bank, Conversation Layer | Not Started |
| D | V3.0 | Platform maturity checkpoint | — (validation checkpoint) | Not Started |
| D | V3.1 | Second curriculum board | Curriculum Model | Not Started |
| D | V3.2 | Mobile app polish | Student Application | Not Started |
| D | V3.3 | Multi-student scale test | LLM Engine, infra | Not Started |
| D | V3.4 | Deferred capabilities decision | OCR intake, voice | Not Started |

---

## 3. Phase A — Foundation

**Phase question: does the core loop actually work, end to end, for one real student?** Nothing in this phase is subject-agnostic yet, and that is intentional — building the generalized plugin interface before a single subject works end to end would mean abstracting something that hasn't been proven to work even once.

### V0.0 — Pre-build setup

**Scope:** Set up the development environment, choose and provision hosting for the backend, set up the database that will hold the Curriculum Model, Student Model, and Session State, and create accounts on the free-tier LLM providers you intend to route between. Confirm a basic end-to-end call succeeds against at least two different providers, since the whole budget strategy depends on having more than one available from day one.

**Out of scope:** Any actual tutoring logic, curriculum content, or UI work.

**Dependencies:** None — this is the starting point.

**Success metrics:**
- A test call against at least two different free-tier providers returns a valid response.
- A record can be written to and read back from each of the three planned data stores (curriculum, student, session).
- The development environment runs without manual workarounds needed each time you start work.

**Status:** Done

### V0.1 — Curriculum schema and Subject 1 population

**Scope:** Implement the generalized concept schema (board, grade, subject, subject type, chapter, prerequisites, textbook sources, difficulty, learning objectives, misconceptions, visual need, language pack) and populate it fully for one real chapter of one subject, reusing content from the original sister-focused build where it already exists.

**Out of scope:** Any second subject, any second board. Populate one chapter fully rather than many chapters shallowly — depth over breadth at this stage.

**Dependencies:** V0.0.

**Success metrics:**
- At least one full chapter is entered with every schema field populated, not left blank.
- Manually tracing the prerequisite chain for five different concepts in this chapter produces a chain that matches what the actual textbook and your own subject knowledge say it should be.
- A concept can be looked up by its identifier and returns a complete, correctly structured record.

**Status:** Done

### V0.2 — Core loop, text-only

**Scope:** Build the Tutor Controller's core decision sequence, the Student Model, and the Session State, wired together into the full teach → question → evaluate → update loop described in the blueprint's workflow section — text only, no visuals yet, no caching yet, live LLM calls for everything generative.

**Out of scope:** Visuals, the pedagogy plugin abstraction (hardcode the one subject's flow directly for now), caching, multiple providers.

**Dependencies:** V0.1.

**Success metrics:**
- One real student (your sister) can complete a full teach-question-evaluate-update cycle for at least one concept without you manually intervening in the backend mid-session.
- A session of at least ten consecutive turns stays coherent — the tutor doesn't lose track of what concept or question is currently active.
- After a correct answer, the Student Model's mastery value for that concept visibly and correctly increases when inspected directly.

**Status:** Done

### V0.3 — Symbolic verifier

**Scope:** Build the symbolic verifier for the quantitative subject you started with, replacing any LLM-based correctness judgment from V0.2 with deterministic algebraic or numeric comparison.

**Out of scope:** The step-based physics verifier and the rubric-based language verifier — both come later, once a second subject exists to need them.

**Dependencies:** V0.2.

**Success metrics:**
- Running the verifier against at least 30 real student answers (a mix of correct, close-but-wrong, and clearly wrong) matches your own manual grading of the same 30 answers on every case.
- The verifier never calls an LLM to determine correctness — confirm this by checking that verification still works correctly with all LLM providers deliberately disabled.

**Status:** Not Started

### V0.4 — Equation rendering

**Scope:** Add proper mathematical notation rendering wherever a formula or expression currently appears as plain typed text.

**Out of scope:** Graphs and diagrams — this version is equations only.

**Dependencies:** V0.2.

**Success metrics:**
- Twenty different explanations pulled from real V0.1 content render their formulas correctly with no manual fixing needed.
- Your sister confirms, using her own judgment, that the rendered equations are at least as clear as what she'd see in her actual textbook.

**Status:** Not Started

### V0.5 — Graphs and diagram templates

**Scope:** Add data-driven graph generation for numeric relationships in this subject, and build the first small set of parameterized diagram templates for recurring structural visuals in this subject's chapter.

**Out of scope:** The LLM-authored fallback for genuinely novel diagram types — only build that path once a real concept actually needs a diagram type no template covers.

**Dependencies:** V0.4.

**Success metrics:**
- At least three distinct graph types relevant to this subject generate correctly from real problem numbers, with no manual correction needed.
- At least five diagram templates exist and have each been reused for more than one distinct question, confirming the "build once, reuse forever" pattern actually works in practice.

**Status:** Not Started

### V0.6 — Misconception library seed

**Scope:** Populate the Misconception Library for this subject's chapter with real, documented misconceptions, each with a diagnostic trigger and a reviewed remediation, and wire the Tutor Controller to check incorrect answers against it before falling back to a live diagnosis.

**Out of scope:** Building this library for any other subject yet.

**Dependencies:** V0.3.

**Success metrics:**
- At least ten misconceptions are documented, each based on a wrong answer a real student (not a hypothetical one) actually gave.
- When a real student's wrong answer matches a documented misconception, the system correctly retrieves the matching remediation instead of generating a fresh diagnosis.

**Status:** Not Started

### V0.7 — Dashboard surface

**Scope:** Build the persistent progress dashboard showing the concept tree with mastery levels, separate from the chat surface, reading directly from the Student Model and Curriculum Model.

**Out of scope:** Any analytics beyond the mastery map itself — deeper analytics come in Phase C.

**Dependencies:** V0.2.

**Success metrics:**
- Checking the dashboard by hand against the raw Student Model records for at least five concepts shows an exact match.
- Your sister can look at the dashboard and correctly state, in her own words, which concepts she's strong and weak in, without you explaining it to her.

**Status:** Not Started

### V0.8 — Internal dogfood validation

**Scope:** No new components. This version is a sustained real-usage validation period for everything built so far, used by your sister as her actual, primary way of studying this chapter — not a demo, not a test session run by you.

**Out of scope:** New features. Resist the urge to add anything here; the point is to find out what's actually broken under real, sustained use.

**Dependencies:** V0.1 through V0.7.

**Success metrics:**
- At least two weeks of real, sister-initiated study sessions occur without you needing to manually intervene in the backend to keep a session working.
- Your sister reports the experience as more useful than her previous approach (the original narrow tutor, or studying without a tutor at all), in her own words.
- Every bug or confusing moment encountered during this period is logged, even minor ones — this log becomes the basis for what gets fixed before Phase B begins.

**Status:** Not Started

---

## 4. Phase B — Generalization Proof

**Phase question: does the architecture actually generalize, or does it just work for one subject?** This is the phase where the design gets tested against reality. Version V1.2 in particular is the single most important checkpoint in the entire build plan.

### V1.0 — First stable release checkpoint

**Scope:** No new build work. This is a formal checkpoint confirming Phase A is genuinely stable before generalization work begins — re-run the same real sessions from V0.8 and confirm consistent, repeatable results.

**Dependencies:** V0.8.

**Success metrics:**
- All Phase A success metrics still hold when re-checked, not just when first achieved.
- At least five consecutive real sessions complete with no manual backend intervention.

**Status:** Not Started

### V1.1 — Pedagogy Router formalized

**Scope:** Refactor the hardcoded teaching flow from V0.2 into the formal Pedagogy Router and plugin interface described in the blueprint, with Subject 1 as the first registered plugin. This should be a behavior-preserving refactor, not a feature change.

**Dependencies:** V1.0.

**Success metrics:**
- Re-running the exact same test sessions used to validate V0.8 produces identical outcomes through the new plugin architecture.
- No subject-specific logic remains inside the Tutor Controller itself — confirmed by a direct read-through of the controller code looking specifically for anything that mentions Subject 1 by name.

**Status:** Not Started

### V1.2 — Second subject added

**Scope:** Add a second subject — ideally one that tests a genuinely different subject type from Subject 1 (a language-arts subject if Subject 1 was quantitative, for instance), including its own curriculum content, its own pedagogy plugin, and enough content bank material to teach at least one real chapter.

**This is the generalization gate.** Track explicitly, as a yes/no answer, whether adding this subject required any change to the Tutor Controller, the Student Model schema, or the Session State schema. If the answer is yes to any of them, stop before continuing to V1.3 and fix the abstraction first — do not proceed with a leaking abstraction and hope it doesn't matter later.

**Dependencies:** V1.1.

**Success metrics:**
- **The generalization gate above returns a clean "no changes required" result.**
- A real student can complete a full teach-question-evaluate-update cycle in the second subject, to the same standard as V0.2 achieved for the first.
- Total new code required for the second subject is limited to the plugin itself, its content, and (if needed) a new verifier type — not core infrastructure.

**Status:** Not Started

### V1.3 — Verifier Registry expanded

**Scope:** Build whichever verifier types V1.2 required that didn't exist yet — most likely a step-based structured verifier if the second subject was quantitative science, or a rubric-based verifier if it was language arts.

**Dependencies:** V1.2.

**Success metrics:**
- A step-based verifier, if built, correctly identifies which specific step failed (formula choice, units, substitution, or final answer) on at least 20 real incorrect attempts.
- A rubric-based verifier, if built, agrees with your own manual grading on at least 85% of a set of 20 real written answers, and every disagreement is reviewed to understand why.

**Status:** Not Started

### V1.4 — Content Bank pipeline

**Scope:** Build the offline, batch generation-and-review pipeline for producing lesson content once per concept rather than live per session, and run it against both subjects' curricula.

**Dependencies:** V1.2.

**Success metrics:**
- At least 80% of both subjects' concepts have reviewed, cached content before this version is considered done.
- The measured number of live LLM calls per 100 tutoring turns is lower after this pipeline goes live than it was before, tracked as a direct before-and-after comparison, not an assumption.

**Status:** Not Started

### V1.5 — Budget LLM router and caching

**Scope:** Build the multi-provider fallback chain and the response cache described in the blueprint's LLM Engine section, replacing any single-provider assumption still remaining from earlier versions.

**Dependencies:** V0.0, V1.4.

**Success metrics:**
- Deliberately rate-limiting or disabling the primary provider during a test session results in the system falling through to a secondary provider or a content-bank fallback, never in an unrecoverable failure.
- Cache hit rate reaches a first milestone (a specific target you set once you see real week-one traffic, but treat anything above zero-growth as a signal the caching key design needs revisiting) within the first month of combined real usage across both subjects.

**Status:** Not Started

### V1.6 — Safety layer hardened

**Scope:** Build out the Verification and Safety Layer with explicit checks for the failure modes named in the blueprint: mismatched verifier and stated answer, malformed rendered equations, diagrams whose labels don't match the question's numbers, and explanations that contradict the curriculum's own stored definitions.

**Dependencies:** V1.3, V1.5.

**Success metrics:**
- A deliberately constructed test set of at least 15 "bad" outputs (one example per failure type described above, repeated across both subjects) is caught before reaching the student in every single case.
- No genuine, correct response is ever incorrectly blocked by this layer — checked by running it against at least 50 real, verified-good responses from earlier phases with zero false blocks.

**Status:** Not Started

---

## 5. Phase C — Multi-Subject Stability

**Phase question: does the system hold up as more subjects, features, and real usage accumulate?**

### V2.0 — Multi-subject stable checkpoint

**Scope:** No new build work. Confirm both subjects are running stably together under real, sustained usage before adding further scope.

**Dependencies:** V1.6.

**Success metrics:**
- A full month of real combined usage across both subjects produces no unrecoverable failures.
- Actual API cost for the month, tracked directly from provider dashboards, stays within your budget expectation — ideally at or near zero given the free-tier design.

**Status:** Not Started

### V2.1 — Third-plus subject added

**Scope:** Add one or more additional subjects, applying the same generalization gate used at V1.2 to each.

**Dependencies:** V2.0.

**Success metrics:**
- The generalization gate (no core changes required) passes again for this subject, the same way it did at V1.2.
- If this subject genuinely mixes subject types within one chapter (chemistry mixing mechanism and stoichiometry, for example), confirm the per-concept subject-type assignment from the blueprint's generalization strategy handles this correctly rather than forcing an awkward single classification on the whole subject.

**Status:** Not Started

### V2.2 — Spaced repetition scheduler

**Scope:** Build the review scheduler that tracks when mastered concepts were last reviewed and surfaces brief re-exposure at increasing intervals.

**Dependencies:** V2.0.

**Success metrics:**
- Concepts marked as mastered are automatically resurfaced for brief review on the schedule the design specifies, confirmed by checking the schedule against actual mastery timestamps.
- Retest performance on previously mastered concepts, measured after the scheduler has been active for four to six weeks, is compared against retest performance on concepts mastered before the scheduler existed — the real-world question this metric answers is whether spaced review is actually improving retention, not just whether the feature runs.

**Status:** Not Started

### V2.3 — Assessment and analytics

**Scope:** Build the structured per-session record-keeping and any summary views beyond the basic mastery dashboard from V0.7 — attempt history, error patterns over time, session-to-session progress trends.

**Dependencies:** V2.0.

**Success metrics:**
- A spot check of at least ten sessions shows the analytics numbers match a manual count from the raw session logs exactly.
- The analytics correctly surface at least one real pattern in your sister's (or another real student's) actual performance that you didn't already know before looking.

**Status:** Not Started

### V2.4 — Exam Preparation Mode

**Scope:** Build the timed, board-style flow described in the blueprint, reusing the existing Problem Engine and Verifier Registry with a different Session State flow.

**Dependencies:** V2.0, V1.3.

**Success metrics:**
- A real student completes at least one full timed mock exam end to end through this mode.
- Grading produced by the system for that mock exam matches your own manual grading of the same paper.

**Status:** Not Started

### V2.5 — Multi-language content parity

**Scope:** Extend the Content Bank so that every live subject has reviewed, correct content in every target language variant, not just the language the first build happened to be authored in.

**Dependencies:** V1.4.

**Success metrics:**
- A fluent reviewer (not an automated check) confirms correctness of the content in each additional language for a representative sample of concepts across every live subject.
- A student can switch language mid-session and receive an explanation that is substantively the same in meaning as the one they'd have received in the original language, not a degraded or generic version.

**Status:** Not Started

---

## 6. Phase D — Platform Maturity and Scale

**Phase question: does the system extend beyond its original single-board, single-family scope?**

### V3.0 — Platform maturity checkpoint

**Scope:** No new build work. Confirm the system is stable across every subject and feature added so far, under real usage, before expanding scope further.

**Dependencies:** V2.0 through V2.5.

**Success metrics:**
- All success metrics from every prior phase still hold when spot-checked again.
- No open, unresolved item remains in the risk register below that would be made worse by adding a second board or scaling to more students.

**Status:** Not Started

### V3.1 — Second curriculum board

**Scope:** Add a second curriculum board's content into the existing schema, testing the board-level generalization the schema was designed for from the start.

**Dependencies:** V3.0.

**Success metrics:**
- Adding the second board requires new curriculum data only — no schema changes to the Curriculum Model, Student Model, or Session State.
- A real student following the second board can be taught through the exact same core loop with no behavior differences beyond the content itself.

**Status:** Not Started

### V3.2 — Mobile app polish

**Scope:** Bring the interface to full feature parity on a mobile app, given the backend has been platform-agnostic since Phase A.

**Dependencies:** V3.0.

**Success metrics:**
- A full lesson, from concept introduction through mastery update, can be completed entirely on the mobile app with no missing functionality compared to the development interface.
- A real student who has only used the earlier interface can switch to mobile and complete a session without needing guidance from you.

**Status:** Not Started

### V3.3 — Multi-student scale test

**Scope:** Test the system under a real or realistically simulated concurrent load beyond a single family's usage, specifically to observe how the free-tier fallback chain behaves under pressure.

**Dependencies:** V3.0, V1.5.

**Success metrics:**
- A defined target number of concurrent real students (set this number based on your actual intended audience at this stage) can use the system in the same time window without hitting an unrecoverable failure.
- Actual free-tier quota consumption under this load is measured directly against provider limits, not estimated, and the point at which the fallback chain would need a fourth option (if any) is identified before it becomes a real outage.

**Status:** Not Started

### V3.4 — Deferred capabilities decision

**Scope:** No build work required by default. Revisit the two explicitly deferred capabilities from the blueprint — photographed-question intake and voice interaction — and make a documented decision on whether either is worth pursuing given the constraints and usage patterns observed by this point.

**Dependencies:** V3.0.

**Success metrics:**
- A written decision exists for each deferred capability, with a stated reason, rather than the question being left silently unresolved.
- If either is greenlit, it is scoped as its own new phase rather than folded ad hoc into existing versions.

**Status:** Not Started

---

## 7. Cross-cutting success metrics

These are tracked continuously from Phase A onward, not tied to a single version, because they measure the health of the system as a whole rather than any one feature.

- **Cost per active student per month**, read directly from provider billing/usage dashboards.
- **Live LLM calls per 100 tutoring turns**, as a direct measure of how much the Content Bank and caching are actually reducing runtime dependency on live generation over time.
- **Verifier accuracy versus manual grading**, sampled on an ongoing basis, not just checked once at the version that introduced each verifier.
- **Session completion rate** — the percentage of started sessions that reach a natural stopping point rather than failing or being abandoned due to a technical problem.
- **Response latency**, from student message to tutor response, tracked because a technically correct answer that arrives too slowly still fails the real-world usability bar.
- **Mastery-score accuracy** — periodically checked by giving a student an unscaffolded, exam-style question on a concept the Student Model claims they've mastered, and confirming their real performance matches what the model believes.
- **Direct qualitative feedback** from real users, collected as an explicit, recurring check-in rather than assumed from usage alone.

---

## 8. Risk register

Carried forward from the blueprint's validation section, tracked here as living items rather than one-time observations.

| Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|
| Content Bank authoring becomes a bottleneck — building it takes real, sustained human effort | High | High | Prioritize content creation in curriculum order, don't gate a version's completion on 100% content coverage | Open |
| Free-tier rate limits exhausted under real concurrent load | Medium | High | Multi-provider fallback chain (V1.5), content-bank fallback as last resort | Open |
| The subject-type abstraction leaks when the second subject is added | Medium | High | Explicit generalization gate at V1.2 and V2.1 — stop and fix rather than proceed | Open |
| Rubric-based verifier is less consistent than symbolic verification for language subjects | Medium | Medium | Treat language-subject mastery scores as lower-confidence in downstream decisions | Open |
| LLM-authored fallback diagrams are structurally or factually wrong | Medium | Low–Medium | Mandatory human review before any LLM-authored diagram is promoted into the permanent template library | Open |
| Board-level generalization surfaces unexpected schema gaps at V3.1 | Low until reached | Medium | Budget explicit validation time when starting the second board rather than assuming a clean fit | Open |

---

## 9. Maintaining this document

Update the Status column in the master tracking table as work progresses, and revisit the risk register at the start of each phase, not just when a risk actually materializes. When a version's real-world success metrics are met, mark it Done and note the date; if a version is attempted and its metrics aren't met, mark it In Progress or Blocked rather than Done, and record what specifically failed — that record becomes the most useful input for deciding whether the plan itself needs to change before continuing.