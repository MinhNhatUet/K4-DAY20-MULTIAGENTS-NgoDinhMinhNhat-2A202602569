# Chạy lab bằng Docker từ PowerShell

Chạy các lệnh tại thư mục gốc của kho. Docker Desktop phải chạy Linux containers.

```powershell
docker build -t lab-deepagents .
docker run --rm --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m pytest
```

Điền thông tin mô hình trong `.env` trước khi chạy thí nghiệm. `.dockerignore` loại `.env` và `.venv/` khỏi build context. Các lệnh sau mount kho để lưu kết quả trên máy Windows; agent làm việc trong bản sao workspace ở thư mục tạm của container.

```powershell
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.runner --condition baseline --tasks learn
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.runner --condition subagents --tasks learn
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.curator
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.runner --condition skills-auto --tasks learn
```

Dừng ở đây để đánh giá skill, ghi giả thuyết và sao lưu kết quả thử skill theo GUIDE. Chỉ chạy tập đánh giá sau commit hypotheses và tag freeze. Không sửa skill bằng tay.

```powershell
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.runner --condition baseline --tasks eval
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.runner --condition subagents --tasks eval
docker run --rm --env-file .env --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python -m lab.runner --condition skills-auto --tasks all
docker run --rm --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents sh -c 'python -m lab.compare > report/table.md'
docker run --rm --mount "type=bind,source=$($PWD.Path),target=/lab" lab-deepagents python scripts/check_breakdown.py
```

Thực hiện các lệnh git commit/tag ở máy chủ. Việc kiểm tra hash freeze phải dùng cùng hệ điều hành Linux với các lượt chạy, vì hàm hash có sẵn sử dụng dấu phân cách đường dẫn của hệ điều hành. Image gốc chưa có git; cần cài git trong container dùng để chạy `scripts/verify_freeze.py`.
