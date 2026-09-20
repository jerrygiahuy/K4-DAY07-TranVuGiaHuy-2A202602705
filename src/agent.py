from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức."

        context_parts = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            source = metadata.get("source_url") or metadata.get("doc_id") or result.get("id", "không rõ")
            context_parts.append(f"[{index}] Nguồn: {source}\n{result['content']}")

        prompt = f"""Bạn là trợ lý hỏi đáp dựa trên cơ sở tri thức.
Chỉ trả lời bằng thông tin trong NGỮ CẢNH bên dưới. Trích dẫn nguồn bằng ký hiệu [1], [2], ...
Nếu ngữ cảnh không đủ để trả lời, hãy nói rõ rằng không tìm thấy thông tin.

NGỮ CẢNH:
{chr(10).join(context_parts)}

CÂU HỎI: {question}
TRẢ LỜI:"""
        return self.llm_fn(prompt)
