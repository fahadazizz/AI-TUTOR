import json
import os
import sys

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def main():
    base_dir = "/mnt/DataDrive/What I want to Achieve/AI Tutor/data/curriculum/mathematics"
    
    concepts_file = os.path.join(base_dir, "concepts.json")
    prereq_file = os.path.join(base_dir, "prerequisites.json")
    questions_file = os.path.join(base_dir, "questions", "ch02_quadratic_equations.json")
    assess_file = os.path.join(base_dir, "questions", "initial_assessment.json")
    misconceptions_file = os.path.join(base_dir, "misconceptions.json")

    concepts_data = load_json(concepts_file)
    prereq_data = load_json(prereq_file)
    questions_data = load_json(questions_file)
    assess_data = load_json(assess_file)
    misconceptions_data = load_json(misconceptions_file)

    if not all([concepts_data, prereq_data, questions_data, assess_data, misconceptions_data]):
        print("Failed to load some JSON files.")
        sys.exit(1)

    # 1. Collect all valid concept IDs
    valid_concept_ids = set([c['concept_id'] for c in concepts_data['concepts']])
    print(f"Loaded {len(valid_concept_ids)} valid concepts.")

    # 2. Check Prerequisites
    errors = 0
    for edge in prereq_data['edges']:
        if edge['concept_id'] not in valid_concept_ids:
            print(f"ERROR: Concept ID {edge['concept_id']} in prerequisites not found in concepts.json")
            errors += 1
        for prereq in edge['prerequisites']:
            if prereq not in valid_concept_ids:
                print(f"ERROR: Prerequisite ID {prereq} for {edge['concept_id']} not found in concepts.json")
                errors += 1

    # 3. Check Questions
    all_question_ids = set()
    for q_data in [questions_data, assess_data]:
        for q in q_data['questions']:
            all_question_ids.add(q['question_id'])
            if q['concept_id'] not in valid_concept_ids:
                print(f"ERROR: Question {q['question_id']} references unknown concept {q['concept_id']}")
                errors += 1

    print(f"Loaded {len(all_question_ids)} total questions.")

    # 4. Check Misconceptions
    for m in misconceptions_data['misconceptions']:
        if m['concept_id'] not in valid_concept_ids:
            print(f"ERROR: Misconception {m['misconception_id']} references unknown concept {m['concept_id']}")
            errors += 1
        
        if m.get('prerequisite_gap') and m['prerequisite_gap'] not in valid_concept_ids:
             print(f"ERROR: Misconception {m['misconception_id']} references unknown prerequisite_gap {m['prerequisite_gap']}")
             errors += 1

        for dq in m['diagnostic_question_ids']:
            if dq not in all_question_ids:
                print(f"ERROR: Misconception {m['misconception_id']} references unknown diagnostic_question {dq}")
                errors += 1
                
        for pq in m['practice_question_ids']:
            if pq not in all_question_ids:
                print(f"ERROR: Misconception {m['misconception_id']} references unknown practice_question {pq}")
                errors += 1

    if errors == 0:
        print("SUCCESS: All cross-references are valid. No dangling IDs found.")
    else:
        print(f"FAILED: Found {errors} cross-reference errors.")

if __name__ == '__main__':
    main()
