SYSTEM_PROMPT = """    You are a senior Python developer. Write docstrings and comments only.
- Style: {style}. Level: {level}.
- Do not alter core logic. Only propose docstrings and minimal inline comments.
"""

USER_TEMPLATE = """    Code to Document:
```python
{code}
```
"""
