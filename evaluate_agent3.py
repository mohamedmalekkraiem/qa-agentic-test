import re
import csv
import os
import sys
import time
import json
import argparse

sys.path.append(os.getcwd())

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
def get_qa_config(json_path: str = "output/qa_analysis.json") -> dict:
    return {"json": json_path}


# ──────────────────────────────────────────────
# Chargement des données QA
# ──────────────────────────────────────────────
def load_qa_results(json_path: str) -> list:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 1 — Coverage
# ──────────────────────────────────────────────
def compute_coverage(results: list) -> float:
    if not results:
        return 0.0
    covered = sum(1 for r in results if r.get("test_cases"))
    return round((covered / len(results)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 2 — Test Case Completeness (CORRIGÉE)
# ──────────────────────────────────────────────
def compute_tc_completeness(results: list) -> float:
    total = 0
    complete = 0
    for r in results:
        for tc in r.get("test_cases", []):
            total += 1
            has_name = bool(tc.get("name", "").strip())
            has_steps = bool(tc.get("steps")) and len(tc.get("steps", [])) >= 1
            
            # ⭐⭐ CORRECTION : expected_result peut être une liste ⭐⭐
            expected = tc.get("expected_result", "")
            if isinstance(expected, list):
                expected = " ".join(str(item) for item in expected)
            has_expected = bool(expected.strip())
            
            if has_name and has_steps and has_expected:
                complete += 1
    return round((complete / total) * 100, 1) if total > 0 else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 3 — Acceptance Criteria Extraction
# ──────────────────────────────────────────────
def compute_ac_extraction(results: list) -> float:
    if not results:
        return 0.0
    good = sum(
        1 for r in results
        if len(r.get("acceptance_criteria", [])) >= 2
    )
    return round((good / len(results)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 4 — Scenario Coverage
# ──────────────────────────────────────────────
def compute_scenario_coverage(results: list) -> float:
    if not results:
        return 0.0

    happy_keywords = [
        "happy path", "nominal", "valid", "success",
        "positive", "correct", "normal"
    ]
    edge_keywords = [
        "edge case", "error", "invalid", "empty",
        "negative", "fail", "exception", "boundary",
        "missing", "incorrect", "unauthorized"
    ]

    good = 0
    for r in results:
        scenarios = " ".join(r.get("test_scenarios", [])).lower()
        tc_text = " ".join(
            tc.get("name", "") + " " + 
            (" ".join(tc.get("expected_result", [])) if isinstance(tc.get("expected_result", ""), list) else tc.get("expected_result", ""))
            for tc in r.get("test_cases", [])
        ).lower()
        full_text = scenarios + " " + tc_text

        has_happy = any(kw in full_text for kw in happy_keywords)
        has_edge = any(kw in full_text for kw in edge_keywords)

        if has_happy and has_edge:
            good += 1

    return round((good / len(results)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 5 — Average Test Cases per US
# ──────────────────────────────────────────────
def compute_avg_tc_per_us(results: list) -> dict:
    if not results:
        return {"avg": 0.0, "score": 0.0}

    counts = [len(r.get("test_cases", [])) for r in results]
    avg = round(sum(counts) / len(counts), 1)

    # Score basé sur la distribution idéale (3-5 TC par US)
    if 3 <= avg <= 5:
        score = 100.0
    elif 2 <= avg <= 6:
        score = 80.0
    elif 1 <= avg <= 7:
        score = 60.0
    else:
        score = 30.0

    return {"avg": avg, "score": score}


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 1 — Step Quality
# ──────────────────────────────────────────────
def compute_step_quality(results: list) -> float:
    action_verbs = [
        "log", "navigate", "click", "enter", "select", "submit",
        "verify", "check", "upload", "download", "open", "close",
        "create", "delete", "update", "search", "filter", "observe",
        "confirm", "attempt", "perform", "access", "fill", "choose",
        "set", "save", "view", "go", "drag", "drop", "trigger",
        "simulate", "run", "add", "remove", "modify"
    ]

    total_steps = 0
    quality_steps = 0

    for r in results:
        for tc in r.get("test_cases", []):
            steps = tc.get("steps", [])
            for step in steps:
                total_steps += 1
                step_lower = step.lower().strip()
                if (len(step_lower) > 10 and
                        any(step_lower.startswith(v) for v in action_verbs)):
                    quality_steps += 1

    return round((quality_steps / total_steps) * 100, 1) if total_steps > 0 else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 2 — AC Alignment
# ──────────────────────────────────────────────
def compute_ac_alignment(results: list, us_text: str = "") -> float:
    if not results:
        return 0.0

    total = 0
    quality = 0
    for r in results:
        for ac in r.get("acceptance_criteria", []):
            total += 1
            if (len(ac) > 20 and
                    any(kw in ac.lower() for kw in
                        ["must", "should", "shall", "need", "require",
                         "doit", "doivent", "nécessaire"])):
                quality += 1
    return round((quality / total) * 100, 1) if total > 0 else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 3 — TC Diversity (CORRIGÉE)
# ──────────────────────────────────────────────
def compute_tc_diversity(results: list) -> float:
    if not results:
        return 0.0

    diversity_scores = []

    for r in results:
        tcs = r.get("test_cases", [])
        if len(tcs) < 2:
            diversity_scores.append(1.0)
            continue

        titles = []
        for tc in tcs:
            name = tc.get("name", "")
            # Récupérer aussi expected pour plus de diversité
            expected = tc.get("expected_result", "")
            if isinstance(expected, list):
                expected = " ".join(str(item) for item in expected)
            titles.append(f"{name} {expected}".lower())

        pairs = 0
        diverse = 0

        for i, t1 in enumerate(titles):
            for t2 in titles[i+1:]:
                pairs += 1
                words1 = set(t1.split())
                words2 = set(t2.split())
                if not words1 or not words2:
                    continue
                overlap = len(words1 & words2) / min(len(words1), len(words2))
                if overlap < 0.60:
                    diverse += 1

        if pairs > 0:
            diversity_scores.append(diverse / pairs)

    return round((sum(diversity_scores) / len(diversity_scores)) * 100, 1) if diversity_scores else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 4 — BERTScore Alignment (CORRIGÉE)
# ──────────────────────────────────────────────
def compute_bert_alignment(results: list) -> float:
    try:
        from bert_score import score as bert_score_fn
    except ImportError:
        print("   ⚠️ bert_score not installed → skipping BERTScore")
        return 0.0

    hypotheses = []
    references = []

    for r in results:
        ac_text = " ".join(r.get("acceptance_criteria", []))
        if not ac_text:
            continue
        for tc in r.get("test_cases", []):
            expected = tc.get("expected_result", "")
            if isinstance(expected, list):
                expected = " ".join(str(item) for item in expected)
            if expected and len(expected) > 10:
                hypotheses.append(expected)
                references.append(ac_text)

    if not hypotheses:
        return 0.0

    hypotheses = hypotheses[:20]
    references = references[:20]

    try:
        P, R, F1 = bert_score_fn(
            hypotheses, references,
            lang="en", verbose=False,
            model_type="distilbert-base-multilingual-cased"
        )
        return round(F1.mean().item() * 100, 1)
    except Exception as e:
        print(f"   ⚠️ BERTScore error: {e}")
        return 0.0


# ──────────────────────────────────────────────
# Main evaluation
# ──────────────────────────────────────────────
def run_evaluation(config: dict, us_text: str = ""):
    json_path = config["json"]

    print(f"\n{'='*60}")
    print(f"📄 QA Analysis : {json_path}")
    print(f"{'='*60}")

    if not os.path.exists(json_path):
        print(f"  ⚠️ JSON introuvable : {json_path}")
        print(f"  → Lance d'abord : python main_agent3.py")
        return

    print(f"  📂 Loading QA results from {json_path}...")
    start = time.time()
    results = load_qa_results(json_path)
    print(f"  → {len(results)} US loaded")

    # ── Métriques simples ──
    print("\n  📐 Computing simple metrics...")
    coverage = compute_coverage(results)
    completeness = compute_tc_completeness(results)
    ac_extract = compute_ac_extraction(results)
    scenario_cov = compute_scenario_coverage(results)
    tc_stats = compute_avg_tc_per_us(results)

    # ── Métriques avancées ──
    print("  🔍 Computing Step Quality...")
    step_quality = compute_step_quality(results)

    print("  📋 Computing AC Alignment...")
    ac_alignment = compute_ac_alignment(results, us_text)

    print("  🎯 Computing Test Case Diversity...")
    tc_diversity = compute_tc_diversity(results)

    print("  🧠 Computing BERTScore Alignment...")
    bert_align = compute_bert_alignment(results)

    duration = round(time.time() - start, 2)

    # ── Statistiques ──
    total_tc = sum(len(r.get("test_cases", [])) for r in results)
    total_ac = sum(len(r.get("acceptance_criteria", [])) for r in results)
    total_sc = sum(len(r.get("test_scenarios", [])) for r in results)

    # ── Affichage ──
    print(f"\n  ✅ Results:")
    print(f"     US Analyzed           : {len(results)}")
    print(f"     Total Test Cases       : {total_tc}")
    print(f"     Total Acceptance Crit. : {total_ac}")
    print(f"     Total Test Scenarios   : {total_sc}")
    print(f"     Avg TC per US          : {tc_stats['avg']}")
    print(f"     ── Métriques simples ──────────────")
    print(f"     Coverage               : {coverage}%")
    print(f"       → % US with ≥1 test case")
    print(f"     TC Completeness        : {completeness}%")
    print(f"       → % TCs with name+steps+expected")
    print(f"     AC Extraction          : {ac_extract}%")
    print(f"       → % US with ≥2 acceptance criteria")
    print(f"     Scenario Coverage      : {scenario_cov}%")
    print(f"       → % US with happy path + edge case")
    print(f"     TC Count Score         : {tc_stats['score']}%")
    print(f"       → Avg {tc_stats['avg']} TC/US (ideal: 3-5)")
    print(f"     ── Métriques avancées ──────────────")
    print(f"     Step Quality           : {step_quality}%")
    print(f"       → % steps starting with action verb")
    print(f"     AC Alignment           : {ac_alignment}%")
    print(f"       → Acceptance criteria use must/should + >20 chars")
    print(f"     TC Diversity           : {tc_diversity}%")
    print(f"       → Test cases are non-redundant within same US")
    print(f"     BERTScore Alignment    : {bert_align}%")
    print(f"       → Semantic alignment between expected results & AC")
    print(f"     Duration               : {duration}s")

    # ── Score global pondéré ──
    score = round(
        coverage      * 0.08 +
        completeness  * 0.08 +
        ac_extract    * 0.08 +
        scenario_cov  * 0.08 +
        tc_stats["score"] * 0.08 +
        step_quality  * 0.20 +
        ac_alignment  * 0.15 +
        tc_diversity  * 0.10 +
        bert_align    * 0.15,
        1
    )

    verdict = (
        "✅ Agent performant et fiable"
        if score >= 85 else
        "⚠️ Agent fonctionnel mais améliorable"
        if score >= 65 else
        "❌ Agent peu fiable — révision nécessaire"
    )

    print(f"\n{'='*60}")
    print("📊 RAPPORT D'ÉVALUATION — AGENT 3 (QA)")
    print(f"{'='*60}")
    print(f"  US Analyzed            : {len(results)}")
    print(f"  Total Test Cases       : {total_tc}")
    print(f"  ── Métriques simples ──────────────────")
    print(f"  Coverage               : {coverage}%")
    print(f"  TC Completeness        : {completeness}%")
    print(f"  AC Extraction          : {ac_extract}%")
    print(f"  Scenario Coverage      : {scenario_cov}%")
    print(f"  TC Count Score         : {tc_stats['score']}%")
    print(f"  ── Métriques avancées ─────────────────")
    print(f"  Step Quality           : {step_quality}%")
    print(f"  AC Alignment           : {ac_alignment}%")
    print(f"  TC Diversity           : {tc_diversity}%")
    print(f"  BERTScore Alignment    : {bert_align}%")
    print(f"\n  📈 Score global pondéré : {score}/100")
    print(f"  Verdict : {verdict}")
    print(f"{'='*60}")

    # ── CSV ──
    os.makedirs("output", exist_ok=True)
    csv_path = "output/agent3_evaluation_report.csv"
    row = {
        "US_Analyzed": len(results),
        "Total_TC": total_tc,
        "Total_AC": total_ac,
        "Avg_TC_per_US": tc_stats["avg"],
        "Coverage_%": coverage,
        "TC_Completeness_%": completeness,
        "AC_Extraction_%": ac_extract,
        "Scenario_Coverage_%": scenario_cov,
        "TC_Count_Score_%": tc_stats["score"],
        "Step_Quality_%": step_quality,
        "AC_Alignment_%": ac_alignment,
        "TC_Diversity_%": tc_diversity,
        "BERTScore_Alignment_%": bert_align,
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
    parser = argparse.ArgumentParser(description="Évaluation Agent 3 (QA)")
    parser.add_argument(
        "--json",
        default="output/qa_analysis.json",
        help="Chemin vers le JSON QA (default: output/qa_analysis.json)"
    )
    parser.add_argument(
        "--us",
        default="output/user_stories.txt",
        help="Chemin vers les US originales (default: output/user_stories.txt)"
    )
    args = parser.parse_args()

    us_text = ""
    if os.path.exists(args.us):
        with open(args.us, "r", encoding="utf-8") as f:
            us_text = f.read()
        print(f"📄 US text loaded: {args.us}")
    else:
        print(f"⚠️ US file not found: {args.us} → AC Alignment uses intrinsic quality")

    config = get_qa_config(args.json)
    run_evaluation(config, us_text)