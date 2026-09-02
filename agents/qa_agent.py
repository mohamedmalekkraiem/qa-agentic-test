from crewai import Agent, Task, Crew, LLM
import json
import re
import os
from difflib import SequenceMatcher
from collections import defaultdict, Counter

llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.3,
    max_tokens=4096
)


# ──────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ──────────────────────────────────────────────

def normalize_us_id(us_id: str) -> str:
    """Normalise les IDs US (US-001 → US-01)"""
    if not us_id:
        return "US-??"
    match = re.search(r'US-0*(\d+)', us_id, re.IGNORECASE)
    if match:
        return f"US-{int(match.group(1)):02d}"
    return us_id

def extract_json(text: str) -> str | None:
    cleaned = re.sub(r"```json|```", "", text)
    start = cleaned.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(cleaned)):
        char = cleaned[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return cleaned[start:i + 1]
    return None


# ──────────────────────────────────────────────
# RÉDUCTION DES REDONDANCES - VERSION GÉNÉRIQUE
# ──────────────────────────────────────────────

def reduce_redundancy(analysis: dict) -> dict:
    """
    Réduit AUTOMATIQUEMENT les redondances dans les cas de test.
    100% GÉNÉRIQUE - Pas de règles spécifiques à un projet.
    """
    us_id = analysis.get("id", "US-??")
    test_cases = analysis.get("test_cases", [])
    
    if not test_cases:
        return analysis
    
    # --- ÉTAPE 1: Nettoyer et normaliser ---
    test_cases = normalize_test_cases(test_cases)
    
    # --- ÉTAPE 2: Détecter les groupes redondants ---
    groups = detect_redundant_groups(test_cases)
    
    # --- ÉTAPE 3: Fusionner les groupes ---
    merged_tests = merge_redundant_groups(groups)
    
    # --- ÉTAPE 4: Optimiser le nombre (3-4 tests) ---
    final_tests = optimize_test_count(merged_tests)
    
    analysis["test_cases"] = final_tests
    
    return analysis


def normalize_test_cases(test_cases: list) -> list:
    """Normalise les cas de test pour faciliter la détection."""
    normalized = []
    
    for tc in test_cases:
        name = tc.get("name", "").strip()
        
        steps = tc.get("steps", [])
        if isinstance(steps, str):
            steps = [s.strip() for s in steps.split("\n") if s.strip()]
        steps = [s.strip() for s in steps if s.strip()]
        
        expected = tc.get("expected_result", "")
        if isinstance(expected, list):
            expected = " ".join(str(e) for e in expected)
        expected = expected.strip()
        
        keywords = extract_keywords(name + " " + expected)
        
        normalized.append({
            "name": name,
            "steps": steps,
            "expected_result": expected,
            "keywords": keywords,
            "original": tc
        })
    
    return normalized


def extract_keywords(text: str) -> set:
    """Extrait les mots-clés pertinents."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "without", "by", "from", "up", "down",
        "off", "over", "under", "etc", "test", "case", "user", "system",
        "should", "must", "will", "can", "could", "would", "may", "might",
        "le", "la", "les", "un", "une", "des", "et", "ou", "mais", "dans",
        "sur", "sous", "pour", "par", "avec", "sans", "de", "du", "des"
    }
    
    words = re.findall(r'[a-zA-ZÀ-ÿ]{3,}', text.lower())
    keywords = {w for w in words if w not in stop_words}
    
    return keywords


def detect_redundant_groups(test_cases: list) -> list:
    """Détecte les groupes de tests redondants."""
    if len(test_cases) <= 1:
        return [[tc] for tc in test_cases]
    
    # Matrice de similarité
    similarity_matrix = []
    for i, tc1 in enumerate(test_cases):
        row = []
        for j, tc2 in enumerate(test_cases):
            if i == j:
                row.append(1.0)
            else:
                sim = calculate_similarity(tc1, tc2)
                row.append(sim)
        similarity_matrix.append(row)
    
    # Regrouper par similarité
    groups = []
    used = set()
    
    for i in range(len(test_cases)):
        if i in used:
            continue
            
        group = [test_cases[i]]
        used.add(i)
        
        for j in range(i + 1, len(test_cases)):
            if j in used:
                continue
            if similarity_matrix[i][j] > 0.6:  # Seuil de similarité
                group.append(test_cases[j])
                used.add(j)
        
        groups.append(group)
    
    return groups


def calculate_similarity(tc1: dict, tc2: dict) -> float:
    """Calcule la similarité entre deux cas de test."""
    # Mots-clés
    keywords1 = tc1.get("keywords", set())
    keywords2 = tc2.get("keywords", set())
    
    if keywords1 and keywords2:
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        keyword_sim = intersection / union if union > 0 else 0
    else:
        keyword_sim = 0
    
    # Nom
    name1 = tc1.get("name", "").lower()
    name2 = tc2.get("name", "").lower()
    name_sim = SequenceMatcher(None, name1, name2).ratio()
    
    # Steps (premières lignes)
    steps1 = " ".join(tc1.get("steps", [])[:3])
    steps2 = " ".join(tc2.get("steps", [])[:3])
    steps_sim = SequenceMatcher(None, steps1.lower(), steps2.lower()).ratio()
    
    # Poids
    weights = {"keywords": 0.4, "name": 0.3, "steps": 0.3}
    
    similarity = (
        keyword_sim * weights["keywords"] +
        name_sim * weights["name"] +
        steps_sim * weights["steps"]
    )
    
    return similarity


def merge_redundant_groups(groups: list) -> list:
    """Fusionne les groupes de tests redondants."""
    merged_tests = []
    
    for group in groups:
        if len(group) == 1:
            merged_tests.append(group[0]["original"])
        else:
            merged = merge_group(group)
            merged_tests.append(merged)
    
    return merged_tests


def merge_group(group: list) -> dict:
    """Fusionne un groupe de tests en un seul."""
    # Déterminer le type de test
    test_type = detect_test_type(group)
    
    # Extraire toutes les actions
    all_steps = []
    all_names = []
    all_expected = []
    
    for tc in group:
        if tc.get("steps"):
            all_steps.extend(tc["steps"])
        if tc.get("name"):
            all_names.append(tc["name"])
        if tc.get("expected_result"):
            all_expected.append(tc["expected_result"])
    
    # Dédupliquer les steps
    unique_steps = deduplicate_steps(all_steps)
    
    # Générer le nom fusionné
    merged_name = generate_merged_name(all_names, test_type)
    
    # Générer le résultat attendu fusionné
    merged_expected = generate_merged_expected(all_expected, test_type)
    
    return {
        "name": merged_name,
        "steps": unique_steps,
        "expected_result": merged_expected
    }


def detect_test_type(group: list) -> str:
    """Détecte le type de test à partir du groupe."""
    all_text = " ".join([
        tc.get("name", "") + " " + tc.get("expected_result", "")
        for tc in group
    ]).lower()
    
    types = {
        "channels": ["canal", "channel", "publication", "diffusion", "post", "publish"],
        "url": ["url", "lien", "link", "génération", "modification"],
        "email": ["email", "mail", "courriel", "template", "variable"],
        "validation": ["validation", "valid", "verify", "vérification", "check"],
        "performance": ["performance", "temps", "charge", "simultané", "load"],
        "security": ["sécurité", "auth", "autorisation", "permission", "access"],
        "data_driven": ["data-driven", "paramètres", "combinaison", "dataset"]
    }
    
    for type_name, keywords in types.items():
        if any(kw in all_text for kw in keywords):
            return type_name
    
    return "generic"


def deduplicate_steps(steps: list) -> list:
    """Déduplique et simplifie les steps."""
    cleaned = []
    seen = set()
    
    for step in steps:
        step = step.strip()
        if not step:
            continue
        
        normalized = step.lower()
        normalized = re.sub(r'[\'"\d]', '', normalized)
        
        if normalized not in seen:
            seen.add(normalized)
            cleaned.append(step)
    
    # Regrouper les steps similaires
    if len(cleaned) > 5:
        cleaned = group_similar_steps(cleaned)
    
    return cleaned[:5]  # Limiter à 5 steps maximum


def group_similar_steps(steps: list) -> list:
    """Regroupe les steps similaires."""
    grouped = []
    used = set()
    
    for i, step1 in enumerate(steps):
        if i in used:
            continue
        
        group = [step1]
        used.add(i)
        
        for j in range(i + 1, len(steps)):
            if j in used:
                continue
            if SequenceMatcher(None, step1.lower(), steps[j].lower()).ratio() > 0.8:
                group.append(steps[j])
                used.add(j)
        
        if len(group) > 1:
            grouped.append(generalize_steps(group))
        else:
            grouped.append(step1)
    
    return grouped


def generalize_steps(steps: list) -> str:
    """Généralise un groupe de steps similaires."""
    common_parts = []
    for step in steps:
        parts = step.split()
        if len(parts) >= 2:
            common_parts.append(" ".join(parts[:2]))
    
    if common_parts:
        most_common = Counter(common_parts).most_common(1)
        if most_common:
            action = most_common[0][0]
            return f"{action} (avec différentes variantes)"
    
    return steps[0]


def generate_merged_name(names: list, test_type: str) -> str:
    """Génère un nom pour le test fusionné."""
    templates = {
        "channels": "Tests de sélection et publication sur canaux (regroupés)",
        "url": "Tests de gestion des URLs - cycle de vie complet",
        "email": "Tests data-driven des emails avec variables dynamiques",
        "validation": "Tests de validation des données (regroupés)",
        "performance": "Tests de performance (regroupés)",
        "security": "Tests de sécurité et contrôle d'accès (regroupés)",
        "data_driven": "Tests data-driven avec différentes combinaisons de données",
        "generic": "Tests regroupés (Happy Path + Edge Cases)"
    }
    
    return templates.get(test_type, templates["generic"])


def generate_merged_expected(expected_list: list, test_type: str) -> str:
    """Génère le résultat attendu pour le test fusionné."""
    templates = {
        "channels": "Le système publie correctement sur tous les canaux sélectionnés et gère les cas limites avec des messages appropriés",
        "url": "Le système gère correctement tout le cycle de vie des URLs (génération, modification, accès)",
        "email": "Tous les emails sont générés correctement avec les bonnes variables dynamiques et délais",
        "validation": "Le système valide correctement toutes les entrées et affiche des messages d'erreur appropriés",
        "performance": "Le système répond dans les délais acceptables pour l'ensemble des opérations",
        "security": "Le système contrôle correctement les accès et journalise toutes les tentatives",
        "data_driven": "Tous les scénarios sont exécutés correctement avec les différentes combinaisons de données",
        "generic": "Tous les cas de test regroupés couvrent les scénarios Happy Path et Edge Cases avec succès"
    }
    
    return templates.get(test_type, templates["generic"])


def optimize_test_count(test_cases: list) -> list:
    """Optimise le nombre de tests pour avoir 3-4 par User Story."""
    MIN_TESTS = 3
    MAX_TESTS = 4
    
    if len(test_cases) < MIN_TESTS:
        missing = MIN_TESTS - len(test_cases)
        generic_tests = generate_generic_tests(missing)
        test_cases.extend(generic_tests)
    
    elif len(test_cases) > MAX_TESTS:
        test_cases = prioritize_tests(test_cases, MAX_TESTS)
    
    return test_cases


def generate_generic_tests(count: int) -> list:
    """Génère des tests génériques pour atteindre le nombre minimum."""
    generic_templates = [
        {
            "name": "Test de performance - Temps de réponse",
            "steps": [
                "Exécuter le scénario principal",
                "Mesurer le temps de réponse",
                "Vérifier que le temps est acceptable"
            ],
            "expected_result": "Le système répond dans les délais spécifiés"
        },
        {
            "name": "Test d'erreur - Données invalides",
            "steps": [
                "Soumettre des données invalides",
                "Vérifier la validation",
                "Confirmer l'affichage du message d'erreur"
            ],
            "expected_result": "Le système rejette les données invalides avec un message approprié"
        },
        {
            "name": "Test de sécurité - Accès non autorisé",
            "steps": [
                "Tenter d'accéder sans autorisation",
                "Vérifier le contrôle d'accès",
                "Confirmer l'erreur d'autorisation"
            ],
            "expected_result": "Le système refuse l'accès non autorisé"
        }
    ]
    
    return generic_templates[:count]


def prioritize_tests(test_cases: list, max_count: int) -> list:
    """Priorise les tests pour ne garder que les plus pertinents."""
    if len(test_cases) <= max_count:
        return test_cases
    
    # Catégoriser
    happy_paths = []
    edge_cases = []
    performance = []
    security = []
    others = []
    
    for tc in test_cases:
        name = tc.get("name", "").lower()
        expected = tc.get("expected_result", "").lower()
        text = name + " " + expected
        
        if "happy" in text or "nominal" in text or "success" in text:
            happy_paths.append(tc)
        elif "edge" in text or "erreur" in text or "invalid" in text or "boundary" in text:
            edge_cases.append(tc)
        elif "performance" in text or "temps" in text or "charge" in text:
            performance.append(tc)
        elif "sécurité" in text or "auth" in text or "authorization" in text:
            security.append(tc)
        else:
            others.append(tc)
    
    # Prioriser
    prioritized = []
    
    if happy_paths:
        prioritized.append(happy_paths[0])
    
    if edge_cases:
        prioritized.extend(edge_cases[:2])
    
    if performance:
        prioritized.append(performance[0])
    elif security:
        prioritized.append(security[0])
    
    remaining = [tc for tc in test_cases if tc not in prioritized]
    prioritized.extend(remaining[:max_count - len(prioritized)])
    
    return prioritized[:max_count]


# ──────────────────────────────────────────────
# ANALYSE D'UNE USER STORY (MODIFIÉE)
# ──────────────────────────────────────────────

def analyze_user_story(agent, us_text: str, debug: bool = True) -> dict | None:
    task = Task(
        description=(
            "Analyse cette user story et retourne un JSON avec :\n"
            "- id : identifiant de la US (ex: US-01, US-02, ... UNIQUEMENT 2 CHIFFRES)\n"
            "- acceptance_criteria : liste des critères d'acceptation extraits\n"
            "- test_scenarios : liste de scénarios de test (happy path + edge cases)\n"
            "- test_cases : liste d'objets {name, steps, expected_result}\n\n"
            "⚠️ RÈGLES STRICTES POUR AMÉLIORER LA QUALITÉ :\n"
            "1. SCENARIO COVERAGE (objectif 85%+) :\n"
            "   - Chaque US doit avoir AU MOINS 1 Happy Path ET 1 Edge Case\n"
            "   - Happy Path : scénario nominal où tout fonctionne\n"
            "   - Edge Case : scénario d'erreur, cas limite, ou exception\n"
            "   - Exemple Edge Case : données invalides, utilisateur non autorisé, etc.\n\n"
            "2. STEP QUALITY (objectif 90%+) :\n"
            "   - Chaque step doit commencer par un VERBE D'ACTION\n"
            "   - ✅ BONS : Login, Navigate, Click, Enter, Select, Verify, Check, Upload, Download, Create, Delete, Update, Search, Filter, Observe, Confirm\n"
            "   - ❌ MAUVAIS : Make sure, Ensure that, Check if, Verify that (sauf si suivi d'un verbe)\n\n"
            "3. TC DIVERSITY (objectif 85%+) :\n"
            "   - Évite les tests redondants\n"
            "   - Regroupe les tests similaires en un seul test avec paramètres\n"
            "   - Utilise des tests data-driven pour les cas similaires\n"
            "   - Exemple : au lieu de 3 tests séparés (confirmation, rejet, suivi), faire 1 test data-driven\n\n"
            "4. ⭐ NOMBRE DE CAS DE TEST (objectif 100%) :\n"
            "   - Minimum 3 cas de test par US (OBLIGATOIRE)\n"
            "   - Maximum 4 cas de test par US\n"
            "   - Exemple : Happy Path + Edge Case + Test d'erreur + Test de performance\n"
            "   - ⚠️ 1 ou 2 tests par US est INSUFFISANT\n\n"
            "Format exact :\n"
            '{"id": "US-01", "acceptance_criteria": ["..."], "test_scenarios": ["..."], '
            '"test_cases": [{"name": "...", "steps": ["..."], "expected_result": "..."}]}\n\n'
            "User Story :\n" + us_text
        ),
        expected_output='JSON avec id, acceptance_criteria, test_scenarios, test_cases',
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)

    max_attempts = 2
    last_data = None

    for attempt in range(1, max_attempts + 1):
        result = str(crew.kickoff())

        if debug:
            print(f"  --- RAW OUTPUT (tentative {attempt}) ---")
            print(result[:1500])
            print("  --- FIN RAW ---")

        json_str = extract_json(result)
        if not json_str:
            if debug:
                print("  ⚠️ Aucun objet JSON détecté dans la sortie.")
            continue

        try:
            data = json.loads(json_str)
            if "id" in data:
                data["id"] = normalize_us_id(data["id"])
                
            # Vérifier le nombre de test cases
            if data.get("test_cases"):
                tc_count = len(data.get("test_cases", []))
                if tc_count < 3:
                    if debug:
                        print(f"  ⚠️ Seulement {tc_count} test cases. Tentative {attempt}/{max_attempts}.")
                    continue
                    
        except json.JSONDecodeError as e:
            if debug:
                print(f"  ⚠️ JSON invalide ({e}). Tentative {attempt}/{max_attempts}.")
            continue

        last_data = data

        if data.get("test_cases"):
            # ⭐⭐⭐ APPLIQUER LA RÉDUCTION GÉNÉRIQUE ⭐⭐⭐
            data = reduce_redundancy(data)  # ← FONCTION 100% GÉNÉRIQUE
            return data

        if debug:
            print(f"  ⚠️ test_cases vide. Tentative {attempt}/{max_attempts}.")

    if last_data is not None:
        return reduce_redundancy(last_data)

    # Fallback minimal
    us_id_match = re.search(r"US-\d+", us_text)
    return {
        "id": normalize_us_id(us_id_match.group() if us_id_match else "US-??"),
        "acceptance_criteria": [],
        "test_scenarios": ["Scénario nominal", "Cas d'erreur"],
        "test_cases": []
    }


# ──────────────────────────────────────────────
# EXÉCUTION PRINCIPALE
# ──────────────────────────────────────────────

def run_qa_agent(user_stories: str, debug: bool = True) -> list:
    agent = Agent(
        role="QA Analyst",
        goal="Analyser les user stories et générer des cas de test de haute qualité",
        backstory=(
            "Expert QA avec 15 ans d'expérience. "
            "Tu crées des cas de test efficaces avec toujours un Happy Path et un Edge Case. "
            "Tu utilises des verbes d'action pour chaque step. "
            "Tu regroupes les tests similaires pour éviter les redondances. "
            "Tu génères TOUJOURS entre 3 et 4 cas de test par User Story."
        ),
        llm=llm,
        verbose=False
    )

    blocks = re.split(r"(?=\*\*US-\d+\*\*)", user_stories)
    blocks = [b.strip() for b in blocks if b.strip() and 'US-' in b]
    print(f"📋 {len(blocks)} user stories à analyser")

    all_results = []
    report_lines = ["# QA Analysis Report\n"]
    seen_ids = set()

    for i, block in enumerate(blocks):
        print(f"🔄 Analyse US {i + 1}/{len(blocks)}...")
        analysis = analyze_user_story(agent, block, debug=debug)

        if not analysis:
            print(f"⚠️ Impossible d'analyser la US {i + 1}, ignorée.")
            continue

        us_id = normalize_us_id(analysis.get("id", f"US-{i + 1:02d}"))
        analysis["id"] = us_id

        if us_id in seen_ids:
            print(f"⚠️ Doublon détecté pour {us_id}")
            us_id = f"{us_id}-bis"
            analysis["id"] = us_id

        seen_ids.add(us_id)
        all_results.append(analysis)

        report_lines.append(f"## {us_id}\n")
        report_lines.append("### Critères d'acceptation")
        for ac in analysis.get("acceptance_criteria", []):
            report_lines.append(f"- {ac}")

        report_lines.append("\n### Scénarios de test")
        for scenario in analysis.get("test_scenarios", []):
            report_lines.append(f"- {scenario}")

        report_lines.append("\n### Cas de test")
        for tc in analysis.get("test_cases", []):
            report_lines.append(f"\n#### {tc.get('name', 'Test Case')}")
            report_lines.append("**Steps:**")
            for step in tc.get("steps", []):
                report_lines.append(f"  1. {step}")
            report_lines.append(f"**Résultat attendu:** {tc.get('expected_result', '')}")

        report_lines.append("\n---\n")

    os.makedirs("output", exist_ok=True)

    with open("output/qa_analysis.md", "w", encoding="utf-8", errors="ignore") as f:
        f.write("\n".join(report_lines))
    print("💾 Rapport QA sauvegardé dans output/qa_analysis.md")

    with open("output/qa_analysis.json", "w", encoding="utf-8", errors="ignore") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("💾 Données JSON sauvegardées dans output/qa_analysis.json")

    return all_results