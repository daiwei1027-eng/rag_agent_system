from sentence_transformers import CrossEncoder
from rag_agent_system.models import RetrievedChunk
from dataclasses import replace
class CrossEncoderReranker:
    def __init__(
        self,
        model_name: str,
        *,
        max_length: int = 512,
        batch_size: int = 8,
    ) -> None:
        # 1. 将三个参数保存为实例属性。
        # 2. 声明 self._model，初始值为 None。
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self._model=None

    def prepare(self) -> None:
        """Load the reranker before timed evaluation queries."""
        self._load_resources()

    def _load_resources(self) -> None:
        if self._model is not None:
            return

        self._model = CrossEncoder(
            self.model_name,
            max_length=self.max_length,
        )

    def rerank(
            self,
            query: str,
            documents: list[RetrievedChunk],
            top_k: int,
    ) -> list[RetrievedChunk]:
        # 1. 检查 query 是非空字符串，top_k 是正整数。
        # 2. documents 为空时返回 []。
        # 3. 调用 self._load_resources()。
        # 4. 构造 pairs，每项为 (query, document.chunk.text)。
        # 5. 调用 self._model.predict() 获取 scores。
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        query = query.strip()
        if not query:
            raise ValueError("query cannot be empty.")
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")
        if not documents:
            return []
        self._load_resources()
        pairs = [
            (query, document.chunk.text)
            for document in documents
        ]
        scores = self._model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False,
        )
        if len(scores) != len(documents):
            raise ValueError("Score count does not match document count.")
        rerank_pairs=[
            (document,float(score))
            for (document,score) in zip(documents, scores)
        ]
        rerank_pairs.sort(key=lambda pair: pair[1], reverse=True)
        results:list[RetrievedChunk] = []
        for i,(document,score) in enumerate(rerank_pairs,start=1):
            if i > top_k:
                break
            reranked_pair=replace(document,rerank_score=score,rerank_rank=i)
            results.append(reranked_pair)
        return results
