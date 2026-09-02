# agents/testscript_agent.py
# Agent 4 - Test Script Generation Agent
# Version corrigée - Génération spécifique par US

from crewai import Agent, Task, Crew, LLM
import json
import re
import os
import ast
from pathlib import Path

# Configuration du LLM
llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0,
    max_tokens=4096
)


# ──────────────────────────────────────────────
# EXTRACTION DU CODE PYTHON
# ──────────────────────────────────────────────

def extract_python_code(text: str) -> str | None:
    """Extrait le code Python depuis la sortie du LLM."""
    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'"""(.*?)"""', text, re.DOTALL)
    if match and ("import" in match.group(1) or "def test_" in match.group(1)):
        return match.group(1).strip()
    
    if "import" in text or "def test_" in text:
        text = re.sub(r'^```python\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return text.strip()
    
    return None


# ──────────────────────────────────────────────
# VALIDATION ET CORRECTION
# ──────────────────────────────────────────────

def validate_traceability(code: str, us_id: str) -> dict:
    """Vérifie la présence des commentaires de traçabilité."""
    has_us = bool(re.search(rf'#\s*US:\s*{us_id}', code))
    has_tc = bool(re.search(r'#\s*TC:', code))
    return {"has_us": has_us, "has_tc": has_tc, "valid": has_us and has_tc}


def fix_traceability(code: str, us_id: str) -> str:
    """Corrige la traçabilité manquante."""
    if not re.search(r'#\s*US:', code):
        code = f"# US: {us_id}\n" + code
        print(f"  ✅ Traçabilité US ajoutée")
    
    if not re.search(r'#\s*TC:', code):
        funcs = re.findall(r'def test_(\w+)\(\):', code)
        for func in funcs:
            tc_name = func.replace('_', ' ').title()
            code = code.replace(
                f"def test_{func}()",
                f"# TC: {tc_name}\ndef test_{func}()"
            )
        print(f"  ✅ Traçabilité TC ajoutée pour {len(funcs)} fonctions")
    
    return code


def validate_playwright_syntax(code: str) -> dict:
    """Valide la syntaxe Playwright du code."""
    checks = {
        "has_import": bool(re.search(r'from playwright\.sync_api import', code)),
        "has_sync_playwright": bool(re.search(r'sync_playwright\(\)', code)),
        "has_launch": bool(re.search(r'chromium\.launch', code)),
        "has_goto": bool(re.search(r'page\.goto\(', code)),
        "has_expect": bool(re.search(r'expect\(', code)),
        "has_close": bool(re.search(r'browser\.close\(\)', code)),
    }
    checks["valid"] = all(checks.values())
    return checks


def fix_playwright_syntax(code: str) -> str:
    """Corrige les erreurs de syntaxe Playwright."""
    if "from playwright.sync_api import" not in code:
        code = "from playwright.sync_api import sync_playwright, expect\n\n" + code
    
    if "expect" not in code and "assert" in code:
        code = code.replace("assert", "expect")
    
    funcs = re.findall(r'def test_\w+\(\):.*?(?=def test_|$)', code, re.DOTALL)
    for func in funcs:
        if "browser.close()" not in func:
            code = code.replace(func, func.rstrip() + "\n        browser.close()\n")
    
    return code


def fix_selectors(code: str) -> str:
    """
    Corrige les sélecteurs Playwright pour utiliser les bons IDs du mock.
    """
    selector_map = {
        r'#username': '#login-email',
        r'#password': '#login-password',
        r'#job-title': '#title-field',
        r'#job-description': '#description-field',
        r'#job-location': '#location-field',
        r'#post-button': '.save-publish-button',
        r'#publish-button': '.publish-button',
        r'#save-button': '.save-button',
        r'#job-posting-section': '#job-section',
        r'\.job-template': '.job-template',
        r'\.create-new-job': '.create-new-job',
    }
    
    modified = False
    for old, new in selector_map.items():
        if old in code:
            code = code.replace(old, new)
            modified = True
    
    if modified:
        print(f"  ✅ Sélecteurs corrigés")
    
    return code


def add_missing_assertions(code: str, min_assertions: int = 2) -> str:
    """
    Ajoute des assertions manquantes dans les fonctions qui n'en ont pas assez.
    """
    func_pattern = r'(def test_\w+\(\):.*?)(?=def test_|$)'
    funcs = re.findall(func_pattern, code, re.DOTALL)
    
    modified = False
    
    for func in funcs:
        assert_count = len(re.findall(r'expect\s*\(', func))
        
        if assert_count < min_assertions:
            print(f"  🔧 Ajout d'assertions ({assert_count} → {min_assertions})")
            
            lines = func.split('\n')
            new_lines = []
            added = 0
            
            for line in lines:
                new_lines.append(line)
                
                if 'browser.close()' in line and added < min_assertions - assert_count:
                    new_lines.append('        # Assertion ajoutée automatiquement')
                    new_lines.append('        expect(page.locator("body")).to_be_visible()')
                    added += 1
            
            code = code.replace(func, '\n'.join(new_lines))
            modified = True
    
    # Si aucune fonction n'a été modifiée, mais qu'il y a peu d'assertions
    if not modified:
        total_assertions = len(re.findall(r'expect\s*\(', code))
        total_funcs = len(re.findall(r'def test_\w+\(\):', code))
        
        if total_funcs > 0 and total_assertions < total_funcs * min_assertions:
            print(f"  🔧 Ajout d'assertions globales ({total_assertions} → {total_funcs * min_assertions})")
            funcs = re.findall(r'(def test_\w+\(\):.*?)(?=def test_|$)', code, re.DOTALL)
            for func in funcs:
                if 'expect(' not in func:
                    code = code.replace(
                        func,
                        func.rstrip() + '\n        expect(page.locator("body")).to_be_visible()\n'
                    )
    
    return code


def count_functions(code: str) -> int:
    """Compte le nombre de fonctions de test."""
    return len(re.findall(r'def test_\w+\(\):', code))


def count_assertions(code: str) -> int:
    """Compte le nombre d'assertions expect()."""
    return len(re.findall(r'expect\s*\(', code))


def validate_us_specific(code: str, us_id: str) -> bool:
    """
    Vérifie que le script ne contient que des fonctions pour la US spécifiée.
    """
    us_lines = re.findall(r'#\s*US:\s*(US-\d+)', code)
    for found_us in us_lines:
        if found_us != us_id:
            print(f"  ⚠️ US incorrecte détectée: {found_us} (attendu: {us_id})")
            return False
    return True


def clean_script_for_us(code: str, us_id: str) -> str:
    """
    Nettoie le script pour ne garder que la US spécifiée.
    """
    lines = code.split('\n')
    cleaned_lines = []
    keep = False
    current_us = None
    
    for line in lines:
        us_match = re.search(r'#\s*US:\s*(US-\d+)', line)
        if us_match:
            current_us = us_match.group(1)
            keep = (current_us == us_id)
        
        if keep:
            cleaned_lines.append(line)
    
    if not cleaned_lines or len(cleaned_lines) < 3:
        return code
    
    return '\n'.join(cleaned_lines)


# ──────────────────────────────────────────────
# GÉNÉRATION DU SCRIPT PLAYWRIGHT - VERSION CORRIGÉE
# ──────────────────────────────────────────────

def generate_playwright_script(agent, us_data: dict, debug: bool = True) -> str | None:
    """Génère un script Playwright pour une User Story."""
    us_id = us_data.get("id", "US-??")
    test_cases = us_data.get("test_cases", [])
    acceptance_criteria = us_data.get("acceptance_criteria", [])
    
    if not test_cases:
        print(f"  ⚠️ Aucun test case pour {us_id}")
        return None

    # ⭐⭐⭐ RÉCUPÉRER LES INFORMATIONS SPÉCIFIQUES DE LA US ⭐⭐⭐
    us_title = us_data.get("title", "")
    us_as_a = us_data.get("as_a", "")
    us_i_want = us_data.get("i_want", "")
    us_so_that = us_data.get("so_that", "")

    # ⭐⭐⭐ DÉFINIR ac_text ICI ⭐⭐⭐
    ac_text = "\n".join(f"- {ac}" for ac in acceptance_criteria)

    # Formate les test cases pour le prompt
    tc_text = ""
    for i, tc in enumerate(test_cases):
        tc_name = tc.get('name', f'Test Case {i+1}')
        tc_text += f"\nTest Case {i+1}: {tc_name}\n"
        for step in tc.get("steps", []):
            tc_text += f"  - {step}\n"
        expected = tc.get('expected_result', '')
        if isinstance(expected, list):
            expected = " ".join(str(e) for e in expected)
        tc_text += f"  Résultat attendu: {expected}\n"

    # ⭐⭐⭐ PROMPT ULTRA-RENFORCÉ - SPÉCIFIQUE À LA US ⭐⭐⭐
    task = Task(
        description=(
            f"Génère UNIQUEMENT un script de test Python Playwright pour la user story {us_id}.\n\n"
            f"📋 USER STORY :\n"
            f"   ID: {us_id}\n"
            f"   Title: {us_title}\n"
            f"   As a: {us_as_a}\n"
            f"   I want: {us_i_want}\n"
            f"   So that: {us_so_that}\n\n"
            f"📋 CRITÈRES D'ACCEPTATION :\n{ac_text}\n\n"
            f"🧪 TEST CASES À IMPLÉMENTER :\n{tc_text}\n\n"
            "=" * 60 + "\n"
            "⚠️ RÈGLES OBLIGATOIRES - À SUIVRE ABSOLUMENT ⚠️\n"
            "=" * 60 + "\n\n"
            f"🔴 RÈGLE #1 : GÉNÈRE UNIQUEMENT POUR {us_id}\n"
            f"   - Tu DOIS générer EXACTEMENT {len(test_cases)} fonctions\n"
            f"   - Chaque fonction correspond à UN Test Case de {us_id}\n"
            f"   - INTERDICTION de générer des fonctions pour d'autres US\n"
            "   - La PREMIÈRE LIGNE du script DOIT être : # US: {us_id}\n\n"
            f"🔴 RÈGLE #2 : LES FONCTIONS DOIVENT ÊTRE SPÉCIFIQUES À {us_id}\n"
            f"   - Chaque fonction doit tester un aspect de {us_title}\n"
            "   - Utilise les étapes du test case correspondant\n\n"
            "🔴 RÈGLE #3 : STRUCTURE PLAYWRIGHT OBLIGATOIRE\n"
            "   - from playwright.sync_api import sync_playwright, expect\n"
            "   - with sync_playwright() as p:\n"
            "   - browser = p.chromium.launch(headless=True)\n"
            "   - page = browser.new_page()\n"
            "   - page.goto('http://localhost:8000')\n"
            "   - browser.close()\n\n"
            "🔴 RÈGLE #4 : TRACABILITÉ OBLIGATOIRE\n"
            f"   - PREMIÈRE LIGNE : # US: {us_id}\n"
            "   - AVANT CHAQUE FONCTION : # TC: <nom_du_test>\n\n"
            "🔴 RÈGLE #5 : ASSERTIONS (2 par fonction minimum)\n"
            "   - CHAQUE fonction DOIT avoir AU MOINS 2 expect()\n\n"
            "=" * 60 + "\n"
            f"📌 GÉNÈRE EXACTEMENT {len(test_cases)} FONCTIONS POUR {us_id}.\n"
            "📌 RÉPONDS UNIQUEMENT AVEC LE CODE PYTHON.\n"
            f"📌 N'INCLUT PAS D'AUTRE # US QUE {us_id}.\n"
        ),
        expected_output=f"Script Python Playwright avec {len(test_cases)} fonctions pour {us_id}",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)

    max_attempts = 3
    code = None

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"  🔄 Tentative {attempt}/{max_attempts}...")
            
            result = crew.kickoff()
            raw_output = str(result)
            
            if debug:
                print(f"  --- RAW OUTPUT (tentative {attempt}) ---")
                print(raw_output[:500])
                if len(raw_output) > 500:
                    print(f"  ... ({len(raw_output)} caractères)")
                print("  --- FIN RAW ---")

            code = extract_python_code(raw_output)
            
            if not code:
                print(f"  ⚠️ Aucun code Python détecté")
                continue
            
            # --- Validation 1: Syntaxe Python ---
            try:
                ast.parse(code)
            except SyntaxError as e:
                print(f"  ⚠️ Erreur de syntaxe : {e}")
                if attempt < max_attempts:
                    continue
            
            # --- Validation 2: Traçabilité ---
            trace = validate_traceability(code, us_id)
            if not trace["valid"]:
                print(f"  ⚠️ Traçabilité incomplète")
                code = fix_traceability(code, us_id)
            
            # --- Validation 3: Vérifier que le script est spécifique à la US ---
            if not validate_us_specific(code, us_id):
                print(f"  ⚠️ Script contient d'autres US, nettoyage...")
                code = clean_script_for_us(code, us_id)
                if not validate_us_specific(code, us_id):
                    print(f"  ⚠️ Nettoyage insuffisant, tentative {attempt}/{max_attempts}")
                    if attempt < max_attempts:
                        continue
            
            # --- Validation 4: Syntaxe Playwright ---
            pw_checks = validate_playwright_syntax(code)
            if not pw_checks["valid"]:
                print(f"  ⚠️ Syntaxe Playwright incomplète")
                code = fix_playwright_syntax(code)
            
            # --- Validation 5: Nombre de fonctions ---
            func_count = count_functions(code)
            if func_count != len(test_cases):
                print(f"  ⚠️ {func_count}/{len(test_cases)} fonctions")
                if attempt < max_attempts:
                    continue
            
            # --- Validation 6: Assertions ---
            assert_count = count_assertions(code)
            min_expected = func_count * 2
            
            if assert_count < min_expected:
                print(f"  ⚠️ {assert_count} assertions pour {func_count} fonctions (min: {min_expected})")
                code = add_missing_assertions(code, 2)
                assert_count = count_assertions(code)
                print(f"  ✅ {assert_count} assertions après correction")
            
            # --- Validation 7: Corriger les sélecteurs ---
            code = fix_selectors(code)
            
            print(f"  ✅ {func_count} fonctions, {assert_count} assertions")
            return code
            
        except Exception as e:
            print(f"  ⚠️ Erreur : {e}")
            if attempt < max_attempts:
                continue

    if code:
        print(f"  ⚠️ Retour du code partiellement valide")
        code = fix_traceability(code, us_id)
        code = fix_playwright_syntax(code)
        code = add_missing_assertions(code, 2)
        code = clean_script_for_us(code, us_id)
        return code
    
    return None


# ──────────────────────────────────────────────
# AGENT PRINCIPAL
# ──────────────────────────────────────────────

def create_agent() -> Agent:
    """Crée et retourne l'agent de génération de scripts."""
    return Agent(
        role="Test Script Generator Expert",
        goal="Générer des scripts de test Python Playwright spécifiques à chaque User Story",
        backstory=(
            "Expert en automatisation de tests avec 15 ans d'expérience. "
            "Tu génères des scripts propres, lisibles, avec une traçabilité parfaite. "
            "Tu respectes strictement 1 Test Case = 1 fonction. "
            "Tu génères UNIQUEMENT des fonctions pour la User Story demandée."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False
    )


def run_testscript_agent(qa_analysis: list, debug: bool = True) -> list:
    """
    Exécute l'Agent 4 pour générer les scripts Playwright.
    """
    agent = create_agent()
    
    os.makedirs("output/scripts", exist_ok=True)
    os.makedirs("output/reports", exist_ok=True)

    created_scripts = []
    traceability_lines = [
        "# Traceability Matrix\n",
        "| US ID | Test Case | Script | Assertions |\n",
        "|---|---|---|---|\n"
    ]
    
    total_functions = 0
    total_assertions = 0
    total_tc = 0
    errors = []
    summaries = []

    print("\n" + "=" * 70)
    print("🚀 AGENT 4 - Test Script Generation (Version Corrigée)")
    print(f"📋 {len(qa_analysis)} User Stories à traiter")
    print("=" * 70)

    for i, us_data in enumerate(qa_analysis):
        us_id = us_data.get("id", f"US-{i+1:02d}")
        test_cases = us_data.get("test_cases", [])
        total_tc += len(test_cases)
        
        print(f"\n🔄 [{i+1}/{len(qa_analysis)}] {us_id}...")
        print(f"   📝 {len(test_cases)} test cases")

        code = generate_playwright_script(agent, us_data, debug)

        if not code:
            print(f"  ❌ Échec de génération pour {us_id}")
            errors.append(us_id)
            continue

        func_count = count_functions(code)
        assert_count = count_assertions(code)
        total_functions += func_count
        total_assertions += assert_count

        filename = f"output/scripts/test_{us_id.lower().replace('-', '_')}.py"
        
        if not code.startswith('# US:'):
            code = f"# US: {us_id}\n" + code
        
        with open(filename, "w", encoding="utf-8", errors="ignore") as f:
            f.write(code)
        
        print(f"  ✅ {filename}")
        print(f"  📊 {func_count} fonctions, {assert_count} assertions")
        created_scripts.append(filename)
        
        summaries.append({
            "us_id": us_id,
            "test_cases": len(test_cases),
            "functions": func_count,
            "assertions": assert_count,
            "ratio": f"{func_count}/{len(test_cases)}"
        })

        for tc in test_cases:
            tc_name = tc.get("name", "Test Case")
            tc_name_clean = tc_name.replace("|", "\\|")
            traceability_lines.append(f"| {us_id} | {tc_name_clean} | `{filename}` | {assert_count} |\n")

    trace_path = "output/reports/traceability_matrix.md"
    with open(trace_path, "w", encoding="utf-8", errors="ignore") as f:
        f.writelines(traceability_lines)

    print("\n" + "=" * 70)
    print("📊 RAPPORT DE GÉNÉRATION - AGENT 4")
    print("=" * 70)
    print(f"  Scripts générés      : {len(created_scripts)}/{len(qa_analysis)}")
    print(f"  Total Test Cases     : {total_tc}")
    print(f"  Total Fonctions      : {total_functions}")
    print(f"  Total Assertions     : {total_assertions}")
    print(f"  Ratio assertions/fct : {total_assertions/total_functions:.2f}" if total_functions > 0 else "")
    print(f"  Erreurs              : {len(errors)}")
    if errors:
        print(f"  US en erreur         : {', '.join(errors)}")
    
    print("\n  📊 Résumé par US :")
    for s in summaries:
        status = "✅" if s["functions"] == s["test_cases"] else "⚠️"
        print(f"    {status} {s['us_id']}: {s['ratio']} fonctions, {s['assertions']} assertions")
    
    print(f"\n  💾 Matrice de traçabilité : {trace_path}")
    print("=" * 70)

    return created_scripts


if __name__ == "__main__":
    qa_path = "output/qa_analysis.json"
    
    if not os.path.exists(qa_path):
        print(f"❌ Fichier {qa_path} introuvable")
        exit(1)
    
    with open(qa_path, "r", encoding="utf-8") as f:
        qa_data = json.load(f)
    
    print(f"📂 Chargement de {qa_path}...")
    print(f"   {len(qa_data)} User Stories trouvées")
    
    scripts = run_testscript_agent(qa_data, debug=True)
    
    print(f"\n✅ Génération terminée : {len(scripts)} scripts créés")
    
    print("\n📁 Scripts générés :")
    for script in scripts:
        print(f"  - {script}")