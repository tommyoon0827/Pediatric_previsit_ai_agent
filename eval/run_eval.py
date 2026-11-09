"""Run the per-answer alert evaluation.

- baseline: the app's own get_ai_feedback_message, taken from app.py source as-is
            (only the Streamlit cache decorator is dropped) so the prompt cannot drift.
- with_criteria: same system prompt, plus the hospital criteria/actions for that question
                 in the user prompt. The app shows these fields on screen but does not pass them to the LLM.
- criteria_strict: with_criteria plus one line telling the model to alert only when the
                   answer itself matches the problem in the criteria.

Raw model output is recorded, so we can tell "PASS" apart from a format violation or an
API error. The app turns all three into "no alert".

Needs OPENAI_API_KEY in the environment.
Run: python eval/run_eval.py [--runs 3] [--variants baseline,with_criteria,criteria_strict]
Out: eval/results/<variant>.jsonl, eval/results/summary.md
"""
import argparse
import ast
import json
import os
import sys
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from langchain_openai import ChatOpenAI

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "infant_survey_app_eng" / "app.py"
_raw = threading.local()


class RecordingChatOpenAI(ChatOpenAI):
    """ChatOpenAI that keeps the raw reply so the eval sees what the app throws away."""

    def invoke(self, *args, **kwargs):
        _raw.error = None
        try:
            out = super().invoke(*args, **kwargs)
        except Exception as e:  # the app swallows this; we record it
            _raw.content, _raw.error = None, repr(e)
            raise
        _raw.content = out.content
        return out


def load_app_function():
    """Pull get_ai_feedback_message and its system prompt out of app.py without importing Streamlit."""
    src = APP.read_text(encoding="utf-8")
    fn = next(n for n in ast.parse(src).body
              if isinstance(n, ast.FunctionDef) and n.name == "get_ai_feedback_message")
    fn.decorator_list = []
    ns = {"os": os, "ChatOpenAI": RecordingChatOpenAI}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(APP), "exec"), ns)
    system_prompt = next(n.value.value for n in ast.walk(fn)
                         if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "system_prompt")
    return ns["get_ai_feedback_message"], system_prompt


STRICT_RULE = """
        Use the reference only to judge THIS answer. Alert only if the guardian's answer itself
        matches the problem the criteria describe. If the answer is the reassuring one, print "PASS".
"""


def with_criteria_fn(system_prompt, strict=False):
    def judge(case):
        llm = RecordingChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.environ["OPENAI_API_KEY"])
        user_prompt = f"""
        [Data]
        - Age: {case['months_old']} months
        - Question: {case['question']}
        - Answer: {case['answer']}

        [Hospital Reference for this question]
        - Criteria: {case['criteria'] or '(none)'}
        - Actions: {case['actions'] or '(none)'}
{STRICT_RULE if strict else ''}
        Analysis Result:
        """
        try:
            feedback = llm.invoke([("system", system_prompt), ("human", user_prompt)]).content.strip()
        except Exception:
            return None
        return feedback if feedback.startswith("⚠️") else None
    return judge


def classify(raw, error):
    if error is not None:
        return "api_error"
    text = (raw or "").strip()
    if text == "PASS":
        return "pass"
    if text.startswith("⚠️"):
        return "alert"
    return "format_error"


def run_variant(name, call, cases, runs):
    def one(job):
        case, r = job
        _raw.content, _raw.error = None, None
        app_result = call(case)
        return {**{k: case[k] for k in ("case_id", "group", "expect")}, "run": r,
                "raw": _raw.content, "error": _raw.error,
                "label": classify(_raw.content, _raw.error),
                "app_alert": app_result is not None}

    jobs = [(c, r) for r in range(runs) for c in cases]
    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(one, jobs))
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / f"{name}.jsonl", "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def summarize(name, rows, runs):
    lines = [f"## {name}", ""]
    for group in ("clinical", "lifestyle"):
        g = [r for r in rows if r["group"] == group]
        flagged = [r for r in g if r["expect"] == "alert"]
        normal = [r for r in g if r["expect"] == "pass"]
        pct = lambda part, whole: f"{100 * len(part) / len(whole):.1f}% ({len(part)}/{len(whole)})"
        lines += [f"### {group}", "",
                  f"- alert on flagged answers (app view): {pct([r for r in flagged if r['app_alert']], flagged)}",
                  f"- alert on normal answers (app view): {pct([r for r in normal if r['app_alert']], normal)}",
                  f"- raw labels: {dict(Counter(r['label'] for r in g))}"]
        by_case = defaultdict(set)
        for r in g:
            by_case[r["case_id"]].add(r["app_alert"])
        stable = [c for c, s in by_case.items() if len(s) == 1]
        lines += [f"- same result in all {runs} runs: {len(stable)}/{len(by_case)} cases", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--variants", default="baseline,with_criteria,criteria_strict")
    args = ap.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set")

    cases = [json.loads(l) for l in open(HERE / "cases.jsonl", encoding="utf-8")]
    app_fn, system_prompt = load_app_function()
    variants = {
        "baseline": lambda c: app_fn(c["question"], c["answer"], c["months_old"]),
        "with_criteria": with_criteria_fn(system_prompt),
        "criteria_strict": with_criteria_fn(system_prompt, strict=True),
    }
    for name in args.variants.split(","):
        rows = run_variant(name, variants[name], cases, args.runs)
        print(summarize(name, rows, args.runs))

    # summary covers every variant that has results, so earlier runs are kept
    report = ["# Per-answer alert evaluation", "",
              f"{len(cases)} cases x {args.runs} runs, gpt-4o-mini, temperature 0", ""]
    for name in variants:
        path = HERE / "results" / f"{name}.jsonl"
        if path.exists():
            rows = [json.loads(l) for l in open(path, encoding="utf-8")]
            report.append(summarize(name, rows, args.runs))
    (HERE / "results" / "summary.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
