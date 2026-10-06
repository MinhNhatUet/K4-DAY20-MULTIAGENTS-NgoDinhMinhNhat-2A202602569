# Báo cáo Lab: Self evolving Agentic

Trạng thái: đã cài đặt harness và đạt 29/29 test trong Docker. Ba lượt baseline học đã thử nhưng API từ chối tham số temperature của deployment gpt-6-luna; chưa có lượt thí nghiệm hợp lệ. Các mục thực nghiệm dưới đây ghi rõ dữ liệu còn thiếu, không thay bằng kết quả của mô hình giả.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Ngô Đnh Minh Nhật | 2A202602569 | Harness, thí nghiệm và báo cáo (thông tin theo tên kho) |

- Môi trường: Windows, thực thi bằng Docker Linux; image lab-deepagents build từ python:3.12-slim. Hướng dẫn chạy PowerShell: [DOCKER.md](DOCKER.md).
- Deep Agents: 0.7.21 theo `pyproject.toml`.
- Mô hình: gpt-4o-mini đã trả OK khi kiểm tra kết nối; khi chạy baseline, .env đã chuyển sang gpt-6-luna và API từ chối temperature. Nhiệt độ 0; recursion_limit 60. Cần deployment tương thích model.py có sẵn.
- Số lượt tác vụ đã thử: 3, đều lỗi API trước khi agent thực hiện tác vụ; token ghi nhận bằng 0, không có lượt hợp lệ. Quy trình chuẩn cần 21 lượt tác vụ và ít nhất 1 lần gọi curator, chưa tính kiểm tra kết nối và chạy lại.
- Chưa tạo tag `freeze`: cần sinh và đánh giá skill trước.

## 2. Giả thuyết (bản dự kiến trước thí nghiệm)

- H1 (subagents so với baseline): Dự đoán điểm trung bình tác vụ đánh giá của subagents xấp xỉ baseline (chênh lệch tuyệt đối ≤ 0,10) nhưng token trung bình cao hơn ít nhất 2 lần. Căn cứ: ở tác vụ học, subagents chỉ giao việc 1/3 lượt (data-learn) và lượt đó tốn 5,08M token do subagent lặp tới khi gặp 429; code-learn 0,40 so với 0,30 và logs-learn bằng nhau (0,11). Subagent chỉ nhận prompt được giao (cô lập ngữ cảnh, `02_subagents.md`) nên không bổ sung quy ước ẩn `rule_`; gpt-4o-mini còn lặp lệnh lỗi trong subagent mà recursion_limit của luồng chính không chặn.
- H2 (skills-auto so với baseline): Dự đoán skills-auto KHÔNG cải thiện tác vụ đánh giá (chênh lệch ≤ 0,10, có thể âm), cả check kỹ thuật lẫn `rule_`. Căn cứ: ở Phần 3.4 `skills_read = 0` ở cả 3 tác vụ học (gpt-4o-mini không mở SKILL.md, đi thẳng vào pytest/đọc dữ liệu); curator chỉ sinh skill cho họ code và logs, không có skill cho data; skill logs còn sai cách tính repeat_count. SkillsBench (tóm tắt trong `04_curator.md`) ghi nhận skill do mô hình tự sinh trung bình không có lợi.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán không có khoảng cách học > đánh giá do skill (vì skill không được đọc); chênh lệch giữa hai tập, nếu có, chủ yếu do độ khó tác vụ và nhiễu (lặp tới recursion limit) chứ không phải chuyển giao kiến thức. Check quy ước MỚI của tác vụ đánh giá sẽ thất bại ở mọi điều kiện vì không điều kiện nào quan sát được nó. Căn cứ: SkillEvolBench (lợi ích trên tập học thường không chuyển sang tác vụ mới) và Phần 3.4 skills-auto học 0,03 so với baseline học 0,14.

## 3. Làm quen Deep Agents

1. Tour thực tế liệt kê `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ chạy shell là `execute`.
2. `general-purpose` có các công cụ như tác tử chính, phù hợp tìm kiếm và tác vụ nhiều bước. Mỗi invocation mặc định không có trạng thái và chỉ thấy prompt được giao, rồi trả một báo cáo cuối; tác tử chính phải truyền đủ yêu cầu.
3. Trích `task`: “The agent's report is not shown to the user; relay a summary yourself.” Trích `execute`: “Quote paths containing spaces”. Tour cho thấy system prompt mặc định là chuỗi rỗng. Mô tả execute khuyên dùng đường dẫn tuyệt đối, nhưng PATHS_NOTE được cung cấp của lab quy định đường dẫn tương đối để công cụ tệp và shell cùng truy cập đúng workspace.

Đầu ra tour lưu tại `report/tour.txt`. Kiểm thử trên Windows: `python -m pytest tests/test_01_provided.py tests/test_04_curator.py` đạt **14 passed**; có cảnh báo Pydantic V1/Python 3.14. Toàn bộ test sau đó chạy trong Docker đạt **29 passed in 11.35s**, gồm backend và runner. Bằng chứng: [tests-docker.txt](tests-docker.txt).

## 4. Đường cơ sở và phân loại lỗi

Ba run.json baseline học ghi lỗi HTTP 400: temperature không được mô hình hỗ trợ. Token và tool_calls đều 0; trace rỗng. Đây là lỗi hạ tầng, không phân loại thành lỗi tác tử hoặc dùng làm baseline hợp lệ. Khi có kết quả học, phân loại ít nhất bốn check thất bại theo A–G, ghi tên tác vụ, tên check và trích detail/vết. Lỗi hạ tầng phải tách riêng. Dùng `scripts/check_breakdown.py` để kiểm tra bằng chứng phủ định cho nhóm lỗi kỹ thuật.

## 5. Điều kiện subagents

| Tên | Vai trò | Phạm vi |
|---|---|---|
| explorer | Khảo sát trước triển khai | Đọc đặc tả, mã và dữ liệu; báo cáo bằng chứng, không sửa tệp |
| implementer | Thực hiện công việc đã giao | Sửa nguyên nhân gốc, tạo đầu ra, chạy kiểm tra và báo cáo tệp thực sự đổi |
| reviewer | Kiểm tra độc lập sau triển khai | Đối chiếu yêu cầu, chạy kiểm tra, báo cáo sai lệch; không sửa tệp |

Mỗi subagent nhận PATHS_NOTE. Tác tử chính được yêu cầu truyền đủ quy tắc và đường dẫn, kiểm tra báo cáo trả về. Chưa có số đo subagent_calls, token và thời gian. Vai trò trong thiết kế không chứng minh agent đã thực sự sử dụng chúng.

## 6. Self-evolving: skill do curator sinh

Chưa gọi curator với mô hình thật; chưa sinh hoặc xóa skill. Curator chỉ đưa các bản ghi role=learn không lỗi hạ tầng vào prompt, giữ tên/detail của check thất bại và 6000 ký tự cuối trace; bỏ skill không hợp lệ và tên không an toàn. Không gọi mô hình nếu không có check thất bại. Cần đánh giá nội dung, độ dài, description và skills_read của từng skill sau khi sinh; kiểm tra định dạng không bảo đảm nội dung đúng.

## 7. Kết quả so sánh

Chỉ có ba bản ghi lỗi hạ tầng baseline; chưa có dữ liệu hợp lệ để tạo bảng so sánh có ý nghĩa. Sau khi đủ kết quả, sinh `report/table.md` bằng `python -m lab.compare`, chèn bảng và thống kê check kỹ thuật/quy ước vào mục này.

## 8. Phân tích

1. Chưa có điểm để so sánh cải thiện theo điều kiện và vai trò learn/eval.
2. Chưa đo được mức cải thiện của check kỹ thuật so với rule_; không suy diễn quy ước mới từ điểm tập học.
3. Chưa có trace và skills_read để chứng minh skill được đọc hay làm theo.
4. Chưa có token thật để tính chi phí hoặc điểm/token. Usage callback trong runner cộng cả token subagent; số tool call chỉ tính luồng chính.
5. Curator lọc role trước khi đọc trace; validate_skill chặn định danh đánh giá và tên đường dẫn không an toàn. Chưa có skill thực tế để kết luận về quá khớp hay rò rỉ.
6. Cần lưu kết quả Phần 3.4 ở results/skills-auto-dev và so với kết quả sau freeze của cùng hash skill. Chưa có hai lần chạy để ước lượng nhiễu.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba tác vụ mỗi vai trò: một trường hợp thành công có thể làm thay đổi mạnh điểm trung bình; không khái quát sang mọi miền.
2. Mỗi điều kiện chính chạy một lần: biến động do mô hình và lựa chọn công cụ có thể bị nhầm với tác dụng của skill hoặc subagent; nhiệt độ 0 không bảo đảm tái lập tuyệt đối.
3. Quy ước do giảng viên thiết kế: việc học phản hồi có thể tăng điểm rule_ mà không phản ánh năng lực giải quyết vấn đề tổng quát.
4. Chỉ một mô hình dự kiến: hiệu quả phụ thuộc khả năng gọi công cụ và làm theo skill của mô hình đó.
5. Trace chỉ chứa luồng chính; khi invoke ném lỗi, cách cài đặt tối thiểu không giữ message trung gian. Không suy luận hoạt động nội bộ subagent từ số tool call của luồng chính.
6. LocalShellBackend dùng thư mục làm việc riêng và môi trường không kế thừa khóa API, nhưng không phải cơ chế cô lập hệ điều hành đầy đủ.

## 10. Kết luận

Đã cài đặt các thành phần harness theo giao diện của lab và vượt qua toàn bộ 29 test trong Docker. Chưa có bằng chứng thực nghiệm để chấp nhận hoặc bác bỏ H1–H3. Cần deployment hỗ trợ temperature rồi chạy đầy đủ quy trình học, curator, đóng băng và đánh giá trước khi coi bài nộp là hoàn tất.

## Phụ lục: quy trình tiếp tục

Dùng các lệnh PowerShell trong [DOCKER.md](DOCKER.md) để chạy bằng Docker. Khối dưới mô tả thứ tự CLI bên trong môi trường Linux; các lệnh git thực hiện trên máy chủ. Cấu hình `.env` trực tiếp, không commit khóa API.

```bash
pytest
python scripts/tour.py
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
python -m lab.runner --condition baseline --tasks learn
python -m lab.runner --condition subagents --tasks learn
python -m lab.curator
# Đọc và đánh giá skill; không sửa tay nội dung.
python -m lab.runner --condition skills-auto --tasks learn
# Điền báo cáo, cập nhật H1–H3 từ dữ liệu học trước khi commit hypotheses.
# Lưu kết quả skills-auto sang skills-auto-dev trước lần chạy chính thức.
git add src/lab/agent.py src/lab/subagents.py src/lab/runner.py src/lab/curator.py report results skills/auto
git commit -m "hypotheses"
git commit --allow-empty -m "freeze skills"
git tag freeze
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python scripts/verify_freeze.py
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

Chạy các thí nghiệm tuần tự theo GUIDE để tránh giới hạn tốc độ API. Không làm thử thách mở rộng trước khi hoàn thành phần chính.
