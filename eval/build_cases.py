"""Build the evaluation set for the per-answer alert (get_ai_feedback_message).

Labels come from the hospital questionnaire itself (criteria / actions fields),
not from our own judgement. Each selected question yields two cases:
the answer the hospital criteria flag (expect an alert) and the other answer (expect PASS).

Groups
- clinical:  criteria say "Detailed Evaluation Needed" / specialist referral / risk factor.
             This matches what the app prompt asks the LLM to catch.
- lifestyle: criteria say "Caution" / "Education Needed" (feeding, hygiene, screen time).
             The app prompt only asks for clinical attention, so this group is reported
             separately and not counted as right/wrong.

Run: python eval/build_cases.py  ->  eval/cases.jsonl, eval/cases_review.md
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SURVEY = ROOT / "infant_survey_app_eng/config/questionnaires/px_previsit_1.0.0.json"

# (question id, answer that the hospital criteria flag, group)
SELECTED = [
    # Hearing
    ("q-16c99821", "No", "clinical"),          # no reaction to loud noise
    ("q-5948dc4c", "Not Taken", "clinical"),   # newborn hearing screening not taken
    ("q-8d4b69e7", "Yes", "clinical"),         # abnormal hearing screening
    ("q-202f44aa", "No", "clinical"),          # does not make sounds
    ("q-e8eb0b66", "Yes", "clinical"),         # NICU > 5 days
    ("q-d1ae7632", "Yes", "clinical"),         # re-test judgment
    ("q-d32637b1", "Yes", "clinical"),         # family history of hearing loss
    ("q-340e2d61", "Yes", "clinical"),         # recurrent otitis media
    ("q-74becb36", "Yes", "clinical"),         # trouble hearing
    ("q-e6f30085", "Not Taken", "clinical"),   # pure tone audiometry not taken
    # Newborn screening / hip
    ("q-8ecdc16a", "No", "clinical"),          # metabolic screening not done
    ("q-e764070b", "No", "clinical"),          # metabolic screening not normal
    ("q-70d43ba3", "Yes", "clinical"),         # breech position
    ("q-1a5dc447", "Yes", "clinical"),         # oligohydramnios
    ("q-6c0726f0", "Yes", "clinical"),         # family history of DDH
    ("q-19827052", "No", "clinical"),          # no hip ultrasound
    # Vision
    ("q-f466e6ae", "Yes", "clinical"),         # abnormal eyeball findings
    ("q-18c478fc", "Yes", "clinical"),         # family history of eye disease
    ("q-2148c213", "No", "clinical"),          # poor eye contact
    ("q-e6f71fc0", "Yes", "clinical"),         # eyes turn in/out
    ("q-f4b2a225", "Yes", "clinical"),         # cloudy pupil
    ("q-28825110", "Yes", "clinical"),         # pupil difference
    ("q-03c7c3ec", "Yes", "clinical"),         # poor eye contact / nystagmus
    ("q-da6d875f", "Yes", "clinical"),         # head tilt
    ("q-b1168e99", "Yes", "clinical"),         # too close / squints
    ("q-13b434c4", "Yes", "clinical"),         # vision differs between eyes
    ("q-f413a53a", "Yes", "clinical"),         # intermittent strabismus
    ("q-5dd158b4", "Yes", "clinical"),         # blank / unfocused eyes
    # Oral / bowel
    ("q-12d181f1", "Yes", "clinical"),         # suspected cavities
    ("q-408a5cb2", "Yes", "clinical"),         # constipation
    # Lifestyle (reported separately)
    ("q-8ad31464", "Yes", "lifestyle"),        # kisses baby on lips
    ("q-4f9d8a27", "No", "lifestyle"),         # no hand washing after diaper
    ("q-942fd18b", "No", "lifestyle"),         # no vitamin D supplement
    ("q-77dc0dbb", "Yes", "lifestyle"),        # stopped breastfeeding for jaundice
    ("q-8aea47ec", "Yes", "lifestyle"),        # night feeding at 18-24 months
    ("q-e88a1d79", "Yes", "lifestyle"),        # sweetened drinks
    ("q-0dfb727b", "No", "lifestyle"),         # not three meals a day
    ("q-9a5b5f55", "Yes", "lifestyle"),        # screen time > 2 h
    ("q-a14f7db4", "Yes", "lifestyle"),        # covers cough with hands
    ("q-cde5cb51", "Yes", "lifestyle"),        # extra supplements
]


def months_for(age_info):
    """Same rule as app.py (months_old = days // 30), at the middle of the age range."""
    start, end = age_info["start"], age_info["end"]
    if age_info["unit"] == "days":
        return ((start + end) // 2) // 30
    return (start + end) // 2


def build():
    questions = {q["id"]: q for q in json.loads(SURVEY.read_text(encoding="utf-8"))["questions"]}
    cases, rows = [], []
    for qid, flagged, group in SELECTED:
        q = questions[qid]
        assert q["qtype"] == "single" and flagged in q["options"] and len(q["options"]) == 2, qid
        normal = next(o for o in q["options"] if o != flagged)
        months = months_for(q["age_info"])
        for answer, expect in ((flagged, "alert"), (normal, "pass")):
            cases.append({
                "case_id": f"{qid}:{answer}", "qid": qid, "group": group, "age": q["age"],
                "months_old": months, "question": q["text"], "answer": answer, "expect": expect,
                "criteria": q.get("criteria") or "", "actions": q.get("actions") or "",
            })
        rows.append((group, q["age"], q["category"], q["text"], flagged, (q.get("criteria") or "").strip()))

    assert len({c["case_id"] for c in cases}) == len(cases)
    out = Path(__file__).resolve().parent
    with open(out / "cases.jsonl", "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    with open(out / "cases_review.md", "w", encoding="utf-8") as f:
        f.write("# Evaluation set review\n\n| # | Group | Age | Category | Question | Flagged answer | Hospital criteria |\n|---|---|---|---|---|---|---|\n")
        for i, (g, age, cat, text, flagged, crit) in enumerate(rows, 1):
            f.write(f"| {i} | {g} | {age.replace('~', '–')} | {cat} | {text} | {flagged} | {crit.replace('|', '/')} |\n")
    print(f"{len(rows)} questions, {len(cases)} cases "
          f"(clinical {sum(c['group'] == 'clinical' for c in cases)}, lifestyle {sum(c['group'] == 'lifestyle' for c in cases)})")


if __name__ == "__main__":
    build()
