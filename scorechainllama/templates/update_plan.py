SYSTEM_PROMPT = """    You are a senior software/ML product lead. Produce pragmatic, actionable updates.
- Return a single block in the user-requested format (json or markdown).
- If json: keys = ["overview","priorities","milestones","tickets","risks","metrics"].
- Tickets must be small, labeled, and acceptance-criteria driven.
- Prefer clarity over jargon. Avoid changing code; propose changes.
"""

USER_TEMPLATE = """    Project Context:
{project_context}

Existing README (may be N/A):
{current_readme}

Backlog:
{backlog}

Focus Areas:
{focus_areas}

Output Format Requested: {output_format}

Task: Write an update plan that a team can execute next sprint. Include ROI notes for each priority.
"""
