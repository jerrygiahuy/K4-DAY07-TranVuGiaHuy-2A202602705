"""Reproducible retrieval benchmark for the TikTok Shop policy corpus."""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from pathlib import Path

from src import Document, EmbeddingStore, FixedSizeChunker, RecursiveChunker


DATA_DIR = Path("data/tiktokshop-policy")
OUTPUT_PATH = Path("ket_qua_benchmark.txt")

BENCHMARKS = [
    {
        "query": "Người mua có bao nhiêu ngày để gửi yêu cầu sau khi đơn đã giao?",
        "gold": "15 ngày dương lịch sau khi trạng thái đơn hàng được cập nhật thành Đã giao hàng.",
        "doc_id": "tiktok-buyer-return-refund",
        "needle": "mười lăm (15) ngày",
        "filter": {"audience": "buyer"},
    },
    {
        "query": "Người bán phải xem xét yêu cầu trả hàng trong thời hạn nào?",
        "gold": "Trong vòng 1 ngày dương lịch; quá hạn yêu cầu tự động được phê duyệt.",
        "doc_id": "tiktok-seller-return-refund",
        "needle": "trong vòng 1 ngày dương lịch",
        "filter": {"audience": "seller"},
    },
    {
        "query": "Nếu ba lần lấy hàng tại nhà đều thất bại thì điều gì xảy ra?",
        "gold": "Phương thức chuyển sang trả tại điểm giao nhận.",
        "doc_id": "tiktok-return-methods",
        "needle": "chuyển thành trả tại điểm giao nhận",
        "filter": {"audience": "seller"},
    },
    {
        "query": "Ai chịu phí trả hàng khi lỗi thuộc về người bán?",
        "gold": "Người bán chịu phí vận chuyển trả hàng.",
        "doc_id": "tiktok-return-methods",
        "needle": "chịu phí vận chuyển trả hàng",
        "filter": {"audience": "seller"},
    },
    {
        "query": "Người bán có bao nhiêu ngày để khiếu nại yêu cầu chỉ hoàn tiền?",
        "gold": "15 ngày dương lịch kể từ khi khoản hoàn tiền được xử lý.",
        "doc_id": "tiktok-seller-appeals",
        "needle": "15 ngày dương lịch kể từ khi khoản hoàn tiền",
        "filter": {"audience": "seller"},
    },
]


def _plain(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


class LexicalEmbedder:
    """Dependency-free normalized hashing vector used for a reproducible benchmark."""

    def __init__(self, dim: int = 2048) -> None:
        self.dim = dim
        self._backend_name = "normalized lexical hashing (benchmark-only)"

    def __call__(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        tokens = _plain(text).split()
        for token in tokens:
            index = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dim
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class HeadingChunker:
    """Keep each Markdown section coherent; recursively split long sections."""

    def __init__(self, chunk_size: int = 650) -> None:
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = re.split(r"(?=^#{1,6}\s+)", text.strip(), flags=re.MULTILINE)
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            heading_match = re.match(r"^(#{1,6}\s+[^\n]+)", section)
            heading = heading_match.group(1) if heading_match else ""
            parts = self.fallback.chunk(section)
            for part in parts:
                if heading and not part.startswith(heading):
                    part = f"{heading}\n\n{part}"
                chunks.append(part)
        return chunks


def parse_document(path: Path) -> tuple[dict[str, str], str]:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Thiếu YAML frontmatter: {path}")
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, match.group(2).strip()


def load_corpus(chunker: object) -> tuple[EmbeddingStore, int]:
    store = EmbeddingStore("tiktokshop_policy", embedding_fn=LexicalEmbedder())
    docs: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, content = parse_document(path)
        for index, chunk in enumerate(chunker.chunk(content)):
            docs.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={**metadata, "doc_id": path.stem, "chunk_index": index},
                )
            )
    store.add_documents(docs)
    return store, len(docs)


def extract_grounded_answer(content: str, needle: str) -> str:
    """Return the sentence containing the expected evidence, never invent text."""
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", content):
        if _plain(needle) in _plain(sentence):
            return sentence.strip().lstrip("# ")
    return "Không tìm thấy câu trả lời có căn cứ trong top-3."


def evaluate(name: str, chunker: object) -> tuple[list[str], int]:
    store, chunk_count = load_corpus(chunker)
    lines = [f"\n=== {name} | {chunk_count} chunks ==="]
    total = 0
    for number, item in enumerate(BENCHMARKS, start=1):
        results = store.search_with_filter(item["query"], 3, item["filter"])
        answer_rank = next(
            (rank for rank, result in enumerate(results, start=1) if _plain(item["needle"]) in _plain(result["content"])),
            None,
        )
        points = 2 if answer_rank == 1 else 1 if answer_rank in (2, 3) else 0
        total += points
        lines.append(f"Q{number}: {item['query']}")
        lines.append(f"Gold: {item['gold']}")
        lines.append(f"Filter: {item['filter']} | answer_rank={answer_rank} | points={points}/2")
        for rank, result in enumerate(results, start=1):
            preview = " ".join(result["content"].split())[:150]
            lines.append(
                f"  {rank}. score={result['score']:.4f} doc_id={result['metadata']['doc_id']} :: {preview}"
            )
        if answer_rank is not None:
            answer = extract_grounded_answer(results[answer_rank - 1]["content"], item["needle"])
        else:
            answer = "Không tìm thấy câu trả lời có căn cứ trong top-3."
        lines.append(f"  Agent answer (extractive, grounded): {answer}")

        if number == 1:
            unfiltered = store.search(item["query"], 3)
            filtered_ids = [result["metadata"]["doc_id"] for result in results]
            unfiltered_ids = [result["metadata"]["doc_id"] for result in unfiltered]
            lines.append(f"  A/B unfiltered={unfiltered_ids}")
            lines.append(f"  A/B filtered  ={filtered_ids}")
    lines.append(f"TOTAL {name}: {total}/10")
    return lines, total


def main() -> None:
    strategies = {
        "fixed_size_650_overlap_100": FixedSizeChunker(chunk_size=650, overlap=100),
        "recursive_650": RecursiveChunker(chunk_size=650),
        "heading_650": HeadingChunker(chunk_size=650),
    }
    output = [
        "BENCHMARK CHÍNH SÁCH TIKTOK SHOP",
        "Embedding: normalized lexical hashing (không phải semantic model)",
        "Scoring: 2 điểm nếu chunk chứa đáp án ở top-1; 1 điểm ở top-2/3; 0 nếu vắng.",
    ]
    scores: dict[str, int] = {}
    for name, chunker in strategies.items():
        lines, score = evaluate(name, chunker)
        output.extend(lines)
        scores[name] = score
    output.append(f"\nSUMMARY: {scores}")
    rendered = "\n".join(output) + "\n"
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
