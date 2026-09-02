# Traceability Matrix
| US ID | Test Case | Script | Assertions |
|---|---|---|---|
| US-01 | Create a job posting using a customizable template - Happy Path | `output/scripts/test_us_01.py` | 8 |
| US-01 | Attempt to create a job posting with invalid template selection - Edge Case | `output/scripts/test_us_01.py` | 8 |
| US-01 | Attempt to create a job posting with missing required fields - Error Scenario | `output/scripts/test_us_01.py` | 8 |
| US-01 | Create multiple job postings in a short period - Performance Scenario | `output/scripts/test_us_01.py` | 8 |
| US-02 | Happy Path - Posting to Multiple Channels | `output/scripts/test_us_02.py` | 6 |
| US-02 | Edge Case: Invalid Channel | `output/scripts/test_us_02.py` | 6 |
| US-02 | Edge Case: Unauthorized User | `output/scripts/test_us_02.py` | 6 |
| US-03 | Tests de sélection et publication sur canaux (regroupés) | `output/scripts/test_us_03.py` | 6 |
| US-03 | Test de performance - Temps de réponse | `output/scripts/test_us_03.py` | 6 |
| US-03 | Test d'erreur - Données invalides | `output/scripts/test_us_03.py` | 6 |
| US-04 | Moderate valid job posting (Happy Path) | `output/scripts/test_us_04.py` | 6 |
| US-04 | Tests de sélection et publication sur canaux (regroupés) | `output/scripts/test_us_04.py` | 6 |
| US-04 | Test de performance - Temps de réponse | `output/scripts/test_us_04.py` | 6 |
| US-05 | Happy Path - Parsing Standard CVs | `output/scripts/test_us_05.py` | 8 |
| US-05 | Edge Case - Parsing Non-Standard CVs | `output/scripts/test_us_05.py` | 8 |
| US-05 | Error Scenario - Parsing Unsupported File Formats | `output/scripts/test_us_05.py` | 8 |
| US-05 | Performance Scenario - Parsing Large Number of CVs | `output/scripts/test_us_05.py` | 8 |
| US-06 | Tests de validation des données (regroupés) | `output/scripts/test_us_06.py` | 6 |
| US-06 | Tests de validation des données (regroupés) | `output/scripts/test_us_06.py` | 6 |
| US-06 | Test de performance - Temps de réponse | `output/scripts/test_us_06.py` | 6 |
| US-07 | Happy Path: Valid Job Description and Candidate Data | `output/scripts/test_us_07.py` | 6 |
| US-07 | Tests de validation des données (regroupés) | `output/scripts/test_us_07.py` | 6 |
| US-07 | Edge Case: Algorithm Compliance Failure | `output/scripts/test_us_07.py` | 6 |
| US-08 | Tests data-driven des emails avec variables dynamiques | `output/scripts/test_us_08.py` | 6 |
| US-08 | Edge Case - Invalid input | `output/scripts/test_us_08.py` | 6 |
| US-08 | Test de performance - Temps de réponse | `output/scripts/test_us_08.py` | 6 |
| US-09 | Happy Path - Configuration Change Logging | `output/scripts/test_us_09.py` | 8 |
| US-09 | Edge Case - Invalid Configuration Change | `output/scripts/test_us_09.py` | 8 |
| US-09 | Happy Path - Notification for UAT Readiness | `output/scripts/test_us_09.py` | 8 |
| US-09 | Edge Case - Notification for UAT Readiness with Unmet Conditions | `output/scripts/test_us_09.py` | 8 |
| US-10 | Tests de sécurité et contrôle d'accès (regroupés) | `output/scripts/test_us_10.py` | 6 |
| US-10 | Candidate documents training sessions - Edge Case | `output/scripts/test_us_10.py` | 6 |
| US-10 | Candidate accesses user guides - Edge Case | `output/scripts/test_us_10.py` | 6 |
| US-11 | Track Estimated Budget - Happy Path | `output/scripts/test_us_11.py` | 8 |
| US-11 | Tests de validation des données (regroupés) | `output/scripts/test_us_11.py` | 8 |
| US-11 | Generate Budget Variance Report - Edge Case | `output/scripts/test_us_11.py` | 8 |
| US-11 | Log Expenses - Happy Path | `output/scripts/test_us_11.py` | 8 |
| US-12 | Tests de performance (regroupés) | `output/scripts/test_us_12.py` | 8 |
| US-12 | Notify Hiring Manager when reports are ready | `output/scripts/test_us_12.py` | 8 |
| US-12 | Invalid signature in reports | `output/scripts/test_us_12.py` | 8 |
| US-12 | No reports generated | `output/scripts/test_us_12.py` | 8 |
| US-13 | Configure recruitment process for a software developer role | `output/scripts/test_us_13.py` | 8 |
| US-13 | Ensure real-time updates are applied | `output/scripts/test_us_13.py` | 8 |
| US-13 | Verify system compliance with F-10 | `output/scripts/test_us_13.py` | 8 |
| US-13 | Test edge case with fewer than 5 steps | `output/scripts/test_us_13.py` | 8 |
| US-14 | Happy Path: Adding and viewing comments and evaluations | `output/scripts/test_us_14.py` | 8 |
| US-14 | Edge Case: Attempting to edit non-editable comments | `output/scripts/test_us_14.py` | 8 |
| US-14 | Error Scenario: Attempting to add comments without login | `output/scripts/test_us_14.py` | 8 |
| US-14 | Performance Scenario: Adding and viewing comments under high load | `output/scripts/test_us_14.py` | 8 |
| US-15 | Happy Path - Customize email with dynamic variables | `output/scripts/test_us_15.py` | 8 |
| US-15 | Edge Case - Dynamic content insertion | `output/scripts/test_us_15.py` | 8 |
| US-15 | Tests data-driven des emails avec variables dynamiques | `output/scripts/test_us_15.py` | 8 |
| US-15 | Happy Path - Compliance with F-14 standards | `output/scripts/test_us_15.py` | 8 |
| US-16 | Tests data-driven des emails avec variables dynamiques | `output/scripts/test_us_16.py` | 6 |
| US-16 | Configure and test edge cases for notification settings | `output/scripts/test_us_16.py` | 6 |
| US-16 | Test de performance - Temps de réponse | `output/scripts/test_us_16.py` | 6 |
| US-17 | Happy Path - Bi-directional Sync and Timezone Management | `output/scripts/test_us_17.py` | 8 |
| US-17 | Happy Path - Calendar Integration Compliance | `output/scripts/test_us_17.py` | 8 |
| US-17 | Edge Case - User Authentication and Authorization | `output/scripts/test_us_17.py` | 8 |
| US-17 | Edge Case - Invalid Calendar Data | `output/scripts/test_us_17.py` | 8 |
| US-18 | Tests regroupés (Happy Path + Edge Cases) | `output/scripts/test_us_18.py` | 6 |
| US-18 | Verify saved and applied steps consistency | `output/scripts/test_us_18.py` | 6 |
| US-18 | Test de performance - Temps de réponse | `output/scripts/test_us_18.py` | 6 |
| US-19 | Happy Path: Encryption of candidate attachments | `output/scripts/test_us_19.py` | 6 |
| US-19 | Edge Case: Upload an attachment without encryption | `output/scripts/test_us_19.py` | 6 |
| US-19 | Edge Case: Unauthorized access to candidate attachments | `output/scripts/test_us_19.py` | 6 |
| US-20 | Tests regroupés (Happy Path + Edge Cases) | `output/scripts/test_us_20.py` | 8 |
| US-20 | Test de performance - Temps de réponse | `output/scripts/test_us_20.py` | 8 |
| US-20 | Test d'erreur - Données invalides | `output/scripts/test_us_20.py` | 8 |
