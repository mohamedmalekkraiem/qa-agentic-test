import os
import re
import json
from datetime import datetime


# ──────────────────────────────────────────────
# UTILITAIRES
# ──────────────────────────────────────────────
def detect_total_us(backlog_path: str) -> int:
    try:
        with open(backlog_path, "r", encoding="utf-8") as f:
            content = f.read()
        us_ids = re.findall(r'\bUS-\d+\b', content)
        return len(set(us_ids))
    except Exception:
        return 20


def load_backlog(backlog_path: str) -> str:
    with open(backlog_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_tickets(content: str) -> list:
    """Parse les tickets depuis le backlog.md"""
    tickets = []
    blocks  = re.split(r'(?=## \[)', content)
    for block in blocks:
        if not block.strip() or "## [" not in block:
            continue
        m_priority = re.search(r'## \[(HIGH|MEDIUM|LOW)\] (.+)', block, re.IGNORECASE)
        m_us       = re.search(r'\*\*User Story:\*\* (US-\d+)', block)
        m_epic     = re.search(r'\*\*Epic:\*\* ([^\n]+)', block)
        m_feature  = re.search(r'\*\*Feature:\*\* ([^\n]+)', block)
        m_issue    = re.search(r'\*\*GitHub Issue:\*\* #(\d+)', block)

        if m_priority:
            tickets.append({
                "priority" : m_priority.group(1).lower(),
                "title"    : m_priority.group(2).strip(),
                "us_id"    : m_us.group(1) if m_us else None,
                "epic"     : m_epic.group(1).strip() if m_epic else None,
                "feature"  : m_feature.group(1).strip() if m_feature else None,
                "issue"    : m_issue.group(1) if m_issue else None,
                "body"     : block,
            })
    return tickets


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 1 — Coverage
# % d'US couvertes par au moins un ticket
# ──────────────────────────────────────────────
def compute_coverage(tickets: list, total_us: int) -> float:
    us_covered = set(t["us_id"] for t in tickets if t["us_id"])
    return round((len(us_covered) / total_us) * 100, 1) if total_us > 0 else 0.0


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 2 — Ticket Completeness
# % de tickets ayant tous les champs requis
# ──────────────────────────────────────────────
def compute_completeness(tickets: list) -> float:
    if not tickets:
        return 0.0
    complete = sum(
        1 for t in tickets
        if t["us_id"] and t["epic"] and t["feature"]
        and t["priority"] and t["title"] and len(t["title"]) >= 10
    )
    return round((complete / len(tickets)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 3 — Traceability
# % de tickets liés à une US
# ──────────────────────────────────────────────
def compute_traceability(tickets: list) -> float:
    if not tickets:
        return 0.0
    traced = sum(1 for t in tickets if t["us_id"])
    return round((traced / len(tickets)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE SIMPLE 4 — Epic Granularity
# Le nombre d'Epics est-il approprié ?
# Idéal : 3-7 Epics pour n'importe quel projet
# ──────────────────────────────────────────────
def compute_epic_granularity(tickets: list) -> float:
    epics = set(t["epic"] for t in tickets if t["epic"])
    n     = len(epics)
    if 4 <= n <= 6:
        return 100.0
    elif 3 <= n <= 8:
        return 80.0
    elif 2 <= n <= 10:
        return 60.0
    elif n == 1:
        return 30.0
    else:
        return 20.0


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 1 — Epic Coherence (BERTScore)
# Les US d'un même Epic sont-elles sémantiquement similaires ?
# Score élevé = bonne organisation des Epics
# ──────────────────────────────────────────────
def compute_epic_coherence(tickets: list) -> float:
    try:
        from bert_score import score as bert_score_fn
    except ImportError:
        print("   ⚠️ bert_score not installed → skipping Epic Coherence")
        return 0.0

    # Grouper les tickets par Epic
    epics = {}
    for t in tickets:
        epic = t["epic"]
        if epic:
            epics.setdefault(epic, []).append(t["title"] + " " + t["body"][:200])

    if len(epics) < 2:
        return 50.0  # Pas assez d'Epics pour comparer

    coherence_scores = []

    for epic_name, texts in epics.items():
        if len(texts) < 2:
            coherence_scores.append(1.0)  # Un seul ticket → cohérent par défaut
            continue

        # Comparer chaque texte avec la moyenne des autres
        hypotheses = texts
        references = [" ".join(texts)] * len(texts)

        try:
            P, R, F1 = bert_score_fn(
                hypotheses, references,
                lang="en", verbose=False,
                model_type="distilbert-base-multilingual-cased"
            )
            coherence_scores.append(F1.mean().item())
        except Exception as e:
            print(f"   ⚠️ BERTScore error for epic '{epic_name}': {e}")
            coherence_scores.append(0.5)

    return round((sum(coherence_scores) / len(coherence_scores)) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 2 — Priority Consistency
# La priorité assignée est-elle cohérente avec le contenu ?
# Score élevé = priorités bien calibrées
# ──────────────────────────────────────────────
def compute_priority_consistency(tickets: list) -> float:
    if not tickets:
        return 0.0

    # Mots clés qui indiquent la priorité
    high_keywords = [
        "security", "encryption", "gdpr", "compliance", "critical",
        "blocking", "auth", "authentication", "mandatory", "must",
        "sécurité", "chiffrement", "obligatoire", "critique", "bloquant",
        "aes", "tls", "mfa", "dpa", "rgpd"
    ]
    low_keywords = [
        "optional", "nice-to-have", "future", "phase 2", "desirable",
        "optionnel", "souhaitable", "amélioration", "enhancement",
        "could", "might", "eventually", "later"
    ]

    consistent = 0
    total      = len(tickets)

    for t in tickets:
        text     = (t["title"] + " " + t["body"]).lower()
        priority = t["priority"]

        has_high_kw = any(kw in text for kw in high_keywords)
        has_low_kw  = any(kw in text for kw in low_keywords)

        if has_high_kw and priority == "high":
            consistent += 1  # ✅ Contenu critique → high
        elif has_low_kw and priority == "low":
            consistent += 1  # ✅ Contenu optionnel → low
        elif not has_high_kw and not has_low_kw and priority == "medium":
            consistent += 1  # ✅ Contenu standard → medium
        elif has_high_kw and priority == "low":
            pass  # ❌ Contenu critique assigné low
        elif has_low_kw and priority == "high":
            pass  # ❌ Contenu optionnel assigné high
        else:
            consistent += 0.5  # ⚠️ Cas ambigu → demi-point

    return round((consistent / total) * 100, 1)


# ──────────────────────────────────────────────
# MÉTRIQUE AVANCÉE 3 — Duplicate Detection
# Deux tickets couvrent-ils la même US ?
# Score élevé = pas de doublons
# ──────────────────────────────────────────────
def compute_duplicate_score(tickets: list) -> float:
    if not tickets:
        return 100.0

    # Vérifier les US couverts plusieurs fois
    us_counts = {}
    for t in tickets:
        if t["us_id"]:
            us_counts[t["us_id"]] = us_counts.get(t["us_id"], 0) + 1

    duplicates = sum(1 for count in us_counts.values() if count > 1)
    total_us   = len(us_counts)

    if total_us == 0:
        return 100.0

    # Vérifier les titres similaires
    titles = [t["title"].lower() for t in tickets if t["title"]]
    title_duplicates = 0
    for i, t1 in enumerate(titles):
        for t2 in titles[i+1:]:
            # Similarité simple par mots communs
            words1 = set(t1.split())
            words2 = set(t2.split())
            if len(words1) > 0 and len(words2) > 0:
                overlap = len(words1 & words2) / min(len(words1), len(words2))
                if overlap > 0.7:  # 70% de mots communs → doublon probable
                    title_duplicates += 1

    duplicate_rate = (duplicates + title_duplicates) / (total_us + len(titles))
    return round((1 - duplicate_rate) * 100, 1)


# ──────────────────────────────────────────────
# Main evaluation
# ──────────────────────────────────────────────
def evaluate_backlog(backlog_path: str) -> dict:
    print(f"\n📄 Loading backlog: {backlog_path}")
    content  = load_backlog(backlog_path)
    tickets  = parse_tickets(content)
    total_us = detect_total_us(backlog_path)

    print(f"   → {len(tickets)} tickets parsed | {total_us} US detected")

    results = {
        "timestamp"    : datetime.now().isoformat(),
        "total_us"     : total_us,
        "total_tickets": len(tickets),
        "metrics"      : {},
        "overall_score": 0.0,
        "status"       : "❌"
    }

    # ── Métriques simples ──
    print("\n📐 Computing simple metrics...")

    coverage     = compute_coverage(tickets, total_us)
    completeness = compute_completeness(tickets)
    traceability = compute_traceability(tickets)
    granularity  = compute_epic_granularity(tickets)

    results["metrics"]["coverage"]     = coverage
    results["metrics"]["completeness"] = completeness
    results["metrics"]["traceability"] = traceability
    results["metrics"]["epic_granularity"] = granularity

    # Statistiques Epics & priorités
    epics     = sorted(set(t["epic"] for t in tickets if t["epic"]))
    features  = sorted(set(t["feature"] for t in tickets if t["feature"]))
    pri_dist  = {
        "high"  : sum(1 for t in tickets if t["priority"] == "high"),
        "medium": sum(1 for t in tickets if t["priority"] == "medium"),
        "low"   : sum(1 for t in tickets if t["priority"] == "low"),
    }

    results["epics"]    = epics
    results["features"] = features
    results["priority_distribution"] = pri_dist

    # ── Métriques avancées ──
    print("  🧠 Computing Epic Coherence (BERTScore)...")
    epic_coherence = compute_epic_coherence(tickets)

    print("  🎯 Computing Priority Consistency...")
    priority_consistency = compute_priority_consistency(tickets)

    print("  🔍 Computing Duplicate Detection...")
    duplicate_score = compute_duplicate_score(tickets)

    results["metrics"]["epic_coherence"]       = epic_coherence
    results["metrics"]["priority_consistency"] = priority_consistency
    results["metrics"]["duplicate_score"]      = duplicate_score

    # ── Score global pondéré ──
    # Métriques simples = 40% | Métriques avancées = 60%
    score = round(
        coverage             * 0.15 +
        completeness         * 0.10 +
        traceability         * 0.10 +
        granularity          * 0.05 +
        epic_coherence       * 0.25 +
        priority_consistency * 0.20 +
        duplicate_score      * 0.15,
        1
    )
    results["overall_score"] = score

    # ── Verdict ──
    if score >= 85:
        results["status"] = "✅ Agent performant et fiable"
    elif score >= 70:
        results["status"] = "⚠️ Agent fonctionnel mais améliorable"
    elif score >= 50:
        results["status"] = "⚠️ Agent moyen — améliorations nécessaires"
    else:
        results["status"] = "❌ Agent peu fiable — révision nécessaire"

    # ── Affichage ──
    total = sum(pri_dist.values())
    print(f"\n\n{'='*60}")
    print("📊 RAPPORT D'ÉVALUATION — AGENT 2")
    print(f"{'='*60}")

    print(f"\n📈 Métriques simples :")
    print(f"   Coverage           : {coverage}%")
    print(f"   Completeness       : {completeness}%")
    print(f"   Traceability       : {traceability}%")
    print(f"   Epic Granularity   : {granularity}%")
    print(f"   Epics ({len(epics)})      : {', '.join(epics)}")
    print(f"   Features           : {len(features)}")
    print(f"   Priority dist.     : "
          f"High={pri_dist['high']} "
          f"({round(pri_dist['high']/total*100,1) if total else 0}%) | "
          f"Medium={pri_dist['medium']} "
          f"({round(pri_dist['medium']/total*100,1) if total else 0}%) | "
          f"Low={pri_dist['low']} "
          f"({round(pri_dist['low']/total*100,1) if total else 0}%)")

    print(f"\n📈 Métriques avancées :")
    print(f"   Epic Coherence     : {epic_coherence}%")
    print(f"     → US within same Epic are semantically similar")
    print(f"   Priority Consist.  : {priority_consistency}%")
    print(f"     → Assigned priorities match content keywords")
    print(f"   Duplicate Score    : {duplicate_score}%")
    print(f"     → No duplicate tickets covering same US")

    print(f"\n{'='*60}")
    print(f"📈 Score global pondéré : {score}/100")
    print(f"📌 Verdict             : {results['status']}")
    print(f"{'='*60}")

    # ── CSV ──
    os.makedirs("output", exist_ok=True)

    import csv
    csv_path = "output/agent2_evaluation_report.csv"
    flat = {
        "total_us"           : total_us,
        "total_tickets"      : len(tickets),
        "coverage_%"         : coverage,
        "completeness_%"     : completeness,
        "traceability_%"     : traceability,
        "epic_granularity_%" : granularity,
        "epics_count"        : len(epics),
        "features_count"     : len(features),
        "priority_high"      : pri_dist["high"],
        "priority_medium"    : pri_dist["medium"],
        "priority_low"       : pri_dist["low"],
        "epic_coherence_%"   : epic_coherence,
        "priority_consistency_%": priority_consistency,
        "duplicate_score_%"  : duplicate_score,
        "overall_score"      : score,
        "status"             : results["status"],
    }
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat.keys())
        writer.writeheader()
        writer.writerow(flat)
    print(f"\n💾 CSV : {csv_path}")

    # ── JSON ──
    json_path = "output/agent2_evaluation.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON: {json_path}")

    return results


if __name__ == "__main__":
    evaluate_backlog("output/backlog.md")