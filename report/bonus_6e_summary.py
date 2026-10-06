"""Rebuild the 6e repeatability summary from the saved run.json files."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ("baseline", "subagents", "skills-auto")
TASKS = ("code-eval", "data-eval", "logs-eval")
ROUNDS = ("main", "bonus-6e-run2", "bonus-6e-run3")


def load(condition: str, task: str, round_name: str) -> dict:
    folder = "results" if round_name == "main" else f"results/{round_name}"
    path = ROOT / folder / condition / task / "run.json"
    return json.loads(path.read_text(encoding="utf-8"))


def pct(record: dict) -> float:
    return record["passed"] / record["total"]


lines = [
    "# Thử thách mở rộng 6e: lặp để đo nhiễu",
    "",
    "Mỗi điều kiện được chạy trên cùng ba tác vụ đánh giá thêm hai lần. Kết quả chính và hai lần lặp được giữ riêng; các lượt bonus nằm trong `results/bonus-6e-run2/` và `results/bonus-6e-run3/`. Chạy tuần tự trong Docker với `gpt-4o-mini`, temperature 0, recursion_limit 60.",
    "",
    "## Tóm tắt",
    "",
    "| Điều kiện | Điểm trung bình chính | Trung bình 3 lượt (từng task chuẩn hóa, %) | Khoảng điểm task quan sát được | Token trung bình/lượt, 3 lần (khoảng theo lượt) | Lượt GraphRecursionError |",
    "|---|---:|---:|---|---:|---:|",
]

for condition in CONDITIONS:
    records = {round_name: [load(condition, task, round_name) for task in TASKS]
               for round_name in ROUNDS}
    round_scores = [sum(pct(r) for r in records[round_name]) / len(TASKS)
                    for round_name in ROUNDS]
    all_records = [r for round_name in ROUNDS for r in records[round_name]]
    all_scores = [pct(r) for r in all_records]
    per_task = [[pct(records[round_name][i]) for round_name in ROUNDS]
                for i in range(len(TASKS))]
    task_ranges = ", ".join(
        f"{task} {min(vals)*100:.1f}–{max(vals)*100:.1f}%"
        for task, vals in zip(TASKS, per_task)
    )
    round_tokens = [sum(r["tokens"]["total"] for r in records[name]) // len(TASKS)
                    for name in ROUNDS]
    errors = sum("GraphRecursionError" in (r.get("error") or "") for r in all_records)
    main_mean = round_scores[0]
    three_mean = sum(all_scores) / len(all_scores)
    lines.append(
        f"| `{condition}` | {main_mean:.3f} | {three_mean*100:.1f}% "
        f"(lượt: {', '.join(f'{x*100:.1f}%' for x in round_scores)}) | {task_ranges} | "
        f"{sum(round_tokens)//len(round_tokens):,} ({min(round_tokens):,}–{max(round_tokens):,}) | {errors}/9 |"
    )

lines += [
    "",
    "## Điểm mỗi tác vụ qua ba lần chạy",
    "",
    "| Điều kiện | Tác vụ | Lượt chính | Lặp 1 | Lặp 2 | Trung bình | Khoảng |",
    "|---|---|---:|---:|---:|---:|---:|",
]
for condition in CONDITIONS:
    for task in TASKS:
        vals = [pct(load(condition, task, round_name)) for round_name in ROUNDS]
        lines.append(
            f"| `{condition}` | `{task}` | "
            + " | ".join(f"{load(condition, task, name)['passed']}/{load(condition, task, name)['total']}"
                          for name in ROUNDS)
            + f" | {sum(vals)/len(vals)*100:.1f}% | {min(vals)*100:.1f}–{max(vals)*100:.1f}% |"
        )

lines += [
    "",
    "## Nhận xét",
    "",
    "Các lượt lặp cho thấy thứ hạng giữa điều kiện không ổn định theo từng tác vụ: `baseline` giữ nguyên điểm code/data nhưng `logs-eval` dao động; `subagents` dao động ở code-eval trong khi data/logs không đổi; `skills-auto` dao động ở cả code-eval và data-eval. Vì vậy điểm skills-auto cao hơn ở tác vụ đánh giá trong lần chạy chính không đủ chứng minh skill gây ra cải thiện. Báo cáo chính ghi `skills_read = 0/6`; kết quả bonus cũng không thể được quy cho việc tác tử đọc skill nếu trường này vẫn bằng 0.",
    "",
    "`GraphRecursionError` xuất hiện lặp lại ở code-eval của cả ba điều kiện, ở data-eval của baseline và skills-auto, và ở cả ba lần code-eval của skills-auto. Điểm bị chặn bởi vòng gọi công cụ dài; đây là nguồn nhiễu và chi phí token chính. Lượt subagents code-eval cũng chạm recursion limit ở cả hai lần lặp.",
    "",
    "Thiết kế này chỉ có ba tác vụ và ba lượt cho mỗi điều kiện. Khoảng min–max mô tả đúng các lượt đã quan sát, không phải khoảng tin cậy. Các lần lặp dùng chung mô hình và harness; kết quả chưa cho phép khái quát sang mô hình khác.",
    "",
    "## Tái lập",
    "",
    "Từ thư mục gốc, sau khi chạy xong cả hai thư mục bonus:",
    "",
    "```powershell",
    "python report/bonus_6e_summary.py",
    "```",
    "",
]
(ROOT / "report" / "bonus-6e.md").write_text("\n".join(lines), encoding="utf-8")
print("Wrote report/bonus-6e.md")
