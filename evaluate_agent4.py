# evaluate_agent4.py
# Évaluation complète de l'Agent 4 (sans Function Coverage)

import re
import csv
import os
import sys
import ast
import time
import json
import argparse
from pathlib import Path

sys.path.append(os.getcwd())


# ──────────────────────────────────────────────
# CHARGEMENT
# ──────────────────────────────────────────────

def load_scripts(scripts_dir: str) -> dict:
    """Charge tous les scripts Playwright."""
    scripts = {}
    if not os.path.exists(scripts_dir):
        return scripts
    for fname in sorted(os.listdir(scripts_dir)):
        if fname.endswith(".py"):
            path = os.path.join(scripts_dir, fname)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                scripts[fname] = f.read()
    return scripts


def load_qa_results(json_path: str) -> list:
    if not os.path.exists(json_path):
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# MÉTRIQUES SIMPLES
# ──────────────────────────────────────────────

def compute_script_coverage(scripts: dict, qa_results: list) -> float:
    """% d'US ayant un script généré"""
    if not qa_results:
        return 0.0
    total = len(qa_results)
    covered = 0
    for r in qa_results:
        us_id = r.get("id", "").lower().replace("-", "_")
        expected = f"test_{us_id}.py"
        if expected in scripts:
            covered += 1
    return round((covered / total) * 100, 1)


def compute_syntax_validity(scripts: dict) -> dict:
    """% de scripts syntaxiquement valides"""
    if not scripts:
        return {"score": 0.0, "valid": 0, "invalid": 0, "errors": []}
    valid = 0
    invalid = 0
    errors = []
    for fname, code in scripts.items():
        try:
            ast.parse(code)
            valid += 1
        except SyntaxError as e:
            invalid += 1
            errors.append(f"{fname}: {e}")
    score = round((valid / len(scripts)) * 100, 1)
    return {"score": score, "valid": valid, "invalid": invalid, "errors": errors}


def compute_traceability(scripts: dict) -> float:
    """% de scripts avec # US: et # TC:"""
    if not scripts:
        return 0.0
    traced = 0
    for code in scripts.values():
        has_us = bool(re.search(r'#\s*US:\s*US-\d+', code))
        has_tc = bool(re.search(r'#\s*TC:', code))
        if has_us and has_tc:
            traced += 1
    return round((traced / len(scripts)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUES AVANCÉES
# ──────────────────────────────────────────────

def compute_playwright_api_usage(scripts: dict) -> float:
    """% de fonctions utilisant les APIs Playwright"""
    if not scripts:
        return 0.0

    required_patterns = [
        r'sync_playwright',
        r'p\.chromium\.launch',
        r'page\.(goto|locator|fill|click|wait)',
    ]
    assertion_pattern = r'expect\s*\('

    total_funcs = 0
    quality_funcs = 0

    for code in scripts.values():
        func_blocks = re.split(r'\ndef test_', code)
        for block in func_blocks[1:]:
            total_funcs += 1
            full_block = "def test_" + block

            has_required = all(
                re.search(p, full_block) for p in required_patterns
            )
            has_assertion = bool(re.search(assertion_pattern, full_block))

            if has_required and has_assertion:
                quality_funcs += 1

    return round((quality_funcs / total_funcs) * 100, 1) if total_funcs > 0 else 0.0


def compute_assertion_density(scripts: dict) -> dict:
    """Nombre moyen d'expect() par fonction"""
    if not scripts:
        return {"avg": 0.0, "score": 0.0}

    assertion_counts = []

    for code in scripts.values():
        func_blocks = re.split(r'\ndef test_', code)
        for block in func_blocks[1:]:
            full_block = "def test_" + block
            count = len(re.findall(r'expect\s*\(', full_block))
            assertion_counts.append(count)

    if not assertion_counts:
        return {"avg": 0.0, "score": 0.0}

    avg = round(sum(assertion_counts) / len(assertion_counts), 1)

    if 1 <= avg <= 3:
        score = 100.0
    elif avg <= 5:
        score = 75.0
    elif avg == 0:
        score = 20.0
    else:
        score = 50.0

    return {"avg": avg, "score": score}


def compute_test_independence(scripts: dict) -> float:
    """% de fonctions indépendantes (propres browser)"""
    if not scripts:
        return 0.0

    total_funcs = 0
    independent_funcs = 0

    for code in scripts.values():
        func_blocks = re.split(r'\ndef test_', code)
        for block in func_blocks[1:]:
            total_funcs += 1
            full_block = "def test_" + block

            has_context_manager = bool(re.search(
                r'with sync_playwright\(\) as p:', full_block
            ))
            has_close = bool(re.search(r'browser\.close\(\)', full_block))

            if has_context_manager:
                independent_funcs += 1
            elif has_close:
                independent_funcs += 1

    return round((independent_funcs / total_funcs) * 100, 1) if total_funcs > 0 else 0.0


def compute_bert_score(scripts: dict, qa_results: list) -> float:
    """Alignement sémantique script / test cases"""
    try:
        from bert_score import score as bert_score_fn
    except ImportError:
        return 0.0

    hypotheses = []
    references = []

    for r in qa_results:
        us_id = r.get("id", "").lower().replace("-", "_")
        expected = f"test_{us_id}.py"

        if expected not in scripts:
            continue

        script_text = scripts[expected]
        tc_text = " ".join(
            tc.get("name", "") + " " + str(tc.get("expected_result", ""))
            for tc in r.get("test_cases", [])
        )

        if script_text and tc_text:
            hypotheses.append(script_text[:500])
            references.append(tc_text[:500])

    if not hypotheses:
        return 0.0

    hypotheses = hypotheses[:15]
    references = references[:15]

    try:
        P, R, F1 = bert_score_fn(
            hypotheses, references,
            lang="en", verbose=False,
            model_type="distilbert-base-multilingual-cased"
        )
        return round(F1.mean().item() * 100, 1)
    except Exception:
        return 0.0


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def run_evaluation(
    scripts_dir: str = "output/scripts",
    qa_json: str = "output/qa_analysis.json"
):
    print(f"\n{'='*60}")
    print("📄 AGENT 4 — Test Script Evaluation")
    print(f"{'='*60}")

    scripts = load_scripts(scripts_dir)
    qa_results = load_qa_results(qa_json)

    print(f"  📂 Scripts loaded   : {len(scripts)}")
    print(f"  📂 QA results loaded: {len(qa_results)}")

    start = time.time()

    # ── Métriques simples ──
    coverage = compute_script_coverage(scripts, qa_results)
    syntax = compute_syntax_validity(scripts)
    traceability = compute_traceability(scripts)

    # ── Métriques avancées ──
    api_usage = compute_playwright_api_usage(scripts)
    assertions = compute_assertion_density(scripts)
    independence = compute_test_independence(scripts)
    bert_s = compute_bert_score(scripts, qa_results)

    duration = round(time.time() - start, 2)

    # ── Stats ──
    total_funcs = sum(
        len(re.findall(r'def test_\w+\s*\(', code))
        for code in scripts.values()
    )
    total_tc = sum(len(r.get("test_cases", [])) for r in qa_results)

    # ── Score global (sans Function Coverage) ──
    score = round(
        coverage * 0.12 +
        syntax["score"] * 0.12 +
        traceability * 0.12 +
        api_usage * 0.20 +
        assertions["score"] * 0.12 +
        independence * 0.16 +
        bert_s * 0.16,
        1
    )

    verdict = (
        "✅ Agent performant et fiable"
        if score >= 85 else
        "⚠️ Agent fonctionnel mais améliorable"
        if score >= 65 else
        "❌ Agent peu fiable — révision nécessaire"
    )

    # ── Affichage ──
    print(f"\n{'='*60}")
    print("📊 RAPPORT D'ÉVALUATION — AGENT 4 (Test Scripts)")
    print(f"{'='*60}")
    print(f"  Scripts generated      : {len(scripts)}")
    print(f"  Test functions total   : {total_funcs}")
    print(f"  QA test cases (Agent3) : {total_tc}")
    print(f"  ── Métriques simples ──────────────────")
    print(f"  Script Coverage        : {coverage}%")
    print(f"    → % US with generated script")
    print(f"  Syntax Validity        : {syntax['score']}%")
    print(f"    → Valid: {syntax['valid']} | Invalid: {syntax['invalid']}")
    if syntax["errors"]:
        for e in syntax["errors"][:3]:
            print(f"    ⚠️ {e}")
    print(f"  Traceability           : {traceability}%")
    print(f"    → % scripts with # US: and # TC: comments")
    print(f"  ── Métriques avancées ─────────────────")
    print(f"  Playwright API Usage   : {api_usage}%")
    print(f"    → % functions using sync_playwright + goto + expect")
    print(f"  Assertion Density      : {assertions['score']}%")
    print(f"    → Avg {assertions['avg']} expect() per function (ideal: 1-3)")
    print(f"  Test Independence      : {independence}%")
    print(f"    → % functions with own browser open/close")
    print(f"  BERTScore              : {bert_s}%")
    print(f"    → Semantic alignment script / Agent3 test cases")
    print(f"\n  📈 Score global pondéré : {score}/100")
    print(f"  Verdict : {verdict}")
    print(f"  Duration               : {duration}s")
    print(f"{'='*60}")

    # ── CSV ──
    os.makedirs("output/reports", exist_ok=True)
    csv_path = "output/reports/agent4_evaluation.csv"
    row = {
        "Scripts_Generated": len(scripts),
        "Total_Test_Functions": total_funcs,
        "Script_Coverage_%": coverage,
        "Syntax_Validity_%": syntax["score"],
        "Traceability_%": traceability,
        "Playwright_API_Usage_%": api_usage,
        "Assertion_Density_avg": assertions["avg"],
        "Assertion_Density_score_%": assertions["score"],
        "Test_Independence_%": independence,
        "BERTScore_%": bert_s,
        "Overall_Score": score,
        "Verdict": verdict,
        "Duration_sec": duration,
    }
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)
    print(f"\n💾 CSV : {csv_path}")

    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Évaluation Agent 4")
    parser.add_argument("--scripts", default="output/scripts")
    parser.add_argument("--qa", default="output/qa_analysis.json")
    args = parser.parse_args()
    run_evaluation(args.scripts, args.qa)