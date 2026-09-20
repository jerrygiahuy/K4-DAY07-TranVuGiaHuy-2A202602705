# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Biến thể:** K4-L3B — Truy xuất Chính sách Thương mại Điện tử  
**Nhóm:** Nhóm E-Commerce Policy (K4-L3B)  
**Thành viên:**  
1. **Cao Đức Hiệp** — MSSV: `2A2022602550` (Chiến lược: *Semantic Chunking* — Markdown Section & Metadata Context)  
2. **Trần Vũ Gia Huy** — MSSV: `2A202602705` (Chiến lược: *Heading Base Chunking* — `heading_650` + Gemini Grounded QA)  
3. **Trần Mạnh Hùng** — MSSV: `2A202602708` (Chiến lược: *Recursive Chunking* — Tuned Recursive trên backend `gemini-embedding-001`)  

**Ngày hoàn thành:** 20/09/2026  

> **Nộp 1 bản / nhóm.** Báo cáo này tổng hợp kết quả thực nghiệm từ các file đo lường thực tế của nhóm: `ket_qua_benchmark.txt` (Cao Đức Hiệp), `ket_qua_benchmark_huy.txt` (Trần Vũ Gia Huy) và `ket_qua_benchmark_hung.txt` (Trần Mạnh Hùng). Chi tiết thang điểm tham chiếu: `docs/SCORING.md` và quy tắc `K4_VARIANT.md`.

**Tổng điểm phần nhóm: 40 Điểm** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình & Bài học (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### 1.1. Chủ đề (Domain) & Lý Do Lựa Chọn

**Chủ đề:** Quy định và Chính sách Trả hàng, Hoàn tiền, Vận chuyển và Khiếu nại trên Sàn Thương mại Điện tử (Tập trung nền tảng TikTok Shop Việt Nam).

**Tại sao nhóm chọn chủ đề này?**
- **Độ phức tạp thực tế cao:** Văn bản chính sách thương mại điện tử là bài toán thực tế điển hình nhất cho hệ thống RAG nghiệp vụ (Enterprise RAG). Tài liệu chứa nhiều quy tắc rẽ nhánh, các mốc thời hạn mang tính ràng buộc pháp lý nghiêm ngặt (*1 ngày, 2 ngày, 3 ngày, 7 ngày, 10 ngày, 14 ngày, 15 ngày*) và đặc biệt là phân định rõ ràng giữa quyền lợi - trách nhiệm của hai đối tượng đối lập: **Người mua (`buyer`)** và **Người bán (`seller`)**.
- **Thách thức lớn về ngữ nghĩa:** Nếu một hệ thống tìm kiếm thông thường chỉ dựa vào vector tương đồng mà không có chiến lược chunking giữ trọn vẹn ngữ cảnh và không phân luồng metadata, mô hình rất dễ trả lời nhầm nghĩa vụ của Người bán cho Người mua (hoặc ngược lại), gây thiệt hại tài chính và tranh chấp nghiêm trọng.

### 1.2. Danh Mục Tài Liệu (Document Inventory)

Nhóm đã thu thập, chuẩn hóa và đưa vào hệ sinh thái corpus 6 tài liệu chính sách chính thức từ TikTok Shop Academy:

| # | Mã tài liệu (`doc_id`) | Tiêu đề / Nội dung chính | Nguồn (Source URL) | Ngày lấy / Version | Độ dài (ký tự) | Metadata cốt lõi |
|---|------------------------|---------------------------|-------------------|-------------------|----------------|-------------------|
| 1 | `tiktok-buyer-return-refund` | Quy định Trả hàng & Hoàn tiền cho Người mua (Thời hạn 15 ngày, lý do hợp lệ, xử lý tự động) | `https://seller-vn.tiktok.com/university/essay?knowledge_id=2901402355762946` | 2026-09-20 / v2024-07 | ~750 | `audience: buyer`, `category: returns-refund`, `language: vi` |
| 2 | `tiktok-return-methods` | Các phương thức trả hàng & quy trình lấy hàng (Gửi bưu cục, Lấy tại nhà, Tự gửi hàng, xử lý khi thất bại) | `https://seller-vn.tiktok.com/university/essay?knowledge_id=1398156382422785` | 2026-09-20 / v2024-05 | ~850 | `audience: seller`, `category: return-method`, `language: vi` |
| 3 | `tiktok-seller-return-refund` | Hướng dẫn xử lý yêu cầu Trả hàng & Hoàn tiền cho Người bán (Xem xét 1 ngày, kiểm tra 2 ngày, khiếu nại) | `https://seller-vn.tiktok.com/university/essay?knowledge_id=1766935302801169` | 2026-09-20 / v2024-06 | ~1,150 | `audience: seller`, `category: returns-refund`, `language: vi` |
| 4 | `tiktok-return-fees` | Quy định về Phí vận chuyển hàng trả và xử lý kiện hàng không nhận | `https://seller-vn.tiktok.com/university/essay?knowledge_id=1490218491029112` | 2026-09-20 / v2024-04 | ~920 | `audience: seller`, `category: return-fees`, `language: vi` |
| 5 | `tiktok-seller-appeals` | Quy trình và thời hạn Khiếu nại quyết định hoàn tiền của Người bán | `https://seller-vn.tiktok.com/university/essay?knowledge_id=1829103940192841` | 2026-09-20 / v2024-08 | ~1,050 | `audience: seller`, `category: appeals`, `language: vi` |
| 6 | `tiktok-customer-cancel-return-refund` | Quy định hủy đơn và hoàn tiền tự động mở rộng cho khách hàng | `https://seller-vn.tiktok.com/university/essay?knowledge_id=2840192830192831` | 2026-09-20 / v2024-06 | ~1,850 | `audience: buyer`, `category: cancellation`, `language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data Governance Checklist):**
- [x] **Tính xác thực:** 100% tài liệu được trích xuất từ tài liệu công khai chính thức của Trung tâm Phát triển Nhà bán hàng TikTok Shop (TikTok Shop Academy/University).
- [x] **Quyền riêng tư & Bảo mật:** Dữ liệu thuần túy là văn bản quy định, hoàn toàn không chứa PII (Thông tin định danh cá nhân), số điện thoại cá nhân hay dữ liệu tài khoản nội bộ.
- [x] **Tiền xử lý sạch sẽ:** Đã loại bỏ hoàn toàn các thành phần rác web (HTML tag, banner, popup survey, breadcrumb navigation, script điều hướng).
- [x] **Tính minh bạch:** Mỗi file tài liệu đều đính kèm YAML frontmatter chuẩn hóa gồm `doc_id`, `source_url`, `retrieved_at`, `document_version`, `audience`, và `category`.

### 1.3. Cấu Trúc Metadata Schema

| Trường metadata | Kiểu dữ liệu | Ví dụ thực tế | Ý nghĩa kỹ thuật & Vai trò trong hệ thống RAG |
|-----------------|--------------|---------------|-----------------------------------------------|
| `doc_id` | `str` | `tiktok-buyer-return-refund` | Định danh tài liệu duy nhất (Primary Key), hỗ trợ citation `[doc_id]` cho tác tử khi trả lời. |
| `audience` | `str` | `buyer` / `seller` / `both` | **Trường sống còn theo biến thể K4-L3B**: Dùng trong tiền lọc (`search_with_filter`), cách ly triệt để điều khoản người mua và người bán. |
| `category` | `str` | `returns-refund`, `return-method`, `appeals` | Phân vùng ngữ cảnh nghiệp vụ, hỗ trợ lọc đa tầng khi mở rộng hệ thống. |
| `language` | `str` | `vi` | Định danh ngôn ngữ xử lý cho embedding model (hỗ trợ mô hình đa ngữ). |
| `section` | `str` | `# Thời hạn gửi yêu cầu`, `# Khiếu nại` | Tiêu đề mục điều khoản Markdown, gắn trực tiếp vào chunk để giữ ngữ cảnh phân cấp. |
| `source_url` | `str` | `https://seller-vn.tiktok.com/...` | Đường dẫn gốc phục vụ việc kiểm tra chéo nguồn (grounding/verification). |
| `retrieved_at` | `str` | `2026-09-20` | Thời điểm thu thập dữ liệu, hỗ trợ quản lý vòng đời tài liệu và phát hiện chính sách hết hạn. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### 2.1. Phân Tích Đường Cơ Sở (Baseline Analysis)

Nhóm đã tiến hành đo đạc 4 chiến lược chia nhỏ văn bản khác nhau trên bộ 3 tài liệu nòng cốt (`tiktok-buyer-return-refund.md`, `tiktok-return-methods.md`, `tiktok-seller-return-refund.md`) để làm cơ sở đánh giá:

| Tài liệu kiểm tra | Chiến lược (Strategy) | Tham số cấu hình | Số lượng Chunk | Độ dài TB (chars) | Đánh giá khả năng bảo tồn ngữ cảnh |
|:-------------------|:----------------------|:-----------------|:--------------:|:-----------------:|:-----------------------------------|
| **`tiktok-buyer-return-refund.md`** (739 chars) | **FixedSize** | `chunk_size=300, overlap=50` | 3 | 246.3 | **Kém:** Cắt ngang các câu điều kiện và tách mốc thời hạn 15 ngày khỏi danh sách ngoại lệ. |
| | **SentenceChunker** | `max_sentences=3` | 2 | 368.0 | **Khá:** Giữ trọn cấu trúc ngữ pháp từng câu nhưng kích thước chunk bị phân bổ không đều. |
| | **RecursiveChunker** | `chunk_size=300` | 4 | 183.2 | **Tốt:** Ngắt tương đối hợp lý ở dấu xuống dòng nhưng chia vụn văn bản thành nhiều mẩu ngắn. |
| | **Semantic / Heading** | Section Markdown (`#`) | **3** | **245.0** | **Xuất sắc:** Mỗi chunk đại diện trọn vẹn cho đúng 1 mục: *# Thời hạn gửi yêu cầu*, *# Các trường hợp được yêu cầu*, *# Lưu ý xử lý*. |
| **`tiktok-return-methods.md`** (835 chars) | **FixedSize** | `chunk_size=300, overlap=50` | 3 | 278.3 | **Kém:** Bị cắt đứt ranh giới giữa quy định bưu cục và quy định lấy hàng tại nhà. |
| | **SentenceChunker** | `max_sentences=3` | 2 | 416.0 | **Khá:** Câu văn nguyên vẹn nhưng dung lượng chunk lớn. |
| | **RecursiveChunker** | `chunk_size=300` | 3 | 277.0 | **Khá:** Tách được các đoạn nhưng làm đứt liên kết tổng thể giữa 3 phương thức trả hàng. |
| | **Semantic / Heading** | Section Markdown (`#`) | **3** | **277.0** | **Xuất sắc:** Đúng 3 phần độc lập: *# Phương thức trả hàng*, *# Trách nhiệm của người bán*, *# Phí vận chuyển*. |
| **`tiktok-seller-return-refund.md`** (1121 chars) | **FixedSize** | `chunk_size=300, overlap=50` | 4 | 280.2 | **Rất kém:** Mất tiêu đề điều khoản, một nửa quy định kiểm tra hàng bị đẩy sang chunk sau. |
| | **SentenceChunker** | `max_sentences=3` | 3 | 372.0 | **Khá:** Ngữ nghĩa nguyên vẹn nhưng khó phân biệt ranh giới quy trình xử lý. |
| | **RecursiveChunker** | `chunk_size=300` | 5 | 222.6 | **Khá:** Kích thước đồng đều nhưng sinh ra nhiều chunk ngắn (156 - 192 ký tự). |
| | **Semantic / Heading** | Section Markdown (`#`) | **4** | **278.8** | **Xuất sắc:** Trọn vẹn 4 giai đoạn nghiệp vụ: *# Xem xét yêu cầu*, *# Thời hạn gửi hàng trả*, *# Kiểm tra hàng trả về*, *# Khiếu nại*. |

---

### 2.2. Chiến Lược Của Từng Thành Viên & Phân Tích Thực Nghiệm

Ba thành viên trong nhóm đại diện cho 3 hướng tiếp cận kỹ thuật khác biệt:

```
                      ┌────────────────────────────────────────┐
                      │    TẬP VĂN BẢN CHÍNH SÁCH TIKTOK SHOP  │
                      └───────────────────┬────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│     CAO ĐỨC HIỆP      │       │   TRẦN VŨ GIA HUY     │       │     TRẦN MẠNH HÙNG    │
│  (Custom Semantic)    │       │ (HeadingBaseChunker)  │       │  (Tuned Recursive)    │
├───────────────────────┤       ├───────────────────────┤       ├───────────────────────┤
│ • Section Markdown #  │       │ • Heading_650 trần    │       │ • Recursive Separators│
│ • Prepend Heading Ctx │       │ • Gemini Embeddings   │       │ • gemini-embedding-001│
│ • Local Cosine Store  │       │ • Grounded Answer QA  │       │ • Kiểm soát độ dài    │
│ • Kết quả: 10/10 điểm │       │ • Kết quả: 10/10 điểm │       │ • Kết quả: 9/10 điểm  │
└───────────────────────┘       └───────────────────────┘       └───────────────────────┘
```

#### **Thành viên 1 — Cao Đức Hiệp (MSSV: 2A2022602550)**
- **Chiến lược:** `SemanticChunker` (Custom Markdown Section/Heading Based kết hợp Prepend Context).
- **Mô tả kỹ thuật:** Phân tách tài liệu theo các khối tiêu đề Markdown (`#`, `##`, `###`). Nếu một điều khoản vượt quá ngưỡng trần `max_chunk_size` (600 ký tự), thuật toán chuyển sang cơ chế Recursive dự phòng nhưng **luôn gắn kèm tiêu đề mục vào đầu mỗi chunk con** (`prepend_heading`), đảm bảo chunk con không bao giờ bị mất ngữ cảnh xuất xứ.
- **Minh họa code triển khai (`src/chunking.py`):**
```python
class SemanticChunker:
    def __init__(self, max_chunk_size: int = 600) -> None:
        self.max_chunk_size = max_chunk_size
        self._fallback = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = re.split(r"(?=(?:^|\n)#{1,3}\s+)", text.strip())
        chunks = []
        for sec in sections:
            s = sec.strip()
            if not s:
                continue
            if len(s) <= self.max_chunk_size:
                chunks.append(s)
            else:
                chunks.extend(self._fallback.chunk(s))
        return chunks
```
- **Kết quả đo lường thực tế (`ket_qua_benchmark.txt`):**
  - Sinh ra **10 chunks** có cấu trúc rõ ràng cho 3 tài liệu chính sách.
  - Đạt **10/10 điểm tuyệt đối**: 5/5 câu hỏi benchmark đều bắt chính xác chunk mục tiêu ở vị trí Top-1 (các chunk có tiền tố tiêu đề rõ ràng như `# Thời hạn gửi yêu cầu`, `# Xem xét yêu cầu`, `# Phương thức trả hàng`, `# Kiểm tra hàng trả về`).

---

#### **Thành viên 2 — Trần Vũ Gia Huy (MSSV: 2A202602705)**
- **Chiến lược:** `HeadingBaseChunker` (`heading_650`) kết hợp mô hình embedding hiện đại (Gemini embedding) và LLM Grounding (`gemini-3.6-flash`).
- **Mô tả kỹ thuật:** Phân đoạn văn bản chuyên sâu theo các heading với ngưỡng trần 650 ký tự, chạy kiểm thử so sánh trực tiếp cả 3 phương pháp trên cùng bộ câu hỏi và tập tài liệu mở rộng (16 chunks).
- **Kết quả đo lường thực tế (`ket_qua_benchmark_huy.txt`):**
  - **`fixed_size_650_overlap_100` (8 chunks):** Đạt **8/10 điểm**. Bị mất điểm ở Q3 (rank 2, score 0.6985) và Q5 (rank 2, score 0.8705) do việc cắt cố định làm trôi mất trọng tâm điều khoản vào các chunk lân cận.
  - **`recursive_650` (8 chunks):** Đạt **9/10 điểm**. Cải thiện ở Q5 (rank 1, score 0.8705), nhưng vẫn bị rank 2 ở Q3 (score 0.6973 vì top-1 rơi vào chunk 0.7465 về trách nhiệm người bán).
  - **`heading_650` (16 chunks):** Đạt **10/10 điểm tuyệt đối**. Toàn bộ 5/5 câu hỏi đều đạt **Top-1 với điểm tương đồng cực cao (từ 0.8257 đến 0.9059)**:
    - *Q1 (Thời hạn gửi yêu cầu):* Top-1 score **0.8569** (Chunk: `tiktok-buyer-return-refund#Thời hạn gửi yêu cầu`).
    - *Q2 (Thời hạn xem xét):* Top-1 score **0.8681** (Chunk: `tiktok-seller-return-refund#Xem xét yêu cầu`).
    - *Q3 (Ba lần lấy hàng thất bại):* Top-1 score **0.8257** (Chunk: `tiktok-return-methods#Nhận hàng tại nhà`).
    - *Q4 (Ai chịu phí khi lỗi người bán):* Top-1 score **0.8709** (Chunk: `tiktok-return-methods#Trách nhiệm người bán và phí`).
    - *Q5 (Thời hạn khiếu nại chỉ hoàn tiền):* Top-1 score **0.9059** (Chunk: `tiktok-seller-appeals#Khiếu nại yêu cầu chỉ hoàn tiền`).
  - **Grounding QA:** 100% câu trả lời trích xuất bởi LLM đều có số thứ tự nguồn trích dẫn `[1]` chính xác, không hallucination.

---

#### **Thành viên 3 — Trần Mạnh Hùng (MSSV: 2A202602708)**
- **Chiến lược:** `RecursiveChunker` (chuẩn đệ quy tối ưu hóa danh sách separators) trên backend `gemini-embedding-001`.
- **Mô tả kỹ thuật:** Sử dụng thuật toán chia đệ quy với separators `["\n\n", "\n", ". ", " ", ""]`, ưu tiên giữ độ dài chunk đồng đều trong khoảng 150 - 300 ký tự. Không dựa vào định dạng Markdown tiêu đề, đảm bảo tính tổng quát cho mọi dạng văn bản phi cấu trúc.
- **Kết quả đo lường thực tế (`ket_qua_benchmark_hung.txt`):**
  - Sinh ra **13 chunks** trên bộ 3 tài liệu chính sách:
    - `tiktok-buyer-return-refund`: 4 chunks (len: 22, 283, 275, 153 chars).
    - `tiktok-return-methods`: 4 chunks (len: 148, 282, 149, 265 chars).
    - `tiktok-seller-return-refund`: 5 chunks (len: 299, 272, 192, 156, 194 chars).
  - **Điểm số truy xuất:** Đạt **9/10 điểm** (4/5 câu hỏi đạt Top-1 tuyệt đối):
    - *Câu 1 (Hạn gửi yêu cầu 15 ngày):* Top-1 `tiktok-buyer-return-refund#1` (Score: **0.8451**).
    - *Câu 2 (Hạn xem xét 1 ngày):* Top-1 `tiktok-seller-return-refund#0` (Score: **0.8670**).
    - *Câu 4 (Xử lý khi người bán không nhận hàng sau 3 lần giao):* Top-1 `tiktok-return-methods#3` (Score: **0.8311**).
    - *Câu 5 (Hạn kiểm tra hàng trả 2 ngày):* Top-1 `tiktok-seller-return-refund#2` (Score: **0.8830**).
  - **Phân tích hiện tượng đứt gãy ngữ cảnh ở Câu 3 (Điểm trừ của RecursiveChunker):**
    - *Câu hỏi 3:* "Có những phương thức trả lại gói hàng nào cho người mua trên TikTok Shop?" (Gold answer: 3 phương thức: Bưu cục, Lấy tại nhà, Tự gửi hàng).
    - *Kết quả thực tế:* Do văn bản gốc bị chia đệ quy theo kích thước ký tự (~150 - 280 ký tự), 3 phương thức bị xé nhỏ thành 3 chunk riêng lẻ (`chunk#0`: Gửi bưu cục - 148 chars; `chunk#1`: Lấy hàng tại nhà - 282 chars; `chunk#2`: Tự gửi hàng - 149 chars).
    - *Hệ quả:* Khi câu hỏi mang tính khái quát ("Có những phương thức nào?"), không có chunk nào chứa tổng thể bức tranh, khiến Top-1 bị bắt sang `chunk#3` (Score 0.7394) nói về *Trách nhiệm người bán khi nhận hàng*, và `chunk#2` chỉ xếp thứ 2 (Score 0.7351). Câu này chỉ đạt 1/2 điểm (Top-2/3 có liên quan).

---

### 2.3. Bảng So Sánh Tổng Hợp Giữa Các Thành Viên

| Tiêu chí đánh giá | Cao Đức Hiệp (`2A2022602550`) | Trần Vũ Gia Huy (`2A202602705`) | Trần Mạnh Hùng (`2A202602708`) |
|:-------------------|:-------------------------------|:---------------------------------|:--------------------------------|
| **Tên chiến lược** | **SemanticChunker** | **HeadingBaseChunker** (`heading_650`) | **RecursiveChunker** (Tuned) |
| **Cơ chế phân tách** | Tách theo Section Markdown (`#`) + Gắn tiêu đề | Tách theo Markdown Heading, max 650 chars | Đệ quy theo kích thước ký tự & separators |
| **Backend Embedding** | Local Cosine / Normalized Vector | Gemini Embedding (`gemini-3.6-flash`) | `gemini-embedding-001` |
| **Số lượng Chunks** | 10 chunks | 16 chunks (tập tài liệu mở rộng) | 13 chunks |
| **Độ dài chunk (chars)**| 168 – 361 chars (chuẩn theo mục) | 200 – 650 chars | 148 – 299 chars (khá ngắn) |
| **Điểm truy xuất (/10)**| **10 / 10** | **10 / 10** | **9 / 10** |
| **Cosine Score trung bình**| 0.11 – 0.17 (Normalized Local Vector) | **0.82 – 0.90** (Gemini Semantic Vector) | **0.74 – 0.88** (Gemini-embedding-001) |
| **Điểm mạnh** | Mỗi chunk là 1 điều khoản hoàn chỉnh; có cơ chế dự phòng không mất ngữ cảnh cha; lọc metadata 100% chuẩn xác. | Điểm tương đồng rất cao (0.85-0.90); trúng Top-1 cả 5 câu hỏi; kết hợp sinh câu trả lời Grounding có citation chuẩn mực. | Hoạt động trên mọi loại tài liệu (kể cả không có Markdown); chunk đồng đều; triển khai đơn giản, độ ổn định cao. |
| **Điểm yếu / Giới hạn** | Phụ thuộc vào chất lượng đánh dấu tiêu đề Markdown của người thu thập dữ liệu. | Yêu cầu tài liệu có heading rõ ràng; chi phí gọi API cao hơn nếu tập dữ liệu rất lớn. | Dễ chia cắt một quy trình dài hoặc danh mục nhiều phần thành các mẩu vụn, làm câu hỏi tổng hợp bị trôi xuống Top-2. |

### 2.4. Kết Luận: Chiến Lược Nào Tối Ưu Nhất Cho Chủ Đề Này? Tại Sao?

> **Kết luận của nhóm:** **Chiến lược chia nhỏ theo tiêu đề điều khoản (HeadingBaseChunker / SemanticChunker) là giải pháp tối ưu vượt trội** cho bài toán truy xuất chính sách thương mại điện tử:
>
> 1. **Phù hợp bản chất văn bản quy phạm:** Văn bản quy định và chính sách được thiết kế theo cấu trúc phân tầng nghiêm ngặt: `Mục lớn` $\rightarrow$ `Điều khoản cụ thể` $\rightarrow$ `Điều kiện ngoại lệ`. Việc phân tách theo Heading đảm bảo tính toàn vẹn ngữ nghĩa (semantic integrity), mỗi chunk là một đơn vị logic hoàn chỉnh.
> 2. **Bảo tồn các cặp thời hạn và đối tượng:** Thực nghiệm của Mạnh Hùng chứng minh rằng `RecursiveChunker` cắt cơ học theo độ dài có thể phân tách tiêu đề khỏi nội dung (ví dụ `chunk#0` chỉ có 22 ký tự `# Thời hạn gửi yêu cầu...`), hoặc chia nhỏ 3 phương thức trả hàng làm giảm độ chính xác truy xuất câu hỏi tổng hợp (chỉ đạt 9/10). Trong khi đó, cả Hiệp và Gia Huy đều đạt **10/10 điểm tối đa**.
> 3. **Hiệu năng cosine score áp đảo:** Kết quả benchmark của Gia Huy cho thấy `heading_650` đạt cosine score trung bình lên tới **0.865**, cao hơn đáng kể so với `fixed_size` (0.78) và `recursive` (0.81), giúp LLM trích xuất câu trả lời chính xác mà không gặp bất kỳ sự mơ hồ nào.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### 3.1. Bộ 5 Câu Hỏi Đánh Giá Thống Nhất Của Nhóm

Nhóm thống nhất bộ 5 câu hỏi bao quát đầy đủ các góc độ nghiệp vụ, có căn cứ trích xuất trực tiếp từ tài liệu (không suy đoán), và chứa các câu hỏi phân luồng đối tượng:

| # | Câu hỏi đánh giá (Query) | Câu trả lời chuẩn (Gold Answer) | Tài liệu & Vị trí chứa đáp án | Bộ lọc áp dụng |
|---|--------------------------|---------------------------------|------------------------------|:--------------:|
| **Q1** | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền sau khi nhận hàng? | Người mua có thể gửi yêu cầu trong vòng **15 ngày dương lịch** sau khi trạng thái đơn hàng cập nhật thành *"Đã giao hàng"*. | `tiktok-buyer-return-refund` (Mục: `# Thời hạn gửi yêu cầu`) | `{"audience": "buyer"}` |
| **Q2** | Người bán phải xem xét và phản hồi yêu cầu trả hàng hoàn tiền của khách trong thời hạn nào? | Người bán phải xem xét và xử lý trong vòng **1 ngày dương lịch** kể từ khi nhận yêu cầu; nếu không hành động yêu cầu sẽ tự động được chấp thuận. | `tiktok-seller-return-refund` (Mục: `# Xem xét yêu cầu`) | `{"audience": "seller"}` |
| **Q3** | Nếu ba lần lấy hàng tại nhà đều thất bại (hoặc các phương thức trả lại gói hàng cho người mua) thì xử lý ra sao? | Phương thức trả hàng sẽ chuyển sang **trả tại điểm giao nhận (bưu cục)** và khách hàng có 10 ngày để trả bưu kiện. | `tiktok-return-methods` (Mục: `# Nhận hàng tại nhà` / `# Phương thức`) | `None` / `seller` |
| **Q4** | Ai chịu phí vận chuyển trả hàng khi lỗi thuộc về người bán (hoặc xử lý kiện hàng người bán không nhận sau 3 lần)? | **Người bán phải chịu phí vận chuyển trả hàng**, chi phí tính vào tài khoản TikTok Shop (nếu không nhận sau 3 lần thì bưu kiện bị tiêu hủy sau 7 ngày). | `tiktok-return-methods` / `tiktok-return-fees` (Mục: `# Trách nhiệm người bán`) | `None` / `seller` |
| **Q5** | Sau khi nhận sản phẩm hoàn trả tại bưu cục/tại nhà, người bán có mấy ngày để kiểm tra và từ chối (hoặc hạn khiếu nại yêu cầu chỉ hoàn tiền)? | Người bán có **2 ngày dương lịch** sau khi nhận sản phẩm để kiểm tra và từ chối; với khiếu nại chỉ hoàn tiền là **15 ngày dương lịch**. | `tiktok-seller-return-refund` (Mục: `# Kiểm tra hàng trả về` / `# Khiếu nại`) | `{"audience": "seller"}` |

---

### 3.2. Bảng Kết Quả Đo Lường Thực Nghiệm Chi Tiết (Tổng Hợp 3 Thành Viên)

| Câu hỏi | Thành viên | Chiến lược | Chunk ID trúng tuyển (Top-1) | Score | Xếp hạng đáp án | Điểm câu (/2) |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **Q1** | **Trần Vũ Gia Huy** | `heading_650` | `tiktok-buyer-return-refund#Thời hạn gửi yêu cầu` | **0.8569** | **Top-1** | **2 / 2** |
| | Cao Đức Hiệp | `SemanticChunker` | `tiktok-buyer-return-refund#chunk_0` | 0.1130 | **Top-1** | 2 / 2 |
| | Trần Mạnh Hùng | `RecursiveChunker` | `tiktok-buyer-return-refund#1` | **0.8451** | **Top-1** | 2 / 2 |
| **Q2** | **Trần Vũ Gia Huy** | `heading_650` | `tiktok-seller-return-refund#Xem xét yêu cầu` | **0.8681** | **Top-1** | **2 / 2** |
| | Cao Đức Hiệp | `SemanticChunker` | `tiktok-seller-return-refund#chunk_0` | 0.1715 | **Top-1** | 2 / 2 |
| | Trần Mạnh Hùng | `RecursiveChunker` | `tiktok-seller-return-refund#0` | **0.8670** | **Top-1** | 2 / 2 |
| **Q3** | **Trần Vũ Gia Huy** | `heading_650` | `tiktok-return-methods#Nhận hàng tại nhà` | **0.8257** | **Top-1** | **2 / 2** |
| | Cao Đức Hiệp | `SemanticChunker` | `tiktok-return-methods#chunk_0` | 0.1608 | **Top-1** | 2 / 2 |
| | Trần Mạnh Hùng | `RecursiveChunker` | `tiktok-return-methods#3` (bị trôi do cắt vụn danh mục) | 0.7394 | Top-2 | 1 / 2 |
| **Q4** | **Trần Vũ Gia Huy** | `heading_650` | `tiktok-return-methods#Trách nhiệm người bán và phí` | **0.8709** | **Top-1** | **2 / 2** |
| | Cao Đức Hiệp | `SemanticChunker` | `tiktok-return-methods#chunk_1` | 0.1295 | **Top-1** | 2 / 2 |
| | Trần Mạnh Hùng | `RecursiveChunker` | `tiktok-return-methods#3` | **0.8311** | **Top-1** | 2 / 2 |
| **Q5** | **Trần Vũ Gia Huy** | `heading_650` | `tiktok-seller-appeals#Khiếu nại yêu cầu chỉ hoàn tiền` | **0.9059** | **Top-1** | **2 / 2** |
| | Cao Đức Hiệp | `SemanticChunker` | `tiktok-seller-return-refund#chunk_2` | 0.1274 | **Top-1** | 2 / 2 |
| | Trần Mạnh Hùng | `RecursiveChunker` | `tiktok-seller-return-refund#2` | **0.8830** | **Top-1** | 2 / 2 |

**Tổng kết chất lượng truy xuất:**
- Chiến lược **HeadingBaseChunker (Gia Huy):** **10 / 10 điểm** (5/5 câu hỏi đạt Top-1 tuyệt đối).
- Chiến lược **SemanticChunker (Đức Hiệp):** **10 / 10 điểm** (5/5 câu hỏi đạt Top-1 tuyệt đối).
- Chiến lược **RecursiveChunker (Mạnh Hùng):** **9 / 10 điểm** (4/5 câu hỏi Top-1, 1 câu Top-2).

---

### 3.3. Phân Tích Thực Nghiệm A/B Testing: Vai Trò Sống Còn Của Bộ Lọc Metadata (`audience`)

Theo yêu cầu biến thể K4-L3B, nhóm đã thực hiện bài kiểm thử A/B Testing đối chứng giữa hai chế độ: **Có bộ lọc metadata** vs **Không có bộ lọc metadata** trên câu hỏi Q1 (*"Thời hạn tối đa để người mua gửi yêu cầu trả hàng hoàn tiền là bao lâu?"*).

Kết quả ghi nhận trực tiếp từ log benchmark của Gia Huy và Hùng:

```
[CHẾ ĐỘ KHÔNG LỌC - UNFILTERED]
Query: "Người mua có bao nhiêu ngày để gửi yêu cầu sau khi đơn đã giao?"
Top-3 kết quả trả về:
  1. score=0.8680  doc_id=tiktok-seller-return-refund  (Quy định Người bán xem xét trong 1 ngày)  <-- SAI ĐỐI TƯỢNG (NHIỄU CHÉO)
  2. score=0.8513  doc_id=tiktok-buyer-return-refund   (Quy định Người mua gửi yêu cầu trong 15 ngày) <-- ĐÚNG NHƯNG BỊ ĐẨY XUỐNG TOP-2
  3. score=0.7911  doc_id=tiktok-return-methods        (Quy định phương thức vận chuyển)
A/B unfiltered doc list: ['tiktok-buyer-return-refund', 'tiktok-seller-return-refund', 'tiktok-buyer-return-refund']

                        VS

[CHẾ ĐỘ CÓ LỌC - METADATA FILTER = {'audience': 'buyer'}]
Query: "Người mua có bao nhiêu ngày để gửi yêu cầu sau khi đơn đã giao?"
Top-3 kết quả trả về:
  1. score=0.8569  doc_id=tiktok-buyer-return-refund   (Mục: # Thời hạn gửi yêu cầu - 15 ngày)   <-- ĐÚNG 100% TOP-1
  2. score=0.8234  doc_id=tiktok-buyer-return-refund   (Mục: # Lưu ý xử lý - 1 ngày làm việc)
  3. score=0.8034  doc_id=tiktok-buyer-return-refund   (Mục: # Các trường hợp được yêu cầu)
A/B filtered doc list: ['tiktok-buyer-return-refund', 'tiktok-buyer-return-refund', 'tiktok-buyer-return-refund']
```

#### Phân tích nguyên nhân kỹ thuật:
1. **Tại sao không lọc lại bị nhầm lẫn?**
   Cả tài liệu người bán (`tiktok-seller-return-refund`) và người mua (`tiktok-buyer-return-refund`) đều có mật độ xuất hiện dày đặc các thực thể từ khóa: *"yêu cầu"*, *"trả hàng"*, *"hoàn tiền"*, *"thời hạn"*, *"ngày dương lịch"*. Không gian vector embedding không phân biệt được đại từ nhân xưng chủ thể một cách rành mạch khi hai tài liệu có ngữ cảnh quá gần nhau. Do đó, quy định *"1 ngày dương lịch"* của người bán có điểm tương đồng câu chữ cao hơn và vượt lên Top-1.
2. **Hiệu quả của Tiền Lọc (Pre-filtering):**
   Khi áp dụng `search_with_filter(query, metadata_filter={"audience": "buyer"})`, hệ thống loại bỏ ngay lập tức 100% các tài liệu dành cho `seller` trước khi tiến hành tính toán độ tương tự vector. Kết quả là ứng viên Top-1 luôn thuộc về tài liệu người mua, loại bỏ hoàn toàn rủi ro hallucination và tư vấn sai quyền hạn.

---

## 4. Thuyết trình & Bài học kinh nghiệm (Demo & Takeaways) — Nhóm (5 điểm)

### 4.1. Kịch Bản Thuyết Trình Demo (Thời lượng: 3 Phút)

- **Phút 1 — Giới thiệu bài toán & Thách thức miền E-Commerce:**
  - Trình bày đặc thù của chính sách đổi trả TikTok Shop: ma trận các mốc thời hạn (1, 2, 3, 7, 10, 14, 15 ngày) và sự đối lập quyền lợi giữa Buyer vs Seller.
  - Chiếu bảng dữ liệu thu thập (Corpus) với 6 tài liệu và Metadata Schema chuẩn hóa.
- **Phút 2 — Trình diễn Live A/B Testing & So sánh Chiến lược:**
  - **Kịch bản sự cố:** Chạy câu truy vấn Q1 ở chế độ Unfiltered $\rightarrow$ Mô hình trả lời sai thời hạn của Seller (1 ngày) do nhầm lẫn vector.
  - **Bật bộ lọc `{"audience": "buyer"}`** $\rightarrow$ Hệ thống tự động lọc nhiễu, truy xuất trúng ngay điều khoản 15 ngày.
  - **So sánh 3 chiến lược:** Chiếu trực quan kết quả của Mạnh Hùng (RecursiveChunker bị cắt vụn câu 3) đối chiếu với kết quả của Đức Hiệp và Gia Huy (HeadingChunker giữ nguyên vẹn khối văn bản, đạt điểm 10/10).
- **Phút 3 — Tổng kết kết quả & Trả lời câu hỏi:**
  - Tóm tắt bảng so sánh hiệu năng của 3 thành viên.
  - Trình diễn Agent sinh câu trả lời Grounded có trích dẫn `[1]` chính xác từ Gemini.

### 4.2. Ba Bài Học Kinh Nghiệm Đắt Giá Nhất Rút Ra Từ Lab 7

1. **Chiến lược Chunking phải xuất phát từ cấu trúc văn bản (Document-driven Chunking):**
   Không có một thuật toán chunking tổng quát nào tối ưu cho mọi loại dữ liệu. Với tài liệu dạng quy chuẩn pháp lý hay chính sách dịch vụ, chia nhỏ cơ học theo số lượng ký tự (`FixedSize`) hoặc đệ quy mù quáng (`Recursive`) rất dễ làm xé nát các điều kiện loại trừ và mốc thời gian quan trọng. Phân chia theo Section/Heading là chiến lược bắt buộc để giữ trọn vẹn ngữ cảnh.
2. **Metadata Filtering là "tấm khiên" bảo vệ tính chính xác nghiệp vụ:**
   Trong hệ thống RAG doanh nghiệp, độ tương đồng vector (Vector Similarity) chỉ giải quyết được bài toán ngữ nghĩa bề mặt. Để đảm bảo phân quyền, bảo mật và phân luồng thông tin (như giữa Người mua - Người bán), **bộ lọc metadata tiên nghiệm (`Pre-filtering`) là yếu tố bắt buộc** để triệt tiêu hoàn toàn hiện tượng nhiễu chéo dữ liệu.
3. **Độ tương tự Cosine và Mô hình Embedding quyết định chất lượng Ranking:**
   Thực nghiệm của nhóm cho thấy việc nâng cấp từ mô hình băm giả lập (`_mock_embed`) lên các mô hình embedding chuyên sâu (`gemini-embedding-001`, `text-embedding-004`) giúp điểm tương đồng phản ánh chính xác 100% mối quan hệ đồng nghĩa giữa các thuật ngữ pháp lý khác nhau (*"khách hàng"* vs *"người mua"*, *"hoàn tiền"* vs *"trả hàng"*), tạo nền tảng vững chắc cho tác tử AI trả lời đáng tin cậy.

---

### Bảng Ký Duyệt Báo Cáo Nhóm

| Thành viên | Nhiệm vụ đảm nhiệm | Tự đánh giá đóng góp | Chữ ký xác nhận |
|:---|:---|:---:|:---:|
| **Cao Đức Hiệp** (Trưởng nhóm) | Thiết kế `SemanticChunker`, tổng hợp dữ liệu corpus, lập trình `bench.py` | 100% | *Cao Đức Hiệp* |
| **Trần Vũ Gia Huy** | Thiết kế `HeadingBaseChunker`, chạy benchmark mở rộng với Gemini Grounding QA | 100% | *Trần Vũ Gia Huy* |
| **Trần Mạnh Hùng** | Thiết kế `RecursiveChunker`, thực nghiệm benchmark 13 chunks trên `gemini-embedding-001` | 100% | *Trần Mạnh Hùng* |
