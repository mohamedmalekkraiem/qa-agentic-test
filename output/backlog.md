# Product Backlog

## [MEDIUM] Add customizable job posting templates
- **User Story:** US-01
- **Epic:** User Authentication
- **Feature:** Job Posting Templates
- **GitHub Issue:** #2318

System must provide ≥ 5 templates. System must have dynamic fields. System must comply with F-01.

## [MEDIUM] Automate job posting to 4 channels
- **User Story:** US-02
- **Epic:** User Authentication
- **Feature:** Job Posting Automation
- **GitHub Issue:** #2320

System must support 1-click posting on ≥ 4 channels. System must automatically post to LinkedIn, Indeed, Welcome to the Jungle, and careers website. System must comply with F-02.

## [MEDIUM] Generate unique application URL per job posting
- **User Story:** US-03
- **Epic:** User Authentication
- **Feature:** Unique Application URL Generation
- **GitHub Issue:** #2322

System must generate a dedicated application URL per job posting. System must track the source of applications. System must comply with F-03.

## [MEDIUM] Moderate job postings before publication
- **User Story:** US-04
- **Epic:** User Authentication
- **Feature:** Job Posting Moderation
- **GitHub Issue:** #2324

System must have an HR + Manager validation workflow
System must require moderation before job posting publication
System must comply with F-04

## [HIGH] Automatically parse candidate CVs
- **User Story:** US-05
- **Epic:** Payment Integration
- **Feature:** CV Parsing
- **GitHub Issue:** #2326

System must recognize ≥ 90% of standard CVs
- System must support parsing of PDF, Word, and LinkedIn CVs
- System must comply with F-05

## [MEDIUM] Store structured candidate CV data
- **User Story:** US-06
- **Epic:** Payment Integration
- **Feature:** CV Parsing
- **GitHub Issue:** #2327

System must store candidate CV data in a structured database. System must support full-text search by skills, experience, and location. System must comply with F-06.

## [MEDIUM] Implement candidate scoring algorithm
- **User Story:** US-07
- **Epic:** Payment Integration
- **Feature:** Candidate Scoring
- **GitHub Issue:** #2329

System must use a transparent algorithm to score candidates.
System must allow customizable scoring criteria.
System must comply with F-07.

## [MEDIUM] Detect duplicate candidate applications
- **User Story:** US-08
- **Epic:** Payment Integration
- **Feature:** Duplicate Application Detection
- **GitHub Issue:** #2331

System must alert if email or first+last name is identical. System must detect applications from the same candidate for different positions. System must comply with F-08.

## [MEDIUM] Implement US-09
- **User Story:** US-09
- **Epic:** Notification System
- **Feature:** Notification System Feature
- **GitHub Issue:** #2333

**US-09** - Recruitment Coordinator
  As a Recruitment Coordinator, I want to to ensure the configuration environment is set up correctly so that to facilitate smooth user acceptance testing
  Acceptance Criteria:
    - System must log all configuration changes made by the coordinator (F-07)
    - System must notify the coordinator when the environment is ready for UAT (F-08)
    - System must track the status of tested flows during UAT (F-09)

## [MEDIUM] Implement US-10
- **User Story:** US-10
- **Epic:** Notification System
- **Feature:** Notification System Feature
- **GitHub Issue:** #2334

**US-10** - Candidate
  As a Candidate, I want to to receive training on the new ATS system so that to be able to use the system effectively
  Acceptance Criteria:
    - System must provide training sessions for candidates (F-10)
    - System must document the training sessions attended by candidates (F-11)
    - System must ensure candidates have access to user guides (F-12)

## [MEDIUM] Implement budget tracking and reporting
- **User Story:** US-11
- **Epic:** Notification System
- **Feature:** Budget Management
- **GitHub Issue:** #2336

System must track the estimated budget for the project (F-13). System must log all expenses against the budget (F-14). System must generate budget variance reports (F-15).

## [MEDIUM] Generate and notify on signed acceptance reports
- **User Story:** US-12
- **Epic:** Notification System
- **Feature:** Signed Acceptance Reports
- **GitHub Issue:** #2338

System must generate signed acceptance reports for the project (F-16). System must notify the hiring manager when the reports are ready (F-17). System must archive the signed reports for future reference (F-18).

## [MEDIUM] Configure steps for job types
- **User Story:** US-13
- **Epic:** User Profile Management
- **Feature:** Recruitment Process Customization
- **GitHub Issue:** #2340

As a Recruiter, I want to configure multiple steps in the recruitment process so that I can tailor the hiring process to different job roles.

Acceptance Criteria:
- ≥ 5 configurable steps (e.g., CV → Phone Screen → Tech Interview → Manager Interview → Offer)
- System must comply with F-10
- System must allow for real-time updates

## [MEDIUM] Add comments and evaluations per step
- **User Story:** US-14
- **Epic:** User Profile Management
- **Feature:** Comments and Evaluations
- **GitHub Issue:** #2342

As a Talent Acquisition Specialist, I want to be able to leave comments and evaluations at each step of the recruitment process so that I can document the candidate's progress and provide feedback.

Acceptance Criteria:
- Complete history, non-modifiable
- System must comply with F-12
- System must ensure comments are non-editable

## [MEDIUM] Customize automated emails
- **User Story:** US-15
- **Epic:** User Profile Management
- **Feature:** Automated Email Customization
- **GitHub Issue:** #2344

Dynamic variables (first name, position, delay) must be supported. System must comply with F-14. Dynamic content insertion must be allowed.

**Acceptance Criteria**:
1. System supports dynamic variables such as first name, position, and delay.
2. System complies with F-14 regulations.
3. System allows for dynamic content insertion.

## [HIGH] Configure push and email notifications (high)
- **User Story:** US-16
- **Epic:** User Profile Management
- **Feature:** Notification Configuration
- **GitHub Issue:** #2346

Per-user configuration
- System must comply with F-17
- System must allow for customizable notification settings

## [MEDIUM] Integrate Calendar for Interview Scheduling
- **User Story:** US-17
- **Epic:** Analytics Dashboard
- **Feature:** Interview Scheduling
- **GitHub Issue:** #2348

Bi-directional sync, timezone management. System must comply with F-15. System must allow for calendar integration.

## [MEDIUM] Configure 5 job-specific recruitment steps
- **User Story:** US-18
- **Epic:** Analytics Dashboard
- **Feature:** Job Type Configurations
- **GitHub Issue:** #2350

System must allow for at least 5 steps to be configured per job type (F-10). Steps must include options for CV review, phone screen, technical interview, manager interview, and offer (F-10). Configured steps must be saved and applied consistently across all job postings (F-10).

## [HIGH] Encrypt and restrict access to candidate attachments
- **User Story:** US-19
- **Epic:** Analytics Dashboard
- **Feature:** Candidate Attachment Security
- **GitHub Issue:** #2352

Ensure that all candidate attachments are encrypted and access-controlled to protect sensitive information during the hiring process.

Acceptance Criteria:
- System must use AES-256 encryption for all candidate attachments (F-09)
- Access to candidate attachments must be restricted to authorized personnel only (F-09)
- Encryption and access controls must be enforced at all times (F-09)

## [HIGH] Implement real-time candidate movement tracking
- **User Story:** US-20
- **Epic:** Analytics Dashboard
- **Feature:** Candidate Movement Tracking
- **GitHub Issue:** #2354

Implement an intuitive drag-and-drop interface for moving candidates between recruitment steps. Ensure real-time updates are visible across all relevant screens and to all team members with access to the candidate's profile.

Acceptance Criteria:
- System must provide an intuitive interface for moving candidates between steps (F-11)
- Candidate movement must be reflected in real-time across all relevant screens (F-11)
- Real-time updates must be visible to all team members with access to the candidate's profile (F-11)
