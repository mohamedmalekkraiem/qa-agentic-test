import re
import csv
import os
import sys
import time
import json
import argparse
import fitz

sys.path.append(os.getcwd())

REQUIRED_FIELDS = ["ID", "Title", "As a", "I want", "So that", "Acceptance Criteria"]

# Pattern générique — couvre tous types de documents
TECH_PATTERN = r'\b([A-Z]{2,}\d*|[A-Z]\d{3}|[DAT]\d{3}|F-\d+|US[A-Z]*-\d+|\d{2,})\b'
TRACE_PATTERN = (
    r'(Art\.?\s*\d+|Article\s+\d+'  # juridique
    r'|[DAT]\d{3}|DECEMP\d+|ANXBEN\d+|ANXDEB\d+|ANXFIN\d+'  # technique fiscal
    r'|F-\d+|NFR-\d+|REQ-\d+'  # fonctionnel
    r'|USRH-\d+|USMAN-\d+|USCAN-\d+|US[A-Z]+-\d+)'  # user stories
)


# ──────────────────────────────────────────────
# Config dynamique
# ──────────────────────────────────────────────
def get_cdc_config(pdf_name: str) -> dict:
    base = os.path.splitext(pdf_name.replace("/", "_").replace("\\", "_"))[0]
    return {
        "pdf": f"input/{pdf_name}",
        "json": "output/user_stories.json",
        "base": base,
    }


# ──────────────────────────────────────────────
# Charger US depuis JSON
# ──────────────────────────────────────────────
def load_stories_from_json(json_path: str) -> str:
    with open(json_path, "r", encoding="utf-8") as f:
        stories = json.load(f)
    lines = []
    for us in stories:
        us_id = us.get("id", "US-??")
        title = us.get("title", "")
        as_a = us.get("as_a", "")
        i_want = us.get("i_want", "")
        so_that = us.get("so_that", "")
        criteria = us.get("acceptance_criteria", [])
        if not isinstance(criteria, list):
            criteria = [str(criteria)]
        lines.append(f"**{us_id}**\n")
        lines.append(f"- **ID**                  : {us_id}")
        lines.append(f"- **Title**               : {title}")
        lines.append(f"- **As a**                : {as_a}")
        lines.append(f"- **I want**              : {i_want}")
        lines.append(f"- **So that**             : {so_that}")
        lines.append(f"- **Acceptance Criteria** :")
        for c in criteria:
            lines.append(f"  - {c}")
        lines.append("")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# Métriques simples
# ──────────────────────────────────────────────
def count_user_stories(text: str) -> int:
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", text)
    return len([b for b in blocks if b.strip() and re.search(r"US-\d+", b)])


def check_format_compliance(text: str) -> bool:
    return all(kw in text for kw in [
        "**US-", "**Title**", "**As a**", "**Acceptance Criteria**"
    ])


def check_structural_validity(text: str) -> float:
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", text)
    blocks = [b.strip() for b in blocks if b.strip() and re.search(r"US-\d+", b)]
    if not blocks:
        return 0.0
    total, present = 0, 0
    for block in blocks:
        for field in REQUIRED_FIELDS:
            total += 1
            if re.search(rf"\*\*{re.escape(field)}\*\*\s*:?\s*(.+)", block):
                present += 1
    return round((present / total) * 100, 1) if total else 0.0


def check_criteria_quality(text: str) -> float:
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", text)
    blocks = [b.strip() for b in blocks if b.strip() and re.search(r"US-\d+", b)]
    if not blocks:
        return 0.0
    good = sum(1 for b in blocks if len(re.findall(r"  - .+", b)) >= 2)
    return round((good / len(blocks)) * 100, 1)


def check_role_quality(text: str) -> float:
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", text)
    blocks = [b.strip() for b in blocks if b.strip() and re.search(r"US-\d+", b)]
    if not blocks:
        return 0.0
    good = 0
    for block in blocks:
        m = re.search(r"\*\*As a\*\*\s*:\s*(.+)", block)
        if m and m.group(1).strip().lower() not in [
            "user", "agent", "utilisateur", ""
        ]:
            good += 1
    return round((good / len(blocks)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE 1 — Coverage Score
# ──────────────────────────────────────────────
def compute_coverage_score(generated_text: str, source_text: str) -> float:
    source_terms = set(re.findall(TECH_PATTERN, source_text))
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", generated_text)
    blocks = [b.strip() for b in blocks if b.strip() and re.search(r"US-\d+", b)]
    if not blocks:
        return 0.0
    all_criteria = []
    for block in blocks:
        all_criteria.extend(re.findall(r"  - (.+)", block))
    if not all_criteria:
        return 0.0
    scores = []
    for criterion in all_criteria:
        crit_terms = set(re.findall(TECH_PATTERN, criterion))
        if not crit_terms:
            scores.append(0.5)
            continue
        found = crit_terms & source_terms
        scores.append(len(found) / len(crit_terms))
    return round((sum(scores) / len(scores)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE 2 — BERTScore
# ──────────────────────────────────────────────
def compute_bert_score(generated_text: str, source_text: str) -> float:
    try:
        from bert_score import score as bert_score_fn
    except ImportError:
        print("   ⚠️ bert_score not installed → skipping")
        return 0.0
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", generated_text)
    blocks = [b.strip() for b in blocks if b.strip() and re.search(r"US-\d+", b)]
    if not blocks:
        return 0.0
    all_criteria = []
    for block in blocks:
        all_criteria.extend(re.findall(r"  - (.+)", block))
    if not all_criteria:
        return 0.0
    hypotheses = all_criteria[:20]
    mid = len(source_text) // 2
    source_chunk = source_text[max(0, mid - 1500):mid + 1500]
    references = [source_chunk] * len(hypotheses)
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
# MÉTRIQUE 3 — Faithfulness
# ──────────────────────────────────────────────
def compute_faithfulness(generated_text: str, source_text: str) -> float:
    """Mesure la fidélité au document source avec un seuil réaliste de 40%"""
    source_lower = source_text.lower()
    blocks = re.split(r"(?=\*\*US-\d+\*\*)", generated_text)
    blocks = [b.strip() for b in blocks if b.strip() and re.search(r"US-\d+", b)]
    if not blocks:
        return 0.0

    faithful_count = 0
    total_criteria = 0

    for block in blocks:
        for criterion in re.findall(r"  - (.+)", block):
            total_criteria += 1

            # Extraire les termes techniques et les mots significatifs
            technical_terms = re.findall(TECH_PATTERN, criterion)
            all_words = [w.lower() for w in re.findall(r'\b\w{4,}\b', criterion)]

            # Compter les termes trouvés dans la source
            found_tech = [t.lower() for t in technical_terms if t.lower() in source_lower]
            found_words = [w for w in all_words if w in source_lower]

            all_terms = all_words + [t.lower() for t in technical_terms]
            found_terms = found_words + found_tech

            if not all_terms:
                faithful_count += 1
                continue

            # SEUIL RÉALISTE : 40%
            if (len(found_terms) / len(all_terms)) >= 0.40:
                faithful_count += 1

    return round((faithful_count / total_criteria) * 100, 1) if total_criteria else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE 4 — Hallucination Rate
# ──────────────────────────────────────────────
def compute_hallucination_rate(stories: list, source_text: str) -> float:
    """
    Détecte les hallucinations avec un seuil réaliste de 50%.
    Une US est hallucinée si moins de 50% de ses termes sont dans la source.
    """
    source_lower = source_text.lower()
    if not stories:
        return 0.0

    hallucinated = 0
    total_analyzed = 0

    for us in stories:
        criteria = us.get("acceptance_criteria", [])
        if not isinstance(criteria, list):
            criteria = [str(criteria)]

        all_terms = []
        for c in criteria:
            technical_terms = re.findall(TECH_PATTERN, c)
            words = re.findall(r'\b\w{4,}\b', c.lower())
            all_terms.extend([t.lower() for t in technical_terms] + words)

        # Éliminer les doublons pour éviter le biais
        all_terms = list(set(all_terms))

        if not all_terms:
            continue

        total_analyzed += 1
        found = sum(1 for t in all_terms if t in source_lower)

        # SEUIL RÉALISTE : 50%
        if (found / len(all_terms)) < 0.50:
            hallucinated += 1

    return round((hallucinated / total_analyzed) * 100, 1) if total_analyzed else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE 5 — F1 Score
# ──────────────────────────────────────────────
def compute_f1_score(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return round(2 * (precision * recall) / (precision + recall), 1)


# ──────────────────────────────────────────────
# MÉTRIQUE 6 — INVEST Score
# ──────────────────────────────────────────────
def compute_invest_score(stories: list) -> dict:
    if not stories:
        return {"Independent": 0, "Negotiable": 0, "Valuable": 0,
                "Estimable": 0, "Small": 0, "Testable": 0, "Overall": 0}
    scores = {
        "Independent": 0, "Negotiable": 0, "Valuable": 0,
        "Estimable": 0, "Small": 0, "Testable": 0
    }
    for us in stories:
        title = us.get("title", "")
        i_want = us.get("i_want", "")
        so_that = us.get("so_that", "")
        criteria = us.get("acceptance_criteria", [])
        if not isinstance(criteria, list):
            criteria = [str(criteria)]

        if not re.search(r'US-\d+|depends on|requires US', i_want + so_that, re.IGNORECASE):
            scores["Independent"] += 1
        rigid_words = ["must exactly", "strictly only", "no other option"]
        if not any(w in (i_want + so_that).lower() for w in rigid_words):
            scores["Negotiable"] += 1
        if so_that and len(so_that.strip()) > 10:
            scores["Valuable"] += 1
        action_verbs = [
            "ensure", "validate", "verify", "check", "confirm",
            "create", "implement", "manage", "track", "generate",
            "schedule", "parse", "integrate", "export", "configure"
        ]
        if i_want and len(i_want.strip()) > 15 and any(v in i_want.lower() for v in action_verbs):
            scores["Estimable"] += 1
        if title and len(title) < 100 and title.lower().count(" and ") <= 1:
            scores["Small"] += 1
        if len(criteria) >= 2:
            scores["Testable"] += 1

    n = len(stories)
    result = {k: round((v / n) * 100, 1) for k, v in scores.items()}
    result["Overall"] = round(sum(result.values()) / len(result), 1)
    return result


# ──────────────────────────────────────────────
# MÉTRIQUE 7 — Traceability Score
# ──────────────────────────────────────────────
def compute_traceability_score(stories: list) -> float:
    """
    Mesure la traçabilité en vérifiant les IDs dans les critères ET les métadonnées.
    """
    if not stories:
        return 0.0

    traced = 0
    for us in stories:
        criteria_list = us.get("acceptance_criteria", [])
        if not isinstance(criteria_list, list):
            criteria_list = [str(criteria_list)]

        # Vérifier dans le texte affiché
        full_text = " ".join([
            us.get("title", ""),
            us.get("i_want", ""),
            us.get("so_that", ""),
            " ".join(criteria_list)
        ])

        # Vérifier dans les métadonnées (requirement_id)
        req_id = us.get("requirement_id", "")

        # Traçable si ID présent dans le texte OU dans les métadonnées
        has_id_in_text = bool(re.search(TRACE_PATTERN, full_text, re.IGNORECASE))
        has_id_in_metadata = bool(req_id and re.search(TRACE_PATTERN, req_id, re.IGNORECASE))

        if has_id_in_text or has_id_in_metadata:
            traced += 1

    return round((traced / len(stories)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE 8 — Requirement Coverage (Recall) - CORRIGÉE
# ──────────────────────────────────────────────
def compute_requirement_coverage(stories: list, source_text: str) -> float:
    """
    Calcule le recall des exigences de manière STRICTE.
    Une exigence est couverte UNIQUEMENT si son ID complet apparaît
    dans le texte généré (pas dans les métadonnées).
    """
    # Extraire les IDs de la source
    articles = set(re.findall(r'(Article\s+\d+)', source_text, re.IGNORECASE))
    records = set(re.findall(
        r'\b(DECEMP\d+|ANXBEN\d+|ANXDEB\d+|ANXFIN\d+)\b', source_text
    ))
    func_reqs = set(re.findall(r'\b(F-\d+|NFR-\d+|REQ-\d+)\b', source_text))
    us_reqs = set(re.findall(
        r'\b(USRH-\d+|USMAN-\d+|USCAN-\d+|US[A-Z]+-\d+)\b', source_text
    ))

    all_requirements = articles | records | func_reqs | us_reqs

    print(f"   DEBUG → Articles: {len(articles)} | Records: {len(records)} | "
          f"Func: {len(func_reqs)} | US: {len(us_reqs)} | "
          f"Total: {len(all_requirements)}")

    if not all_requirements:
        print("   DEBUG → No traceable requirements found in document")
        return 0.0

    # Texte complet des US générées (SANS les métadonnées)
    full_us_text = ""
    for us in stories:
        criteria_list = us.get("acceptance_criteria", [])
        if not isinstance(criteria_list, list):
            criteria_list = [str(criteria_list)]
        
        # NE PAS inclure requirement_id ici - seulement le texte affiché
        full_us_text += " ".join([
            us.get("title", ""),
            us.get("i_want", ""),
            us.get("so_that", ""),
            " ".join(criteria_list)
        ]) + " "

    full_us_lower = full_us_text.lower()

    covered = []
    not_covered = []

    for req in all_requirements:
        req_lower = req.lower()
        
        # Recherche STRICTE : l'ID complet doit apparaître
        # Pas de correspondance partielle sur les chiffres
        found = req_lower in full_us_lower
        
        # Vérification supplémentaire pour les patterns comme "F-01"
        if not found:
            # Essayer avec et sans espace après le préfixe
            match = re.match(r'([A-Za-z]+[-]?)(\d+)', req)
            if match:
                prefix = match.group(1).lower()
                number = match.group(2)
                # Chercher exactement "prefixnumber" ou "prefix number"
                if f"{prefix}{number}" in full_us_lower or f"{prefix} {number}" in full_us_lower:
                    found = True

        if found:
            covered.append(req)
        else:
            not_covered.append(req)

    print(f"   DEBUG → Covered: {len(covered)} | Not covered: {len(not_covered)}")
    if not_covered:
        print(f"   DEBUG → Not covered (first 10): {sorted(not_covered)[:10]}")

    return round((len(covered) / len(all_requirements)) * 100, 1)


# ──────────────────────────────────────────────
# Main evaluation
# ──────────────────────────────────────────────
def run_evaluation(cdc_list: list):
    print(f"📋 {len(cdc_list)} CDC à évaluer")
    print("⚡ Mode rapide : US chargées depuis output/user_stories.json\n")

    results = []

    for cdc in cdc_list:
        cdc_path = cdc["pdf"]
        json_path = cdc["json"]
        cdc_file = os.path.basename(cdc_path)

        print(f"\n{'='*60}")
        print(f"📄 CDC : {cdc_file}")
        print(f"{'='*60}")

        if not os.path.exists(json_path):
            print(f"  ⚠️ JSON introuvable : {json_path}")
            print(f"  → Lance d'abord : python main_agent1.py")
            continue
        if not os.path.exists(cdc_path):
            print(f"  ⚠️ PDF introuvable : {cdc_path}")
            continue

        try:
            doc = fitz.open(cdc_path)
            source_text = "\n".join(p.get_text() for p in doc)
        except Exception as e:
            print(f"  ⚠️ Cannot read PDF: {e}")
            continue

        print(f"  📂 Loading US from {json_path}...")
        start = time.time()
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                stories = json.load(f)
            output_text = load_stories_from_json(json_path)
        except Exception as e:
            print(f"  ⚠️ Cannot load JSON: {e}")
            continue

        # ── Métriques simples ──
        nb_us = count_user_stories(output_text)
        fmt_ok = check_format_compliance(output_text)
        validity = check_structural_validity(output_text)
        criteria_q = check_criteria_quality(output_text)
        role = check_role_quality(output_text)

        # ── Métriques avancées ──
        print("  📐 Computing Coverage Score...")
        coverage = compute_coverage_score(output_text, source_text)

        print("  🧠 Computing BERTScore...")
        bert_s = compute_bert_score(output_text, source_text)

        print("  🔍 Computing Faithfulness...")
        faith = compute_faithfulness(output_text, source_text)

        print("  🚨 Computing Hallucination Rate...")
        halluc = compute_hallucination_rate(stories, source_text)

        print("  🎯 Computing Requirement Coverage (Recall)...")
        req_coverage = compute_requirement_coverage(stories, source_text)

        print("  📊 Computing F1 Score...")
        f1 = compute_f1_score(precision=coverage, recall=req_coverage)

        print("  ✨ Computing INVEST Score...")
        invest = compute_invest_score(stories)

        print("  🔗 Computing Traceability Score...")
        traceability = compute_traceability_score(stories)

        duration = round(time.time() - start, 2)

        print(f"\n  ✅ Results for {cdc_file}:")
        print(f"     US Count               : {nb_us}")
        print(f"     Format Compliance      : {'✅' if fmt_ok else '❌'}")
        print(f"     Structural Validity    : {validity}%")
        print(f"     Criteria Quality       : {criteria_q}%")
        print(f"     Role Quality           : {role}%")
        print(f"     ── Métriques avancées ──────────────")
        print(f"     Coverage Score         : {coverage}%")
        print(f"     BERTScore              : {bert_s}%")
        print(f"     Faithfulness           : {faith}%")
        print(f"     Hallucination Rate     : {halluc}%  (plus bas = mieux)")
        print(f"     Requirement Coverage   : {req_coverage}%  (Recall)")
        print(f"     F1 Score               : {f1}%")
        print(f"     Traceability Score     : {traceability}%")
        print(f"     INVEST Score           : {invest['Overall']}%")
        print(f"       - Independent : {invest['Independent']}%")
        print(f"       - Negotiable  : {invest['Negotiable']}%")
        print(f"       - Valuable    : {invest['Valuable']}%")
        print(f"       - Estimable   : {invest['Estimable']}%")
        print(f"       - Small       : {invest['Small']}%")
        print(f"       - Testable    : {invest['Testable']}%")
        print(f"     Duration               : {duration}s")

        results.append({
            "CDC": cdc_file,
            "US_Count": nb_us,
            "Format_Compliance": "OK" if fmt_ok else "KO",
            "Structural_Validity_%": validity,
            "Criteria_Quality_%": criteria_q,
            "Role_Quality_%": role,
            "Coverage_Score_%": coverage,
            "BERTScore_%": bert_s,
            "Faithfulness_%": faith,
            "Hallucination_Rate_%": halluc,
            "Requirement_Coverage_%": req_coverage,
            "F1_Score_%": f1,
            "Traceability_Score_%": traceability,
            "INVEST_Score_%": invest['Overall'],
            "Duration_sec": duration,
        })

    if not results:
        print("⚠️ Aucun résultat")
        return

    print(f"\n\n{'='*100}")
    print("📊 RAPPORT D'ÉVALUATION — AGENT 1")
    print(f"{'='*100}\n")

    for r in results:
        print(f"CDC: {r['CDC']}")
        print(f"  US: {r['US_Count']} | Fmt: {r['Format_Compliance']} | "
              f"Valid: {r['Structural_Validity_%']}% | Crit: {r['Criteria_Quality_%']}% | "
              f"Role: {r['Role_Quality_%']}%")
        print(f"  Coverage: {r['Coverage_Score_%']}% | BERT: {r['BERTScore_%']}% | "
              f"Faith: {r['Faithfulness_%']}%")
        print(f"  Hallucination: {r['Hallucination_Rate_%']}% | "
              f"Req.Coverage: {r['Requirement_Coverage_%']}% | F1: {r['F1_Score_%']}%")
        print(f"  Traceability: {r['Traceability_Score_%']}% | "
              f"INVEST: {r['INVEST_Score_%']}% | Time: {r['Duration_sec']}s")
        print()

    def avg(key):
        vals = [r[key] for r in results if isinstance(r[key], (int, float))]
        return round(sum(vals) / len(vals), 1) if vals else 0.0

    # Pondération corrigée et équilibrée
    score = round(
        avg('Structural_Validity_%') * 0.05 +
        avg('Criteria_Quality_%') * 0.05 +
        avg('Role_Quality_%') * 0.05 +
        avg('Coverage_Score_%') * 0.15 +
        avg('BERTScore_%') * 0.10 +
        avg('Faithfulness_%') * 0.15 +
        (100 - avg('Hallucination_Rate_%')) * 0.15 +
        avg('Requirement_Coverage_%') * 0.10 +
        avg('F1_Score_%') * 0.10 +
        avg('Traceability_Score_%') * 0.05 +
        avg('INVEST_Score_%') * 0.05,
        1
    )

    print(f"📈 Score global pondéré : {score}/100")
    verdict = (
        "✅ Agent performant et fiable"
        if score >= 80 else
        "⚠️ Agent fonctionnel mais améliorable"
        if score >= 60 else
        "❌ Agent peu fiable — révision nécessaire"
    )
    print(f"Verdict : {verdict}")

    os.makedirs("output", exist_ok=True)
    csv_path = "output/agent1_evaluation_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n💾 Rapport CSV : {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Évaluation Agent 1")
    parser.add_argument("pdf", help="Nom du PDF dans input/ (ex: EMPCCA_25V3.pdf)")
    args = parser.parse_args()
    CDC_FILES = [get_cdc_config(args.pdf)]
    run_evaluation(CDC_FILES)