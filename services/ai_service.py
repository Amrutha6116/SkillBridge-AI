"""
SkillBridge AI - Recommendation Service
Provides an intelligent dual-mode engine:
1. External AI Integration: Queries external LLM API (e.g. Google Gemini) when GEMINI_API_KEY is configured.
2. Deterministic Recommendation Engine: A rule-based expert system that analyzes exact measured
   deficits (required - actual) and generates customized, structured learning tasks, milestones,
   and project suggestions with zero external dependencies.
"""

import os
import json
import urllib.request
import urllib.error


class AIService:
    """Intelligent recommendation service for campus placement readiness."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY', '').strip()

    def is_ai_connected(self):
        """Check if a non-empty external API key is supplied."""
        return bool(self.api_key and len(self.api_key) > 8)

    def generate_plan(self, student_name, target_role_title, skill_gaps, strengths):
        """
        Generate a structured learning plan.
        
        Parameters:
            student_name: str
            target_role_title: str
            skill_gaps: list of dicts with keys: 'skill_name', 'current_level', 'required_level', 'gap'
            strengths: list of dicts with keys: 'skill_name', 'current_level'
            
        Returns:
            dict containing:
                'title': str
                'summary': str
                'generated_by': 'ai' or 'fallback'
                'milestones': list of milestone dicts
                'tasks': list of task dicts
        """
        # Attempt external AI API if configured
        if self.is_ai_connected():
            try:
                ai_result = self._call_gemini_api(student_name, target_role_title, skill_gaps, strengths)
                if ai_result:
                    return ai_result
            except Exception as e:
                # Log error safely without exposing keys and seamlessly use deterministic fallback
                print(f"[AIService Warning] External AI API failed: {e}. Activating deterministic fallback.")

        # Deterministic Expert Rule Engine Fallback
        return self._generate_deterministic_fallback(student_name, target_role_title, skill_gaps, strengths)

    def _call_gemini_api(self, student_name, target_role_title, skill_gaps, strengths):
        """Invoke Google Gemini API securely with strict prompt validation."""
        # Clean inputs
        gaps_summary = ", ".join([f"{g['skill_name']} (Current: L{g['current_level']}, Target: L{g['required_level']}, Deficit: -{g['gap']})" for g in skill_gaps])
        strengths_summary = ", ".join([f"{s['skill_name']} (L{s['current_level']})" for s in strengths]) if strengths else "None recorded"

        prompt = f"""
You are an expert Computer Science Campus Placement Advisor for undergraduate engineering students.
Generate a structured placement improvement plan for {student_name} targeting the role '{target_role_title}'.

Student Deficits/Gaps: {gaps_summary}
Student Strengths: {strengths_summary}

Respond ONLY with valid, raw JSON (no markdown fences, no explanatory preambles) in this exact format:
{{
  "title": "{target_role_title} Placement Readiness Roadmap",
  "summary": "Brief 2-sentence encouraging summary of the plan.",
  "tasks": [
    {{
      "skill_name": "Exact skill name from gaps list",
      "title": "Clear actionable task title",
      "description": "Specific exercise, practice problem, or implementation detail",
      "priority": "High" or "Medium" or "Low",
      "current_level": float,
      "target_level": float,
      "estimated_duration": "1 week"
    }}
  ]
}}
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                raw_body = response.read().decode('utf-8')
                res_data = json.loads(raw_body)
                content_text = res_data['candidates'][0]['content']['parts'][0]['text']
                clean_json = content_text.strip()
                if clean_json.startswith('```json'):
                    clean_json = clean_json[7:]
                if clean_json.endswith('```'):
                    clean_json = clean_json[:-3]
                
                parsed = json.loads(clean_json.strip())
                parsed['generated_by'] = 'ai'
                return parsed

        return None

    def _generate_deterministic_fallback(self, student_name, target_role_title, skill_gaps, strengths):
        """
        Comprehensive rule-based expert recommendation engine.
        Maps deficits to curated technical practice activities, milestones, and project goals.
        """
        CURATED_RECOMMENDATIONS = {
            "Data Structures & Algorithms": {
                "high_gap": {
                    "title": "Master Core Linear & Tree Data Structures",
                    "desc": "Solve 2 LeetCode/GeeksforGeeks problems daily on Binary Trees, Hash Tables, and Two-Pointer sliding windows. Practice time and space complexity derivation.",
                    "duration": "2–3 weeks"
                },
                "low_gap": {
                    "title": "Algorithmic Complexity & Graph Optimization",
                    "desc": "Focus on BFS, DFS, Dijkstra's algorithm, and dynamic programming memoization. Complete 10 standard interview patterns.",
                    "duration": "1–2 weeks"
                }
            },
            "Database Systems & SQL": {
                "high_gap": {
                    "title": "Relational Schema Normalization & Complex JOINs",
                    "desc": "Practice writing multi-table INNER/LEFT JOINs, subqueries, and aggregate GROUP BY with HAVING. Design a 3NF schema for an e-commerce order workflow.",
                    "duration": "1–2 weeks"
                },
                "low_gap": {
                    "title": "Query Indexing & ACID Transaction Isolation",
                    "desc": "Analyze execution plans with EXPLAIN ANALYZE. Understand B-tree indexing trade-offs and write transactional rollback scripts.",
                    "duration": "1 week"
                }
            },
            "HTML5 & Modern CSS": {
                "high_gap": {
                    "title": "Semantic Layout & CSS Grid Architecture",
                    "desc": "Build a responsive multi-column dashboard using semantic tags (<main>, <aside>, <section>), CSS Grid repeat(auto-fit), and Flexbox without UI frameworks.",
                    "duration": "1 week"
                },
                "low_gap": {
                    "title": "Responsive Accessibility & Cross-Browser Polish",
                    "desc": "Audit contrast ratios, add ARIA attributes, ensure keyboard accessibility (tabindex/focus-visible), and test on mobile viewports.",
                    "duration": "4–5 days"
                }
            },
            "JavaScript & DOM": {
                "high_gap": {
                    "title": "Asynchronous JS & Fetch API Integration",
                    "desc": "Build a data-driven UI that queries REST endpoints, handles Promises, async/await errors, and dynamically updates the DOM without full page reloads.",
                    "duration": "1–2 weeks"
                },
                "low_gap": {
                    "title": "Event Delegation & ES6+ Functional Patterns",
                    "desc": "Implement event bubbling/delegation, closures, array map/filter/reduce, and state management in vanilla JavaScript.",
                    "duration": "1 week"
                }
            },
            "Python & Backend APIs": {
                "high_gap": {
                    "title": "Modular RESTful Backend Architecture",
                    "desc": "Develop a modular Flask application using Blueprints, SQLAlchemy ORM models with foreign key constraints, and Werkzeug PBKDF2 password security.",
                    "duration": "2 weeks"
                },
                "low_gap": {
                    "title": "API Authentication, Sessions & Validation",
                    "desc": "Implement robust server-side input validation, error handling middleware, and role-based access decorators (@login_required, @admin_required).",
                    "duration": "1 week"
                }
            },
            "Operating Systems & Networks": {
                "high_gap": {
                    "title": "Process Synchronization & Memory Management",
                    "desc": "Review critical sections, semaphores vs mutexes, Coffman's deadlock conditions, paging, and virtual memory thrashing.",
                    "duration": "1–2 weeks"
                },
                "low_gap": {
                    "title": "TCP/IP Protocol Stack & HTTP/S Lifecycle",
                    "desc": "Deep dive into the 3-way TCP handshake, DNS resolution process, SSL/TLS encryption handshakes, and REST status codes.",
                    "duration": "1 week"
                }
            },
            "Quantitative Aptitude": {
                "high_gap": {
                    "title": "Foundational Numerical Ability & Formulas",
                    "desc": "Practice speed calculations, percentages, profit & loss, ratios, and time-speed-distance problems with timed 20-minute mock quizzes.",
                    "duration": "1–2 weeks"
                },
                "low_gap": {
                    "title": "Advanced Combinatorics & Data Sufficiency",
                    "desc": "Solve probability distributions, permutation-combination arrangements, and syllogisms commonly asked in Tier-1 online screening rounds.",
                    "duration": "1 week"
                }
            },
            "Data Analysis & Statistics": {
                "high_gap": {
                    "title": "Exploratory Data Analysis with Python Pandas",
                    "desc": "Load real placement CSV datasets, handle missing values, compute summary statistics (mean, median, IQR), and plot distributions.",
                    "duration": "1–2 weeks"
                },
                "low_gap": {
                    "title": "Statistical Hypothesis Testing & Visualization",
                    "desc": "Perform correlation analyses, interpret p-values, and generate communicative visualization dashboards.",
                    "duration": "1 week"
                }
            }
        }

        tasks = []
        if not skill_gaps:
            # If student has 0 gaps, provide advanced mastery tasks
            tasks.append({
                "skill_name": "Data Structures & Algorithms",
                "title": "Advanced Interview Mock Rounds & System Design",
                "description": "Solve LeetCode hard problems on dynamic programming on trees and review basic high-level system design principles.",
                "priority": "Medium",
                "current_level": 4.5,
                "target_level": 5.0,
                "estimated_duration": "2 weeks"
            })
        else:
            for g in skill_gaps:
                name = g["skill_name"]
                gap = g["gap"]
                cur_lvl = g["current_level"]
                req_lvl = g["required_level"]

                # Determine priority
                priority = "High" if gap >= 1.5 else ("Medium" if gap >= 0.8 else "Low")
                gap_tier = "high_gap" if gap >= 1.0 else "low_gap"

                # Look up curated recommendation or build dynamic fallback
                if name in CURATED_RECOMMENDATIONS:
                    rec = CURATED_RECOMMENDATIONS[name][gap_tier]
                    t_title = rec["title"]
                    t_desc = rec["desc"]
                    t_duration = rec["duration"]
                else:
                    t_title = f"Strengthen Competency in {name}"
                    t_desc = f"Review foundational textbooks, complete 5 practice exercises, and build a proof-of-concept demonstrating Level {req_lvl} mastery."
                    t_duration = "1–2 weeks"

                tasks.append({
                    "skill_name": name,
                    "title": t_title,
                    "description": t_desc,
                    "priority": priority,
                    "current_level": cur_lvl,
                    "target_level": req_lvl,
                    "estimated_duration": t_duration
                })

        summary = (
            f"Based on your diagnostic assessment for {target_role_title}, {len(tasks)} targeted learning tasks have been identified. "
            f"Addressing these technical milestones will systematically close your skill gaps and elevate your campus placement readiness."
        )

        return {
            "title": f"{target_role_title} Placement Learning Roadmap",
            "summary": summary,
            "generated_by": "fallback",
            "tasks": tasks
        }

