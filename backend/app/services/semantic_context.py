"""
Optional semantic workspace context (ML-ToolBox benefit: embed + similarity).
When sentence-transformers is installed and use_semantic_context is True in context,
inject "Relevant snippets" into the agent system prompt. No dependency on ML-ToolBox.
"""
import os
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

_SENTENCE_TRANSFORMERS_AVAILABLE = False
_embed_model = None

try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    pass

# Text file extensions to consider for embedding
_SNIPPET_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".md", ".txt", ".json")
_MAX_FILES = 30
_MAX_CHARS_PER_FILE = 1500
_MAX_SNIPPETS = 5
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Lazy-load the embedding model once."""
    global _embed_model
    if not _SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
    if _embed_model is None:
        try:
            _embed_model = SentenceTransformer(_MODEL_NAME)
        except Exception as e:
            logger.warning("sentence_transformers model load failed: %s", e)
            _embed_model = False  # mark as failed so we don't retry
    return _embed_model if _embed_model else None


def get_semantic_snippets(workspace_root: str, query: str, max_snippets: int = _MAX_SNIPPETS) -> List[Tuple[str, str, float]]:
    """
    Return (path, snippet_text, score) for the top snippets most similar to query.
    Returns [] if sentence_transformers is not installed or workspace_root is invalid.
    """
    if not query or not workspace_root or not os.path.isdir(workspace_root):
        return []
    model = _get_model()
    if model is None:
        return []

    # Collect file paths and snippets (path, first N chars)
    snippets: List[Tuple[str, str]] = []
    try:
        for dirpath, _dirnames, filenames in os.walk(workspace_root):
            if len(snippets) >= _MAX_FILES:
                break
            for name in filenames:
                if len(snippets) >= _MAX_FILES:
                    break
                if not any(name.endswith(ext) for ext in _SNIPPET_EXT):
                    continue
                full = os.path.join(dirpath, name)
                try:
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        text = f.read(_MAX_CHARS_PER_FILE)
                    if text.strip():
                        rel = os.path.relpath(full, workspace_root)
                        rel = rel.replace("\\", "/")
                        snippets.append((rel, text.strip()))
                except (OSError, UnicodeDecodeError):
                    continue
    except OSError:
        return []

    if not snippets:
        return []

    paths = [s[0] for s in snippets]
    texts = [s[1] for s in snippets]
    try:
        query_emb = model.encode(query, convert_to_numpy=True)
        text_embs = model.encode(texts, convert_to_numpy=True)
        # Cosine similarity (vectors are normalized by default)
        scores = (text_embs @ query_emb).tolist()
        scored = list(zip(paths, texts, scores))
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:max_snippets]
    except Exception as e:
        logger.debug("Semantic snippet search failed: %s", e)
        return []


def format_semantic_block(workspace_root: str, query: str, max_snippets: int = _MAX_SNIPPETS) -> str:
    """
    Return a string block for the system prompt: "Relevant snippets (semantic): ..."
    Empty string if not available or no snippets.
    """
    results = get_semantic_snippets(workspace_root, query, max_snippets=max_snippets)
    if not results:
        return ""
    lines = ["\nRelevant snippets (semantic match to last message):"]
    for path, text, score in results:
        preview = text.replace("\n", " ")[:200].strip()
        lines.append(f"  {path} (score={score:.2f}): {preview}")
    return "\n".join(lines)
