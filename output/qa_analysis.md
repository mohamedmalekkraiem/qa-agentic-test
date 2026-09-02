# QA Analysis Report

## US-01

### Critères d'acceptation
- System must provide ≥ 5 templates
- System must have dynamic fields
- System must comply with F-01

### Scénarios de test
- Happy Path: Create a job posting using a customizable template
- Edge Case: Attempt to create a job posting with invalid template selection
- Error Scenario: Attempt to create a job posting with missing required fields
- Performance Scenario: Create multiple job postings in a short period

### Cas de test

#### Create a job posting using a customizable template - Happy Path
**Steps:**
  1. Login as HR Manager
  1. Navigate to Job Posting Templates
  1. Select a template from the available 5+ templates
  1. Click on 'Create Job Posting'
  1. Fill in all required fields dynamically
  1. Review and confirm the job posting details
  1. Click 'Save' to create the job posting
**Résultat attendu:** Job posting is successfully created and saved with all required fields filled and template applied

#### Attempt to create a job posting with invalid template selection - Edge Case
**Steps:**
  1. Login as HR Manager
  1. Navigate to Job Posting Templates
  1. Select an invalid or non-existent template
  1. Click on 'Create Job Posting'
  1. Observe error message indicating invalid template selection
**Résultat attendu:** System displays an error message indicating that the selected template is invalid or non-existent

#### Attempt to create a job posting with missing required fields - Error Scenario
**Steps:**
  1. Login as HR Manager
  1. Navigate to Job Posting Templates
  1. Select a template
  1. Click on 'Create Job Posting'
  1. Do not fill in any required fields
  1. Click 'Save' to create the job posting
**Résultat attendu:** System displays error messages for each missing required field

#### Create multiple job postings in a short period - Performance Scenario
**Steps:**
  1. Login as HR Manager
  1. Navigate to Job Posting Templates
  1. Select a template
  1. Click on 'Create Job Posting'
  1. Fill in required fields and click 'Save' to create the first job posting
  1. Repeat steps 3-4 to create additional job postings
  1. Observe system performance during the creation of multiple job postings
**Résultat attendu:** System handles the creation of multiple job postings without any performance degradation or errors

---

## US-02

### Critères d'acceptation
- System must support 1-click posting on ≥ 4 channels
- System must automatically post to LinkedIn, Indeed, Welcome to the Jungle, and careers website
- System must comply with F-02

### Scénarios de test
- Happy Path
- Edge Case: Invalid Channel
- Edge Case: Unauthorized User

### Cas de test

#### Happy Path - Posting to Multiple Channels
**Steps:**
  1. Login to the system as a Hiring Manager
  1. Navigate to the job listing section
  1. Select the job listing to be posted
  1. Click the '1-click post' button
  1. Verify that the job listing is posted on LinkedIn
  1. Verify that the job listing is posted on Indeed
  1. Verify that the job listing is posted on Welcome to the Jungle
  1. Verify that the job listing is posted on the careers website
**Résultat attendu:** The job listing is successfully posted on all selected channels.

#### Edge Case: Invalid Channel
**Steps:**
  1. Login to the system as a Hiring Manager
  1. Navigate to the job listing section
  1. Select the job listing to be posted
  1. Enter an invalid channel name in the '1-click post' field
  1. Click the '1-click post' button
  1. Observe that the system does not allow posting to the invalid channel
**Résultat attendu:** The system displays an error message indicating that the channel name is invalid.

#### Edge Case: Unauthorized User
**Steps:**
  1. Login to the system as a non-Hiring Manager user
  1. Navigate to the job listing section
  1. Attempt to click the '1-click post' button
  1. Observe that the system denies the action and displays an error message
**Résultat attendu:** The system denies the action and displays an error message indicating that the user is not authorized to post job listings.

---

## US-03

### Critères d'acceptation
- System must generate a dedicated application URL per job posting
- System must track the source of applications
- System must comply with F-03

### Scénarios de test
- Happy Path: Generate and track a unique application URL for a job posting
- Edge Case: Generate a unique application URL with invalid job posting data
- Error Case: Generate a unique application URL for a non-existent job posting
- Performance: Generate and track multiple unique application URLs in a short period

### Cas de test

#### Tests de sélection et publication sur canaux (regroupés)
**Steps:**
  1. Login as Recruiter
  1. Navigate to Job Postings section
  1. Click on 'Create Job Posting' button
  1. Enter job posting details
  1. Click on 'Generate URL' button
**Résultat attendu:** Le système publie correctement sur tous les canaux sélectionnés et gère les cas limites avec des messages appropriés

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

#### Test d'erreur - Données invalides
**Steps:**
  1. Soumettre des données invalides
  1. Vérifier la validation
  1. Confirmer l'affichage du message d'erreur
**Résultat attendu:** Le système rejette les données invalides avec un message approprié

---

## US-04

### Critères d'acceptation
- System must have an HR + Manager validation workflow
- System must require moderation before job posting publication
- System must comply with F-04

### Scénarios de test
- Moderation workflow with valid job posting
- Moderation workflow with invalid job posting
- Moderation workflow with incomplete job posting

### Cas de test

#### Moderate valid job posting (Happy Path)
**Steps:**
  1. Login as Talent Acquisition Specialist
  1. Create a new job posting
  1. Enter valid job posting details
  1. Submit job posting for moderation
  1. HR reviews and approves the job posting
  1. Manager reviews and approves the job posting
  1. Verify that the job posting is published
**Résultat attendu:** Job posting is successfully published after HR and Manager approval

#### Tests de sélection et publication sur canaux (regroupés)
**Steps:**
  1. Login as Talent Acquisition Specialist
  1. Create a new job posting
  1. Enter invalid (avec différentes variantes)
  1. Submit job posting for moderation
  1. HR reviews and rejects the job posting
**Résultat attendu:** Le système publie correctement sur tous les canaux sélectionnés et gère les cas limites avec des messages appropriés

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

---

## US-05

### Critères d'acceptation
- System must recognize ≥ 90% of standard CVs
- System must support parsing of PDF, Word, and LinkedIn CVs
- System must comply with F-05

### Scénarios de test
- Parsing standard CVs
- Parsing non-standard CVs
- Parsing unsupported file formats
- Parsing large number of CVs

### Cas de test

#### Happy Path - Parsing Standard CVs
**Steps:**
  1. Login to the system as an IT Manager
  1. Upload a standard CV in PDF format
  1. Verify that the system successfully parses the CV
  1. Check that all key information is correctly extracted
  1. Confirm that the system recognizes the CV with ≥ 90% accuracy
**Résultat attendu:** The system successfully parses the standard CV, extracts all key information, and recognizes the CV with ≥ 90% accuracy.

#### Edge Case - Parsing Non-Standard CVs
**Steps:**
  1. Login to the system as an IT Manager
  1. Upload a non-standard CV in Word format with missing sections
  1. Verify that the system still attempts to parse the CV
  1. Check that the system extracts as much information as possible despite missing sections
  1. Confirm that the system still recognizes the CV with ≥ 90% accuracy
**Résultat attendu:** The system attempts to parse the non-standard CV, extracts as much information as possible, and still recognizes the CV with ≥ 90% accuracy.

#### Error Scenario - Parsing Unsupported File Formats
**Steps:**
  1. Login to the system as an IT Manager
  1. Upload a CV in an unsupported file format (e.g., .jpeg)
  1. Verify that the system rejects the file
  1. Check that an appropriate error message is displayed
  1. Confirm that the system does not attempt to parse the unsupported file
**Résultat attendu:** The system rejects the CV in the unsupported file format, displays an appropriate error message, and does not attempt to parse the file.

#### Performance Scenario - Parsing Large Number of CVs
**Steps:**
  1. Login to the system as an IT Manager
  1. Upload 100 standard CVs in PDF format
  1. Verify that the system can process all 100 CVs within a reasonable time frame
  1. Check that all 100 CVs are successfully parsed
  1. Confirm that the system maintains its ≥ 90% accuracy rate
**Résultat attendu:** The system successfully processes all 100 standard CVs within a reasonable time frame, parses all 100 CVs, and maintains its ≥ 90% accuracy rate.

---

## US-06

### Critères d'acceptation
- System must store candidate CV data in a structured database
- System must support full-text search by skills, experience, and location
- System must comply with F-06

### Scénarios de test
- Happy Path: Storing a candidate CV with valid data
- Edge Case: Storing a candidate CV with invalid data
- Error Case: Storing a candidate CV with missing required fields
- Performance Case: Storing multiple candidate CVs in a short period

### Cas de test

#### Tests de validation des données (regroupés)
**Steps:**
  1. Login as GDPR Officer
  1. Navigate to the Candidate CV Management section
  1. Click on (avec différentes variantes)
  1. Enter valid (avec différentes variantes)
  1. Upload a valid CV file
**Résultat attendu:** Le système valide correctement toutes les entrées et affiche des messages d'erreur appropriés

#### Tests de validation des données (regroupés)
**Steps:**
  1. Login as GDPR Officer
  1. Navigate to the Candidate CV Management section
  1. Click on (avec différentes variantes)
  1. Enter invalid (avec différentes variantes)
  1. Upload an invalid CV file (e.g., corrupted file)
**Résultat attendu:** Le système valide correctement toutes les entrées et affiche des messages d'erreur appropriés

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

---

## US-07

### Critères d'acceptation
- System must use a transparent algorithm to score candidates
- System must allow customizable scoring criteria
- System must comply with F-07

### Scénarios de test
- Happy Path: Valid Job Description and Candidate Data
- Edge Case: Invalid Job Description
- Edge Case: Candidate Data Missing or Invalid
- Edge Case: Algorithm Compliance Failure

### Cas de test

#### Happy Path: Valid Job Description and Candidate Data
**Steps:**
  1. Login as HR Business Partner
  1. Navigate to the Candidate Scoring module
  1. Enter a valid job description
  1. Enter valid candidate data
  1. Click on the 'Score' button
  1. Verify that the system generates a score for the candidate
  1. Check that the score is based on the provided job description
  1. Confirm that the system uses a transparent algorithm
**Résultat attendu:** The system generates a score for the candidate based on the provided job description, and the score is displayed transparently.

#### Tests de validation des données (regroupés)
**Steps:**
  1. Login as HR Business Partner
  1. Navigate to the Candidate Scoring module
  1. Enter an invalid job description (e.g., an empty string or non-descriptive text)
  1. Enter valid candidate data
  1. Click on the 'Score' button
**Résultat attendu:** Le système valide correctement toutes les entrées et affiche des messages d'erreur appropriés

#### Edge Case: Algorithm Compliance Failure
**Steps:**
  1. Login as HR Business Partner
  1. Navigate to the Candidate Scoring module
  1. Enter a valid job description
  1. Enter valid candidate data
  1. Click on the 'Score' button
  1. Verify that the system generates a score for the candidate
  1. Check that the score is within the expected range
  1. Confirm that the system complies with F-07
**Résultat attendu:** The system generates a score for the candidate, and the score is within the expected range, ensuring compliance with F-07.

---

## US-08

### Critères d'acceptation
- System must alert if email or first+last name is identical
- System must detect applications from the same candidate for different positions
- System must comply with F-08

### Scénarios de test
- Detect duplicate by email
- Detect duplicate by first+last name
- Detect duplicate across different positions
- Handle edge cases

### Cas de test

#### Tests data-driven des emails avec variables dynamiques
**Steps:**
  1. Login as Talent Manager
  1. Navigate to Candidate Applications
  1. Enter a (avec différentes variantes)
  1. Click 'Submit'
  1. Verify system alerts for duplicate email
**Résultat attendu:** Tous les emails sont générés correctement avec les bonnes variables dynamiques et délais

#### Edge Case - Invalid input
**Steps:**
  1. Login as Talent Manager
  1. Navigate to Candidate Applications
  1. Enter a candidate application with an invalid email (e.g., missing '@')
  1. Click 'Submit'
  1. Verify system does not process the application and displays an error message
**Résultat attendu:** System rejects the application and displays an error message for invalid input

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

---

## US-09

### Critères d'acceptation
- System must log all configuration changes made by the coordinator (F-07)
- System must notify the coordinator when the environment is ready for UAT (F-08)
- System must track the status of tested flows during UAT (F-09)

### Scénarios de test
- Configure environment and verify logging of changes
- Receive notification when environment is ready for UAT
- Track status of tested flows during UAT

### Cas de test

#### Happy Path - Configuration Change Logging
**Steps:**
  1. Login as Recruitment Coordinator
  1. Make a configuration change
  1. Verify the change is logged in the system
**Résultat attendu:** The system logs the configuration change made by the coordinator

#### Edge Case - Invalid Configuration Change
**Steps:**
  1. Login as Recruitment Coordinator
  1. Attempt to make an invalid configuration change
  1. Verify the system does not log the invalid change
**Résultat attendu:** The system does not log invalid configuration changes

#### Happy Path - Notification for UAT Readiness
**Steps:**
  1. Login as Recruitment Coordinator
  1. Complete the setup process
  1. Verify the system sends a notification when the environment is ready for UAT
**Résultat attendu:** The system sends a notification to the coordinator when the environment is ready for UAT

#### Edge Case - Notification for UAT Readiness with Unmet Conditions
**Steps:**
  1. Login as Recruitment Coordinator
  1. Attempt to send a notification before the environment is fully ready
  1. Verify the system does not send a notification
**Résultat attendu:** The system does not send a notification until all conditions for UAT readiness are met

---

## US-10

### Critères d'acceptation
- System must provide training sessions for candidates (F-10)
- System must document the training sessions attended by candidates (F-11)
- System must ensure candidates have access to user guides (F-12)

### Scénarios de test
- Candidate accesses training sessions
- Candidate documents training sessions
- Candidate accesses user guides

### Cas de test

#### Tests de sécurité et contrôle d'accès (regroupés)
**Steps:**
  1. Login to the ATS system as a candidate
  1. Navigate to the 'Training Sessions' section
  1. Click on a training session
  1. Verify that the training session details are displayed
  1. Try to access a training session that is not available
**Résultat attendu:** Le système contrôle correctement les accès et journalise toutes les tentatives

#### Candidate documents training sessions - Edge Case
**Steps:**
  1. Login to the ATS system as a candidate
  1. Navigate to the 'Training Sessions' section
  1. Attempt to document a training session without completing it
  1. Verify that an error message is displayed indicating the session must be completed first
**Résultat attendu:** Candidate sees an error message indicating the training session must be completed before it can be documented.

#### Candidate accesses user guides - Edge Case
**Steps:**
  1. Login to the ATS system as a candidate
  1. Navigate to the 'User Guides' section
  1. Try to access a user guide that is not available
  1. Verify that an error message is displayed indicating the guide is not available
**Résultat attendu:** Candidate sees an error message indicating the user guide is not available.

---

## US-11

### Critères d'acceptation
- System must track the estimated budget for the project (F-13)
- System must log all expenses against the budget (F-14)
- System must generate budget variance reports (F-15)

### Scénarios de test
- Budget Tracking
- Expense Logging
- Budget Variance Reporting

### Cas de test

#### Track Estimated Budget - Happy Path
**Steps:**
  1. Login as HR Manager
  1. Navigate to Project Budget Tracking section
  1. Enter estimated budget amount
  1. Save the estimated budget
**Résultat attendu:** Estimated budget is successfully saved and displayed in the system

#### Tests de validation des données (regroupés)
**Steps:**
  1. Login as HR Manager
  1. Navigate to Project Budget Tracking section
  1. Enter an invalid budget amount (e.g., negative value)
  1. Attempt to save the estimated budget
  1. Navigate to Project Expenses section
**Résultat attendu:** Le système valide correctement toutes les entrées et affiche des messages d'erreur appropriés

#### Generate Budget Variance Report - Edge Case
**Steps:**
  1. Login as HR Manager
  1. Navigate to Budget Variance Reports section
  1. Select a non-existent project
  1. Attempt to generate the budget variance report
**Résultat attendu:** System displays an error message indicating the non-existent project

#### Log Expenses - Happy Path
**Steps:**
  1. Login as HR Manager
  1. Navigate to Project Expenses section
  1. Enter expense details (amount, category, date)
  1. Save the expense
**Résultat attendu:** Expense is successfully logged and displayed in the system

---

## US-12

### Critères d'acceptation
- System must generate signed acceptance reports for the project (F-16)
- System must notify the hiring manager when the reports are ready (F-17)
- System must archive the signed reports for future reference (F-18)

### Scénarios de test
- Happy Path - Hiring Manager receives signed acceptance reports
- Edge Case - Hiring Manager receives reports with invalid signature
- Error Scenario - Hiring Manager does not receive any reports

### Cas de test

#### Tests de performance (regroupés)
**Steps:**
  1. Login as Hiring Manager
  1. Navigate to Project Management section
  1. Select project F-16
  1. Click on Generate Reports
  1. Verify signed (avec différentes variantes)
**Résultat attendu:** Le système répond dans les délais acceptables pour l'ensemble des opérations

#### Notify Hiring Manager when reports are ready
**Steps:**
  1. Login as Hiring Manager
  1. Navigate to Project Management section
  1. Select project F-16
  1. Click on Generate Reports
  1. Observe system notification
  1. Verify notification indicates reports are ready
**Résultat attendu:** System sends a notification to the Hiring Manager indicating that the reports are ready

#### Invalid signature in reports
**Steps:**
  1. Login as Hiring Manager
  1. Navigate to Project Management section
  1. Select project F-16
  1. Click on Generate Reports
  1. Verify system generates reports with invalid signature
  1. Check if system notifies Hiring Manager about invalid signature
**Résultat attendu:** System generates reports with invalid signature and notifies Hiring Manager about the issue

#### No reports generated
**Steps:**
  1. Login as Hiring Manager
  1. Navigate to Project Management section
  1. Select project F-16
  1. Click on Generate Reports
  1. Verify no reports are generated
  1. Check if system notifies Hiring Manager about the issue
**Résultat attendu:** System does not generate any reports and notifies Hiring Manager about the issue

---

## US-13

### Critères d'acceptation
- ≥ 5 configurable steps (e.g., CV → Phone Screen → Tech Interview → Manager Interview → Offer)
- System must comply with F-10
- System must allow for real-time updates

### Scénarios de test
- Configure recruitment process for a software developer role
- Ensure real-time updates are applied
- Verify system compliance with F-10
- Test edge case with fewer than 5 steps

### Cas de test

#### Configure recruitment process for a software developer role
**Steps:**
  1. Log in as Recruiter
  1. Navigate to Job Type Settings
  1. Click on 'Add Step'
  1. Enter 'CV Review' as step name
  1. Click 'Save'
  1. Repeat for 'Phone Screen', 'Tech Interview', 'Manager Interview', and 'Offer'
  1. Verify steps are added in correct order
  1. Click on 'Save' to confirm changes
**Résultat attendu:** 5 steps are successfully added and displayed in the correct order

#### Ensure real-time updates are applied
**Steps:**
  1. Log in as Recruiter
  1. Navigate to Job Type Settings
  1. Add a new step named 'Initial Assessment'
  1. Verify the new step is immediately visible in the list
  1. Update the step name to 'Technical Assessment'
  1. Verify the step name is updated in real-time
**Résultat attendu:** New step is added and updated in real-time

#### Verify system compliance with F-10
**Steps:**
  1. Log in as Recruiter
  1. Navigate to Compliance Settings
  1. Select 'F-10' compliance level
  1. Click 'Apply'
  1. Verify all steps are compliant with F-10
  1. Check for any warnings or errors
**Résultat attendu:** All steps are compliant with F-10 and no warnings or errors are displayed

#### Test edge case with fewer than 5 steps
**Steps:**
  1. Log in as Recruiter
  1. Navigate to Job Type Settings
  1. Add only 4 steps: 'CV Review', 'Phone Screen', 'Tech Interview', and 'Manager Interview'
  1. Verify the system allows fewer than 5 steps
  1. Try to add a 5th step and verify the system prevents it
**Résultat attendu:** System allows only 4 steps and prevents adding a 5th step

---

## US-14

### Critères d'acceptation
- Complete history, non-modifiable
- System must comply with F-12
- System must ensure comments are non-editable

### Scénarios de test
- Happy Path: Adding and viewing comments and evaluations
- Edge Case: Attempting to edit non-editable comments
- Error Scenario: Attempting to add comments without login
- Performance Scenario: Adding and viewing comments under high load

### Cas de test

#### Happy Path: Adding and viewing comments and evaluations
**Steps:**
  1. Login as Talent Acquisition Specialist
  1. Navigate to candidate profile
  1. Click on 'Add Comment' button
  1. Enter a comment and select the step
  1. Click 'Save' button
  1. Verify that the comment is added to the history
  1. Click on the comment to view it
  1. Verify that the comment is displayed correctly
**Résultat attendu:** Comment is successfully added and displayed in the history, non-editable

#### Edge Case: Attempting to edit non-editable comments
**Steps:**
  1. Login as Talent Acquisition Specialist
  1. Navigate to candidate profile
  1. Click on a comment in the history
  1. Attempt to edit the comment
  1. Verify that the comment cannot be edited
**Résultat attendu:** Attempt to edit the comment fails and the comment remains non-editable

#### Error Scenario: Attempting to add comments without login
**Steps:**
  1. Navigate to candidate profile
  1. Click on 'Add Comment' button
  1. Enter a comment and select the step
  1. Click 'Save' button
  1. Verify that the system redirects to the login page
**Résultat attendu:** System redirects to the login page when attempting to add comments without login

#### Performance Scenario: Adding and viewing comments under high load
**Steps:**
  1. Simulate high load by multiple users adding and viewing comments simultaneously
  1. Login as Talent Acquisition Specialist
  1. Navigate to candidate profile
  1. Click on 'Add Comment' button
  1. Enter a comment and select the step
  1. Click 'Save' button
  1. Verify that the comment is added to the history
  1. Click on the comment to view it
  1. Verify that the comment is displayed correctly
**Résultat attendu:** System handles high load without crashing and comments are added and viewed correctly

---

## US-15

### Critères d'acceptation
- The system must support dynamic variables such as first name, position, and delay in emails.
- The system must comply with F-14 standards.
- The system must allow for dynamic content insertion.
- The system must be able to send emails at specified intervals.

### Scénarios de test
- Customize email with dynamic variables
- Compliance with F-14 standards
- Dynamic content insertion
- Email sending at specified intervals

### Cas de test

#### Happy Path - Customize email with dynamic variables
**Steps:**
  1. Login to the system as an IT Manager
  1. Navigate to the email customization section
  1. Enter the first name variable and save
  1. Enter the position variable and save
  1. Enter the delay variable and save
  1. Verify that the dynamic variables are saved correctly
**Résultat attendu:** The system displays the saved dynamic variables.

#### Edge Case - Dynamic content insertion
**Steps:**
  1. Login to the system as an IT Manager
  1. Navigate to the email customization section
  1. Insert a dynamic content placeholder (e.g., {{content}}) and save
  1. Verify that the system allows for dynamic content insertion
  1. Check that the placeholder is correctly saved
**Résultat attendu:** The system allows for dynamic content insertion and saves the placeholder correctly.

#### Tests data-driven des emails avec variables dynamiques
**Steps:**
  1. Login to the system as an IT Manager
  1. Navigate to (avec différentes variantes)
  1. Enter the (avec différentes variantes)
  1. Enter an invalid delay variable (e.g., 'abc') and save
  1. Verify that the system displays an error message
**Résultat attendu:** Tous les emails sont générés correctement avec les bonnes variables dynamiques et délais

#### Happy Path - Compliance with F-14 standards
**Steps:**
  1. Login to the system as an IT Manager
  1. Navigate to the email settings section
  1. Verify that the system settings comply with F-14 standards
  1. Check the email content for compliance with F-14 standards
**Résultat attendu:** The system settings and email content comply with F-14 standards.

---

## US-16

### Critères d'acceptation
- Per-user configuration
- System must comply with F-17
- System must allow for customizable notification settings

### Scénarios de test
- Configure push notifications for a user
- Configure email notifications for a user
- Configure both push and email notifications for a user
- Configure and test edge cases for notification settings

### Cas de test

#### Tests data-driven des emails avec variables dynamiques
**Steps:**
  1. Login as a GDPR Officer
  1. Navigate to the notification settings page
  1. Click on (avec différentes variantes)
  1. Select the (avec différentes variantes)
  1. Save the configuration
**Résultat attendu:** Tous les emails sont générés correctement avec les bonnes variables dynamiques et délais

#### Configure and test edge cases for notification settings
**Steps:**
  1. Login as a GDPR Officer
  1. Navigate to the notification settings page
  1. Click on the push notifications tab
  1. Select an invalid event (non-existent event)
  1. Save the configuration
  1. Verify that the system displays an error message
  1. Click on the email notifications tab
  1. Enter invalid email addresses (e.g., missing @ symbol)
  1. Select an invalid event (non-existent event)
  1. Save the configuration
  1. Verify that the system displays an error message
**Résultat attendu:** The system should display appropriate error messages for invalid events and email addresses.

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

---

## US-17

### Critères d'acceptation
- Bi-directional sync, timezone management
- System must comply with F-15
- System must allow for calendar integration

### Scénarios de test
- Bi-directional sync and timezone management
- Calendar integration compliance
- User authentication and authorization
- Edge cases for calendar integration

### Cas de test

#### Happy Path - Bi-directional Sync and Timezone Management
**Steps:**
  1. Login as HR Business Partner
  1. Create a new interview event in the integrated calendar
  1. Verify the event is created in both the HR system and the calendar
  1. Change the timezone of the HR system
  1. Verify the event time is updated in the calendar
  1. Change the event time in the calendar
  1. Verify the event time is updated in the HR system
**Résultat attendu:** The event is created and updated bi-directionally between the HR system and the calendar, and the timezone is managed correctly.

#### Happy Path - Calendar Integration Compliance
**Steps:**
  1. Login as HR Business Partner
  1. Create a new interview event in the HR system
  1. Verify the event is created in the integrated calendar
  1. Check if the event complies with F-15 standards
  1. Update the event in the HR system
  1. Verify the update is reflected in the calendar
  1. Delete the event in the HR system
  1. Verify the event is deleted from the calendar
**Résultat attendu:** The event is created, updated, and deleted in compliance with F-15 standards.

#### Edge Case - User Authentication and Authorization
**Steps:**
  1. Login as an unauthorized user
  1. Attempt to create a new interview event in the integrated calendar
  1. Verify the system denies access
  1. Login as HR Business Partner
  1. Create a new interview event in the integrated calendar
  1. Verify the event is created in the HR system
  1. Login as a different HR Business Partner with different permissions
  1. Attempt to create a new interview event in the integrated calendar
  1. Verify the system allows access only to authorized users
**Résultat attendu:** Unauthorized users are denied access, and only authorized users can create, update, and delete events.

#### Edge Case - Invalid Calendar Data
**Steps:**
  1. Login as HR Business Partner
  1. Attempt to create an interview event with invalid data (e.g., missing date, incorrect format)
  1. Verify the system rejects the event
  1. Attempt to create an interview event with a date in the past
  1. Verify the system rejects the event
  1. Attempt to create an interview event with a date that is too far in the future
  1. Verify the system rejects the event
**Résultat attendu:** The system rejects events with invalid or inappropriate data.

---

## US-18

### Critères d'acceptation
- System must allow for at least 5 steps to be configured per job type (F-10)
- Steps must include options for CV review, phone screen, technical interview, manager interview, and offer (F-10)
- Configured steps must be saved and applied consistently across all job postings (F-10)

### Scénarios de test
- Configure job-specific recruitment steps
- Ensure minimum 5 steps are allowed per job type
- Verify saved and applied steps consistency

### Cas de test

#### Tests regroupés (Happy Path + Edge Cases)
**Steps:**
  1. Login as Talent Manager
  1. Navigate to Job Configuration
  1. Select job type
  1. Click 'Add Step'
  1. Enter step name 'CV Review'
**Résultat attendu:** Tous les cas de test regroupés couvrent les scénarios Happy Path et Edge Cases avec succès

#### Verify saved and applied steps consistency
**Steps:**
  1. Login as Talent Manager
  1. Navigate to Job Configuration
  1. Select job type
  1. Verify all 5 steps are listed
  1. Click 'Edit'
  1. Verify step 'CV Review' is selected
  1. Click 'Save'
  1. Navigate to another job type
  1. Verify step 'CV Review' is not selected
  1. Click 'Edit'
  1. Verify step 'CV Review' is not selected
  1. Click 'Save'
  1. Navigate back to original job type
  1. Verify step 'CV Review' is selected
**Résultat attendu:** Configured steps are saved and applied consistently across all job postings

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

---

## US-19

### Critères d'acceptation
- System must use AES-256 encryption for all candidate attachments (F-09)
- Access to candidate attachments must be restricted to authorized personnel only (F-09)
- Encryption and access controls must be enforced at all times (F-09)

### Scénarios de test
- Encryption of candidate attachments
- Access control for candidate attachments
- Edge cases for encryption and access control

### Cas de test

#### Happy Path: Encryption of candidate attachments
**Steps:**
  1. Login as Recruitment Coordinator
  1. Upload a candidate attachment
  1. Verify that the system prompts for encryption
  1. Select AES-256 encryption
  1. Submit the attachment
  1. Check the database to confirm AES-256 encryption is applied
**Résultat attendu:** Candidate attachment is encrypted using AES-256 and stored in the database

#### Edge Case: Upload an attachment without encryption
**Steps:**
  1. Login as Recruitment Coordinator
  1. Upload a candidate attachment
  1. Verify that the system prompts for encryption
  1. Do not select any encryption
  1. Submit the attachment
  1. Check the database to confirm the attachment is not encrypted
**Résultat attendu:** System should prevent submission of unencrypted attachments and display an error message

#### Edge Case: Unauthorized access to candidate attachments
**Steps:**
  1. Login as a non-authorized user
  1. Navigate to the candidate attachments section
  1. Verify that the system denies access
  1. Attempt to download a candidate attachment
  1. Check the system logs to confirm access was denied
**Résultat attendu:** System should deny access to candidate attachments and display an error message

---

## US-20

### Critères d'acceptation
- System must provide an intuitive interface for moving candidates between steps (F-11)
- Candidate movement must be reflected in real-time across all relevant screens (F-11)
- Real-time updates must be visible to all team members with access to the candidate's profile (F-11)

### Scénarios de test
- Happy Path: Moving a candidate between recruitment steps using the drag-and-drop interface
- Edge Case: Attempting to move a candidate to a non-existent step
- Error Case: Attempting to move a candidate with insufficient permissions

### Cas de test

#### Tests regroupés (Happy Path + Edge Cases)
**Steps:**
  1. Login as (avec différentes variantes)
  1. Navigate to the candidate's profile
  1. Locate the candidate in the list of candidates
  1. Click and (avec différentes variantes)
  1. Drag the candidate to the desired recruitment step
**Résultat attendu:** Tous les cas de test regroupés couvrent les scénarios Happy Path et Edge Cases avec succès

#### Test de performance - Temps de réponse
**Steps:**
  1. Exécuter le scénario principal
  1. Mesurer le temps de réponse
  1. Vérifier que le temps est acceptable
**Résultat attendu:** Le système répond dans les délais spécifiés

#### Test d'erreur - Données invalides
**Steps:**
  1. Soumettre des données invalides
  1. Vérifier la validation
  1. Confirmer l'affichage du message d'erreur
**Résultat attendu:** Le système rejette les données invalides avec un message approprié

---
