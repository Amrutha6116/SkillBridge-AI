import sqlite3

db = sqlite3.connect("instance/skillbridge.db")

tables = [
    "users",
    "skills",
    "job_roles",
    "role_skill_requirements",
    "assessment_questions",
    "assessment_attempts",
    "assessment_responses",
    "assessment_results",
    "improvement_plans",
    "improvement_plan_tasks"
]

print("Database connection: SUCCESS")
print("\nRecord counts:")

for table in tables:
    count = db.execute(
        f'SELECT COUNT(*) FROM "{table}"'
    ).fetchone()[0]
    print(f"{table}: {count}")

db.close()