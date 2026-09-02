# Traceability Matrix
| US ID | Test Case | Script |
|---|---|---|
| US-01 | Happy Path - Create Job Posting Using Template | `output/scripts/test_us_01.py` |
| US-01 | Edge Case - Invalid Data in Dynamic Fields | `output/scripts/test_us_01.py` |
| US-01 | Happy Path - Edit Saved Job Posting | `output/scripts/test_us_01.py` |
| US-01 | Edge Case - Attempt to Publish Without Saving Changes | `output/scripts/test_us_01.py` |
| US-02 | Post job listing with valid data - Happy Path | `output/scripts/test_us_02.py` |
| US-02 | Post job listing with invalid data - Edge Case | `output/scripts/test_us_02.py` |
| US-02 | User not authorized to post - Edge Case | `output/scripts/test_us_02.py` |
| US-03 | Generate and Track Dedicated Application URL - Happy Path | `output/scripts/test_us_03.py` |
| US-03 | Generate Dedicated Application URL with Invalid Job Posting ID - Edge Case | `output/scripts/test_us_03.py` |
| US-03 | Access Generated URLs - Happy Path | `output/scripts/test_us_03.py` |
| US-04 | Happy Path: Job posting is validated successfully | `output/scripts/test_us_04.py` |
| US-04 | Edge Case: Job posting with invalid data | `output/scripts/test_us_04.py` |
| US-04 | Tests de sélection et publication sur canaux (regroupés) | `output/scripts/test_us_04.py` |
| US-05 | Candidate submits a valid standard CV | `output/scripts/test_us_05.py` |
| US-05 | Candidate uploads an invalid file type | `output/scripts/test_us_05.py` |
| US-05 | Recognition rate display during submission | `output/scripts/test_us_05.py` |
| US-06 | Store and Search Structured CV Data - Happy Path | `output/scripts/test_us_06.py` |
| US-06 | Store and Search Structured CV Data - Edge Case: Invalid Input in the Search Field | `output/scripts/test_us_06.py` |
| US-06 | Store and Search Structured CV Data - Error Scenario: User without Permission to Access the Database | `output/scripts/test_us_06.py` |
| US-07 | Test Happy Path - Candidate Meets All Predefined Criteria | `output/scripts/test_us_07.py` |
| US-07 | Test Edge Case - Candidate Does Not Meet Any Predefined Criteria | `output/scripts/test_us_07.py` |
| US-07 | Test Error Handling - System Fails Due to Invalid Input | `output/scripts/test_us_07.py` |
| US-08 | Happy Path - Vendor Selection Notification | `output/scripts/test_us_08.py` |
| US-08 | Tests data-driven des emails avec variables dynamiques | `output/scripts/test_us_08.py` |
| US-08 | Test de performance - Temps de réponse | `output/scripts/test_us_08.py` |
| US-09 | Generate, Store, and Email Report - Happy Path | `output/scripts/test_us_09.py` |
| US-09 | Invalid User Attempts to Access Report - Edge Case | `output/scripts/test_us_09.py` |
| US-09 | System Fails to Send Email - Error Scenario | `output/scripts/test_us_09.py` |
| US-10 | Happy Path - Candidate successfully downloads multiple job description templates | `output/scripts/test_us_10.py` |
| US-10 | Edge Case - Candidate attempts to access templates with invalid credentials | `output/scripts/test_us_10.py` |
| US-10 | Happy Path - Candidate searches for a specific job description template by name or keyword | `output/scripts/test_us_10.py` |
| US-11 | Happy Path - Valid CV Parsing | `output/scripts/test_us_11.py` |
| US-11 | Edge Case - Invalid CV Parsing | `output/scripts/test_us_11.py` |
| US-11 | Notification Sent Within 7 Days | `output/scripts/test_us_11.py` |
| US-12 | Verify Display of Risk Mitigation Plan | `output/scripts/test_us_12.py` |
| US-12 | Verify DPO Validation Steps Included in Plan | `output/scripts/test_us_12.py` |
| US-12 | Verify HR Manager Receives Plan Timely | `output/scripts/test_us_12.py` |
| US-13 | Tests de performance (regroupés) | `output/scripts/test_us_13.py` |
| US-13 | Tests de gestion des URLs - cycle de vie complet | `output/scripts/test_us_13.py` |
| US-13 | Test de performance - Temps de réponse | `output/scripts/test_us_13.py` |
| US-14 | Happy Path - Configure Pipeline with Five Stages | `output/scripts/test_us_14.py` |
| US-14 | Edge Case - Add an Extra Step Beyond Five Stages | `output/scripts/test_us_14.py` |
| US-14 | Edge Case - Remove a Step from the Pipeline | `output/scripts/test_us_14.py` |
| US-14 | Happy Path - Reorder Steps in the Pipeline | `output/scripts/test_us_14.py` |
| US-15 | Create a customizable email with dynamic content (Happy Path) | `output/scripts/test_us_15.py` |
| US-15 | Schedule an email template at specific intervals (Happy Path) | `output/scripts/test_us_15.py` |
| US-15 | Handle invalid input for dynamic fields (Edge Case) | `output/scripts/test_us_15.py` |
| US-15 | Test the system's performance under high load (Performance Test) | `output/scripts/test_us_15.py` |
| US-16 | Happy Path - Integration with Outlook Calendar | `output/scripts/test_us_16.py` |
| US-16 | Tests de validation des données (regroupés) | `output/scripts/test_us_16.py` |
| US-16 | Happy Path - Real-time Updates Across Time Zones | `output/scripts/test_us_16.py` |
| US-17 | Tests de sécurité et contrôle d'accès (regroupés) | `output/scripts/test_us_17.py` |
| US-17 | Edge Case - Sharing a candidate profile with invalid recipient | `output/scripts/test_us_17.py` |
| US-17 | Edge Case - Revoking access to a shared candidate profile | `output/scripts/test_us_17.py` |
| US-18 | Upload a secure document with valid credentials | `output/scripts/test_us_18.py` |
| US-18 | Attempt unauthorized access to a secure document | `output/scripts/test_us_18.py` |
| US-18 | Log all access attempts and notify administrators of unauthorized access | `output/scripts/test_us_18.py` |
| US-19 | Tests de sélection et publication sur canaux (regroupés) | `output/scripts/test_us_19.py` |
| US-19 | Tests de sélection et publication sur canaux (regroupés) | `output/scripts/test_us_19.py` |
| US-19 | Add a new step to a job type - Edge Case (Step Limit Exceeded) | `output/scripts/test_us_19.py` |
| US-19 | Remove an existing step from a job type - Edge Case (Non-Existent Step) | `output/scripts/test_us_19.py` |
| US-20 | Tests regroupés (Happy Path + Edge Cases) | `output/scripts/test_us_20.py` |
| US-20 | Display Real-Time Dashboard with Customizable Widgets - Edge Case: Invalid Widget Selection | `output/scripts/test_us_20.py` |
| US-20 | Real-Time Data Update - Edge Case: No Network Connection | `output/scripts/test_us_20.py` |
