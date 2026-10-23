# SkillBridge AI: An Intelligent Campus Placement Readiness and Skill Gap Analysis System

[![Python Version](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![ORM](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20MySQL%20Ready-green.svg)](https://sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-22%20Passed%20(100%25)-brightgreen.svg)]()

> A full-stack academic and portfolio web application built for Computer Science & Engineering students to evaluate technical competencies, diagnose skill deficits against real campus recruitment benchmarks, and receive actionable AI-powered learning plans.

---

## 1. Project Overview

Graduating engineering students frequently struggle to bridge the gap between academic course syllabi and corporate placement hiring standards. **SkillBridge AI** provides an objective, data-driven diagnostic solution that:

1. **Assesses Technical Competencies**: Delivers timed, diagnostic evaluations covering Web Development (HTML/CSS, JS/DOM, Backend APIs), Core CS (Data Structures, Algorithms, DBMS, OS, Networks), and Aptitude.
2. **Calculates Transparent Skill Gaps**: Uses a mathematical deficit formula comparing student performance directly against company hiring tiers:
   $$\text{Skill Gap} = \max(0, \text{Required Role Benchmark} - \text{Measured Student Proficiency})$$
3. **Generates Dual-Mode AI Learning Plans**: Connects to the **Google Gemini API** when configured with an API key, and seamlessly defaults to an offline **Deterministic Placement Rules Engine** when offline or without an API key.
4. **Tracks Learning Progression**: Enables students to convert suggestions into interactive checklists with real-time status progression (*Not Started* $\rightarrow$ *In Progress* $\rightarrow$ *Completed*) persisted via the Fetch API.

---

## 2. Mandatory Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5 (Semantic), CSS3 (Custom Variables, Flexbox, Grid), Vanilla JavaScript (ES6+), Fetch API, Chart.js (v4.4.1) |
| **Backend** | Python 3, Flask 3.1, Flask Blueprints (Modular Architecture), Werkzeug Security Utilities |
| **Database** | SQLite (Default for zero-setup local dev/vivas), SQLAlchemy 2.0 ORM (Fully MySQL-compatible) |
| **AI Integration**| Dual-Mode: Google Gemini API adapter + Deterministic Fallback Rules Engine |
| **Testing** | Pytest (22 automated unit, integration, and security tests) |

---

## 3. Official Color Palette

SkillBridge AI strictly adheres to the official design tokens:
- **Primary Navy** (`#0F2D58`): Headers, sidebars, branding, and footers.
- **Electric Indigo** (`#6366F1`): Primary buttons, interactive elements, charts, and progress fills.
- **Soft Lavender** (`#A78BFA`): Highlights, secondary accents, badges, and illustrations.
- **Cloud White** (`#F8FAFC`): Page backgrounds, clean cards, and input surfaces.
- **Slate Dark** (`#1E293B`): Body text, high-contrast typography.
- **Success Green** (`#10B981`): Scores, completed roadmap tasks, and positive feedback.

---

## 4. Required 11 Screens Implementation Map

| Screen # | Screen Name | Template / Route | Key Features & Implementation |
| :---: | :--- | :--- | :--- |
| **Screen 1** | Landing Page | [`templates/landing.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/landing.html) (`/`) | Hero headline: *"Your Skills. Our AI. A Stronger Future."*, diagnostic visualizer card, 4 feature highlights (*Assess Your Skills, Find Skill Gaps, Get AI Suggestions, Achieve Your Goals*), placement readiness formula, and contact form. |
| **Screen 2** | Sign Up Page | [`templates/auth/signup.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/auth/signup.html) (`/auth/signup`) | Student/Admin role selector, password visibility toggle, institutional secret token verification for Admin accounts, duplicate email/USN prevention, and PBKDF2:SHA256 password hashing. |
| **Screen 3** | Login Page | [`templates/auth/login.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/auth/login.html) (`/auth/login`) | Multi-identifier login (supports both email and USN register number), password toggle, 7-day remember-me option, forgot password guidance, and quick demo credentials. |
| **Screen 4** | Student Dashboard | [`templates/dashboard/index.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/dashboard/index.html) (`/dashboard/`) | Personalized greeting, 4 database-backed metric cards (*Assessments Taken, Skill Gaps Identified, Improvement Tasks, Job Roles Available*), 4-step placement journey roadmap, and recent activity table. |
| **Screen 5** | Take Assessment | [`templates/assessment/take.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/assessment/take.html) (`/assessment/take/<id>`) | Interactive single-page assessment engine, dynamic question counter, progress bar, radio option cards, previous/next navigation, server-side scoring (correct answers never exposed to DOM), and duplicate submission prevention. |
| **Screen 6** | Results & Skill Gap Analysis | [`templates/assessment/results.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/assessment/results.html) (`/assessment/results/<id>`) | Big score card, proficiency levels (1.0–5.0), Chart.js comparison bar & radar charts, prioritized skill deficits, verified strengths, and *"Generate AI Improvement Plan"* CTA. |
| **Screen 7** | Job Roles & Skill Comparison | [`templates/roles/index.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/roles/index.html) (`/roles/`) | Searchable role catalogue, category filter pills (*Software Dev, Frontend, Web Dev, Data Analyst*), role cards with salaries and demand badges, and individual benchmark comparison view ([`roles/detail.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/roles/detail.html)). |
| **Screen 8** | Personalized Improvement Plan | [`templates/improvement/index.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/improvement/index.html) (`/improvement/`) | AI-generated learning milestones, priority badges, current vs target levels, estimated durations, interactive status checklist synced via Fetch API, and placement advisory disclaimer. |
| **Screen 9** | Assessment History | [`templates/history/index.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/history/index.html) (`/history/`) | Database-backed chronological history table, score percentage badges, status indicators, direct links to individual results, and user data privacy isolation. |
| **Screen 10** | Profile and Settings | [`templates/profile/index.html`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/templates/profile/index.html) (`/profile/`) | Student profile with USN, degree, and graduation year, editable profile details, password change form with current password verification, and PBKDF2 hash updates. |
| **Screen 11** | Responsive Mobile View | All Templates & [`static/css/style.css`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/static/css/style.css) | Mobile hamburger navigation, responsive sidebar drawer toggle (`#sidebar-toggle-btn`), touch targets >= 44px, fluid grid collapse, and zero horizontal overflow. |

---

## 5. Database Architecture (10 Relational Models)

```
       +--------------------+          +---------------------------+
       |       users        |          |         job_roles         |
       +--------------------+          +---------------------------+
       | id (PK)            |          | id (PK)                   |
       | email (Unique)     |          | title, category, packages |
       | register_number    |          +---------------------------+
       | password_hash      |                       |
       +--------------------+                       | 1:N
                 | 1:N                              v
                 |                     +---------------------------+
                 v                     |  role_skill_requirements  |
       +--------------------+          +---------------------------+
       | assessment_attempts|<---------| role_id (FK), skill_id(FK)|
       +--------------------+          | required_level, weight    |
       | id (PK), user_id   |          +---------------------------+
       | total_score, max   |                       ^
       +--------------------+                       |
                 | 1:N                              | 1:N
                 v                                  |
       +--------------------+          +---------------------------+
       | assessment_results |--------->|          skills           |
       +--------------------+          +---------------------------+
       | attempt_id,skill_id|          | id (PK), name, category   |
       | proficiency, gap   |          +---------------------------+
       +--------------------+                       ^
                                                    |
       +--------------------+          +---------------------------+
       | improvement_plans  |--------->|  improvement_plan_tasks   |
       +--------------------+   1:N    +---------------------------+
       | id (PK), user_id   |          | plan_id (FK), skill_id(FK)|
       | title, generated_by|          | title, priority, status   |
       +--------------------+          +---------------------------+
```

---

## 6. Windows PowerShell Setup & Execution Guide

### Prerequisites
- Python 3.10+ (Verified on Python 3.14.0)
- Windows PowerShell

### Step 1: Clone or Navigate to Directory
```powershell
cd "c:\Users\admin\OneDrive\Desktop\Project SkiilBridge-AI"
```

### Step 2: (Optional) Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Optional)* Add your Google Gemini API key inside `.env` under `GEMINI_API_KEY`. If left empty, the application automatically uses the built-in deterministic rules fallback.

### Step 5: Initialize & Seed Database
```powershell
python seed.py
```
This populates:
- 8 Core Technical & Aptitude Skills
- 4 Campus Recruitment Job Roles with benchmarks
- 20 Original Placement Questions
- Demo Student Account: `student@college.edu` / `student123` (USN: `2026CSE042`)
- Demo Admin Account: `admin@college.edu` / `admin123` (USN: `ADMIN001`)

### Step 6: Start Flask Server
```powershell
python app.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000`**

---

## 7. Running Automated Test Suite

Execute all 22 tests with verbose reporting:
```powershell
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- `tests/test_landing.py`: Page rendering, branding, 4 feature highlights, and 404 handler.
- `tests/test_auth.py`: Registration, PBKDF2 password hashing, duplicate account rejection, admin token security, and dual-identifier login.
- `tests/test_dashboard_roles.py`: Unauthorized redirection, dashboard metric computations, and role benchmark comparisons.
- `tests/test_assessment.py`: Assessment initiation, secure question delivery (no answer leaks), and server-side scoring.
- `tests/test_results.py`: Results score card, Chart.js elements, skill gap calculations, and student data isolation.
- `tests/test_improvement.py`: Learning plan synthesis, deterministic fallback execution, and Fetch API task status persistence.
- `tests/test_history_profile.py`: History isolation, profile edits, and password change verification.

---

## 8. AI Service & Deterministic Fallback Architecture

SkillBridge AI features a decoupled recommendation adapter in [`services/ai_service.py`](file:///c:/Users/admin/OneDrive/Desktop/Project%20SkiilBridge-AI/services/ai_service.py):
1. **Google Gemini LLM Mode**: When `GEMINI_API_KEY` is present in `.env`, the system constructs an engineering viva prompt and invokes the Gemini API via secure server-side POST requests.
2. **Deterministic Fallback Engine**: If the API key is empty, network connection drops, or API quota is exceeded, the fallback engine calculates gap priorities and outputs tailored milestones, LeetCode/algorithm recommendations, and SQL/web development deliverables.
3. **Transparency**: The UI clearly displays which engine generated the roadmap (*"External AI Engine (Gemini)"* vs. *"Deterministic Rules Engine"*).

---

## 9. Future Enhancements

- Integration with GitHub API to verify student code repository commits against roadmap milestones.
- Real-time peer percentile benchmarking across batch years.
- Multi-college administrator dashboard with batch-wide skill gap analytics exports (CSV / PDF).
- MySQL production containerization via Docker.

