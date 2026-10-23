"""
SkillBridge AI - Database Seeder Script
Initializes tables and seeds initial skills, job roles, benchmarks, sample questions, and demo accounts.
Run with: python seed.py
"""

from app import create_app
from extensions import db
from models import (
    User, Skill, JobRole, RoleSkillRequirement, AssessmentQuestion,
    AssessmentAttempt, AssessmentResult, ImprovementPlan, ImprovementPlanTask
)


def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping existing tables and recreating schema...")
        db.drop_all()
        db.create_all()

        print("Seeding demo accounts...")
        # Demo Student
        student = User(
            full_name="Alex Vance",
            email="student@college.edu",
            register_number="2026CSE042",
            role="student",
            course="B.E. Computer Science and Engineering",
            college="College of Engineering and Technology",
            graduation_year=2027
        )
        student.set_password("student123")

        # Demo Placement Admin
        admin = User(
            full_name="Dr. K. Placement Officer",
            email="admin@college.edu",
            register_number="ADMIN001",
            role="admin",
            course="Campus Placement & Training Cell",
            college="College of Engineering and Technology",
            graduation_year=2020
        )
        admin.set_password("admin123")

        db.session.add_all([student, admin])
        db.session.commit()

        print("Seeding technical and placement skills...")
        skills_data = [
            # Web Development
            {"name": "HTML5 & Modern CSS", "category": "Web Development", "description": "Semantic markup, CSS Grid, Flexbox, responsive web design principles."},
            {"name": "JavaScript & DOM", "category": "Web Development", "description": "ES6+ syntax, asynchronous programming (Promises/async-await), DOM events, and Fetch API."},
            {"name": "Python & Backend APIs", "category": "Web Development", "description": "Flask/Django backends, RESTful architecture, HTTP methods, authentication & sessions."},
            
            # Core CS
            {"name": "Data Structures & Algorithms", "category": "Core CS", "description": "Arrays, Linked Lists, Trees, Graphs, Sorting, Searching, Big-O algorithmic complexity."},
            {"name": "Database Systems & SQL", "category": "Core CS", "description": "Relational schema design, normalization, ACID transactions, JOINs, indexing, and aggregations."},
            {"name": "Operating Systems & Networks", "category": "Core CS", "description": "Processes, threads, CPU scheduling, virtual memory, TCP/IP stack, DNS, and HTTP/HTTPS."},
            
            # Aptitude & Analytics
            {"name": "Quantitative Aptitude", "category": "Aptitude", "description": "Numerical calculations, percentages, ratios, probability, permutations, and time-work problems."},
            {"name": "Data Analysis & Statistics", "category": "Data & AI", "description": "Data wrangling, summary statistics, probability distributions, pandas, and data visualization."}
        ]

        skills_dict = {}
        for s in skills_data:
            skill = Skill(name=s["name"], category=s["category"], description=s["description"])
            db.session.add(skill)
            db.session.flush()
            skills_dict[s["name"]] = skill

        print("Seeding campus recruitment job roles...")
        roles_data = [
            {
                "title": "Software Developer",
                "category": "Software Developer",
                "description": "Designs, implements, and tests core software systems and algorithmic solutions. Focuses on robust backend services and data structures.",
                "min_experience": "Fresher / Campus Hire",
                "avg_package": "7.5 - 14 LPA",
                "demand_level": "Very High",
                "requirements": [
                    ("Data Structures & Algorithms", 4.5, 1.5),
                    ("Database Systems & SQL", 4.0, 1.2),
                    ("Python & Backend APIs", 3.8, 1.0),
                    ("Operating Systems & Networks", 3.5, 1.0),
                    ("Quantitative Aptitude", 3.5, 0.8)
                ]
            },
            {
                "title": "Frontend Developer",
                "category": "Frontend Developer",
                "description": "Specializes in building responsive, accessible, interactive web interfaces, client-side state handling, and seamless user experiences.",
                "min_experience": "Fresher / Campus Hire",
                "avg_package": "6.0 - 11 LPA",
                "demand_level": "High",
                "requirements": [
                    ("HTML5 & Modern CSS", 4.5, 1.5),
                    ("JavaScript & DOM", 4.5, 1.5),
                    ("Python & Backend APIs", 3.0, 0.8),
                    ("Data Structures & Algorithms", 3.0, 0.9),
                    ("Quantitative Aptitude", 3.0, 0.7)
                ]
            },
            {
                "title": "Full Stack Web Developer",
                "category": "Web Developer",
                "description": "Architects and develops complete end-to-end web applications, encompassing frontend client interfaces, backend servers, and relational databases.",
                "min_experience": "Fresher / Campus Hire",
                "avg_package": "8.0 - 15 LPA",
                "demand_level": "Very High",
                "requirements": [
                    ("JavaScript & DOM", 4.2, 1.3),
                    ("Python & Backend APIs", 4.2, 1.4),
                    ("Database Systems & SQL", 4.0, 1.2),
                    ("HTML5 & Modern CSS", 3.8, 1.0),
                    ("Data Structures & Algorithms", 3.5, 1.0)
                ]
            },
            {
                "title": "Data Analyst",
                "category": "Data Analyst",
                "description": "Collects, processes, and performs statistical analysis of corporate datasets to discover actionable placement and business intelligence.",
                "min_experience": "Fresher / Campus Hire",
                "avg_package": "6.5 - 12 LPA",
                "demand_level": "High",
                "requirements": [
                    ("Database Systems & SQL", 4.5, 1.5),
                    ("Data Analysis & Statistics", 4.5, 1.5),
                    ("Python & Backend APIs", 3.5, 1.0),
                    ("Quantitative Aptitude", 4.0, 1.2),
                    ("Data Structures & Algorithms", 2.5, 0.7)
                ]
            }
        ]

        roles_dict = {}
        for r in roles_data:
            role = JobRole(
                title=r["title"],
                category=r["category"],
                description=r["description"],
                min_experience=r["min_experience"],
                avg_package=r["avg_package"],
                demand_level=r["demand_level"]
            )
            db.session.add(role)
            db.session.flush()
            roles_dict[r["title"]] = role

            for req in r["requirements"]:
                skill_name, req_level, weight = req
                skill_obj = skills_dict[skill_name]
                role_req = RoleSkillRequirement(
                    role_id=role.id,
                    skill_id=skill_obj.id,
                    required_level=req_level,
                    importance_weight=weight
                )
                db.session.add(role_req)

        print("Seeding diagnostic assessment questions...")
        questions_data = [
            # HTML & Modern CSS
            {
                "skill": "HTML5 & Modern CSS",
                "text": "Which semantic HTML5 tag is most appropriate for enclosing self-contained blog posts or syndicated news articles?",
                "a": "<div>", "b": "<article>", "c": "<section>", "d": "<aside>",
                "correct": "B", "diff": "Beginner",
                "exp": "<article> represents a complete, self-contained composition in a document, page, or site intended to be independently distributable."
            },
            {
                "skill": "HTML5 & Modern CSS",
                "text": "In CSS Flexbox, which property aligns items along the cross axis (perpendicular to main axis)?",
                "a": "justify-content", "b": "align-items", "c": "flex-direction", "d": "align-content",
                "correct": "B", "diff": "Beginner",
                "exp": "align-items defines the default behavior for how flex items are laid out along the cross axis on the current line."
            },
            {
                "skill": "HTML5 & Modern CSS",
                "text": "What does CSS Grid property 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))' accomplish?",
                "a": "Forces exactly 4 columns regardless of container width",
                "b": "Creates a responsive grid where columns wrap automatically without media queries",
                "c": "Creates a fixed 250px grid layout with overflow scroll",
                "d": "Disables grid alignment on smaller mobile displays",
                "correct": "B", "diff": "Medium",
                "exp": "auto-fit with minmax enables dynamic column calculation that automatically wraps columns cleanly across viewport changes."
            },

            # JavaScript & DOM
            {
                "skill": "JavaScript & DOM",
                "text": "What is the primary difference between 'let' and 'var' declarations in modern JavaScript?",
                "a": "'let' is function-scoped while 'var' is block-scoped",
                "b": "'let' is block-scoped while 'var' is function-scoped",
                "c": "'let' cannot be reassigned after declaration",
                "d": "'var' causes strict mode syntax errors in ES6+",
                "correct": "B", "diff": "Beginner",
                "exp": "'let' binds variables to the nearest enclosing block scope, avoiding accidental leaking into outer function scopes unlike 'var'."
            },
            {
                "skill": "JavaScript & DOM",
                "text": "What does the JavaScript Fetch API's fetch() function return?",
                "a": "A JSON object immediately",
                "b": "An XMLHttpRequest instance",
                "c": "A Promise that resolves to a Response object",
                "d": "A callback function handle",
                "correct": "C", "diff": "Beginner",
                "exp": "fetch() initiates an asynchronous network request and returns a Promise resolving to the Response representing the response to that request."
            },
            {
                "skill": "JavaScript & DOM",
                "text": "How can you prevent a form submit event from triggering a full page reload in client-side JavaScript?",
                "a": "event.stopPropagation()",
                "b": "event.preventDefault()",
                "c": "event.stopImmediatePropagation()",
                "d": "return false inside HTML form tag",
                "correct": "B", "diff": "Beginner",
                "exp": "event.preventDefault() cancels the default browser action, such as page reloads on HTML form submissions."
            },

            # Python & Backend APIs
            {
                "skill": "Python & Backend APIs",
                "text": "In a RESTful architecture, which HTTP method should be used to completely replace an existing resource?",
                "a": "POST", "b": "PUT", "c": "PATCH", "d": "GET",
                "correct": "B", "diff": "Medium",
                "exp": "PUT is idempotent and replaces the entire target resource with the requested payload, whereas PATCH performs partial modifications."
            },
            {
                "skill": "Python & Backend APIs",
                "text": "In Flask, what is the role of Flask Blueprints?",
                "a": "Connecting to external relational databases",
                "b": "Organizing related routes, views, and templates into modular application components",
                "c": "Compiling CSS files into minified production assets",
                "d": "Encrypting passwords before saving to the database",
                "correct": "B", "diff": "Medium",
                "exp": "A Blueprint in Flask provides modular application structuring, allowing routes to be organized into clean, reusable subsystems."
            },
            {
                "skill": "Python & Backend APIs",
                "text": "Why should password hashing use algorithms like PBKDF2, bcrypt, or Argon2 instead of plain MD5 or SHA-256?",
                "a": "MD5 cannot hash strings longer than 16 characters",
                "b": "Plain hashes are fast to compute, making them vulnerable to brute-force and rainbow table attacks",
                "c": "Python standard library does not support SHA-256",
                "d": "PBKDF2 compresses the password to save database storage",
                "correct": "B", "diff": "Medium",
                "exp": "PBKDF2 uses salting and configurable iteration counts to intentionally slow down computation, thwarting GPU/rainbow table brute force."
            },

            # Data Structures & Algorithms
            {
                "skill": "Data Structures & Algorithms",
                "text": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST)?",
                "a": "O(1)", "b": "O(log n)", "c": "O(n)", "d": "O(n log n)",
                "correct": "C", "diff": "Medium",
                "exp": "In the worst case, an unbalanced BST degenerates into a linear linked list where searching requires traversing all n nodes (O(n))."
            },
            {
                "skill": "Data Structures & Algorithms",
                "text": "Which data structure follows the Last-In, First-Out (LIFO) order and is used for function call stacks?",
                "a": "Queue", "b": "Stack", "c": "Priority Queue", "d": "Hash Map",
                "correct": "B", "diff": "Beginner",
                "exp": "A Stack operates on the LIFO principle, making it the foundational structure for recursive call stacks and expression parsing."
            },
            {
                "skill": "Data Structures & Algorithms",
                "text": "Which sorting algorithm achieves an average and worst-case time complexity of O(n log n) by recursively dividing arrays?",
                "a": "Bubble Sort", "b": "Quick Sort", "c": "Merge Sort", "d": "Selection Sort",
                "correct": "C", "diff": "Medium",
                "exp": "Merge Sort divides the array into halves and merges sorted sub-arrays, guaranteeing O(n log n) even in worst-case conditions."
            },

            # Database Systems & SQL
            {
                "skill": "Database Systems & SQL",
                "text": "What is the purpose of database normalization up to Third Normal Form (3NF)?",
                "a": "To speed up full-text document searches",
                "b": "To eliminate data redundancy and prevent insertion, update, and deletion anomalies",
                "c": "To convert relational tables into NoSQL document collections",
                "d": "To bypass the need for primary and foreign key constraints",
                "correct": "B", "diff": "Medium",
                "exp": "3NF ensures that all attributes are functionally dependent only on the primary key, eliminating transitive dependencies and redundancies."
            },
            {
                "skill": "Database Systems & SQL",
                "text": "Which SQL clause is used to filter records resulting from an aggregate function like COUNT() or AVG()?",
                "a": "WHERE", "b": "HAVING", "c": "ORDER BY", "d": "GROUP BY",
                "correct": "B", "diff": "Beginner",
                "exp": "WHERE filters rows before aggregation, whereas HAVING filters grouped result sets after aggregation functions are evaluated."
            },
            {
                "skill": "Database Systems & SQL",
                "text": "In relational database ACID properties, what does 'Atomicity' guarantee?",
                "a": "Data is synchronized across multiple physical disks",
                "b": "All operations within a transaction succeed completely or none take effect at all",
                "c": "Concurrent transactions do not interfere with each other",
                "d": "Committed transactions survive server power crashes",
                "correct": "B", "diff": "Beginner",
                "exp": "Atomicity ensures that a transaction is treated as an indivisible single unit: either all modifications succeed, or the entire transaction rolls back."
            },

            # Operating Systems & Networks
            {
                "skill": "Operating Systems & Networks",
                "text": "What are the four necessary conditions for a Deadlock to occur in an operating system?",
                "a": "Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait",
                "b": "Paging, Segmentation, Swapping, Thrashing",
                "c": "Process, Thread, Semaphore, Mutex",
                "d": "First-Come, Shortest-Job, Priority, Round-Robin",
                "correct": "A", "diff": "Advanced",
                "exp": "Coffman's four conditions are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. If any one is prevented, deadlock cannot occur."
            },
            {
                "skill": "Operating Systems & Networks",
                "text": "Which protocol operates at the Transport Layer of the OSI Model and provides reliable, connection-oriented data transmission?",
                "a": "UDP", "b": "IP", "c": "TCP", "d": "HTTP",
                "correct": "C", "diff": "Beginner",
                "exp": "TCP (Transmission Control Protocol) establishes a connection via 3-way handshake and guarantees in-order, error-checked delivery."
            },

            # Quantitative Aptitude
            {
                "skill": "Quantitative Aptitude",
                "text": "A train 180 meters long is traveling at 54 km/h. How many seconds will it take to pass a stationary signal pole?",
                "a": "10 seconds", "b": "12 seconds", "c": "15 seconds", "d": "18 seconds",
                "correct": "B", "diff": "Beginner",
                "exp": "54 km/h = 54 * (5/18) = 15 m/s. Time to pass pole = Distance / Speed = 180 / 15 = 12 seconds."
            },
            {
                "skill": "Quantitative Aptitude",
                "text": "If a student buys an article for Rs. 400 and sells it for Rs. 500, what is the profit percentage?",
                "a": "20%", "b": "25%", "c": "30%", "d": "15%",
                "correct": "B", "diff": "Beginner",
                "exp": "Profit = 500 - 400 = 100. Profit % = (Profit / Cost Price) * 100 = (100 / 400) * 100 = 25%."
            },

            # Data Analysis & Statistics
            {
                "skill": "Data Analysis & Statistics",
                "text": "Which measure of central tendency is least sensitive to extreme outliers in skewed datasets?",
                "a": "Mean", "b": "Median", "c": "Variance", "d": "Standard Deviation",
                "correct": "B", "diff": "Beginner",
                "exp": "The Median is the middle value and remains robust against extreme high or low outlier values, unlike the arithmetic mean."
            }
        ]

        for q in questions_data:
            skill_obj = skills_dict[q["skill"]]
            question = AssessmentQuestion(
                skill_id=skill_obj.id,
                question_text=q["text"],
                option_a=q["a"],
                option_b=q["b"],
                option_c=q["c"],
                option_d=q["d"],
                correct_option=q["correct"],
                difficulty=q["diff"],
                explanation=q["exp"]
            )
            db.session.add(question)

        db.session.commit()
        print("Database initialized and seeded successfully!")
        print(f"-> Skills: {len(skills_data)}")
        print(f"-> Job Roles: {len(roles_data)}")
        print(f"-> Questions: {len(questions_data)}")
        print(f"-> Demo Student: student@college.edu / student123")
        print(f"-> Demo Admin:   admin@college.edu / admin123")


if __name__ == '__main__':
    seed_database()

