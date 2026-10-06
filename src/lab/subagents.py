"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {"name": "explorer",
         "description": "Use before implementation to inspect specifications, code, or unfamiliar data and identify constraints.",
         "system_prompt": "Inspect README files, docstrings and relevant inputs. Do not modify files. Report evidence, edge cases and a concise implementation plan; distinguish observations from assumptions."},
        {"name": "implementer",
         "description": "Use to implement a scoped code fix or data/log transformation with explicit requirements.",
         "system_prompt": "Follow every delegated requirement. Inspect relevant specifications, fix root causes, implement the requested outputs and run available tests. Report actual changed files, commands and results, including unresolved failures."},
        {"name": "reviewer",
         "description": "Use after implementation to independently verify outputs against requirements and edge cases.",
         "system_prompt": "Review files and run independent checks against all delegated requirements. Do not modify files. Report concrete discrepancies with paths and evidence. Do not claim success without verification."},
    ]
