import re

filepath = "mekhane/synedrion/ai_auditor.py"
with open(filepath, "r") as f:
    content = f.read()

# 1. Replace Severity.X with AuditSeverity.X
content = content.replace("Severity.CRITICAL", "AuditSeverity.CRITICAL")
content = content.replace("Severity.HIGH", "AuditSeverity.HIGH")
content = content.replace("Severity.MEDIUM", "AuditSeverity.MEDIUM")
content = content.replace("Severity.LOW", "AuditSeverity.LOW")
content = content.replace("Severity.INFO", "AuditSeverity.INFO")

# 2. Add Issue factory function at the top (after imports)
# We need to find where imports end or where Issue class used to be.
# I replaced Issue class with imports in previous step.
# Let's add it before AuditResult class.

factory_code = '''
# PURPOSE: Issue factory for compatibility
def Issue(
    code: str,
    name: str,
    severity: AuditSeverity,
    line: int,
    message: str,
    suggestion: Optional[str] = None,
) -> AuditIssue:
    """Factory to create AuditIssue from legacy Issue signature."""
    return AuditIssue(
        agent="AI-Auditor",
        code=code,
        severity=severity,
        message=f"{name}: {message}",
        location=f"Line {line}",
        suggestion=suggestion,
    )
'''

if "class AuditResult:" in content:
    content = content.replace("class AuditResult:", factory_code + "\n\nclass AuditResult:")

with open(filepath, "w") as f:
    f.write(content)

print("Migration script completed.")
