"""
Smart Water Usage Advisor - Lightweight Deterministic Knowledge Retriever
Location: 5_AI_COMPONENTS/chatbot/retrieval.py
Phase 3C - Week 6 Implementation

Implements a deterministic, lightweight retrieval-augmented generation (RAG) module:
- Tokenizes and cleans user queries
- Computes keyword, topic, and BM25-style term overlap scores against knowledge entries
- Ranks and filters relevant knowledge base documents with identifiable source IDs
- Fully offline, reproducible, and verifiable in unit tests
"""

import re
import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
try:
    from .knowledge_base import WaterConservationKnowledgeBase, KnowledgeEntry
except (ImportError, ValueError):
    from knowledge_base import WaterConservationKnowledgeBase, KnowledgeEntry

# Standard English conversational stopwords
STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "can", "will", "i",
    "my", "me", "we", "our", "you", "your", "he", "she", "it", "they", "them"
}

@dataclass
class RetrievalResult:
    """Structured search result with identifiable source attribution."""
    entry_id: str
    title: str
    category: str
    snippet: str
    relevance_score: float
    savings_estimate_liters_day: float
    topic: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LightweightKnowledgeRetriever:
    """
    Lightweight deterministic RAG retriever.
    Operates on structured KnowledgeEntry objects without requiring external vector databases.
    """

    def __init__(self, knowledge_base: WaterConservationKnowledgeBase):
        self.kb = knowledge_base
        self._doc_index = []
        self._doc_lengths = []
        self._idf_cache: Dict[str, float] = {}
        self._avg_dl = 0.0
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        """Sanitizes and tokenizes text into lowercased content tokens."""
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        tokens = [t for t in clean.split() if t and t not in STOPWORDS]
        return tokens

    def _build_index(self):
        """Builds term-frequency representations and IDF cache across all entries."""
        entries = self.kb.get_all_entries()
        n_docs = len(entries)
        if n_docs == 0:
            return

        doc_frequencies: Dict[str, int] = {}
        total_len = 0

        for entry in entries:
            # Combine title, keywords, category, and content
            text = f"{entry.title} {' '.join(entry.keywords)} {entry.category} {entry.topic} {entry.content}"
            tokens = self._tokenize(text)
            self._doc_index.append((entry, tokens))
            dl = len(tokens)
            self._doc_lengths.append(dl)
            total_len += dl

            seen = set(tokens)
            for t in seen:
                doc_frequencies[t] = doc_frequencies.get(t, 0) + 1

        self._avg_dl = total_len / float(n_docs) if n_docs > 0 else 1.0

        # Compute smoothed IDF for all vocabulary terms
        for term, df in doc_frequencies.items():
            self._idf_cache[term] = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.1,
        category_boost: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Retrieves top-k most relevant knowledge entries for a given user query.
        Returns empty list if query has no tokens or relevance falls below threshold.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: List[Tuple[float, KnowledgeEntry, str]] = []
        k1 = 1.5
        b = 0.75

        for i, (entry, doc_tokens) in enumerate(self._doc_index):
            dl = self._doc_lengths[i]
            token_counts: Dict[str, int] = {}
            for t in doc_tokens:
                token_counts[t] = token_counts.get(t, 0) + 1

            bm25_score = 0.0
            keyword_matches = 0

            # Match against query tokens
            for qt in query_tokens:
                if qt in token_counts:
                    tf = token_counts[qt]
                    idf = self._idf_cache.get(qt, 1.0)
                    numerator = tf * (k1 + 1.0)
                    denominator = tf + k1 * (1.0 - b + b * (dl / self._avg_dl))
                    bm25_score += idf * (numerator / denominator)

                # Extra weight for exact matches in entry's designated keywords
                if any(qt in kw.lower() for kw in entry.keywords):
                    keyword_matches += 1

            score = bm25_score + (keyword_matches * 1.5)

            # Optional boost for matching category
            if category_boost and category_boost.lower() in entry.category.lower():
                score *= 1.3

            if score > 0.0:
                # Truncate content snippet to 200 characters
                snippet = entry.content[:200] + "..." if len(entry.content) > 200 else entry.content
                scores.append((score, entry, snippet))

        # Sort descending by score
        scores.sort(key=lambda x: x[0], reverse=True)

        # Normalize scores to [0.0, 1.0] relative to top score
        results: List[RetrievalResult] = []
        if scores:
            max_s = scores[0][0]
            for s, entry, snip in scores[:top_k]:
                norm_score = round(s / max_s, 3) if max_s > 0 else 0.0
                if norm_score >= threshold:
                    results.append(RetrievalResult(
                        entry_id=entry.id,
                        title=entry.title,
                        category=entry.category,
                        snippet=snip,
                        relevance_score=norm_score,
                        savings_estimate_liters_day=entry.savings_estimate_liters_day,
                        topic=entry.topic
                    ))

        return results
