# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Ngô Đinh Minh Nhật | 2A202602569 | Harness, thí nghiệm và báo cáo |

- Mô hình: `gpt-4o-mini` qua `api.openai.com` (cấu hình Azure/OpenAI-compatible của `model.py`), `LAB_TEMPERATURE=0`, `recursion_limit=60` (mặc định, giữ nguyên cho mọi lượt). Giới hạn của tổ chức: 200.000 token/phút (TPM).
- Deep Agents 0.7.21, Python 3.12, chạy trong Docker Linux (image `lab-deepagents` từ `python:3.12-slim`) trên máy Windows 11. Lệnh PowerShell: [DOCKER.md](DOCKER.md).
- Số lần chạy tác vụ: 29 lượt (21 lượt theo quy trình chuẩn + 3 lượt lỗi API gpt-6-luna + 3 lượt baseline đầu tiên mất vết + 2 lượt lỗi hạ tầng chạy lại), 3 lần gọi curator.
- Tag `freeze`: commit `b76fca2` ("freeze skills"); commit giả thuyết `f9c3697` ("hypotheses") đứng trước tag. `scripts/verify_freeze.py`: **OK** ([verify_freeze.txt](verify_freeze.txt)).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán điểm trung bình tác vụ đánh giá của subagents xấp xỉ baseline (chênh lệch tuyệt đối ≤ 0,10) nhưng token trung bình cao hơn ít nhất 2 lần. Căn cứ: ở tác vụ học, subagents chỉ giao việc 1/3 lượt (data-learn) và lượt đó tốn 5,08M token do subagent lặp tới khi gặp 429; code-learn 0,40 so với 0,30 và logs-learn bằng nhau (0,11). Subagent chỉ nhận prompt được giao (cô lập ngữ cảnh, `02_subagents.md`) nên không bổ sung quy ước ẩn `rule_`; gpt-4o-mini còn lặp lệnh lỗi trong subagent mà recursion_limit của luồng chính không chặn.
- H2 (skills-auto so với baseline): Dự đoán skills-auto KHÔNG cải thiện tác vụ đánh giá (chênh lệch ≤ 0,10, có thể âm), cả check kỹ thuật lẫn `rule_`. Căn cứ: ở Phần 3.4 `skills_read = 0` ở cả 3 tác vụ học (gpt-4o-mini không mở SKILL.md, đi thẳng vào pytest/đọc dữ liệu); curator chỉ sinh skill cho họ code và logs, không có skill cho data; skill logs còn sai cách tính repeat_count. SkillsBench (tóm tắt trong `04_curator.md`) ghi nhận skill do mô hình tự sinh trung bình không có lợi.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán không có khoảng cách học > đánh giá do skill (vì skill không được đọc); chênh lệch giữa hai tập, nếu có, chủ yếu do độ khó tác vụ và nhiễu (lặp tới recursion limit) chứ không phải chuyển giao kiến thức. Check quy ước MỚI của tác vụ đánh giá sẽ thất bại ở mọi điều kiện vì không điều kiện nào quan sát được nó. Căn cứ: SkillEvolBench (lợi ích trên tập học thường không chuyển sang tác vụ mới) và Phần 3.4 skills-auto học 0,03 so với baseline học 0,14.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tour (`report/tour.txt`) liệt kê `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task` (cùng `write_todos`). Công cụ chạy lệnh shell là `execute`.
2. `general-purpose` có cùng bộ công cụ như tác tử chính, dùng cho tìm kiếm và tác vụ nhiều bước. Mỗi lần gọi không có trạng thái: subagent chỉ thấy prompt (`description`) được giao, không thấy hội thoại của tác tử chính, và trả về một báo cáo cuối; tác tử chính phải truyền đủ yêu cầu.
3. Trích `task`: "The agent's report is not shown to the user; relay a summary yourself." Trích `execute`: "Quote paths containing spaces". System prompt mặc định rỗng nên hành vi chủ yếu do mô tả công cụ quy định; lab bổ sung `BASE_PROMPT`/`PATHS_NOTE` để công cụ tệp và shell dùng chung đường dẫn tương đối.

Test: `pytest` trong Docker đạt **29 passed** ([tests-docker.txt](tests-docker.txt)).

**Thay đổi harness trong quá trình làm.** Bản `run_task` đầu dùng `agent.invoke`; khi gặp `GraphRecursionError` toàn bộ message bị mất (trace rỗng, `tool_calls = 0`), không phân loại lỗi được. Đã đổi sang `agent.stream(..., stream_mode="values")` và giữ trạng thái cuối, nên lượt lỗi vẫn có vết đầy đủ. Ba lượt baseline đầu (không có vết) lưu ở `results/baseline-v0-no-trace/` và chỉ dùng để ước lượng nhiễu.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Baseline học: code-learn 3/10, data-learn 0/8 (GraphRecursionError), logs-learn 1/9. 22 check thất bại; bảng dưới phân loại theo nguyên nhân gốc trong vết (các check cùng nguyên nhân được gộp một dòng, số check ghi trong ngoặc).

| Tác vụ | Check thất bại | Nhóm | Bằng chứng (detail hoặc vết) |
|---|---|---|---|
| code-learn | `visible_suite_passes` | A, B | Vết: chạy `pytest workspace/tests/` từ thư mục gốc, gặp `ImportError while importing test module`, dù README ghi "Run the tests from the `workspace/` folder: cd workspace && python -m pytest". Không đọc README (5 lần `read_file`, không lần nào là README). detail: "2 failed, 6 passed". |
| code-learn | `tests_not_modified` | C | Để né ImportError, tác tử ghi đè `tests/test_report.py` (thêm `sys.path`) 4 lần, vi phạm "Do not modify the existing files in tests/". detail: "the original files in tests/ must not be modified". |
| code-learn | `parse_price_all_formats` | A, D | detail: "wrong for: ['(12.00)']". Chỉ thêm `.replace(",", "")`, bỏ qua định dạng kế toán `(12.00) -> -12.00` ghi trong docstring. |
| code-learn | `csv_quoting_follows_docstring` | A | detail: "to_csv_row returned 'Desk, large \"oak\",10.00,2'": không trích dấu ngoặc theo docstring; tác tử không sửa `export.py`. |
| code-learn | `rule_type_hints`, `rule_regression_tests`, `rule_changelog` (3) | E | detail: "RULE: every public function ... has type annotations", "RULE: add tests/test_regressions.py ...", "RULE: record each fix in CHANGELOG.md under '## Unreleased' ...". |
| data-learn | 5 check đáp án + `rule_money_in_cents`, `rule_meta_block` (7) | G (lặp), B | detail: "FileNotFoundError: ... workspace/answer.json". Vết: cùng một lệnh `python3 -c "...; with open('workspace/answer.json','w') as f: json.dump(...)"` (câu `with` trong lệnh một dòng gây SyntaxError) lặp ~25 lần tới recursion limit; không bao giờ ghi được tệp. |
| data-learn | `rule_clean_csv` | E | detail: "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents ...". |
| logs-learn | `entry_count`, `timestamps_utc`, `exception_fields`, `repeat_counts`, `counts_by_service` (5) | A, B, D | detail: "wrong number of entries (got 10)", "4/25 timestamps match", "21 wrong `exception` values". Vết chỉ có 3 tool call: đọc log 2 lần rồi `write_file` JSON viết tay; không đọc README định dạng, không viết code phân tích, không kiểm tra lại. |
| logs-learn | `rule_service_names`, `rule_sorted_errors`, `rule_schema_header` (3) | E | detail: "RULE: service names ... lower-case with '-' replaced by '_'", "RULE: `errors` is sorted by service, then by timestamp_utc", "RULE: ... \"schema_version\": 2 and \"generated_by\": \"log-triage\"". |

**Nhận xét.** Khác kỳ vọng trong GUIDE (lỗi chủ yếu nhóm E với mô hình mạnh), với gpt-4o-mini các check kỹ thuật cũng thất bại phần lớn: `check_breakdown.py` cho baseline học **4/18 check kỹ thuật** và **0/9 check quy ước** đạt. Theo số check, nhóm lỗi đông nhất là hệ quả của **G (lặp lệnh lỗi tới recursion limit)** và **A/B (không đọc đặc tả, không kiểm chứng)**; nhóm E chiếm 7/22 check nhưng có mặt ở cả ba tác vụ. Nguyên nhân chung: mô hình hành động ngay (pytest/ghi tệp) mà không đọc README/docstring, và khi lệnh lỗi thì lặp lại nguyên văn thay vì đổi cách. Một skill có thể phòng nhóm E (quy ước cố định, phát biểu rõ trong detail) và một phần A/B (checklist "đọc README trước, chạy lại test"), nhưng chỉ khi tác tử chịu đọc skill; nhóm G là giới hạn năng lực của mô hình, khó sửa bằng ngữ cảnh.

## 5. Điều kiện `subagents` (Phần 2.3)

- Subagent đã định nghĩa (`src/lab/subagents.py`), mỗi subagent nhận thêm `PATHS_NOTE`:

| Tên | Vai trò | Lý do thiết kế |
|---|---|---|
| explorer | Đọc đặc tả, mã, dữ liệu; báo cáo ràng buộc; không sửa tệp | Nhắm nhóm A (bỏ qua đặc tả) |
| implementer | Sửa nguyên nhân gốc, tạo đầu ra, chạy test, báo cáo tệp thực sự đổi | Nhắm nhóm C, F |
| reviewer | Kiểm tra độc lập theo yêu cầu, không sửa tệp, không nhận thành công khi chưa kiểm chứng | Nhắm nhóm B, F |

- `subagent_calls`: học: code 0, data 1 (`implementer`), logs 0; đánh giá: code 0, data 0, logs 1. Tổng 2/6 lượt có giao việc; explorer và reviewer chưa từng được gọi. Khi không giao việc, tác tử chính tự làm như baseline: với gpt-4o-mini, công cụ `task` chỉ được chọn khi tác vụ trông như "phân tích dữ liệu nhiều bước"; tác vụ sửa code được xem là đủ đơn giản để tự làm.
- Thông tin giao việc: ở data-learn, lời giao cho `implementer` chép đủ 5 chỉ số và quy tắc tính, có câu "adhering to Acme reporting conventions" nhưng **bỏ sót** yêu cầu ghi `clean.csv` của đề và không nêu quy ước cụ thể nào (tác tử chính cũng không biết). Báo cáo của subagent không được kiểm tra: subagent lặp bên trong tới khi gặp lỗi 429, luồng chính không nhận được báo cáo nào.
- Token và thời gian: subagents data-learn tốn **5.079.516 token, 1.520 s** (lần thử trước đó 1.182.324 token, cũng lỗi 429; lưu ở `results/infrastructure-429/`). recursion_limit=60 chỉ áp dụng cho luồng chính, không chặn vòng lặp bên trong subagent. Trung bình token học: subagents 1.759.490 so với baseline 168.541 (gấp ~10 lần, chủ yếu do một lượt chạy mất kiểm soát). Ở tác vụ đánh giá subagents dùng 97.097 token/lượt (ít hơn baseline 205.323) vì data-eval kết thúc sớm sau 7 call với 0/9.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 3 (lần đầu + 2 lần chạy lại tối đa cho phép).
  - Lần 1: 3 skill, đều chỉ cho họ code (`add-regression-tests`, `enforce-type-annotations`, `maintain-changelog`). **Xóa cả 3** vì (a) không có skill nào cho quy ước logs/data dù detail có RULE rõ ràng, (b) có bước gây hại/không thực hiện được trong sandbox ("Commit ... Push the changes to the repository", "Confirm ... continuous integration pipeline"), (c) `add-regression-tests` bảo ghi changelog "for each regression test" mâu thuẫn với định dạng `fix(<function name>)`. Bản lưu: `report/curator-run1/`. Sửa prompt của `curate_skills` (không sửa skill): yêu cầu phủ mọi loại tác vụ, một skill mỗi loại, không có bước git/CI.
  - Lần 2: mô hình sinh 3 skill nhưng `validate_skill` loại cả 3 vì tên có dấu gạch dưới (`test_functionality`, `log_parsing`, `csv_formatting`). Bổ sung ví dụ tên hợp lệ vào prompt.
  - Lần 3 (cuối): 2 skill hợp lệ, giữ nguyên, không sửa tay.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai | Độ dài, `description`, `skills_read` (Phần 3.4) |
|---|---|---|---|
| `code-testing-conventions` | Khá tổng quát: nêu quy ước Acme (type hints, `tests/test_regressions.py` ≥ 3 test, CHANGELOG `## Unreleased` ≥ 3 mục, không sửa test cũ), không nhắc tên hàm hay tệp riêng của code-learn. | Đúng một phần: bỏ mất định dạng bắt buộc `- fix(<function name>): ...`; mục 6–10 ("review the test coverage", "document changes in test cases") chung chung, không kiểm chứng được. Thiếu bài học kỹ thuật quan trọng nhất của vết: chạy test từ `workspace/` theo README. | 20 dòng. description "Use when you need to ensure that code changes adhere to testing conventions" hơi hẹp: tác vụ được phát biểu là "fix the failing test suite", không nói "conventions". `skills_read = 0`. |
| `log-triage-conventions` | Tổng quát cho họ logs: quy ước tên service, sắp xếp, header schema; không có con số hay tên tệp log. | **Có chỗ sai**: bước 6 "Count occurrences of each error message to determine repeat_count" mâu thuẫn với đề (repeat_count = 1 + tổng N của dòng "last message repeated N times"). Bước 8 chỉ nói "include `schema_version` and `generated_by`" mà không nêu giá trị (2, "log-triage") có trong detail. | 20 dòng. description "Use when you need to parse logs and generate structured error reports" phù hợp tình huống kích hoạt. `skills_read = 0`. |

Không có skill cho họ data: detail của data-learn chủ yếu là `FileNotFoundError` (tác tử không ghi được tệp), chỉ có một RULE (`rule_clean_csv`), nên curator không có đủ phản hồi để rút quy ước. Không có skill nào chứa định danh tác vụ đánh giá (`validate_skill` đạt).

Phần 3.4 (`results/skills-auto-dev/`): code-learn 1/10, data-learn 0/8, logs-learn 0/9; **`skills_read = 0` ở cả 3 lượt**. Vết code-learn: tác tử `glob` → đọc 4 tệp nguồn → `pytest workspace/tests/` rồi lặp cùng lệnh `pytest -m "not slow" ... --ignore=...` hơn 15 lần; không lần nào `read_file` vào `skills/`.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

`report/table.md` (sinh bằng `python -m lab.compare`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 3/10 | 4/10 | 0/10 |
| data-learn | 0/8 | 0/8 | 2/8 |
| logs-learn | 1/9 | 1/9 | 0/9 |
| code-eval | 1/11 | 0/11 | 3/11 |
| data-eval | 0/9 | 0/9 | 3/9 |
| logs-eval | 2/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.14 | 0.17 | 0.08 |
| **Mean score - evaluation tasks** | 0.10 | 0.03 | 0.24 |
| **Mean tokens per run** | 186,932 | 928,293 | 83,241 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

`python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      2/18         1/12         205,323      0/3
baseline      learn     4/18         0/9          168,541      0/3
subagents     eval      1/18         0/12          97,097      0/3
subagents     learn     5/18         0/9        1,759,490      0/3
skills-auto   eval      7/18         0/12          74,015      0/3
skills-auto   learn     2/18         0/9           92,468      0/3
```

Lượt có `error`:
- `GraphRecursionError` (lỗi của tác tử, được giữ và chấm điểm), 7/18 lượt: baseline data-learn, code-eval, data-eval; subagents code-learn, code-eval; skills-auto code-learn, code-eval.
- Lỗi hạ tầng: subagents data-learn (429 sau 5,08M token do subagent lặp; đã thử 2 lần, cả hai cùng mẫu, giữ lần sau làm kết quả và ghi rõ); skills-auto logs-learn ở Phần 3.4 lần đầu bị `OpenAITimeoutError` do chạy song song chạm TPM, đã chạy lại (bản lỗi ở `results/infrastructure-429/`). 3 lượt gpt-6-luna lỗi 400 `temperature` ở `results/infrastructure-gpt-6-luna/`.
- `skills_modified = false` ở mọi lượt.

## 8. Phân tích

1. **Học/đánh giá.** So với baseline, chỉ subagents nhỉnh hơn ở tác vụ học (0,17 so với 0,14, do code-learn 4/10 so với 3/10, một check); skills-auto thấp hơn ở tác vụ học (0,08) nhưng cao nhất ở tác vụ đánh giá (0,24 so với 0,10). Mẫu "tốt ở đánh giá, kém ở học" ngược với mẫu quá khớp; vì `skills_read = 0` ở mọi lượt, nó không thể do skill gây ra mà là dấu hiệu của **nhiễu giữa các lượt** (xem câu 6).
2. **Kỹ thuật và quy ước.** Check quy ước gần như luôn trượt: 1/63 check `rule_` đạt trên toàn bộ 18 lượt (baseline logs-eval `rule_sorted_errors`, một lượt duy nhất, không điều kiện nào khác đạt check này nên không có cơ chế lặp lại được). Skill không giúp check quy ước nào: skills-auto 0/9 (học) và 0/12 (đánh giá). Check quy ước **mới** của tác vụ đánh giá (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) trượt ở cả 3 điều kiện, đúng như H3: không điều kiện nào quan sát được chúng, và curator không được (và không nên) thấy dữ liệu đánh giá. Phần tăng của skills-auto đánh giá nằm hoàn toàn ở check kỹ thuật (7/18 so với 2/18).
3. **Cơ chế qua vết.**
   - Check skill *không* giúp: `rule_type_hints`/`rule_changelog` ở code-learn và code-eval. Skill `code-testing-conventions` có đúng các quy tắc này, nhưng `skills_read = 0`: vết skills-auto code-learn không có `read_file` nào vào `skills/`; tác tử dành 60 bước cho vòng lặp pytest. Nguyên nhân: skill không được đọc (mô hình không dùng cơ chế nạp dần), không phải skill thiếu.
   - Check "được cải thiện" nhưng không nhờ skill: skills-auto data-eval đạt `top_category`, `missing_total_orders`, `duplicate_events_removed` (3/9, 3 tool call, 12.951 token). Vết: tác tử đọc `orders.json`, **đọc `README.md`**, rồi viết một lệnh `python3 -c` nhiều dòng thật (có xuống dòng) nên không vấp SyntaxError. Baseline data-eval đọc tệp theo 6 đoạn, ghi `answer.json` toàn số 0, rồi lặp lệnh một dòng tới recursion limit. Không có skill nào về data, và skill không được đọc; khác biệt đến từ lựa chọn ngẫu nhiên cách viết lệnh ở bước đầu.
4. **Chi phí.** Token trung bình/lượt: baseline 186.932, subagents 928.293, skills-auto 83.241. Điểm trên 1M token (trung bình cả 6 tác vụ): baseline ~0,64, subagents ~0,11, skills-auto ~1,9. skills-auto "hiệu quả nhất" chỉ vì nhiều lượt kết thúc sớm, không phải nhờ skill. Đa tác tử **không đáng chi phí** trong thí nghiệm này: điểm không tăng (0,10 → 0,03 ở đánh giá) trong khi một lượt duy nhất tốn 5,08M token, gần 30 lần một lượt baseline, vì vòng lặp trong subagent không bị recursion_limit của luồng chính chặn.
5. **Rò rỉ và quá khớp.** Curator chỉ đọc `role == "learn"` (test_04 kiểm tra prompt không chứa tác vụ đánh giá), `validate_skill` chặn định danh của tác vụ đánh giá; hai skill cuối không chứa tên tệp dữ liệu, tên hàm hay con số của tác vụ học, chỉ có tên do quy ước Acme yêu cầu (`tests/test_regressions.py`, `CHANGELOG.md`, `## Unreleased`). Quy ước mới của tác vụ đánh giá không xuất hiện trong skill nào. Không có dấu hiệu rò rỉ; cũng không thể có quá khớp đo được vì skill không được dùng.
6. **Nhiễu.** Cùng bộ skill, tác vụ học: Phần 3.4 0,03 (1/10, 0/8, 0/9) so với sau đóng băng 0,08 (0/10, 2/8, 0/9): chênh lệch trung bình 0,05, theo từng tác vụ lên tới 0,25 (data-learn 0/8 → 2/8). Baseline học chạy hai lần (bản v0 không vết và bản chính): 0,13 (4/10, 0/8, 0/9) so với 0,14 (3/10, 0/8, 1/9), lệch từng tác vụ 0,10–0,11. Vậy với gpt-4o-mini ở nhiệt độ 0, một tác vụ có thể dao động 0,1–0,25 chỉ do nhiễu; mọi chênh lệch trung bình trong mục 7 (0,03–0,14) nằm trong hoặc sát biên độ này và **không đủ để kết luận** điều kiện nào tốt hơn.

**Đối chiếu giả thuyết.** H1 đúng về điểm (|0,03 − 0,10| ≤ 0,10) và đúng về chi phí trên toàn bộ lượt (928k so với 187k), nhưng ở riêng tác vụ đánh giá token subagents lại thấp hơn baseline (97k so với 205k). H2 sai về con số (skills-auto đánh giá +0,14) nhưng cơ chế dự đoán đúng: skill không được đọc, và phần tăng không đến từ skill. H3 đúng: không có khoảng cách học > đánh giá do skill, check quy ước mới trượt ở mọi điều kiện.

## 9. Hạn chế và tính hợp lệ

1. **Chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần.** Một check đổi kết quả làm điểm trung bình đổi 0,03–0,04; nhiễu đo được (mục 8.6) tới 0,25 mỗi tác vụ. Mọi chênh lệch trong mục 7 vì vậy chỉ là quan sát, không phải kết luận thống kê; cần ít nhất 3–5 lần lặp (hướng 6e) để có khoảng tin cậy.
2. **Một mô hình yếu (gpt-4o-mini).** Phần lớn điểm bị quyết định bởi việc tác tử có lặp tới recursion limit hay không (7/18 lượt chính thức lỗi `GraphRecursionError`), chứ không bởi điều kiện thí nghiệm. Mô hình không dùng cơ chế nạp dần skill (0/6 lượt đọc skill), nên thí nghiệm không kiểm tra được giả thuyết "skill có giúp khi được đọc". Kết luận không áp dụng cho mô hình mạnh hơn.
3. **Giới hạn hạ tầng.** Giới hạn 200k TPM gây 429/timeout; một lượt subagents data-learn bị dừng bởi 429 chứ không phải kết thúc tự nhiên, nên điểm 0/8 và 5,08M token là cận dưới của chi phí thật. Nhiệt độ 0 không bảo đảm tái lập (mục 8.6).
4. **Tác vụ và quy ước do giảng viên thiết kế.** Check `rule_` là quy ước ẩn không có trong đề; tăng điểm `rule_` chỉ đo khả năng học phản hồi, không đo năng lực giải quyết vấn đề tổng quát. Với mô hình này, ngay cả check kỹ thuật cũng trượt nhiều nên khó tách hai hiệu ứng.
5. **Curator chạy 3 lần với prompt được chỉnh giữa các lần.** Bộ skill cuối phụ thuộc vào prompt và tính ngẫu nhiên của mô hình; một lần chạy khác có thể sinh skill khác (lần 1 chỉ có skill họ code). Vết chỉ ghi luồng chính nên hoạt động bên trong subagent không quan sát được.

## 10. Kết luận

Harness hoạt động đúng (29/29 test, `verify_freeze` OK) và quy trình học → curator → đóng băng → đánh giá đã được thực hiện đầy đủ với gpt-4o-mini. Không điều kiện nào cải thiện đáng tin cậy so với baseline: chênh lệch điểm (0,03–0,14) nằm trong biên độ nhiễu đo được (tới 0,25 mỗi tác vụ), check quy ước gần như luôn trượt (1/63), và skill tự sinh không được đọc lần nào (0/6), nên điểm 0,24 của skills-auto ở tác vụ đánh giá không thể quy cho skill. Đa tác tử tốn chi phí lớn nhất (928k token/lượt trung bình) vì vòng lặp trong subagent không bị giới hạn. Đề xuất tiếp theo: giới hạn số bước cho subagent và lặp lại thí nghiệm với một mô hình gọi công cụ ổn định hơn (ví dụ gpt-4.1-mini), chạy mỗi điều kiện ≥ 3 lần để tách hiệu ứng khỏi nhiễu.

## Phụ lục

Lệnh đã chạy, theo thứ tự (PowerShell trên máy chủ: `docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents <lệnh>`; xem [DOCKER.md](DOCKER.md)):

```bash
python -m pytest                                          # 29 passed
python scripts/tour.py
python -m lab.runner --condition baseline --tasks data-learn
python -m lab.runner --condition baseline --tasks code-learn logs-learn
python -m lab.runner --condition subagents --tasks learn
python -m lab.curator                                     # 3 lần (xem mục 6)
python -m lab.runner --condition skills-auto --tasks learn
python -m lab.runner --condition subagents --tasks data-learn      # chạy lại (429)
python -m lab.runner --condition skills-auto --tasks logs-learn    # chạy lại (timeout)
mv results/skills-auto results/skills-auto-dev
git commit -m "hypotheses"; git commit --allow-empty -m "freeze skills"; git tag freeze   # trên máy chủ
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python scripts/verify_freeze.py                           # trong image có git, core.autocrlf=true
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

Ghi chú:
- `verify_freeze.py` phải chạy trên Linux vì `hash_skills` băm đường dẫn theo dấu phân cách của hệ điều hành. Image `lab-deepagents` không có git; dùng image phái sinh có cài git và đặt `core.autocrlf=true` như kho trên Windows. Nếu đặt `false`, git báo `skills/auto/README.md` khác tag chỉ vì ký tự xuống dòng (CRLF/LF), nội dung giống hệt.
- Thư mục kết quả phụ: `results/baseline-v0-no-trace/` (baseline đầu, mất vết), `results/skills-auto-dev/` (Phần 3.4), `results/infrastructure-429/`, `results/infrastructure-gpt-6-luna/` (lỗi hạ tầng). Skill của curator lần 1: `report/curator-run1/`.
- Không làm thử thách mở rộng.
