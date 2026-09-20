# Báo Cáo Cá Nhân — Lab 7

**Họ tên:** Trần Vũ Gia Huy

**MSSV:** 2A20262705

**Nhóm:** TikTok Shop Policy Retrieval
**Ngày:** 20/09/2026

## 1. Khởi động (5 điểm)

Cosine similarity cao nghĩa là hai vector hướng gần giống nhau, nên văn bản thường gần nhau về nội dung dù không dùng đúng cùng từ. Ví dụ cao: “Khách hàng được hoàn tiền khi sản phẩm bị lỗi” và “Người mua có thể nhận lại tiền nếu hàng hóa hỏng”. Ví dụ thấp: “Người bán phải xử lý yêu cầu trả hàng” và “Thời tiết Hà Nội có mưa”. Cosine đo hướng nên ít bị ảnh hưởng bởi độ lớn vector/độ dài văn bản hơn Euclid.

Với 10.000 ký tự, `chunk_size=500`, `overlap=50`: `ceil((10000-50)/(500-50)) = 23 chunks`; chạy `FixedSizeChunker` cũng cho 23. Tăng overlap lên 100 cho `ceil(9900/400) = 25 chunks`. Overlap tăng chi phí nhưng giảm mất ngữ cảnh ở biên.

## 2. Hướng tiếp cận (10 điểm)

- `SentenceChunker`: dùng look-behind `(?<=[.!?])` để tách sau dấu câu mà giữ dấu, gom tối đa N câu; text trắng trả `[]`. Hạn chế: chữ viết tắt/số thập phân có thể bị cắt sai.
- `RecursiveChunker`: thử đoạn → dòng → câu → từ → cắt cứng. Mảnh dài đệ quy xuống separator nhỏ hơn, mảnh nhỏ liền kề được gom lên gần `chunk_size`. Có base case cho text rỗng, vừa kích thước, hết separator và separator rỗng.
- `compute_similarity`: dot product chia tích hai chuẩn L2; vector zero trả `0.0`.
- `EmbeddingStore`: in-memory ổn định trên mọi máy; copy metadata, bảo đảm `doc_id`; xếp hạng dot product. Filter ứng viên trước top-k; xóa mọi chunk có cùng `metadata.doc_id`.
- `KnowledgeBaseAgent`: truy xuất top-k, đánh số nguồn `[1]...`, buộc LLM chỉ dùng ngữ cảnh và trích dẫn; store rỗng không gọi LLM.

## 3. Hoàn thiện code (30 điểm)

```text
$ .venv/bin/python -m pytest tests/ -v
platform darwin -- Python 3.11.16, pytest-9.1.1
collected 42 items
tests/test_solution.py .......................................... [100%]
42 passed in 0.14s
```

**Kết quả: 42/42 passed.** `python main.py "Chunking là gì?"` cũng chạy hết luồng nạp → search → agent.

## 4. Dự đoán similarity (5 điểm)

Điểm được tính bằng `gemini-embedding-001`, tức semantic embedding đa ngữ dùng trong benchmark chính thức.

| # | Cặp câu (rút gọn) | Dự đoán | Thực tế | Đúng? |
|---|---|---|---:|---|
| 1 | Người mua hoàn tiền trong 15 ngày / Khách hàng có 15 ngày trả hàng | cao | 0.8485 | Có |
| 2 | Người bán chịu phí trả hàng / Phí gửi trả do nhà bán hàng trả | cao | 0.8787 | Có |
| 3 | Người bán phản hồi một ngày / Tự động duyệt nếu quá hạn | trung bình | 0.7766 | Có |
| 4 | Sản phẩm còn bảo hành / Trời mưa lớn | thấp | 0.6276 | Có |
| 5 | Trả tại điểm giao nhận / Python là ngôn ngữ lập trình | thấp | 0.5551 | Có |

Cặp 2 cao nhất (0.8787), đúng dự đoán vì hai câu diễn đạt cùng trách nhiệm bằng từ khác nhau. Bất ngờ là hai cặp không liên quan vẫn có điểm dương khá cao (0.6276 và 0.5551); vì vậy không nên dùng một ngưỡng cosine cố định mà cần đánh giá thứ hạng top-k trên chính corpus.

## 5. Kết quả truy xuất cá nhân (10 điểm)

Chiến lược: `HeadingChunker(650)` có recursive fallback; backend `gemini-embedding-001`; agent dùng `gemini-3.6-flash`; 16 chunks. Top-3 và câu trả lời Gemini đầy đủ ở `ket_qua_benchmark.txt`.

| # | Query | Top-1 | Score | Kết luận có căn cứ |
|---|---|---|---:|---|
| 1 | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền sau khi nhận hàng? (`audience=buyer`) | Thời hạn gửi yêu cầu | 0.8766 | 15 ngày dương lịch |
| 2 | Người bán phải xem xét và phản hồi yêu cầu trả hàng hoàn tiền trong thời hạn nào? (`audience=seller`) | Xem xét yêu cầu | 0.8747 | 1 ngày; quá hạn tự động duyệt |
| 3 | Nếu ba lần lấy hàng tại nhà đều thất bại thì điều gì xảy ra? | Nhận hàng tại nhà | 0.8257 | Chuyển sang điểm giao nhận |
| 4 | Ai chịu phí trả hàng khi lỗi thuộc về người bán? | Trách nhiệm và phí | 0.8709 | Người bán chịu phí |
| 5 | Người bán có bao nhiêu ngày khiếu nại yêu cầu chỉ hoàn tiền? | Khiếu nại chỉ hoàn tiền | 0.9059 | 15 ngày dương lịch |

**5/5 query có bằng chứng ở top-1, đạt 10/10.** Filter được áp dụng đúng cho câu 1 (`buyer`), câu 2 và 5 (`seller`); câu 3–4 chạy không filter. Sau retrieval, kết quả được đưa vào `KnowledgeBaseAgent.answer()`; agent dựng prompt có nguồn rồi gọi `llm_fn=GeminiGenerator`. `gemini-3.6-flash` trả lời đúng cả 5 câu và kèm trích dẫn. Câu 1 không lọc bị lẫn tài liệu seller trong top-3; filter loại nhiễu này. Failure case: fixed-size cắt giữa từ/ý và chỉ đạt 8/10; heading giữ section mạch lạc hơn.

| Tự đánh giá | Điểm |
|---|---:|
| Khởi động | 5/5 |
| Hướng tiếp cận | 10/10 |
| Code | 30/30 |
| Similarity | 5/5 |
| Retrieval | 10/10 |
| **Tổng** | **60/60** |
