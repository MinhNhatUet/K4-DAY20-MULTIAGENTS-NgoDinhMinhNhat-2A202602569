# Thử thách mở rộng 6e: lặp để đo nhiễu

Mỗi điều kiện được chạy trên cùng ba tác vụ đánh giá thêm hai lần. Kết quả chính và hai lần lặp được giữ riêng; các lượt bonus nằm trong `results/bonus-6e-run2/` và `results/bonus-6e-run3/`. Chạy tuần tự trong Docker với `gpt-4o-mini`, temperature 0, recursion_limit 60.

## Tóm tắt

| Điều kiện | Điểm trung bình chính | Trung bình 3 lượt (từng task chuẩn hóa, %) | Khoảng điểm task quan sát được | Token trung bình/lượt, 3 lần (khoảng theo lượt) | Lượt GraphRecursionError |
|---|---:|---:|---|---:|---:|
| `baseline` | 0.097 | 7.5% (lượt: 9.7%, 6.4%, 6.4%) | code-eval 9.1–9.1%, data-eval 0.0–0.0%, logs-eval 10.0–20.0% | 156,400 (40,239–223,640) | 4/9 |
| `subagents` | 0.033 | 4.3% (lượt: 3.3%, 6.4%, 3.3%) | code-eval 0.0–9.1%, data-eval 0.0–0.0%, logs-eval 10.0–10.0% | 123,871 (88,169–186,349) | 3/9 |
| `skills-auto` | 0.235 | 13.1% (lượt: 23.5%, 6.4%, 9.4%) | code-eval 9.1–27.3%, data-eval 0.0–33.3%, logs-eval 10.0–10.0% | 159,420 (74,015–204,282) | 5/9 |

## Điểm mỗi tác vụ qua ba lần chạy

| Điều kiện | Tác vụ | Lượt chính | Lặp 1 | Lặp 2 | Trung bình | Khoảng |
|---|---|---:|---:|---:|---:|---:|
| `baseline` | `code-eval` | 1/11 | 1/11 | 1/11 | 9.1% | 9.1–9.1% |
| `baseline` | `data-eval` | 0/9 | 0/9 | 0/9 | 0.0% | 0.0–0.0% |
| `baseline` | `logs-eval` | 2/10 | 1/10 | 1/10 | 13.3% | 10.0–20.0% |
| `subagents` | `code-eval` | 0/11 | 1/11 | 0/11 | 3.0% | 0.0–9.1% |
| `subagents` | `data-eval` | 0/9 | 0/9 | 0/9 | 0.0% | 0.0–0.0% |
| `subagents` | `logs-eval` | 1/10 | 1/10 | 1/10 | 10.0% | 10.0–10.0% |
| `skills-auto` | `code-eval` | 3/11 | 1/11 | 2/11 | 18.2% | 9.1–27.3% |
| `skills-auto` | `data-eval` | 3/9 | 0/9 | 0/9 | 11.1% | 0.0–33.3% |
| `skills-auto` | `logs-eval` | 1/10 | 1/10 | 1/10 | 10.0% | 10.0–10.0% |

## Nhận xét

Các lượt lặp cho thấy thứ hạng giữa điều kiện không ổn định theo từng tác vụ: `baseline` giữ nguyên điểm code/data nhưng `logs-eval` dao động; `subagents` dao động ở code-eval trong khi data/logs không đổi; `skills-auto` dao động ở cả code-eval và data-eval. Vì vậy điểm skills-auto cao hơn ở tác vụ đánh giá trong lần chạy chính không đủ chứng minh skill gây ra cải thiện. `skills_read = 0` ở cả sáu lượt bonus của `skills-auto`, nên điểm ở các lượt này không thể quy cho tác tử đọc skill.

`GraphRecursionError` xuất hiện lặp lại ở code-eval của cả ba điều kiện, ở data-eval của baseline và skills-auto, và ở cả ba lần code-eval của skills-auto. Điểm bị chặn bởi vòng gọi công cụ dài; đây là nguồn nhiễu và chi phí token chính. Lượt subagents code-eval cũng chạm recursion limit ở cả hai lần lặp.

Thiết kế này chỉ có ba tác vụ và ba lượt cho mỗi điều kiện. Khoảng min–max mô tả đúng các lượt đã quan sát, không phải khoảng tin cậy. Các lần lặp dùng chung mô hình và harness; kết quả chưa cho phép khái quát sang mô hình khác.

## Tái lập

Từ thư mục gốc, sau khi chạy xong cả hai thư mục bonus:

```powershell
python report/bonus_6e_summary.py
```
