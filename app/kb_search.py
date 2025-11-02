from pathlib import Path
from typing import List, Dict
import math, re
from collections import Counter

TOKEN = re.compile(r"[A-Za-z0-9]+")

def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN.findall(text)]

class KBSearch:
    def __init__(self, kb_dir: str):
        self.kb_dir = Path(kb_dir)
        self.docs: List[str] = []
        self.meta: List[Dict] = []
        self.doc_tokens: List[List[str]] = []
        self.df: Counter = Counter()
        self.N: int = 0
        self._load()

    def _load(self):
        self.docs = []
        self.meta = []
        self.doc_tokens = []
        self.df = Counter()

        for p in sorted(self.kb_dir.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="ignore")
            self.docs.append(text)
            self.meta.append({"title": p.stem, "path": str(p)})
            toks = _tokenize(text)
            self.doc_tokens.append(toks)
            # document frequency per term
            for term in set(toks):
                self.df[term] += 1

        self.N = len(self.docs)

    def _score(self, query: str, i: int) -> float:
        """Simple TF-IDF cosine-like score without external libs."""
        if self.N == 0:
            return 0.0
        q_toks = _tokenize(query)
        if not q_toks:
            return 0.0

        doc = self.doc_tokens[i]
        if not doc:
            return 0.0

        tf_doc = Counter(doc)
        len_doc = len(doc)

        tf_q = Counter(q_toks)
        len_q = len(q_toks)

        # compute weighted dot product
        dot = 0.0
        norm_q = 0.0
        norm_d = 0.0

        for term, qcnt in tf_q.items():
            df = self.df.get(term, 0)
            idf = math.log((self.N + 1) / (df + 1)) + 1.0  # smooth idf
            wq = (qcnt / len_q) * idf
            norm_q += wq * wq

            dcnt = tf_doc.get(term, 0)
            wd = (dcnt / len_doc) * idf
            norm_d += wd * wd

            dot += wq * wd

        denom = math.sqrt(norm_q) * math.sqrt(norm_d)
        return dot / denom if denom else 0.0

    def search(self, query: str, k: int = 3) -> List[Dict]:
        if not self.docs:
            return []
        scores = [(i, self._score(query, i)) for i in range(self.N)]
        scores.sort(key=lambda x: x[1], reverse=True)
        out = []
        for i, s in scores[:k]:
            out.append({
                "title": self.meta[i]["title"],
                "score": float(s),
                "snippet": self.docs[i][:500],
                "path": self.meta[i]["path"],
            })
        return out
