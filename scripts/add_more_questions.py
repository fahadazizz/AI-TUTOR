import json
import os

questions_to_add = [
    {
      "question_id": "math10.ch2.qexpr.q03",
      "concept_id": "math10.ch2.quadratic_expression",
      "difficulty": 2,
      "question_type": "recognition",
      "question_text_ur": "کیا 5 - 2x + 8x² ایک مربعی مقدار ہے؟",
      "question_text_en": "Is 5 - 2x + 8x² a quadratic expression?",
      "expected_answer": "yes",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "مقدار میں متغیر (x) کی سب سے بڑی طاقت چیک کریں", "math": "8x² کی وجہ سے طاقت 2 ہے"},
        {"step": 2, "description_ur": "چونکہ طاقت 2 ہے لہذا یہ مربعی مقدار ہے", "math": "ہاں"}
      ],
      "hints": [
        "حدود کی ترتیب سے فرق نہیں پڑتا، بس x کی سب سے بڑی طاقت دیکھو"
      ],
      "tags": ["recognition", "quadratic_expression", "out_of_order"]
    },
    {
      "question_id": "math10.ch2.qexpr.q04",
      "concept_id": "math10.ch2.quadratic_expression",
      "difficulty": 2,
      "question_type": "recognition",
      "question_text_ur": "کیا (x+2)(x-3) ایک مربعی مقدار ہے؟ (پھیلا کر چیک کریں)",
      "question_text_en": "Is (x+2)(x-3) a quadratic expression? (Expand and check)",
      "expected_answer": "yes",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "مقدار کو پھیلائیں", "math": "x(x) - 3x + 2x - 6 = x² - x - 6"},
        {"step": 2, "description_ur": "سب سے بڑی طاقت 2 ہے", "math": "ہاں"}
      ],
      "hints": [
        "پہلے brackets کو آپس میں ضرب دو"
      ],
      "tags": ["recognition", "quadratic_expression", "expansion_needed"]
    },
    {
      "question_id": "math10.ch2.sf.q04",
      "concept_id": "math10.ch2.standard_form",
      "difficulty": 3,
      "question_type": "procedural",
      "question_text_ur": "x(x+7) = -12 کو معیاری شکل (standard form) میں لکھو اور a,b,c کی قدریں بتاؤ",
      "question_text_en": "Write x(x+7) = -12 in standard form and state a,b,c",
      "expected_answer": "x^2 + 7x + 12 = 0, a=1, b=7, c=12",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "پہلے بائیں طرف ضرب دیں", "math": "x² + 7x = -12"},
        {"step": 2, "description_ur": "-12 کو بائیں طرف لائیں", "math": "x² + 7x + 12 = 0"},
        {"step": 3, "description_ur": "ax² + bx + c = 0 سے موازنہ کریں", "math": "a=1, b=7, c=12"}
      ],
      "hints": [
        "بریکٹ کو ضرب دیں: x کو x اور پھر 7 سے"
      ],
      "tags": ["procedural", "standard_form"]
    },
    {
      "question_id": "math10.ch2.fact.q04",
      "concept_id": "math10.ch2.solving_by_factorization",
      "difficulty": 3,
      "question_type": "procedural",
      "question_text_ur": "x² - x - 20 = 0 کو تحلیل سے حل کرو",
      "question_text_en": "Solve x² - x - 20 = 0 by factorization",
      "expected_answer": "x = 5, x = -4",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "ایسے عدد جن کی ضرب -20 اور جمع -1 ہو", "math": "-5 اور 4"},
        {"step": 2, "description_ur": "تحلیل کریں", "math": "(x-5)(x+4) = 0"},
        {"step": 3, "description_ur": "حل کریں", "math": "x = 5, x = -4"}
      ],
      "hints": [
        "15 اور 20 کے عوامل (factors) پر غور کریں"
      ],
      "tags": ["procedural", "factorization"]
    },
    {
      "question_id": "math10.ch2.fact.q05",
      "concept_id": "math10.ch2.solving_by_factorization",
      "difficulty": 4,
      "question_type": "procedural",
      "question_text_ur": "3x² - 10x + 8 = 0 کو تحلیل سے حل کرو",
      "question_text_en": "Solve 3x² - 10x + 8 = 0 by factorization",
      "expected_answer": "x = 2, x = 4/3",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "a×c = 24. عدد جن کی ضرب 24 اور جمع -10 ہو", "math": "-6 اور -4"},
        {"step": 2, "description_ur": "درمیانی حد توڑیں", "math": "3x² - 6x - 4x + 8 = 0"},
        {"step": 3, "description_ur": "مشترک لیں", "math": "3x(x-2) - 4(x-2) = 0"},
        {"step": 4, "description_ur": "عامل بنائیں", "math": "(3x-4)(x-2) = 0"},
        {"step": 5, "description_ur": "جواب نکالیں", "math": "x = 4/3, x = 2"}
      ],
      "hints": [
        "a اور c کا حاصل ضرب 24 ہے۔ اب 24 کے factors دیکھیں"
      ],
      "tags": ["procedural", "factorization"]
    },
    {
      "question_id": "math10.ch2.comp.q02",
      "concept_id": "math10.ch2.completing_the_square",
      "difficulty": 4,
      "question_type": "procedural",
      "question_text_ur": "x² - 8x + 15 = 0 کو مربع مکمل کر کے حل کرو",
      "question_text_en": "Solve x² - 8x + 15 = 0 by completing the square",
      "expected_answer": "x = 3, x = 5",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "مستقل عدد کو دائیں طرف لے جائیں", "math": "x² - 8x = -15"},
        {"step": 2, "description_ur": "(-8/2)² یعنی 16 کو دونوں طرف جمع کریں", "math": "x² - 8x + 16 = -15 + 16"},
        {"step": 3, "description_ur": "کامل مربع بنائیں", "math": "(x-4)² = 1"},
        {"step": 4, "description_ur": "جذر لیں اور حل کریں", "math": "x - 4 = ±1 ➔ x = 5, x = 3"}
      ],
      "hints": [
        "x کے ضریب (-8) کو 2 پر تقسیم کر کے اس کا مربع لیں"
      ],
      "tags": ["procedural", "completing_square"]
    },
    {
      "question_id": "math10.ch2.comp.q03",
      "concept_id": "math10.ch2.completing_the_square",
      "difficulty": 5,
      "question_type": "board_style",
      "question_text_ur": "2x² - 5x - 3 = 0 کو مربع مکمل کر کے حل کرو",
      "question_text_en": "Solve 2x² - 5x - 3 = 0 by completing the square",
      "expected_answer": "x = 3, x = -1/2",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "پوری مساوات کو 2 سے تقسیم کریں", "math": "x² - (5/2)x - 3/2 = 0"},
        {"step": 2, "description_ur": "مستقل کو دائیں طرف لے جائیں", "math": "x² - (5/2)x = 3/2"},
        {"step": 3, "description_ur": "(-5/4)² = 25/16 دونوں طرف جمع کریں", "math": "x² - (5/2)x + 25/16 = 3/2 + 25/16 = 49/16"},
        {"step": 4, "description_ur": "کامل مربع اور جذر", "math": "(x - 5/4)² = 49/16 ➔ x - 5/4 = ±7/4"},
        {"step": 5, "description_ur": "حل کریں", "math": "x = 3, x = -1/2"}
      ],
      "hints": [
        "سب سے پہلے x² کو اکیلا کریں یعنی پوری مساوات کو 2 سے تقسیم کریں"
      ],
      "tags": ["board_style", "completing_square", "fraction"]
    },
    {
      "question_id": "math10.ch2.disc.q04",
      "concept_id": "math10.ch2.discriminant",
      "difficulty": 2,
      "question_type": "procedural",
      "question_text_ur": "9x² - 12x + 4 = 0 کا discriminant نکالو",
      "question_text_en": "Find the discriminant of 9x² - 12x + 4 = 0",
      "expected_answer": "0",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "a=9, b=-12, c=4", "math": "D = (-12)² - 4(9)(4)"},
        {"step": 2, "description_ur": "حل کریں", "math": "D = 144 - 144 = 0"}
      ],
      "hints": [
        "D = b² - 4ac میں قدریں رکھیں"
      ],
      "tags": ["procedural", "discriminant"]
    },
    {
      "question_id": "math10.ch2.nor.q04",
      "concept_id": "math10.ch2.nature_of_roots",
      "difficulty": 3,
      "question_type": "procedural",
      "question_text_ur": "4x² - 5x + 2 = 0 کی جڑوں کی نوعیت کیا ہے؟",
      "question_text_en": "What is the nature of roots of 4x² - 5x + 2 = 0?",
      "expected_answer": "no_real_roots",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "Discriminant نکالیں", "math": "D = (-5)² - 4(4)(2) = 25 - 32 = -7"},
        {"step": 2, "description_ur": "چونکہ D منفی ہے، اس لئے حقیقی جڑیں نہیں ہیں", "math": "مفروضی جڑیں (no real roots)"}
      ],
      "hints": [
        "Discriminant کا جواب منفی آئے تو نوعیت کیا ہوتی ہے؟"
      ],
      "tags": ["procedural", "nature_of_roots"]
    },
    {
      "question_id": "math10.ch2.nor.q05",
      "concept_id": "math10.ch2.nature_of_roots",
      "difficulty": 4,
      "question_type": "application",
      "question_text_ur": "ثابت کرو کہ مساوات x² - 2x + 5 = 0 کی جڑیں مفروضی (imaginary) ہیں",
      "question_text_en": "Prove that the roots of the equation x² - 2x + 5 = 0 are imaginary",
      "expected_answer": "D = -16, roots are imaginary",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "ممیز نکالیں", "math": "D = (-2)² - 4(1)(5)"},
        {"step": 2, "description_ur": "حل کریں", "math": "D = 4 - 20 = -16"},
        {"step": 3, "description_ur": "چونکہ جواب منفی ہے، ثابت ہوا کہ جڑیں مفروضی ہیں", "math": "D < 0"}
      ],
      "hints": [
        "imaginary جڑوں کی شرط D < 0 ہوتی ہے۔ بس D نکال کر دیکھو"
      ],
      "tags": ["application", "nature_of_roots", "proof"]
    },
    {
      "question_id": "math10.ch2.qf.q05",
      "concept_id": "math10.ch2.quadratic_formula",
      "difficulty": 3,
      "question_type": "procedural",
      "question_text_ur": "x² - x - 6 = 0 کو مربعی فارمولے سے حل کرو",
      "question_text_en": "Solve x² - x - 6 = 0 using quadratic formula",
      "expected_answer": "x = 3, x = -2",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "a=1, b=-1, c=-6", "math": ""},
        {"step": 2, "description_ur": "فارمولے میں رکھیں", "math": "x = (-(-1) ± √((-1)² - 4(1)(-6))) / 2"},
        {"step": 3, "description_ur": "حل کریں", "math": "x = (1 ± √(1 + 24)) / 2 = (1 ± 5) / 2"},
        {"step": 4, "description_ur": "دو جوابات", "math": "x = 6/2 = 3, x = -4/2 = -2"}
      ],
      "hints": [
        "فارمولے میں -b کا مطلب ہے -(-1) = 1"
      ],
      "tags": ["procedural", "quadratic_formula"]
    },
    {
      "question_id": "math10.ch2.qf.q06",
      "concept_id": "math10.ch2.quadratic_formula",
      "difficulty": 4,
      "question_type": "board_style",
      "question_text_ur": "6x² - 13x + 6 = 0 کو مربعی فارمولے سے حل کرو",
      "question_text_en": "Solve 6x² - 13x + 6 = 0 using quadratic formula",
      "expected_answer": "x = 3/2, x = 2/3",
      "answer_tolerance": None,
      "expected_answer_unit": None,
      "solution_steps": [
        {"step": 1, "description_ur": "a=6, b=-13, c=6", "math": ""},
        {"step": 2, "description_ur": "فارمولا", "math": "x = (13 ± √(169 - 144)) / 12"},
        {"step": 3, "description_ur": "جذر", "math": "x = (13 ± √25) / 12 = (13 ± 5) / 12"},
        {"step": 4, "description_ur": "جواب", "math": "x = 18/12 = 3/2, x = 8/12 = 2/3"}
      ],
      "hints": [
        "13 کا مربع 169 ہوتا ہے"
      ],
      "tags": ["board_style", "quadratic_formula"]
    },
    {
      "question_id": "math10.ch2.wp.q04",
      "concept_id": "math10.ch2.word_problems",
      "difficulty": 5,
      "question_type": "word_problem",
      "question_text_ur": "ایک مربع (square) کا رقبہ 81 سینٹی میٹر² ہے۔ اس کے ضلع کی لمبائی معلوم کرو",
      "question_text_en": "The area of a square is 81 cm². Find the length of its side.",
      "expected_answer": "9",
      "answer_tolerance": None,
      "expected_answer_unit": "cm",
      "solution_steps": [
        {"step": 1, "description_ur": "ضلع کو x مان لیں", "math": "x"},
        {"step": 2, "description_ur": "رقبہ کا فارمولا x² ہے", "math": "x² = 81"},
        {"step": 3, "description_ur": "دونوں طرف جذر لیں", "math": "x = ±9"},
        {"step": 4, "description_ur": "لمبائی منفی نہیں ہو سکتی اس لیے x = 9", "math": "x = 9"}
      ],
      "hints": [
        "مربع کے رقبے کا فارمولا ضلع × ضلع ہوتا ہے"
      ],
      "tags": ["word_problem", "square", "area"]
    },
    {
      "question_id": "math10.ch2.wp.q05",
      "concept_id": "math10.ch2.word_problems",
      "difficulty": 6,
      "question_type": "challenge",
      "question_text_ur": "ایک مثلث کا قاعدہ (base) اس کے ارتفاع (altitude) سے 3 سینٹی میٹر زیادہ ہے۔ اگر اس کا رقبہ 54 سینٹی میٹر² ہو، تو قاعدہ اور ارتفاع معلوم کرو",
      "question_text_en": "The base of a triangle is 3 cm more than its altitude. If the area is 54 cm², find the base and altitude.",
      "expected_answer": "altitude = 9, base = 12",
      "answer_tolerance": None,
      "expected_answer_unit": "cm",
      "solution_steps": [
        {"step": 1, "description_ur": "ارتفاع کو x اور قاعدے کو x+3 مانیں", "math": "altitude=x, base=x+3"},
        {"step": 2, "description_ur": "رقبے کا فارمولا: 1/2 × قاعدہ × ارتفاع = 54", "math": "1/2 * x(x+3) = 54"},
        {"step": 3, "description_ur": "2 کو ادھر ضرب دیں", "math": "x² + 3x = 108"},
        {"step": 4, "description_ur": "مساوات بنائیں", "math": "x² + 3x - 108 = 0"},
        {"step": 5, "description_ur": "تحلیل کریں", "math": "(x+12)(x-9) = 0 ➔ x = 9 (منفی نظر انداز)"},
        {"step": 6, "description_ur": "جواب", "math": "altitude=9, base=12"}
      ],
      "hints": [
        "مثلث کے رقبے کا فارمولا (1/2 * base * height) استعمال کرو"
      ],
      "tags": ["challenge", "word_problem", "triangle"]
    }
]

file_path = "/mnt/DataDrive/What I want to Achieve/AI Tutor/data/curriculum/mathematics/questions/ch02_quadratic_equations.json"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

data['questions'].extend(questions_to_add)
data['_meta']['total_questions'] = len(data['questions'])

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {len(questions_to_add)} questions. Total is now {data['_meta']['total_questions']}.")
