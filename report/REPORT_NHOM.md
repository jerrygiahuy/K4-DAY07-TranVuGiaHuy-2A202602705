# Báo Cáo Nhóm — Lab 7

**Nhóm:** TikTok Shop Policy Retrieval

**Thành viên:**

- Trần Vũ Gia Huy — 2A20262705
- Cao Đức Hiệp — 2A202602550
- Trần Mạnh Hùng — 2A202602708
**Ngày:** 20/09/2026

## 1. Lựa chọn tài liệu (10 điểm)

Chủ đề là trả hàng và hoàn tiền TikTok Shop Việt Nam—miền có nhiều mốc thời gian và trách nhiệm buyer/seller dễ nhầm. Nhóm chỉ dùng các link 1, 2 và 4 đã chọn; nguồn dài được tách theo section để tạo 5 tài liệu. Corpus đã bỏ menu/footer, chỉ giữ điều khoản có thể kiểm chứng.

| # | Tài liệu | Nguồn | Ngày/phiên bản | Ký tự | Metadata |
|---|---|---|---|---:|---|
| 1 | Yêu cầu trả hàng của người mua | [TikTok](https://seller-vn.tiktok.com/university/essay?default_language=vi-VN&knowledge_id=2901402355762946) | 2026-09-20 / 2024-07-18 | 739 | buyer, returns-refund, vi |
| 2 | Trả hàng cho người bán | [TikTok — link 2](https://seller-vn.tiktok.com/university/essay?course_type=1&from=search&identity=1&knowledge_id=1766935302801169&role=1) | 2026-09-20 / not-stated | 1,121 | seller, returns-refund, vi |
| 3 | Khiếu nại của người bán | [TikTok — link 2](https://seller-vn.tiktok.com/university/essay?course_type=1&from=search&identity=1&knowledge_id=1766935302801169&role=1) | 2026-09-20 / not-stated | 505 | seller, returns-appeal, vi |
| 4 | Phương thức trả hàng | [TikTok — link 4](https://seller-vn.tiktok.com/university/essay?knowledge_id=1398156382422785&lang=vi-VN) | 2026-09-20 / not-stated | 850 | seller, return-method, vi |
| 5 | Phí vận chuyển hàng trả | [TikTok — link 4](https://seller-vn.tiktok.com/university/essay?knowledge_id=1398156382422785&lang=vi-VN) | 2026-09-20 / not-stated | 532 | seller, return-fee, vi |

Đây là nguồn công khai, không có dữ liệu cá nhân; `sources.csv` khớp 1–1. Schema gồm `doc_id` (truy vết/xóa), `source_url`, `retrieved_at`, `document_version` (provenance/freshness), `audience` và `category` (filter), `language`.

## 2. Thiết kế chiến lược (15 điểm)

Baseline `ChunkingStrategyComparator(chunk_size=650)`:

| Tài liệu | Fixed count/avg | Sentence count/avg | Recursive count/avg |
|---|---:|---:|---:|
| buyer-return-refund | 2 / 369.5 | 2 / 368.0 | 2 / 368.5 |
| return-fees | 1 / 532.0 | 2 / 265.0 | 1 / 532.0 |
| return-methods | 2 / 425.0 | 3 / 281.7 | 2 / 424.0 |

| Thành viên | Chiến lược thử nghiệm | Chunks | Điểm | Điểm mạnh / yếu |
|---|---|---:|---:|---|
| Cao Đức Hiệp | Fixed 650, overlap 100 | 8 | 8/10 | Ít chunk, có overlap / có thể cắt giữa ý |
| Trần Mạnh Hùng | Recursive 650 | 8 | 9/10 | Ranh giới tự nhiên / có thể gộp nhiều section |
| Trần Vũ Gia Huy | Heading 650 + recursive fallback | 16 | 10/10 | Mạch lạc, dễ truy vết / nhiều chunk hơn |

Heading phù hợp nhất vì tiêu đề chính sách là ranh giới ngữ nghĩa; section dài được recursive-split và gắn lại heading. Với Gemini embedding, Heading đạt 10/10, Recursive đạt 9/10 và Fixed đạt 8/10. Ở câu 5, Heading đưa đúng section lên top-1 với score 0.9059.

## 3. Benchmark (10 điểm)

| # | Query | Gold answer | Chunk |
|---|---|---|---|
| 1 | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền sau khi nhận hàng? (`audience=buyer`) | 15 ngày dương lịch sau khi trạng thái đơn được cập nhật thành Đã giao hàng | buyer-return-refund / Thời hạn |
| 2 | Người bán phải xem xét và phản hồi yêu cầu trả hàng hoàn tiền trong thời hạn nào? (`audience=seller`) | Trong vòng 1 ngày dương lịch; quá hạn yêu cầu tự động được phê duyệt | seller-return-refund / Xem xét |
| 3 | Nếu ba lần lấy hàng tại nhà đều thất bại thì điều gì xảy ra? | Phương thức chuyển sang trả tại điểm giao nhận | return-methods / Nhận tại nhà |
| 4 | Ai chịu phí trả hàng khi lỗi thuộc về người bán? | Người bán chịu phí vận chuyển trả hàng | return-methods / Trách nhiệm và phí |
| 5 | Người bán có bao nhiêu ngày để khiếu nại yêu cầu chỉ hoàn tiền? (`audience=seller`) | 15 ngày dương lịch kể từ khi khoản hoàn tiền được xử lý | seller-appeals / Khiếu nại chỉ hoàn tiền |

Với heading, mọi query có đáp án ở top-1. Câu 1, 2 và 5 dùng filter đúng theo bộ câu hỏi; câu 3–4 không filter. Benchmark đưa kết quả qua `KnowledgeBaseAgent.answer()`, nơi prompt được dựng từ các chunk và `llm_fn` gọi `gemini-3.6-flash`; model trả lời đúng, có trích dẫn cho cả 5 câu. A/B câu 1: không filter, top-3 có cả chunk seller; với `audience=buyer`, cả ba đều đúng tài liệu buyer.

Benchmark chính thức dùng semantic embedding `gemini-embedding-001` và model sinh câu trả lời `gemini-3.6-flash`. `bench.py` vẫn có lexical fallback để chạy offline, nhưng số liệu trong báo cáo và `ket_qua_benchmark.txt` là kết quả Gemini thật.

## 4. Demo và bài học (5 điểm)

Demo: chạy `.venv/bin/python bench.py`, trình bày A/B câu 1 và heading câu 5. Ba insight: pre-filter tránh tài liệu sai audience chiếm top-k; heading tăng coherence/traceability; kiểm nội dung chứa đáp án nghiêm ngặt hơn kiểm `doc_id`.

Failure case là fixed-size bắt đầu chunk giữa từ và nối hai section. Nó chưa gây sai trên corpus nhỏ nhưng làm grounding khó đọc. Nếu làm lại, nhóm sẽ thêm hard-negative cùng từ khóa nhưng khác audience, bổ sung ngày hiệu lực chính thức, và dùng semantic embedder.

| Tự đánh giá | Điểm |
|---|---:|
| Corpus | 10/10 |
| Strategy | 15/15 |
| Retrieval | 10/10 |
| Demo | 5/5 |
| **Tổng** | **40/40** |
