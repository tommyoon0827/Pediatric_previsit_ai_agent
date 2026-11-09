# Evaluation: real-time risk alert

For each question the app shows the hospital's criteria and recommended actions under "Detailed Info". On top of that, it shows an alert right after a guardian answers. An LLM (gpt-4o-mini) reads the child's age, the question and the answer, and replies either `PASS` or `⚠️ <advice>` (`get_ai_feedback_message` in `infant_survey_app_eng/app.py`).
This folder measures how often that judgement is right.

## Evaluation set

- 40 single-choice questions from the questionnaire, two cases each: the answer the hospital criteria flag (an alert is expected) and the other answer (`PASS` is expected). 80 cases.
- Labels come from the questionnaire's own `criteria` / `actions` fields, written from the hospital's pre-visit material, not from our judgement. For two hearing items the criteria text is generic, so the `actions` text ("no reaction to sound → ENT visit") was used.
- **clinical (30 questions):** criteria say "Detailed Evaluation Needed", a specialist referral, or a risk factor. This is what the app prompt asks the LLM to catch, so these are scored.
- **lifestyle (10 questions):** criteria say "Caution" or "Education Needed" (feeding, hygiene, screen time). The app prompt only asks for clinical attention, so this group is reported but not scored.
- Left out: injury-prevention and sleep-safety items (their criteria field is empty, so the label would be ours), and the stool-colour item (it asks "which colour" but its options are Yes/No).
- Age is passed the way the app does it (`days // 30`), at the middle of each age range.

The list with the criteria text is in [cases_review.md](cases_review.md); the cases are in `cases.jsonl`.

## Variants

| Variant | Prompt |
|---|---|
| `baseline` | The app's function, taken from `app.py` source unchanged |
| `with_criteria` | Same system prompt, plus that question's hospital criteria and actions. The app shows these fields to the guardian under "Detailed Info", but the LLM alert is decided without them |
| `criteria_strict` | `with_criteria` plus one line: alert only if the answer itself matches the problem the criteria describe |

Each case was run 3 times (gpt-4o-mini, temperature 0). Raw replies are recorded, so `PASS`, a format violation and an API error can be told apart; the app turns all three into "no alert".

## Results

Clinical group, 90 flagged and 90 normal answers per variant:

| | baseline | with_criteria | criteria_strict |
|---|---:|---:|---:|
| Alert on flagged answers (recall) | 93.3% (84/90) | **100%** (90/90) | 94.4% (85/90) |
| Alert on normal answers (false alarm) | 6.7% (6/90) | 11.1% (10/90) | **5.6%** (5/90) |
| Same result in all 3 runs | 60/60 | 59/60 | 58/60 |

Lifestyle group (not scored):

| | baseline | with_criteria | criteria_strict |
|---|---:|---:|---:|
| Alert on flagged answers | 50.0% (15/30) | 90.0% (27/30) | 90.0% (27/30) |
| Alert on normal answers | 10.0% (3/30) | 30.0% (9/30) | 13.3% (4/30) |

Format violations and API errors: 0 in all 720 calls.

### Where it went wrong (clinical)

- **baseline:** two items were judged in the reverse direction, 3 out of 3 runs. "Did you receive a 're-test' judgment in the newborn hearing screening?" (4–6 months) and "Does the child consistently turn or tilt their head when looking at objects in front?" (18–24 months): `Yes` got `PASS`, `No` got an alert. All 6 misses and all 6 false alarms come from these two items.
- **with_criteria:** no misses, but the model started repeating the criteria regardless of the answer, e.g. "Immediate referral to ophthalmology is recommended" for `No` to "Do you feel there is a difference in vision between the two eyes?". False alarms on the two items above plus this one (3/3) and the pupil-difference item (1/3).
- **criteria_strict:** false alarms dropped, but the re-test item was missed again (3/3) even though its criteria say "If re-test judgment received, ENT treatment needed within 3 months". The head-tilt item was missed in 2 of 3 runs.

## What this shows

- Changing the prompt moved errors around instead of removing them: fewer misses meant more false alarms, and the reverse.
- Temperature 0 did not make the output fully repeatable (58/60 in the last variant).
- For yes/no items the hospital criteria already say which answer is the problem. Turning that into data and deciding by rule would be exact and repeatable. The LLM is better used for free-text answers and for wording the advice.
- The app's error handling turns a format violation or an API failure into "no alert". It did not happen in this run, but a failure there is silent.

## Limits

- 40 of 196 single-choice questions, chosen by us; one model; English version only.
- `with_criteria` gives the model the same text the labels were taken from, so part of its 100% recall is expected. It still matters because the app already shows this text on screen; it is only the LLM alert that does not see it.
- The clinical summary and the RAG chatbot are not evaluated here (the chatbot's documents are not in this repository).

## Re-run

```bash
pip install langchain-openai
python eval/build_cases.py                      # rebuilds cases.jsonl and cases_review.md
export OPENAI_API_KEY=...                       # PowerShell: $env:OPENAI_API_KEY = Read-Host "key"
python eval/run_eval.py                         # all variants, 3 runs each
python eval/run_eval.py --variants criteria_strict --runs 1
```

Results go to `results/<variant>.jsonl` (one line per call, with the raw reply) and `results/summary.md`.
